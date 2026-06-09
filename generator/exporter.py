from __future__ import annotations

from logging import Logger
from pathlib import Path

import pandas as pd

from config import (
    EXCEL_MAX_DATA_ROWS,
    OUTPUT_SHEETS,
    SCHEMA_GUIDE_SHEET,
    ensure_directories,
)
from generator.errors import ExportError


def build_schema_guide() -> pd.DataFrame:
    rows = [
        (None, None, None, None),
        ("TABLE", "TYPE", "ROWS", "PRIMARY KEY  ->  DESCRIPTION"),
        (
            "DIM_Employee",
            "Dimension",
            "",
            "Employee_ID -> SAP Personnel No. | Employee_Name, Department, Grade_Level, Employee_Category, FIC",
        ),
        (
            "DIM_Date",
            "Dimension",
            "",
            "Date_SK -> YYYYMMDD date key | Full_Date, Day, Month, Quarter, Year",
        ),
        (
            "DIM_Cost_Centre",
            "Dimension",
            "",
            "Cost_Centre_ID -> Existing cost centre code | Cost_Centre_Name",
        ),
        (
            "DIM_Shift",
            "Dimension",
            "",
            "Shift_Code -> Existing shift code | Shift_Type",
        ),
        (
            "DIM_Attendance_Type",
            "Dimension",
            "",
            "Att_Code -> Existing attendance code | Att_Description, Att_Category",
        ),
        (
            "DIM_Remarks",
            "Dimension",
            "",
            "Remarks -> Existing remarks text | Remarks_Category, Is_Present, Is_Authorised",
        ),
        (
            "FACT_Attendance",
            "Fact",
            "",
            "One row per raw attendance row, using only existing business keys and derived measures",
        ),
        (None, None, None, None),
        ("RELATIONSHIP", "FACT COLUMN", "DIMENSION", "DIMENSION KEY"),
        (
            "Employee",
            "FACT_Attendance.Employee_ID",
            "DIM_Employee",
            "Employee_ID",
        ),
        ("Date", "FACT_Attendance.Date_SK", "DIM_Date", "Date_SK"),
        (
            "Cost Centre",
            "FACT_Attendance.Cost_Centre_ID",
            "DIM_Cost_Centre",
            "Cost_Centre_ID",
        ),
        ("Shift", "FACT_Attendance.Shift_Code", "DIM_Shift", "Shift_Code"),
        (
            "1st Half Attendance",
            "FACT_Attendance.Att_1st_Half_Code",
            "DIM_Attendance_Type",
            "Att_Code",
        ),
        (
            "2nd Half Attendance",
            "FACT_Attendance.Att_2nd_Half_Code",
            "DIM_Attendance_Type",
            "Att_Code",
        ),
        ("Remarks", "FACT_Attendance.Remarks", "DIM_Remarks", "Remarks"),
        (None, None, None, None),
        ("STAR SCHEMA DIAGRAM", "", "", ""),
        ("DIM_Employee", "", "", ""),
        ("DIM_Date", "", "", ""),
        ("DIM_Cost_Centre", "", "", ""),
        ("DIM_Shift -> FACT_Attendance <- DIM_Attendance_Type", "", "", ""),
        ("DIM_Remarks", "", "", ""),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "STAR SCHEMA \u2014 ATTENDANCE POWER BI MODEL",
            None,
            None,
            None,
        ],
    )


def export_star_schema(
    tables: dict[str, pd.DataFrame], output_path: Path, logger: Logger | None = None
) -> Path:
    ensure_directories()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if len(tables["FACT_Attendance"]) > EXCEL_MAX_DATA_ROWS:
        raise ExportError(
            "FACT_Attendance exceeds the Excel sheet limit of 1,048,575 data rows. "
            "Please split or filter the source file before exporting to Excel."
        )

    workbook_tables = dict(tables)
    workbook_tables[SCHEMA_GUIDE_SHEET] = build_schema_guide()

    try:
        with pd.ExcelWriter(
            output_path, engine="xlsxwriter", datetime_format="yyyy-mm-dd"
        ) as writer:
            for sheet_name in OUTPUT_SHEETS:
                frame = workbook_tables[sheet_name]
                if logger:
                    logger.info(
                        "Exporting sheet %s with %s row(s)", sheet_name, len(frame)
                    )
                frame.to_excel(writer, sheet_name=sheet_name, index=False)
                _format_sheet(writer, sheet_name, frame)
                if logger:
                    logger.info("Finished sheet %s", sheet_name)
    except PermissionError as exc:
        raise ExportError(
            f"Permission denied while writing output workbook: {output_path}"
        ) from exc
    except Exception as exc:  # pragma: no cover - writer exceptions vary by platform
        raise ExportError(f"Could not export star schema workbook: {exc}") from exc

    return output_path


def _format_sheet(writer: pd.ExcelWriter, sheet_name: str, frame: pd.DataFrame) -> None:
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    header_format = workbook.add_format(
        {"bold": True, "font_color": "white", "bg_color": "#1F4E79", "border": 1}
    )
    text_format = workbook.add_format({"font_name": "Calibri", "font_size": 11})

    worksheet.freeze_panes(1, 0)

    for index, column in enumerate(frame.columns):
        series = frame.iloc[:, index].astype(str)
        width = min(
            max([len(str(column)), *series.head(1000).map(len).tolist()]) + 2, 60
        )
        worksheet.set_column(index, index, width, text_format)
        worksheet.write(0, index, column, header_format)

    if sheet_name == SCHEMA_GUIDE_SHEET:
        return

    if len(frame) > 0 and len(frame.columns) > 0:
        table_name = sheet_name.replace(" ", "_")[:31]
        worksheet.add_table(
            0,
            0,
            len(frame),
            len(frame.columns) - 1,
            {
                "name": table_name,
                "style": "Table Style Medium 2",
                "columns": [
                    {"header": column, "header_format": header_format}
                    for column in frame.columns
                ],
            },
        )
    elif len(frame.columns) > 0:
        worksheet.autofilter(0, 0, 0, len(frame.columns) - 1)
