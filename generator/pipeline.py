from __future__ import annotations

import time
from dataclasses import dataclass
from logging import Logger
from pathlib import Path

import pandas as pd

from config import DEFAULT_OUTPUT_FILE, ensure_directories
from generator.attendance_dimension import build_attendance_dimension
from generator.cleaner import CleaningStats, clean_attendance_data
from generator.costcentre_dimension import build_costcentre_dimension
from generator.date_dimension import build_date_dimension
from generator.employee_dimension import build_employee_dimension
from generator.errors import AttendanceGeneratorError
from generator.excel_reader import read_raw_excel
from generator.exporter import export_star_schema
from generator.fact_builder import build_fact_attendance, validate_foreign_keys
from generator.logger import get_logger
from generator.remarks_dimension import build_remarks_dimension
from generator.shift_dimension import build_shift_dimension
from generator.validator import canonicalize_required_columns


@dataclass(frozen=True)
class GenerationResult:
    output_path: Path
    sheet_name: str
    cleaning: CleaningStats
    table_counts: dict[str, int]
    processing_seconds: float


def generate_tables(
    input_path: Path, logger: Logger | None = None
) -> tuple[dict[str, pd.DataFrame], str, CleaningStats]:
    if logger:
        logger.info("Reading Excel workbook")
    raw, sheet_name = read_raw_excel(input_path)
    if logger:
        logger.info("Sheet read: %s", sheet_name)
        logger.info("Rows read: %s", len(raw))

    if logger:
        logger.info("Validating required columns")
    canonical = canonicalize_required_columns(raw)

    if logger:
        logger.info("Cleaning raw attendance rows")
    cleaned, stats = clean_attendance_data(canonical)
    if logger:
        logger.info("Blank rows removed: %s", stats.blank_rows_removed)
        logger.info("Duplicates removed: %s", stats.duplicates_removed)
        logger.info("Rows after cleaning: %s", stats.rows_after_cleaning)
        logger.info("Invalid dates converted to null: %s", stats.invalid_dates)
        logger.info("Invalid times converted to null: %s", stats.invalid_times)

    if logger:
        logger.info("Building DIM_Employee")
    employee = build_employee_dimension(cleaned)
    if logger:
        logger.info("DIM_Employee count: %s", len(employee))

    if logger:
        logger.info("Building DIM_Date")
    date = build_date_dimension(cleaned)
    if logger:
        logger.info("DIM_Date count: %s", len(date))

    if logger:
        logger.info("Building DIM_Cost_Centre")
    costcentre = build_costcentre_dimension(cleaned)
    if logger:
        logger.info("DIM_Cost_Centre count: %s", len(costcentre))

    if logger:
        logger.info("Building DIM_Shift")
    shift = build_shift_dimension(cleaned)
    if logger:
        logger.info("DIM_Shift count: %s", len(shift))

    if logger:
        logger.info("Building DIM_Attendance_Type")
    attendance = build_attendance_dimension(cleaned)
    if logger:
        logger.info("DIM_Attendance_Type count: %s", len(attendance))

    if logger:
        logger.info("Building DIM_Remarks")
    remarks = build_remarks_dimension(cleaned)
    if logger:
        logger.info("DIM_Remarks count: %s", len(remarks))

    if logger:
        logger.info("Building FACT_Attendance")
    fact = build_fact_attendance(
        cleaned, employee, date, costcentre, shift, attendance, remarks
    )
    if logger:
        logger.info("FACT_Attendance count: %s", len(fact))
        logger.info("Validating foreign keys")
    validate_foreign_keys(fact, employee, date, costcentre, shift, attendance, remarks)
    if logger:
        logger.info("Foreign key validation passed")

    tables = {
        "DIM_Employee": employee,
        "DIM_Date": date,
        "DIM_Cost_Centre": costcentre,
        "DIM_Shift": shift,
        "DIM_Attendance_Type": attendance,
        "DIM_Remarks": remarks,
        "FACT_Attendance": fact,
    }
    return tables, sheet_name, stats


def generate_star_schema(
    input_path: Path, output_path: Path | None = None
) -> GenerationResult:
    ensure_directories()
    logger = get_logger()
    start = time.perf_counter()
    resolved_output = output_path or DEFAULT_OUTPUT_FILE

    logger.info("Starting attendance star schema generation")
    logger.info("Input file: %s", input_path)

    try:
        tables, sheet_name, cleaning = generate_tables(input_path, logger)
        logger.info("Exporting star schema workbook")
        exported_path = export_star_schema(tables, resolved_output, logger)
        processing_seconds = time.perf_counter() - start

        logger.info("Export status: success")
        logger.info("Output file: %s", exported_path)
        logger.info("Processing time seconds: %.3f", processing_seconds)

        return GenerationResult(
            output_path=exported_path,
            sheet_name=sheet_name,
            cleaning=cleaning,
            table_counts={name: len(table) for name, table in tables.items()},
            processing_seconds=processing_seconds,
        )
    except AttendanceGeneratorError as exc:
        logger.error("Generation failed: %s", exc)
        raise
    except MemoryError as exc:
        message = "Not enough memory to process this workbook. Try splitting the input file into smaller files."
        logger.error(message)
        raise AttendanceGeneratorError(message) from exc
