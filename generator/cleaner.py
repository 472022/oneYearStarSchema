from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from config import NULL_LIKE_VALUES


@dataclass(frozen=True)
class CleaningStats:
    rows_read: int
    blank_rows_removed: int
    duplicates_removed: int
    rows_after_cleaning: int
    invalid_dates: int
    invalid_times: int


def _clean_string_value(value: object) -> object:
    if pd.isna(value):
        return pd.NA
    text = str(value).strip()
    text = " ".join(text.split())
    if text.lower() in NULL_LIKE_VALUES:
        return pd.NA
    return text


def _normalize_time_column(series: pd.Series) -> tuple[pd.Series, int]:
    original_not_null = series.notna()
    numeric = pd.to_numeric(series, errors="coerce")
    excel_fraction_mask = numeric.notna() & numeric.between(0, 1, inclusive="left")

    normalized = pd.Series(pd.NA, index=series.index, dtype="object")
    if excel_fraction_mask.any():
        seconds = (numeric.loc[excel_fraction_mask] * 24 * 60 * 60).round().astype(int)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        normalized.loc[excel_fraction_mask] = (
            hours.astype(str).str.zfill(2)
            + ":"
            + minutes.astype(str).str.zfill(2)
            + ":"
            + secs.astype(str).str.zfill(2)
        )

    parse_mask = original_not_null & ~excel_fraction_mask
    if parse_mask.any():
        parsed = pd.to_datetime(series.loc[parse_mask], errors="coerce", format="mixed")
        normalized.loc[parse_mask] = parsed.dt.strftime("%H:%M:%S")

    normalized = normalized.where(normalized.notna(), pd.NA)
    invalid = int((original_not_null & normalized.isna()).sum())
    return normalized, invalid


def clean_attendance_data(frame: pd.DataFrame) -> tuple[pd.DataFrame, CleaningStats]:
    rows_read = len(frame)
    cleaned = frame.copy()

    for column in cleaned.columns:
        cleaned[column] = cleaned[column].map(_clean_string_value)

    blank_mask = cleaned.isna().all(axis=1)
    blank_rows_removed = int(blank_mask.sum())
    cleaned = cleaned.loc[~blank_mask].copy()

    before_duplicates = len(cleaned)
    cleaned = cleaned.drop_duplicates().reset_index(drop=True)
    duplicates_removed = before_duplicates - len(cleaned)

    raw_dates_not_null = cleaned["Date"].notna()
    cleaned["Date"] = pd.to_datetime(
        cleaned["Date"], errors="coerce", dayfirst=True, format="mixed"
    ).dt.date
    invalid_dates = int((raw_dates_not_null & cleaned["Date"].isna()).sum())

    invalid_times = 0
    for column in ("In Time", "Out Time"):
        cleaned[column], invalid = _normalize_time_column(cleaned[column])
        invalid_times += invalid

    stats = CleaningStats(
        rows_read=rows_read,
        blank_rows_removed=blank_rows_removed,
        duplicates_removed=duplicates_removed,
        rows_after_cleaning=len(cleaned),
        invalid_dates=invalid_dates,
        invalid_times=invalid_times,
    )
    return cleaned, stats
