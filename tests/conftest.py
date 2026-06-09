from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture()
def sample_raw_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Per. No.": "1001",
                "Name": "Asha Rao",
                "Date": "2025-05-17",
                "PSA Text": "Plant",
                "ESG Text": "Staff",
                "Employee Category": "Permanent",
                "FIC": "F1",
                "Cost Centre": "CC10",
                "Cost Centre Text": "Assembly",
                "Actual Shift": "G",
                "In Time": "09:00",
                "Out Time": "17:30",
                "Att./Abs.(1st half)": "P",
                "Att./Abs.(1st half) Text": "Present",
                "Att./Abs.(2nd half)": "P",
                "Att./Abs.(2nd half) Text": "Present",
                "Remarks": "On time",
            },
            {
                "Per. No.": "1002",
                "Name": "Vikram Singh",
                "Date": "2025-05-18",
                "PSA Text": "Plant",
                "ESG Text": "Worker",
                "Employee Category": "Contract",
                "FIC": "F2",
                "Cost Centre": "CC20",
                "Cost Centre Text": "Packing",
                "Actual Shift": "B",
                "In Time": "13:00",
                "Out Time": "21:00",
                "Att./Abs.(1st half)": "P",
                "Att./Abs.(1st half) Text": "Present",
                "Att./Abs.(2nd half)": "A",
                "Att./Abs.(2nd half) Text": "Absent",
                "Remarks": "-",
            },
        ]
    )
