from __future__ import annotations

from pathlib import Path

import streamlit as st

from config import OUTPUT_DIR, PROCESS_LOG_FILE, UPLOAD_DIR, ensure_directories
from generator.errors import AttendanceGeneratorError
from generator.pipeline import generate_star_schema

st.set_page_config(page_title="Attendance Star Schema Generator", layout="wide")

ensure_directories()

st.title("Attendance Star Schema Generator")

uploaded_file = st.file_uploader("Upload raw attendance Excel file", type=["xlsx"])

if uploaded_file:
    input_path = UPLOAD_DIR / uploaded_file.name
    input_path.write_bytes(uploaded_file.getbuffer())

    output_path = OUTPUT_DIR / "Attendance_StarSchema.xlsx"
    with st.spinner("Generating star schema workbook..."):
        try:
            result = generate_star_schema(input_path, output_path)
        except AttendanceGeneratorError as exc:
            st.error(str(exc))
        else:
            st.success("Workbook generated successfully.")
            col1, col2, col3 = st.columns(3)
            col1.metric("Rows read", result.cleaning.rows_read)
            col2.metric("Fact rows", result.table_counts["FACT_Attendance"])
            col3.metric("Seconds", f"{result.processing_seconds:.2f}")

            st.dataframe(
                [
                    {"Table": table, "Rows": count}
                    for table, count in result.table_counts.items()
                ],
                use_container_width=True,
                hide_index=True,
            )

            with Path(result.output_path).open("rb") as handle:
                st.download_button(
                    "Download workbook",
                    data=handle,
                    file_name=Path(result.output_path).name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

if PROCESS_LOG_FILE.exists():
    with st.expander("Processing log"):
        st.code(PROCESS_LOG_FILE.read_text(encoding="utf-8")[-8000:])
