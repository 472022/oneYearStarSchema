from __future__ import annotations

import pandas as pd
import pytest

from generator.attendance_dimension import build_attendance_dimension
from generator.cleaner import clean_attendance_data
from generator.costcentre_dimension import build_costcentre_dimension
from generator.date_dimension import build_date_dimension
from generator.employee_dimension import build_employee_dimension
from generator.errors import ValidationError
from generator.fact_builder import build_fact_attendance, validate_foreign_keys
from generator.remarks_dimension import build_remarks_dimension
from generator.shift_dimension import build_shift_dimension
from generator.validator import canonicalize_required_columns


def test_validation_reports_missing_columns(sample_raw_frame: pd.DataFrame) -> None:
    frame = sample_raw_frame.drop(columns=["Actual Shift", "Remarks"])
    with pytest.raises(ValidationError) as error:
        canonicalize_required_columns(frame)

    message = str(error.value)
    assert "Actual Shift" in message
    assert "Remarks" in message


def test_cleaning_removes_blank_and_duplicate_rows(
    sample_raw_frame: pd.DataFrame,
) -> None:
    frame = pd.concat(
        [sample_raw_frame, sample_raw_frame.iloc[[0]], pd.DataFrame([{}])],
        ignore_index=True,
    )
    canonical = canonicalize_required_columns(frame)
    cleaned, stats = clean_attendance_data(canonical)

    assert len(cleaned) == 2
    assert stats.blank_rows_removed == 1
    assert stats.duplicates_removed == 1
    assert cleaned.loc[1, "Remarks"] is pd.NA


def test_date_dimension_fields(sample_raw_frame: pd.DataFrame) -> None:
    cleaned, _ = clean_attendance_data(canonicalize_required_columns(sample_raw_frame))
    dimension = build_date_dimension(cleaned)

    assert list(dimension["Date_SK"]) == [20250517, 20250518]
    assert dimension.loc[0, "Quarter"] == "Q2"
    assert dimension.loc[0, "Is_Weekend"] == "Yes"


def test_dimensions_and_fact_keep_integrity(sample_raw_frame: pd.DataFrame) -> None:
    cleaned, _ = clean_attendance_data(canonicalize_required_columns(sample_raw_frame))
    employee = build_employee_dimension(cleaned)
    date = build_date_dimension(cleaned)
    costcentre = build_costcentre_dimension(cleaned)
    shift = build_shift_dimension(cleaned)
    attendance = build_attendance_dimension(cleaned)
    remarks = build_remarks_dimension(cleaned)

    fact = build_fact_attendance(
        cleaned, employee, date, costcentre, shift, attendance, remarks
    )
    validate_foreign_keys(fact, employee, date, costcentre, shift, attendance, remarks)

    assert len(employee) == 2
    assert len(costcentre) == 2
    assert len(shift) == 2
    assert set(attendance["Att_Code"]) == {"P", "A"}
    assert len(fact) == len(cleaned)
    assert fact.columns.tolist() == [
        "Employee_ID",
        "Date_SK",
        "Cost_Centre_ID",
        "Shift_Code",
        "Att_1st_Half_Code",
        "Att_2nd_Half_Code",
        "Remarks",
        "In_Time",
        "Out_Time",
        "In_Time_Mins",
        "Out_Time_Mins",
        "Work_Duration_Mins",
        "Is_Present",
        "Is_Absent_Auth",
        "Is_Absent_Unauth",
    ]
    assert "Fact_ID" not in fact.columns
    assert "Employee_Key" not in employee.columns
