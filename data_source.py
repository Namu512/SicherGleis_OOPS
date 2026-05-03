"""
data_source.py  (REFACTORED)
===========================
Backward-compatible public API shim.

All original function names are preserved so that streamlit_app.py and
dashboard.py continue to work without modification.

Implementation is now delegated to the modular packages:
  Backend/data/       → loading & financial simulation data
  Backend/core/       → analytics classes
  Backend/utils/      → formatting helpers & static data
"""

import logging

import streamlit as st
import pandas as pd
import numpy as np

# ── Internal modules ─────────────────────────────────────────────────────────
from Backend.data.loader import load_data, transform_data          # noqa: F401 (re-exported)
from Backend.data.financial import get_financial_model_data        # noqa: F401 (re-exported)
from Backend.core.station_analytics import StationAnalytics, NetworkAnalytics
from Backend.utils.static_data import get_leadership_data, get_tech_stack  # noqa: F401
from Backend.utils.gate_history import get_gate_performance_history        # noqa: F401

# Configure logging once for the whole application
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# STATION METRICS  (delegated to StationAnalytics)
# ─────────────────────────────────────────────

@st.cache_data(ttl=60, show_spinner=False)
def get_metrics(df: pd.DataFrame, station_name: str) -> tuple:
    """
    Get comprehensive station-level metrics.
    Returns a 7-tuple for backward compatibility:
    (gates_total, gates_active, people_total, critical_count,
     avg_sync, warning_count, metrics_dict)
    """
    return StationAnalytics(df, station_name).get_metrics()


# ─────────────────────────────────────────────
# PSD ANALYTICS  (delegated to StationAnalytics)
# ─────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def get_psd_analytics(station_name: str):
    """Deterministic hourly chart data for door cycles and temperature."""
    # We need a dummy df to instantiate StationAnalytics; the method
    # doesn't actually use self._station_df for this computation.
    return StationAnalytics(pd.DataFrame(), station_name).get_psd_analytics()


# ─────────────────────────────────────────────
# NETWORK SUMMARY  (delegated to NetworkAnalytics)
# ─────────────────────────────────────────────

@st.cache_data(ttl=60, show_spinner=False)
def get_network_summary(df: pd.DataFrame) -> dict:
    """Comprehensive network-wide analytics."""
    return NetworkAnalytics(df).get_network_summary()


# ─────────────────────────────────────────────
# MAINTENANCE FORECAST  (delegated to StationAnalytics)
# ─────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def get_maintenance_forecast(station_name: str) -> pd.DataFrame:
    """Return 7-day predicted risk trajectory DataFrame."""
    return StationAnalytics(pd.DataFrame(), station_name).get_maintenance_forecast()


# ─────────────────────────────────────────────
# PASSENGER HEATMAP  (delegated to StationAnalytics)
# ─────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def get_passenger_heatmap(station_name: str) -> pd.DataFrame:
    """Return 7-day × 12-hour passenger flow matrix."""
    return StationAnalytics(pd.DataFrame(), station_name).get_passenger_heatmap()


# ─────────────────────────────────────────────
# INCIDENT LOG  (delegated to NetworkAnalytics)
# ─────────────────────────────────────────────

@st.cache_data(ttl=60, show_spinner=False)
def get_incident_log(df: pd.DataFrame) -> pd.DataFrame:
    """Generate incident records from CRITICAL and WARNING gates."""
    return NetworkAnalytics(df).get_incident_log()


# ─────────────────────────────────────────────
# TRAIN SCHEDULE  (delegated to StationAnalytics)
# ─────────────────────────────────────────────

@st.cache_data(ttl=60, show_spinner=False)
def get_train_schedule(station_name: str, df: pd.DataFrame) -> pd.DataFrame:
    """Generate a realistic train schedule for a station."""
    return StationAnalytics(df, station_name).get_train_schedule()


# ─────────────────────────────────────────────
# PLATFORM OCCUPANCY PREDICTION  (delegated to StationAnalytics)
# ─────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def predict_platform_occupancy(
    station_name: str, df: pd.DataFrame, time_window_minutes: int = 30
) -> dict:
    """Predict platform occupancy for the next time window."""
    return StationAnalytics(df, station_name).predict_platform_occupancy(
        time_window_minutes=time_window_minutes
    )


# ─────────────────────────────────────────────
# STATION DETAILED PROFILE  (inline – kept for backward compat)
# ─────────────────────────────────────────────

def _calc_avg_maintenance_age(series: pd.Series) -> float:
    """Helper: average days since last maintenance date."""
    from datetime import datetime
    today = datetime.now()
    ages = []
    for val in series:
        try:
            dt = datetime.strptime(str(val), "%Y-%m-%d")
            ages.append((today - dt).days)
        except (ValueError, TypeError):
            ages.append(0)
    return round(sum(ages) / len(ages), 1) if ages else 0.0


@st.cache_data(ttl=300, show_spinner=False)
def get_station_detailed_profile(df: pd.DataFrame, station_name: str) -> dict:
    """Generate a comprehensive analytics profile for a specific station."""
    from datetime import datetime
    station_df = df[df["station"] == station_name].copy()
    if station_df.empty:
        logger.warning("No data for station '%s' in detailed profile.", station_name)
        return {}

    profile = {
        "station_name": station_name,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "infrastructure": {
            "total_gates":         len(station_df),
            "platforms":           station_df["platform"].nunique(),
            "avg_platform_length": station_df.get("platform_length", pd.Series(420)).mean(),
            "track_count":         station_df.get("track_number",   pd.Series(1)).nunique(),
        },
        "performance": {
            "avg_sync_score":     round(station_df["sync_score"].mean(), 1),
            "avg_risk_score":     round(station_df["risk_score"].mean(), 1),
            "network_health_score": round(
                station_df["sync_score"].mean() * 0.4
                + (100 - station_df["risk_score"].mean()) * 0.4
                + (len(station_df[station_df["maintenance_status"] == "OPTIMAL"]) / len(station_df) * 100) * 0.2,
                1,
            ),
            "total_passengers":   int(station_df["people"].sum()),
            "avg_occupancy_rate": round(station_df.get("occupancy_rate", pd.Series(0)).mean() * 100, 1),
        },
        "maintenance": {
            "critical_gates": len(station_df[station_df["maintenance_status"] == "CRITICAL"]),
            "warning_gates":  len(station_df[station_df["maintenance_status"] == "WARNING"]),
            "optimal_gates":  len(station_df[station_df["maintenance_status"] == "OPTIMAL"]),
            "jammed_gates":   len(station_df[station_df["door_state"] == "jammed"]),
            "avg_days_since_maintenance": _calc_avg_maintenance_age(
                station_df.get("last_maintenance", pd.Series(datetime.now().strftime("%Y-%m-%d")))
            ),
        },
        "energy": {
            "total_power_kw":       round(station_df.get("power_consumption", pd.Series(15)).sum(), 1),
            "avg_power_per_gate":   round(station_df.get("power_consumption", pd.Series(15)).mean(), 1),
            "energy_ratings":       station_df.get("energy_rating", pd.Series("B")).value_counts().to_dict(),
        },
        "train_operations": {
            "unique_train_types": station_df.get("train_type", pd.Series("Standard")).nunique(),
            "unique_operators":   station_df.get("operator",   pd.Series("DB")).nunique(),
            "avg_delay":          round(station_df.get("delay", pd.Series(0)).abs().mean(), 1),
            "on_time_percentage": round(
                len(station_df[station_df.get("delay", 0) == 0]) / len(station_df) * 100, 1
            ) if len(station_df) > 0 else 0,
        },
        "connectivity": {
            "connection_lines": station_df.get("connection_line", pd.Series("U1")).unique().tolist(),
            "signal_system":    "GSM-R" if "signal_status" in station_df.columns else "Legacy",
        },
    }
    logger.info("Detailed profile generated for station '%s'.", station_name)
    return profile