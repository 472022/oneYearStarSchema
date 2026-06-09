from __future__ import annotations

import pandas as pd


def build_remarks_dimension(frame: pd.DataFrame) -> pd.DataFrame:
    dimension = (
        frame[["Remarks"]]
        .dropna(subset=["Remarks"])
        .drop_duplicates()
        .sort_values(["Remarks"], na_position="last", kind="mergesort")
        .reset_index(drop=True)
    )
    dimension["Remarks_Category"] = dimension["Remarks"].map(_remarks_category)
    dimension["Is_Present"] = dimension["Remarks"].map(
        lambda value: "Yes" if str(value).strip().lower() == "present" else "No"
    )
    dimension["Is_Authorised"] = dimension["Remarks"].map(_is_authorised)
    return dimension


def _remarks_category(value: object) -> str:
    text = str(value).strip().lower()
    if text == "present":
        return "Attendance"
    if "absence" in text or "absent" in text:
        return "Absence"
    return "Other"


def _is_authorised(value: object) -> str:
    text = str(value).strip().lower()
    if text == "present":
        return "Yes"
    if "unauthorised" in text or "unauthorized" in text:
        return "No"
    if "authorised" in text or "authorized" in text:
        return "Yes"
    return "No"
