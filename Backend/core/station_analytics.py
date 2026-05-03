"""
core/station_analytics.py  — FIXED
====================================
Every return shape matches exactly what streamlit_app.py expects.

Key contracts
-------------
get_psd_analytics()       → (cycles_df, temp_df)
                             cycles_df: columns [Hour, Door Cycles]
                             temp_df:   columns [Hour, Avg Temp (°C)]

get_maintenance_forecast() → DataFrame columns: [Date, Predicted Risk %]

get_network_summary()     → dict with keys:
                             total_gates, total_stations, total_people,
                             critical_count, warning_count, optimal_count,
                             avg_sync, avg_risk, health_score,
                             station_summary  (DataFrame: Station, Gates,
                                               Avg Sync %, Avg Risk, Passengers)
                             status_dist      (DataFrame: maintenance_status, Count)
                             train_type_dist  (DataFrame: train_type, Count)
                             door_dist        (DataFrame: door_state, Count)
                             operator_stats   (DataFrame: Operator, Gates,
                                               Avg Sync %, Avg Risk)
                             network_sync, network_risk, network_health

get_incident_log()        → DataFrame columns:
                             [Time, Severity, Station, Description,
                              Temp (°C), Vibration]
"""

from __future__ import annotations

import logging
import math
import random
from datetime import datetime, timedelta
from typing import Dict, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# STATION ANALYTICS
# ─────────────────────────────────────────────────────────────────────────────

class StationAnalytics:
    """Compute analytics for a single station."""

    def __init__(self, df: pd.DataFrame, station_name: str) -> None:
        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                f"df must be pd.DataFrame, got {type(df).__name__}"
            )
        self._df           = df
        self._station_name = station_name
        self._station_df   = (
            df[df["station"] == station_name].copy()
            if not df.empty else pd.DataFrame()
        )

    # ── 7-tuple metrics ───────────────────────────────────────────────────────
    def get_metrics(self) -> Tuple:
        """
        Returns
        -------
        (gates_total, gates_active, people_total, critical_count,
         avg_sync, warning_count, metrics_dict)
        """
        sdf = self._station_df
        if sdf.empty:
            return (0, 0, 0, 0, 0.0, 0, {})

        gates_total    = len(sdf)
        gates_active   = (len(sdf[sdf["door_state"] != "jammed"])
                          if "door_state" in sdf.columns else gates_total)
        people_total   = int(sdf["people"].sum()) if "people" in sdf.columns else 0
        critical_count = int((sdf["maintenance_status"] == "CRITICAL").sum()) if "maintenance_status" in sdf.columns else 0
        warning_count  = int((sdf["maintenance_status"] == "WARNING").sum())  if "maintenance_status" in sdf.columns else 0
        avg_sync       = round(float(sdf["sync_score"].mean()), 1) if "sync_score" in sdf.columns else 0.0

        metrics_dict = {
            "gates_total":    gates_total,
            "gates_active":   gates_active,
            "people_total":   people_total,
            "critical_count": critical_count,
            "warning_count":  warning_count,
            "avg_sync":       avg_sync,
            "avg_risk":       round(float(sdf["risk_score"].mean()), 1) if "risk_score" in sdf.columns else 0.0,
        }
        return (gates_total, gates_active, people_total, critical_count,
                avg_sync, warning_count, metrics_dict)

    # ── PSD analytics → (cycles_df, temp_df) ─────────────────────────────────
    def get_psd_analytics(self):
        """
        Returns (cycles_df, temp_df).

        cycles_df columns : Hour (int 0-23), Door Cycles (float)
        temp_df   columns : Hour (int 0-23), Avg Temp (°C) (float)

        Used by streamlit_app.py line 4320:
            cycles_df, temp_df = get_psd_analytics_cached(current_station)
        and lines 4324, 4361 which access:
            temp_df["Hour"], temp_df["Avg Temp (°C)"]
            cycles_df["Hour"], cycles_df["Door Cycles"]
        """
        rng   = np.random.default_rng(abs(hash(self._station_name)) % (2**31))
        hours = list(range(24))

        cycles, temps = [], []
        for h in hours:
            rush = (30 * math.exp(-((h - 8) ** 2) / 8)
                    + 25 * math.exp(-((h - 18) ** 2) / 8))
            cycles.append(round(20 + rush + float(rng.normal(0, 3)), 1))
            temps.append(round(22.0 + 0.5 * math.sin(h / 3.8)
                               + float(rng.normal(0, 0.4)), 1))

        cycles_df = pd.DataFrame({"Hour": hours, "Door Cycles": cycles})
        temp_df   = pd.DataFrame({"Hour": hours, "Avg Temp (°C)": temps})
        return cycles_df, temp_df

    # ── Maintenance forecast ──────────────────────────────────────────────────
    def get_maintenance_forecast(self) -> pd.DataFrame:
        """
        Returns DataFrame with columns:
            Date (str YYYY-MM-DD), Predicted Risk % (float)

        Used by streamlit_app.py line 4817:
            x=forecast_df["Date"], y=forecast_df["Predicted Risk %"]
        """
        rng       = np.random.default_rng(abs(hash(self._station_name)) % (2**31))
        today     = datetime.now().date()
        base_risk = float(rng.uniform(20, 60))

        rows = []
        for i in range(14):
            day_risk = min(100.0, max(0.0, base_risk + float(rng.normal(i * 1.5, 5))))
            rows.append({
                "Date":             (today + timedelta(days=i)).strftime("%Y-%m-%d"),
                "Predicted Risk %": round(day_risk, 1),
            })
        return pd.DataFrame(rows)

    # ── Passenger heatmap ─────────────────────────────────────────────────────
    def get_passenger_heatmap(self) -> pd.DataFrame:
        """Return a 7-day × 12-hour passenger flow matrix (index = day name)."""
        rng   = np.random.default_rng(abs(hash(self._station_name)) % (2**31))
        days  = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        slots = ["06:00", "07:00", "08:00", "09:00", "10:00", "11:00",
                 "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]

        rows = []
        for d in days:
            row = {"day": d}
            for s in slots:
                hour       = int(s.split(":")[0])
                is_weekend = d in ("Sat", "Sun")
                base       = 300 if not is_weekend else 150
                rush       = (200 * math.exp(-((hour - 8) ** 2) / 4)
                              + 180 * math.exp(-((hour - 17) ** 2) / 4))
                row[s] = max(0, int(base + rush + float(rng.normal(0, 30))))
            rows.append(row)

        return pd.DataFrame(rows).set_index("day")

    # ── Train schedule ────────────────────────────────────────────────────────
    def get_train_schedule(self, df: pd.DataFrame | None = None) -> pd.DataFrame:
        rng  = random.Random(abs(hash(self._station_name)))
        base = datetime.now().replace(second=0, microsecond=0)
        rows = []
        for i in range(20):
            dep   = base + timedelta(minutes=i * 8 + rng.randint(0, 5))
            delay = rng.randint(0, 12) if rng.random() < 0.25 else 0
            rows.append({
                "Line":      rng.choice(["S1", "S2", "S3", "U4", "U5", "RE10", "ICE72"]),
                "Direction": rng.choice(["Northbound", "Southbound", "Eastbound", "Westbound"]),
                "Scheduled": dep.strftime("%H:%M"),
                "Delay_min": delay,
                "Status":    "Delayed" if delay > 0 else "On Time",
                "Platform":  rng.randint(1, 8),
            })
        return pd.DataFrame(rows)

    # ── Platform occupancy prediction ─────────────────────────────────────────
    def predict_platform_occupancy(self, time_window_minutes: int = 30) -> Dict:
        sdf  = self._station_df
        cur  = (int(sdf["people"].sum())
                if not sdf.empty and "people" in sdf.columns else 500)
        pred = round(cur * (1 + 0.015 * (time_window_minutes / 10)))
        cap  = 2000
        return {
            "current_occupancy":   cur,
            "predicted_occupancy": pred,
            "capacity":            cap,
            "utilisation_pct":     round(pred / cap * 100, 1),
            "time_window_minutes": time_window_minutes,
            "alert_level":         ("HIGH"   if pred / cap > 0.8 else
                                    "MEDIUM" if pred / cap > 0.6 else "LOW"),
        }


# ─────────────────────────────────────────────────────────────────────────────
# NETWORK ANALYTICS
# ─────────────────────────────────────────────────────────────────────────────

class NetworkAnalytics:
    """Compute network-wide analytics from the full dataframe."""

    def __init__(self, df: pd.DataFrame) -> None:
        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                f"df must be pd.DataFrame, got {type(df).__name__}"
            )
        self._df = df

    def get_network_summary(self) -> Dict:
        """
        Returns a dict with ALL keys used by streamlit_app.py.

        Scalar keys
        -----------
        total_gates, total_stations, total_people,
        critical_count, warning_count, optimal_count,
        avg_sync, avg_risk, health_score,
        network_sync, network_risk, network_health

        DataFrame keys
        --------------
        station_summary  — columns: Station, Gates, Avg Sync %, Avg Risk, Passengers
        status_dist      — columns: maintenance_status, Count
        train_type_dist  — columns: train_type, Count
        door_dist        — columns: door_state, Count
        operator_stats   — columns: Operator, Gates, Avg Sync %, Avg Risk
        """
        df = self._df
        if df.empty:
            return {}

        total_gates    = len(df)
        critical_count = int((df["maintenance_status"] == "CRITICAL").sum()) if "maintenance_status" in df.columns else 0
        warning_count  = int((df["maintenance_status"] == "WARNING").sum())  if "maintenance_status" in df.columns else 0
        optimal_count  = int((df["maintenance_status"] == "OPTIMAL").sum())  if "maintenance_status" in df.columns else 0
        total_people   = int(df["people"].sum())                 if "people"     in df.columns else 0
        avg_sync       = round(float(df["sync_score"].mean()), 1) if "sync_score" in df.columns else 0.0
        avg_risk       = round(float(df["risk_score"].mean()), 1) if "risk_score" in df.columns else 0.0
        n_stations     = df["station"].nunique()                  if "station"    in df.columns else 0

        health_score = round(
            avg_sync * 0.4
            + (100 - avg_risk) * 0.4
            + (optimal_count / max(total_gates, 1) * 100) * 0.2,
            1,
        )

        # ── station_summary ───────────────────────────────────────────────────
        grp = df.groupby("station", sort=True)
        station_summary = pd.DataFrame({
            "Station":    grp["station"].first().values,
            "Gates":      grp["sync_score"].count().values,
            "Avg Sync %": grp["sync_score"].mean().round(1).values,
            "Avg Risk":   grp["risk_score"].mean().round(1).values,
            "Passengers": grp["people"].sum().astype(int).values,
        })

        # ── status_dist ───────────────────────────────────────────────────────
        if "maintenance_status" in df.columns:
            _vc = df["maintenance_status"].value_counts().reset_index()
            _vc.columns = ["maintenance_status", "Count"]
            status_dist = _vc
        else:
            status_dist = pd.DataFrame(columns=["maintenance_status", "Count"])

        # ── train_type_dist ───────────────────────────────────────────────────
        if "train_type" in df.columns:
            _vc = df["train_type"].value_counts().reset_index()
            _vc.columns = ["train_type", "Count"]
            train_type_dist = _vc
        else:
            train_type_dist = pd.DataFrame(columns=["train_type", "Count"])

        # ── door_dist ─────────────────────────────────────────────────────────
        if "door_state" in df.columns:
            _vc = df["door_state"].value_counts().reset_index()
            _vc.columns = ["door_state", "Count"]
            door_dist = _vc
        else:
            door_dist = pd.DataFrame(columns=["door_state", "Count"])

        # ── operator_stats ────────────────────────────────────────────────────
        if "operator" in df.columns:
            _op = (
                df.groupby("operator", sort=True)
                .agg(
                    Gates      =("sync_score", "count"),
                    **{"Avg Sync %": ("sync_score", lambda x: round(float(x.mean()), 1))},
                    **{"Avg Risk":   ("risk_score", lambda x: round(float(x.mean()), 1))},
                )
                .reset_index()
                .rename(columns={"operator": "Operator"})
            )
            operator_stats = _op[["Operator", "Gates", "Avg Sync %", "Avg Risk"]]
        else:
            operator_stats = pd.DataFrame(
                columns=["Operator", "Gates", "Avg Sync %", "Avg Risk"])

        return {
            # scalars
            "total_gates":     total_gates,
            "total_stations":  n_stations,
            "total_people":    total_people,
            "critical_count":  critical_count,
            "warning_count":   warning_count,
            "optimal_count":   optimal_count,
            "avg_sync":        avg_sync,
            "avg_risk":        avg_risk,
            "health_score":    health_score,
            "network_sync":    avg_sync,
            "network_risk":    avg_risk,
            "network_health":  health_score,
            # DataFrames
            "station_summary": station_summary,
            "status_dist":     status_dist,
            "train_type_dist": train_type_dist,
            "door_dist":       door_dist,
            "operator_stats":  operator_stats,
        }

    def get_incident_log(self) -> pd.DataFrame:
        """
        Returns DataFrame with columns:
            Time, Severity, Station, Description, Temp (°C), Vibration

        Used by streamlit_app.py lines 4745-4787:
            incidents["Severity"].str.contains("CRITICAL")
            row['Time'], row['Severity'], row['Station']
            row['Description'], row['Temp (°C)'], row['Vibration']
        """
        _empty = pd.DataFrame(
            columns=["Time", "Severity", "Station", "Description",
                     "Temp (°C)", "Vibration"])

        df = self._df
        if df.empty or "maintenance_status" not in df.columns:
            return _empty

        incidents = df[df["maintenance_status"].isin(["CRITICAL", "WARNING"])].copy()
        if incidents.empty:
            return _empty

        now  = datetime.now()
        rows = []
        for i, (_, row) in enumerate(incidents.iterrows()):
            status  = str(row.get("maintenance_status", "WARNING"))
            temp    = float(row.get("sensor_temp", round(25.0 + i * 0.7, 1)))
            vib     = float(row.get("sensor_vib",  round(0.50 + i * 0.05, 2)))
            gate_id = str(row.get("gate_id",  f"G{i:02d}"))
            station = str(row.get("station",  "Unknown"))

            if status == "CRITICAL":
                desc = f"Gate {gate_id} — door jammed, temp {temp:.1f}°C"
            else:
                desc = f"Gate {gate_id} — elevated vibration {vib:.2f} mm/s"

            rows.append({
                "Time":        (now - timedelta(minutes=i * 7)).strftime("%H:%M:%S"),
                "Severity":    status,
                "Station":     station,
                "Description": desc,
                "Temp (°C)":   round(temp, 1),
                "Vibration":   round(vib, 2),
            })

        return pd.DataFrame(rows)
