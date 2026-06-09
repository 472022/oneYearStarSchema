from __future__ import annotations

import pandas as pd


def build_costcentre_dimension(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame[["Cost Centre", "Cost Centre Text"]]
        .dropna(subset=["Cost Centre"])
        .drop_duplicates(subset=["Cost Centre"], keep="first")
        .sort_values(["Cost Centre"], na_position="last", kind="mergesort")
        .reset_index(drop=True)
        .rename(
            columns={
                "Cost Centre": "Cost_Centre_ID",
                "Cost Centre Text": "Cost_Centre_Name",
            }
        )
    )
