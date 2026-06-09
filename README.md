# Attendance Star Schema Generator

Convert one raw attendance Excel workbook into a normalized Power BI-ready star schema workbook.

## Features

- Reads `.xlsx` attendance files and automatically selects the `Raw Data` sheet when present.
- Validates required attendance columns with tolerant header matching.
- Cleans whitespace, null-like values, dates, times, duplicate rows, and blank rows.
- Generates dimension tables, a fact table using existing business keys, schema guide, logs, and a formatted Excel workbook.
- Includes both CLI and Streamlit interfaces.

## Setup

Use Python 3.12 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## CLI Usage

```powershell
python app.py Raw_Attendance.xlsx
python app.py Raw_Attendance.xlsx --output outputs/myfile.xlsx
```

The default output is:

```text
outputs/Attendance_StarSchema.xlsx
```

## Streamlit Usage

```powershell
streamlit run streamlit_app.py
```

Upload a raw `.xlsx` file, generate the workbook, and download the result.

## Output Sheets

- `⭐ Schema Guide`
- `DIM_Employee`
- `DIM_Date`
- `DIM_Cost_Centre`
- `DIM_Shift`
- `DIM_Attendance_Type`
- `DIM_Remarks`
- `FACT_Attendance`

The generated model does not add surrogate IDs such as `Fact_ID` or `Employee_Key`. It uses keys already present in the source data, such as `Employee_ID`, `Cost_Centre_ID`, `Shift_Code`, attendance codes, and remarks. `Date_SK` is the standard `YYYYMMDD` date key derived from the source date.

## Required Input Columns

- `Per. No.`
- `Name`
- `Date`
- `PSA Text`
- `ESG Text`
- `Employee Category`
- `FIC`
- `Cost Centre`
- `Cost Centre Text`
- `Actual Shift`
- `In Time`
- `Out Time`
- `Att./Abs.(1st half)`
- `Att./Abs.(1st half) Text`
- `Att./Abs.(2nd half)`
- `Att./Abs.(2nd half) Text`
- `Remarks`

Header matching is normalized for case, whitespace, and punctuation.

## Excel Size Limit

Excel worksheets can contain at most 1,048,576 rows, including the header. If the generated fact table exceeds 1,048,575 data rows, the export stops with a clear message recommending that the source data be split or filtered.

## Logs

Processing logs are written to:

```text
logs/process.log
```

## Tests

```powershell
pytest
```
