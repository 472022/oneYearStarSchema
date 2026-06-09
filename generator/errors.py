from __future__ import annotations


class AttendanceGeneratorError(Exception):
    """Base class for user-facing generator errors."""


class ExcelReadError(AttendanceGeneratorError):
    """Raised when the input workbook cannot be read."""


class ValidationError(AttendanceGeneratorError):
    """Raised when input data does not satisfy the required schema."""


class ExportError(AttendanceGeneratorError):
    """Raised when the star schema workbook cannot be exported."""


class ForeignKeyError(AttendanceGeneratorError):
    """Raised when generated fact keys do not match dimensions."""
