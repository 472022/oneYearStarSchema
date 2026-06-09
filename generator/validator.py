from __future__ import annotations

import pandas as pd

from config import REQUIRED_COLUMNS
from generator.errors import ValidationError
from generator.utils import normalize_name


def canonicalize_required_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Rename required input columns to canonical display names."""
    normalized_to_original: dict[str, object] = {}
    duplicates: list[str] = []

    for column in frame.columns:
        normalized = normalize_name(column)
        if normalized in normalized_to_original:
            duplicates.append(str(column))
        normalized_to_original[normalized] = column

    if duplicates:
        raise ValidationError(
            f"Duplicate headers detected after normalization: {', '.join(duplicates)}"
        )

    missing = [
        display_name
        for normalized, display_name in REQUIRED_COLUMNS.items()
        if normalized not in normalized_to_original
    ]
    if missing:
        joined = "\n".join(f"- {column}" for column in missing)
        raise ValidationError(f"Missing required columns:\n{joined}")

    renamed = frame.rename(
        columns={
            normalized_to_original[normalized]: display_name
            for normalized, display_name in REQUIRED_COLUMNS.items()
        }
    )
    return renamed[list(REQUIRED_COLUMNS.values())].copy()
