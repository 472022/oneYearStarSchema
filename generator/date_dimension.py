from __future__ import annotations

import pandas as pd


def build_date_dimension(frame: pd.DataFrame) -> pd.DataFrame:
    dates = pd.Series(frame["Date"].dropna().drop_duplicates(), name="Full_Date")
    dates = pd.to_datetime(dates).sort_values().reset_index(drop=True)
    dimension = pd.DataFrame({"Date_SK": dates.dt.strftime("%Y%m%d").astype(int)})
    dimension["Full_Date"] = dates.dt.strftime("%d-%m-%Y")
    dimension["Day"] = dates.dt.day
    dimension["Month_Num"] = dates.dt.month
    dimension["Month_Name"] = dates.dt.month_name()
    dimension["Quarter"] = "Q" + dates.dt.quarter.astype(str)
    dimension["Year"] = dates.dt.year
    dimension["Week_Num"] = dates.dt.isocalendar().week.astype(int)
    dimension["Day_of_Week"] = dates.dt.day_name()
    dimension["Is_Weekend"] = (dates.dt.dayofweek >= 5).map({True: "Yes", False: "No"})
    return dimension
