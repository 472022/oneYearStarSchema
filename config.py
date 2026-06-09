from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
LOG_DIR = BASE_DIR / "logs"
MAPPING_DIR = BASE_DIR / "mappings"

DEFAULT_OUTPUT_FILE = OUTPUT_DIR / "Attendance_StarSchema.xlsx"
PROCESS_LOG_FILE = LOG_DIR / "process.log"
SCHEMA_GUIDE_SHEET = "\u2b50 Schema Guide"

RAW_DATA_SHEET_NAME = "raw data"
EXCEL_MAX_ROWS = 1_048_576
EXCEL_MAX_DATA_ROWS = EXCEL_MAX_ROWS - 1

REQUIRED_COLUMNS: dict[str, str] = {
    "per no": "Per. No.",
    "name": "Name",
    "date": "Date",
    "psa text": "PSA Text",
    "esg text": "ESG Text",
    "employee category": "Employee Category",
    "fic": "FIC",
    "cost centre": "Cost Centre",
    "cost centre text": "Cost Centre Text",
    "actual shift": "Actual Shift",
    "in time": "In Time",
    "out time": "Out Time",
    "att abs 1st half": "Att./Abs.(1st half)",
    "att abs 1st half text": "Att./Abs.(1st half) Text",
    "att abs 2nd half": "Att./Abs.(2nd half)",
    "att abs 2nd half text": "Att./Abs.(2nd half) Text",
    "remarks": "Remarks",
}

NULL_LIKE_VALUES = {"", "na", "n/a", "-", "null", "none", "nan"}

OUTPUT_SHEETS = [
    SCHEMA_GUIDE_SHEET,
    "DIM_Employee",
    "DIM_Date",
    "DIM_Cost_Centre",
    "DIM_Shift",
    "DIM_Attendance_Type",
    "DIM_Remarks",
    "FACT_Attendance",
]


def ensure_directories() -> None:
    """Create runtime directories used by the application."""
    for directory in (UPLOAD_DIR, OUTPUT_DIR, LOG_DIR, MAPPING_DIR):
        directory.mkdir(parents=True, exist_ok=True)
