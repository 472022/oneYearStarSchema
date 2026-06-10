from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, request, send_file, send_from_directory

from config import OUTPUT_DIR, PROCESS_LOG_FILE, UPLOAD_DIR, ensure_directories
from generator.errors import AttendanceGeneratorError
from generator.pipeline import generate_star_schema

app = Flask(__name__, static_folder="static")

ensure_directories()

OUTPUT_FILE = OUTPUT_DIR / "Attendance_StarSchema.xlsx"


@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.post("/upload")
def upload():
    if "file" not in request.files:
        return jsonify(success=False, error="No file provided.")

    f = request.files["file"]
    if not f.filename or not f.filename.lower().endswith(".xlsx"):
        return jsonify(success=False, error="Please upload a .xlsx file.")

    input_path = UPLOAD_DIR / Path(f.filename).name
    f.save(input_path)

    try:
        result = generate_star_schema(input_path, OUTPUT_FILE)
    except AttendanceGeneratorError as exc:
        return jsonify(success=False, error=str(exc))

    table_counts = [
        {"table": table, "rows": count}
        for table, count in result.table_counts.items()
    ]

    return jsonify(
        success=True,
        rows_read=result.cleaning.rows_read,
        fact_rows=result.table_counts.get("FACT_Attendance", 0),
        seconds=round(result.processing_seconds, 2),
        table_counts=table_counts,
    )


@app.get("/download")
def download():
    if not OUTPUT_FILE.exists():
        return jsonify(success=False, error="No output file available yet."), 404
    return send_file(
        OUTPUT_FILE,
        as_attachment=True,
        download_name="Attendance_StarSchema.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@app.get("/logs")
def logs():
    if not PROCESS_LOG_FILE.exists():
        return jsonify(content="")
    text = PROCESS_LOG_FILE.read_text(encoding="utf-8")[-8000:]
    return jsonify(content=text)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
