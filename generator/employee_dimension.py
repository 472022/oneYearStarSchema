from __future__ import annotations

import pandas as pd


def build_employee_dimension(frame: pd.DataFrame) -> pd.DataFrame:
    dimension = (
        frame[["Per. No.", "Name", "PSA Text", "ESG Text", "Employee Category", "FIC"]]
        .dropna(subset=["Per. No."])
        .drop_duplicates(subset=["Per. No."], keep="first")
        .sort_values(["Per. No."], na_position="last", kind="mergesort")
        .reset_index(drop=True)
        .rename(
            columns={
                "Per. No.": "Employee_ID",
                "Name": "Employee_Name",
                "PSA Text": "Department",
                "ESG Text": "Grade_Level",
                "Employee Category": "Employee_Category",
            }
        )
    )
    return dimension[
        [
            "Employee_ID",
            "Employee_Name",
            "Department",
            "Grade_Level",
            "Employee_Category",
            "FIC",
        ]
    ]
