import io
import json
import zipfile
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from constants import CO2_PER_KM_CAR, DISTANCE_FACTOR, FUEL_PER_KM, MONTH_NAMES_PL_SHORT, MONTH_NAMES_SHORT


def _build_trips_df(trips_data) -> pd.DataFrame:
    rows = []
    for t in trips_data:
        start = t["_startStation"]
        end = t["_endStation"]
        row = {
            "trip_id": t["_id"],
            "started_at": pd.to_datetime(t["_tripStarted"], utc=True).tz_convert("Europe/Warsaw").tz_localize(None),
            "ended_at": pd.to_datetime(t["_tripEnded"], utc=True).tz_convert("Europe/Warsaw").tz_localize(None),
            "duration_s": t["_tripDuration"],
        }
        if start is not None:
            row["start_station_id"] = start["_id"]
            row["start_station_code"] = start["_title"]
            row["start_station_address"] = start["_subtitle"]
            row["start_lat"] = start["_coords"]["_latitude"]
            row["start_lng"] = start["_coords"]["_longitude"]
        else:
            row["start_station_id"] = np.nan
            row["start_station_code"] = np.nan
            row["start_station_address"] = np.nan
            row["start_lat"] = np.nan
            row["start_lng"] = np.nan
        if end is not None:
            row["end_station_id"] = end["_id"]
            row["end_station_code"] = end["_title"]
            row["end_station_address"] = end["_subtitle"]
            row["end_lat"] = end["_coords"]["_latitude"]
            row["end_lng"] = end["_coords"]["_longitude"]
        else:
            row["end_station_id"] = np.nan
            row["end_station_code"] = np.nan
            row["end_station_address"] = np.nan
            row["end_lat"] = np.nan
            row["end_lng"] = np.nan
        rows.append(row)

    df = pd.DataFrame(rows)
    df["has_start_station"] = df["start_lat"].notna()
    df["has_end_station"] = df["end_lat"].notna()
    df["date"] = df["started_at"].dt.date
    df["hour"] = df["started_at"].dt.hour
    df["day_of_week"] = df["started_at"].dt.dayofweek  # 0=Mon
    df["year_month"] = df["started_at"].dt.to_period("M").astype(str)
    return df


def parse_zip(uploaded_file) -> tuple[pd.DataFrame, list]:
    buf = io.BytesIO(uploaded_file.read())
    with zipfile.ZipFile(buf) as z:
        with z.open("trips.json") as f:
            trips = json.load(f)
        with z.open("orders.json") as f:
            orders = json.load(f)
    return _build_trips_df(trips), orders


def parse_json_files(trips_file, orders_file=None) -> tuple[pd.DataFrame, list]:
    trips_data = json.load(trips_file)
    orders_data = json.load(orders_file) if orders_file is not None else []
    return _build_trips_df(trips_data), orders_data


def compute_total_cost(orders_data):
    total = 0.0
    subscription_cost = 0.0
    trip_cost = 0.0
    order_count = 0
    for o in orders_data:
        if o.get("_status") != "completed":
            continue
        if o.get("_type") == "wallet_deposit":
            continue
        amount = o.get("_amount", 0)
        total += amount
        order_count += 1
        if o.get("_type") == "subscription":
            subscription_cost += amount
        elif o.get("_type") == "trip":
            trip_cost += amount
    return {
        "total_cost_pln": round(total, 2),
        "subscription_cost": round(subscription_cost, 2),
        "trip_cost": round(trip_cost, 2),
        "order_count": order_count,
    }


def haversine(lat1, lng1, lat2, lng2):
    R = 6371.0
    lat1, lng1, lat2, lng2 = map(np.radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlng / 2) ** 2
    return R * 2 * np.arcsin(np.sqrt(a))


def compute_distances(df):
    mask = df["has_start_station"] & df["has_end_station"]
    distances = pd.Series(np.nan, index=df.index)
    if mask.any():
        distances[mask] = (
            haversine(
                df.loc[mask, "start_lat"].values,
                df.loc[mask, "start_lng"].values,
                df.loc[mask, "end_lat"].values,
                df.loc[mask, "end_lng"].values,
            )
            * DISTANCE_FACTOR
        )
    return distances


def compute_overview_metrics(df, distances):
    unique_starts = df.loc[df["has_start_station"], "start_station_code"].nunique()
    unique_ends = df.loc[df["has_end_station"], "end_station_code"].nunique()
    all_codes = set()
    if df["has_start_station"].any():
        all_codes.update(df.loc[df["has_start_station"], "start_station_code"].unique())
    if df["has_end_station"].any():
        all_codes.update(df.loc[df["has_end_station"], "end_station_code"].unique())

    valid_distances = distances.dropna()
    return {
        "total_trips": len(df),
        "total_distance_km": distances.sum(),
        "total_duration_s": df["duration_s"].sum(),
        "avg_duration_s": df["duration_s"].mean(),
        "avg_distance_km": valid_distances.mean() if len(valid_distances) > 0 else 0,
        "unique_stations": len(all_codes),
        "days_with_trips": df["date"].nunique(),
        "date_min": df["started_at"].min(),
        "date_max": df["started_at"].max(),
        "null_end_count": (~df["has_end_station"]).sum(),
        "null_start_count": (~df["has_start_station"]).sum(),
    }


def compute_station_stats(df):
    starts_df = df[df["has_start_station"]]
    starts = (
        starts_df.groupby(["start_station_id", "start_station_code", "start_station_address", "start_lat", "start_lng"])
        .size()
        .reset_index(name="start_count")
        .rename(columns={
            "start_station_id": "station_id",
            "start_station_code": "code",
            "start_station_address": "address",
            "start_lat": "lat",
            "start_lng": "lng",
        })
    )

    ends_df = df[df["has_end_station"]]
    ends = (
        ends_df.groupby(["end_station_id", "end_station_code", "end_station_address", "end_lat", "end_lng"])
        .size()
        .reset_index(name="end_count")
        .rename(columns={
            "end_station_id": "station_id",
            "end_station_code": "code",
            "end_station_address": "address",
            "end_lat": "lat",
            "end_lng": "lng",
        })
    )

    merged = starts.merge(ends, on=["station_id", "code", "address", "lat", "lng"], how="outer").fillna(0)
    merged["start_count"] = merged["start_count"].astype(int)
    merged["end_count"] = merged["end_count"].astype(int)
    merged["total_count"] = merged["start_count"] + merged["end_count"]
    return merged.sort_values("total_count", ascending=False).reset_index(drop=True)


def compute_day_hour_matrix(df):
    counts = df.groupby(["day_of_week", "hour"]).size().reset_index(name="count")
    matrix = counts.pivot(index="day_of_week", columns="hour", values="count").fillna(0).astype(int)
    matrix = matrix.reindex(index=range(7), columns=range(24), fill_value=0)
    return matrix


def compute_frequency(df, freq="month"):
    """Compute trip frequency grouped by day, week, or month."""
    if freq == "day":
        grouped = df.groupby("date").size().reset_index(name="trips")
        grouped.columns = ["period", "trips"]
        grouped["period"] = pd.to_datetime(grouped["period"])
        # Fill missing days
        all_days = pd.date_range(grouped["period"].min(), pd.Timestamp.today().normalize(), freq="D")
        full = pd.DataFrame({"period": all_days})
        full = full.merge(grouped, on="period", how="left").fillna(0)
        full["trips"] = full["trips"].astype(int)
        full["label"] = full["period"].dt.strftime("%Y-%m-%d")
        return full
    elif freq == "week":
        df_copy = df.copy()
        df_copy["week_start"] = df_copy["started_at"].dt.to_period("W").apply(lambda p: p.start_time)
        grouped = df_copy.groupby("week_start").size().reset_index(name="trips")
        grouped.columns = ["period", "trips"]
        # Fill missing weeks
        all_weeks = pd.date_range(grouped["period"].min(), pd.Timestamp.today().normalize(), freq="W-MON")
        full = pd.DataFrame({"period": all_weeks})
        full = full.merge(grouped, on="period", how="left").fillna(0)
        full["trips"] = full["trips"].astype(int)
        full["label"] = full["period"].dt.strftime("%d.%m.%Y")
        return full
    else:  # month
        monthly = df.groupby("year_month").size().reset_index(name="trips")
        start = df["started_at"].min().to_period("M")
        end = pd.Timestamp.today().to_period("M")
        all_months = pd.period_range(start, end, freq="M").astype(str)
        full = pd.DataFrame({"year_month": all_months})
        full = full.merge(monthly, on="year_month", how="left").fillna(0)
        full["trips"] = full["trips"].astype(int)
        full["label"] = full["year_month"]
        full["period"] = pd.to_datetime(full["year_month"])
        return full


def compute_duration_bins(df):
    return df["duration_s"] / 60.0


def compute_activity_heatmap(df, month_names_short=None):
    """Compute GitHub-style activity heatmap data for the last 12 months.

    Returns a list of weeks, where each week is a list of 7 dicts
    (Mon=0 to Sun=6) with keys: date, count, in_range.
    Also returns month labels with their column positions.
    """
    from datetime import date

    if month_names_short is None:
        month_names_short = MONTH_NAMES_PL_SHORT

    today = date.today()
    year_ago = today - timedelta(days=364)

    # Count trips per date
    trip_counts = df.groupby("date").size().to_dict()

    # Find the Monday on or before year_ago
    start_monday = year_ago - timedelta(days=year_ago.weekday())

    weeks = []
    month_labels = []
    current = start_monday
    prev_month = None

    while current <= today:
        week = []
        for dow in range(7):
            d = current + timedelta(days=dow)
            in_range = year_ago <= d <= today
            week.append({
                "date": d,
                "count": trip_counts.get(d, 0) if in_range else 0,
                "in_range": in_range,
            })
            if in_range and d.month != prev_month and d.day <= 7:
                month_labels.append({
                    "month": month_names_short[d.month],
                    "col": len(weeks),
                })
                prev_month = d.month
        weeks.append(week)
        current += timedelta(days=7)

    return {"weeks": weeks, "month_labels": month_labels}


def compute_fun_stats(df, distances):
    total_km = distances.sum()
    total_hours = df["duration_s"].sum() / 3600.0

    # Environmental
    co2_saved_kg = (total_km * CO2_PER_KM_CAR) / 1000.0
    fuel_saved_liters = total_km * FUEL_PER_KM

    # Records
    longest_idx = df["duration_s"].idxmax()
    longest_trip = df.loc[longest_idx]

    trips_per_day = df.groupby("date").size()
    most_trips_day = trips_per_day.idxmax()
    most_trips_count = trips_per_day.max()

    # Streak
    unique_dates = sorted(df["date"].unique())
    max_streak = 1
    current_streak = 1
    streak_end = unique_dates[0]
    best_streak_end = unique_dates[0]
    for i in range(1, len(unique_dates)):
        if (unique_dates[i] - unique_dates[i - 1]).days == 1:
            current_streak += 1
            streak_end = unique_dates[i]
            if current_streak > max_streak:
                max_streak = current_streak
                best_streak_end = streak_end
        else:
            current_streak = 1
            streak_end = unique_dates[i]
    best_streak_start = best_streak_end - timedelta(days=max_streak - 1)

    # Favorite station
    all_stations = pd.concat([
        df.loc[df["has_start_station"], ["start_station_code", "start_station_address"]].rename(
            columns={"start_station_code": "code", "start_station_address": "address"}
        ),
        df.loc[df["has_end_station"], ["end_station_code", "end_station_address"]].rename(
            columns={"end_station_code": "code", "end_station_address": "address"}
        ),
    ])
    fav = all_stations.groupby(["code", "address"]).size().reset_index(name="count")
    fav_row = fav.loc[fav["count"].idxmax()]

    # Milestones
    df_sorted = df.sort_values("started_at")
    first_trip_date = df_sorted.iloc[0]["started_at"]
    hundredth_trip_date = df_sorted.iloc[99]["started_at"] if len(df_sorted) >= 100 else None

    busiest_month_raw = df.groupby("year_month").size().idxmax()
    # Format as MM.YYYY
    bm_period = pd.Period(busiest_month_raw, freq="M")
    busiest_month = f"{bm_period.month:02d}.{bm_period.year}"

    # Most active week — return date range instead of week number
    df_copy = df.copy()
    df_copy["week_start"] = df_copy["started_at"].dt.to_period("W").apply(lambda p: p.start_time)
    weekly = df_copy.groupby("week_start").size()
    most_active_week_start = weekly.idxmax()
    most_active_week_end = most_active_week_start + timedelta(days=6)
    most_active_week = (
        f"{most_active_week_start.strftime('%d.%m.%Y')} — {most_active_week_end.strftime('%d.%m.%Y')}"
    )
    most_active_week_count = int(weekly.max())

    return {
        "environmental": {
            "co2_saved_kg": round(co2_saved_kg, 1),
            "fuel_saved_liters": round(fuel_saved_liters, 1),
            "total_distance_km": round(total_km, 1),
        },
        "records": {
            "longest_trip_duration_s": int(longest_trip["duration_s"]),
            "longest_trip_start": longest_trip["start_station_code"] if longest_trip["has_start_station"] else "?",
            "longest_trip_end": longest_trip["end_station_code"] if longest_trip["has_end_station"] else "?",
            "most_trips_in_day_date": str(most_trips_day),
            "most_trips_in_day_count": int(most_trips_count),
            "longest_streak_days": max_streak,
            "longest_streak_range": f"{best_streak_start.strftime('%d.%m.%Y')} — {best_streak_end.strftime('%d.%m.%Y')}",
            "favorite_station_code": fav_row["code"],
            "favorite_station_address": fav_row["address"],
            "favorite_station_count": int(fav_row["count"]),
        },
        "milestones": {
            "first_trip_date": first_trip_date,
            "hundredth_trip_date": hundredth_trip_date,
            "busiest_month": busiest_month,
            "most_active_week": most_active_week,
            "most_active_week_count": most_active_week_count,
        },
    }
