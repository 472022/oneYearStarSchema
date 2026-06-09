from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd


def normalize_name(value: object) -> str:
    """Normalize sheet or column names for tolerant matching."""
    text = "" if value is None else str(value)
    text = text.strip().lower()
    text = re.sub(r"[\./()\[\]:;,_-]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_columns(columns: list[object]) -> list[str]:
    return [normalize_name(column) for column in columns]


def stable_distinct(
    frame: pd.DataFrame, columns: list[str], sort_by: list[str] | None = None
) -> pd.DataFrame:
    distinct = frame[columns].drop_duplicates().copy()
    order = sort_by or columns
    return distinct.sort_values(
        order, na_position="last", kind="mergesort"
    ).reset_index(drop=True)


def add_surrogate_key(frame: pd.DataFrame, key_name: str) -> pd.DataFrame:
    output = frame.copy()
    output.insert(0, key_name, range(1, len(output) + 1))
    return output


def load_json_mapping(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        return {}
    return payload


def stringify_for_key(series: pd.Series) -> pd.Series:
    return series.astype("string").fillna("<NULL>")
