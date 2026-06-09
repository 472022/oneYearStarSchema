from __future__ import annotations

from pathlib import Path

import pandas as pd

from config import RAW_DATA_SHEET_NAME
from generator.errors import ExcelReadError, ValidationError
from generator.utils import normalize_name


def read_raw_excel(path: Path) -> tuple[pd.DataFrame, str]:
    """Read the Raw Data sheet if present, otherwise the first sheet."""
    if not path.exists():
        raise ExcelReadError(f"Input file does not exist: {path}")
    if path.suffix.lower() != ".xlsx":
        raise ExcelReadError("Input file must be an .xlsx workbook.")

    try:
        workbook = pd.ExcelFile(path, engine="openpyxl")
    except Exception as exc:  # pragma: no cover - exact exception depends on openpyxl
        raise ExcelReadError(f"Could not open Excel workbook: {exc}") from exc

    if not workbook.sheet_names:
        raise ExcelReadError("Workbook does not contain any sheets.")

    normalized_sheets = {normalize_name(name): name for name in workbook.sheet_names}
    sheet_name = normalized_sheets.get(RAW_DATA_SHEET_NAME, workbook.sheet_names[0])

    try:
        frame = pd.read_excel(workbook, sheet_name=sheet_name, dtype=object)
    except Exception as exc:  # pragma: no cover
        raise ExcelReadError(f"Could not read sheet '{sheet_name}': {exc}") from exc

    if frame.empty:
        raise ValidationError(f"Sheet '{sheet_name}' does not contain any rows.")

    return frame, sheet_name
