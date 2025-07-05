# Forecast income router
from fastapi import APIRouter, Query
import pandas as pd
import numpy as np
from prophet import Prophet
from sqlalchemy import create_engine, text
import os
import logging

router = APIRouter()

# Database connection (adjust as needed)
DB_URL = os.getenv("NNDR_DB_URL", "postgresql://nndr:nndrpass@localhost:5432/nndr_db")
engine = create_engine(DB_URL)

@router.post("/forecast")
def forecast_income(
    date_col: str = "last_billed_date",
    value_col: str = "rateable_value",
    periods: int = 12,
    category_code: str = None,
    area: str = None,
    agg: str = "sum"
):
    # Build SQL query for flexible forecasting
    where_clauses = [f"{date_col} IS NOT NULL", f"{value_col} IS NOT NULL"]
    params = {}
    if category_code:
        where_clauses.append("category_code = :category_code")
        params["category_code"] = category_code
    if area:
        where_clauses.append("postcode LIKE :area")
        params["area"] = f"{area}%"
    where_sql = " AND ".join(where_clauses)
    sql = f"""
        SELECT {date_col}, {value_col}
        FROM properties
        WHERE {where_sql}
    """
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn, params=params)
    # Parse date and value columns
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    df = df.dropna(subset=[date_col, value_col])
    if df.empty:
        return {"error": "No data available for forecast."}
    # Aggregate by month
    if agg == "count":
        df_grouped = (
            df.groupby(df[date_col].dt.to_period("M"))[value_col]
            .count()
            .reset_index()
            .rename(columns={date_col: "ds", value_col: "y"})
        )
    else:
        df_grouped = (
            df.groupby(df[date_col].dt.to_period("M"))[value_col]
            .sum()
            .reset_index()
            .rename(columns={date_col: "ds", value_col: "y"})
        )
    df_grouped["ds"] = df_grouped["ds"].dt.to_timestamp()
    model = Prophet()
    model.fit(df_grouped)
    future = model.make_future_dataframe(periods=periods, freq="MS")
    forecast = model.predict(future)
    forecast_result = forecast[["ds", "yhat"]].tail(periods).to_dict(orient="records")
    # Clean output
    for i, row in enumerate(forecast_result):
        row["ds"] = str(row["ds"])
        yhat = row.get("yhat")
        try:
            yhat = float(yhat)
            if not np.isfinite(yhat):
                logging.warning(f"Row {i}: Non-finite yhat value: {row['yhat']}")
                yhat = None
        except Exception as e:
            logging.warning(f"Row {i}: Exception converting yhat: {row['yhat']} ({e})")
            yhat = None
        row["yhat"] = yhat
    return {"forecast": forecast_result}
