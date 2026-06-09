from __future__ import annotations

import pandas as pd

from config import MAPPING_DIR
from generator.utils import load_json_mapping


def build_shift_dimension(frame: pd.DataFrame) -> pd.DataFrame:
    mapping = load_json_mapping(MAPPING_DIR / "shift_mapping.json")
    dimension = (
        frame[["Actual Shift"]]
        .dropna(subset=["Actual Shift"])
        .drop_duplicates()
        .sort_values(["Actual Shift"], na_position="last", kind="mergesort")
        .reset_index(drop=True)
        .rename(columns={"Actual Shift": "Shift_Code"})
    )
    dimension["Shift_Type"] = dimension["Shift_Code"].map(
        lambda code: _shift_name(code, mapping)
    )
    return dimension


def _shift_name(code: object, mapping: dict[str, object]) -> object:
    if pd.isna(code):
        return pd.NA
    value = str(code)
    mapped = mapping.get(value)
    if isinstance(mapped, dict):
        return mapped.get("Shift_Name") or mapped.get("name") or value
    if isinstance(mapped, str):
        return mapped
    return value
