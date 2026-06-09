from __future__ import annotations

import pandas as pd

from config import MAPPING_DIR
from generator.utils import load_json_mapping


def build_attendance_dimension(frame: pd.DataFrame) -> pd.DataFrame:
    first_half = frame[["Att./Abs.(1st half)", "Att./Abs.(1st half) Text"]].rename(
        columns={
            "Att./Abs.(1st half)": "Att_Code",
            "Att./Abs.(1st half) Text": "Att_Description",
        }
    )
    second_half = frame[["Att./Abs.(2nd half)", "Att./Abs.(2nd half) Text"]].rename(
        columns={
            "Att./Abs.(2nd half)": "Att_Code",
            "Att./Abs.(2nd half) Text": "Att_Description",
        }
    )
    dimension = (
        pd.concat([first_half, second_half], ignore_index=True)
        .dropna(subset=["Att_Code"])
        .drop_duplicates(subset=["Att_Code"], keep="first")
        .sort_values(["Att_Code"], na_position="last", kind="mergesort")
        .reset_index(drop=True)
    )

    mapping = load_json_mapping(MAPPING_DIR / "attendance_mapping.json")
    dimension["Att_Category"] = dimension["Att_Code"].map(
        lambda code: _attendance_category(code, mapping)
    )

    return dimension


def _attendance_category(code: object, mapping: dict[str, object]) -> object:
    if pd.isna(code):
        return "Other"
    payload = mapping.get(str(code), {})
    if isinstance(payload, dict):
        return (
            payload.get("Attendance_Category") or payload.get("Att_Category") or "Other"
        )
    return "Other"
