from __future__ import annotations

import pandas as pd

from generator.errors import ForeignKeyError


def build_fact_attendance(
    frame: pd.DataFrame,
    employee: pd.DataFrame,
    date: pd.DataFrame,
    costcentre: pd.DataFrame,
    shift: pd.DataFrame,
    attendance: pd.DataFrame,
    remarks: pd.DataFrame,
) -> pd.DataFrame:
    fact = frame.copy()
    fact["Date_SK"] = pd.to_datetime(fact["Date"]).dt.strftime("%Y%m%d").astype("Int64")
    fact["In_Time_Mins"] = _time_to_minutes(fact["In Time"])
    fact["Out_Time_Mins"] = _time_to_minutes(fact["Out Time"])
    fact["Work_Duration_Mins"] = _work_duration(
        fact["In_Time_Mins"], fact["Out_Time_Mins"]
    )
    fact["Is_Present"] = fact["Remarks"].map(
        lambda value: 1 if str(value).strip().lower() == "present" else 0
    )
    fact["Is_Absent_Auth"] = fact["Remarks"].map(_is_authorised_absence)
    fact["Is_Absent_Unauth"] = fact["Remarks"].map(_is_unauthorised_absence)

    output = fact[
        [
            "Per. No.",
            "Date_SK",
            "Cost Centre",
            "Actual Shift",
            "Att./Abs.(1st half)",
            "Att./Abs.(2nd half)",
            "Remarks",
            "In Time",
            "Out Time",
            "In_Time_Mins",
            "Out_Time_Mins",
            "Work_Duration_Mins",
            "Is_Present",
            "Is_Absent_Auth",
            "Is_Absent_Unauth",
        ]
    ].copy()
    return output.rename(
        columns={
            "Per. No.": "Employee_ID",
            "Cost Centre": "Cost_Centre_ID",
            "Actual Shift": "Shift_Code",
            "Att./Abs.(1st half)": "Att_1st_Half_Code",
            "Att./Abs.(2nd half)": "Att_2nd_Half_Code",
            "In Time": "In_Time",
            "Out Time": "Out_Time",
        }
    )


def validate_foreign_keys(
    fact: pd.DataFrame,
    employee: pd.DataFrame,
    date: pd.DataFrame,
    costcentre: pd.DataFrame,
    shift: pd.DataFrame,
    attendance: pd.DataFrame,
    remarks: pd.DataFrame,
) -> None:
    checks = {
        "Employee_ID": set(employee["Employee_ID"]),
        "Date_SK": set(date["Date_SK"]),
        "Cost_Centre_ID": set(costcentre["Cost_Centre_ID"]),
        "Shift_Code": set(shift["Shift_Code"]),
        "Att_1st_Half_Code": set(attendance["Att_Code"]),
        "Att_2nd_Half_Code": set(attendance["Att_Code"]),
        "Remarks": set(remarks["Remarks"]),
    }
    failures: list[str] = []
    for column, valid_keys in checks.items():
        populated = fact[column].notna()
        missing_mask = populated & ~fact[column].isin(valid_keys)
        missing_count = int(missing_mask.sum())
        if missing_count:
            failures.append(f"{column}: {missing_count} orphan record(s)")

    if failures:
        raise ForeignKeyError(
            "Foreign key validation failed:\n"
            + "\n".join(f"- {item}" for item in failures)
        )


def _time_to_minutes(series: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(series, errors="coerce", format="%H:%M:%S")
    minutes = parsed.dt.hour * 60 + parsed.dt.minute
    return minutes.astype("Int64")


def _work_duration(in_minutes: pd.Series, out_minutes: pd.Series) -> pd.Series:
    duration = out_minutes - in_minutes
    overnight = in_minutes.notna() & out_minutes.notna() & (out_minutes < in_minutes)
    duration.loc[overnight] = (
        out_minutes.loc[overnight] + 1440 - in_minutes.loc[overnight]
    )
    duration = duration.where(duration > 0, pd.NA)
    return duration.astype("Int64")


def _is_authorised_absence(value: object) -> int:
    text = str(value).strip().lower()
    return int(
        ("authorised absence" in text or "authorized absence" in text)
        and "unauthor" not in text
    )


def _is_unauthorised_absence(value: object) -> int:
    text = str(value).strip().lower()
    return int("unauthorised absence" in text or "unauthorized absence" in text)
