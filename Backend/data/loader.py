"""
data/loader.py
==============
Data loading and transformation utilities.

Provides:
    load_data       – load stations CSV (or generate synthetic data)
    transform_data  – enrich raw DataFrame with derived columns
"""

from __future__ import annotations

import logging
import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────

_STATIONS = [
    "München Hbf", "München Ost", "Marienplatz", "Sendlinger Tor",
    "Hauptbahnhof", "Karlsplatz", "Isartor", "Rosenheimer Platz",
    "Max-Weber-Platz", "Münchner Freiheit",
]

_DOOR_STATES   = ["open", "closed", "jammed", "maintenance"]
_MAINT_STATUS  = ["OPTIMAL", "WARNING", "CRITICAL"]
_TRAIN_TYPES   = ["S-Bahn", "U-Bahn", "Tram", "Bus", "ICE", "RE"]
_OPERATORS     = ["DB", "MVG", "BVG", "ÖBB", "SBB"]
_ENERGY_GRADES = ["A+", "A", "B", "C", "D"]
_CONNECTION    = ["U1", "U2", "U3", "U4", "U5", "U6", "S1", "S2", "S3", "S4"]

# ─────────────────────────────────────────────────────────────────────────────


@st.cache_data(ttl=60, show_spinner=False)
def load_data(csv_path: str = "stations.csv") -> pd.DataFrame:
    """
    Load station gate data from *csv_path*.

    Falls back to synthetic data generation when the file is not found.
    """
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            logger.info("Loaded %d rows from '%s'.", len(df), csv_path)
            return transform_data(df)
        except Exception as exc:
            logger.warning("Failed to read '%s': %s – using synthetic data.", csv_path, exc)

    logger.info("'%s' not found – generating synthetic data.", csv_path)
    return _generate_synthetic(n_per_station=12)


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich a raw DataFrame with derived / missing columns.

    Safe to call on already-transformed data (idempotent for numeric cols).
    """
    rng = np.random.default_rng(0)

    n = len(df)

    # Ensure mandatory columns exist
    if "station" not in df.columns:
        df["station"] = np.random.choice(_STATIONS, n)

    if "sync_score" not in df.columns:
        df["sync_score"] = rng.uniform(40, 100, n).round(1)

    if "risk_score" not in df.columns:
        df["risk_score"] = (100 - df["sync_score"] + rng.uniform(-10, 10, n)).clip(0, 100).round(1)

    if "people" not in df.columns:
        df["people"] = rng.integers(50, 800, n)

    if "maintenance_status" not in df.columns:
        df["maintenance_status"] = np.where(
            df["risk_score"] >= 70, "CRITICAL",
            np.where(df["risk_score"] >= 45, "WARNING", "OPTIMAL")
        )

    if "door_state" not in df.columns:
        df["door_state"] = np.random.choice(
            _DOOR_STATES, n, p=[0.55, 0.35, 0.05, 0.05]
        )

    if "platform" not in df.columns:
        df["platform"] = rng.integers(1, 9, n)

    if "power_consumption" not in df.columns:
        df["power_consumption"] = rng.uniform(10, 25, n).round(2)

    if "energy_rating" not in df.columns:
        df["energy_rating"] = np.random.choice(_ENERGY_GRADES, n, p=[0.1, 0.3, 0.35, 0.2, 0.05])

    if "train_type" not in df.columns:
        df["train_type"] = np.random.choice(_TRAIN_TYPES, n)

    if "operator" not in df.columns:
        df["operator"] = np.random.choice(_OPERATORS, n)

    if "delay" not in df.columns:
        df["delay"] = rng.integers(-2, 15, n)

    if "connection_line" not in df.columns:
        df["connection_line"] = np.random.choice(_CONNECTION, n)

    if "occupancy_rate" not in df.columns:
        df["occupancy_rate"] = (df["people"] / 800).clip(0, 1).round(3)

    if "last_maintenance" not in df.columns:
        today = datetime.now()
        df["last_maintenance"] = [
            (today - timedelta(days=int(d))).strftime("%Y-%m-%d")
            for d in rng.integers(1, 180, n)
        ]

    if "signal_status" not in df.columns:
        df["signal_status"] = np.random.choice(["OK", "DEGRADED", "FAULT"], n, p=[0.8, 0.15, 0.05])

    logger.debug("transform_data: output shape %s", df.shape)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# SYNTHETIC DATA GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def _generate_synthetic(n_per_station: int = 12) -> pd.DataFrame:
    """Create a realistic synthetic gate dataset for all stations."""
    random.seed(42)
    rng = np.random.default_rng(42)
    rows = []

    for station in _STATIONS:
        for gate_idx in range(1, n_per_station + 1):
            sync  = round(float(rng.uniform(35, 98)), 1)
            risk  = round(float(np.clip(100 - sync + float(rng.normal(0, 8)), 0, 100)), 1)
            rows.append({
                "station":     station,
                "gate_id":     f"{station[:3].upper()}-G{gate_idx:02d}",
                "sync_score":  sync,
                "risk_score":  risk,
                "people":      int(rng.integers(50, 900)),
            })

    df = pd.DataFrame(rows)
    return transform_data(df)
