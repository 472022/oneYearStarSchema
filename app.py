from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from config import DEFAULT_OUTPUT_FILE
from generator.errors import AttendanceGeneratorError
from generator.pipeline import generate_star_schema

cli = typer.Typer(
    help="Convert a raw attendance Excel workbook into a Power BI star schema workbook."
)


@cli.command()
def main(
    input_file: Path = typer.Argument(
        ..., exists=True, file_okay=True, dir_okay=False, readable=True
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help=f"Output workbook path. Defaults to {DEFAULT_OUTPUT_FILE}.",
    ),
) -> None:
    """Generate an attendance star schema workbook from one raw .xlsx file."""
    try:
        result = generate_star_schema(input_file, output)
    except AttendanceGeneratorError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo("Attendance star schema generated successfully.")
    typer.echo(f"Input sheet: {result.sheet_name}")
    typer.echo(f"Rows read: {result.cleaning.rows_read}")
    typer.echo(
        f"Rows exported to FACT_Attendance: {result.table_counts['FACT_Attendance']}"
    )
    typer.echo(f"Output: {result.output_path}")


if __name__ == "__main__":
    cli()
