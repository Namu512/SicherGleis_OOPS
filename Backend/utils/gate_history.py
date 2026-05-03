"""
utils/gate_history.py
=====================
Historical gate performance data helper.

Provides:
    get_gate_performance_history  – 30-day rolling gate KPI history
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)


@st.cache_data(ttl=3600, show_spinner=False)
def get_gate_performance_history(station_name: str, days: int = 30) -> pd.DataFrame:
    """
    Return a synthetic 30-day daily performance history for *station_name*.

    Columns
    -------
    date, avg_sync_score, avg_risk_score, total_people,
    critical_gates, warning_gates, optimal_gates
    """
    rng = np.random.default_rng(abs(hash(station_name)) % (2**31))
    today = datetime.now().date()

    rows = []
    base_sync = float(rng.uniform(60, 85))
    base_risk = round(100 - base_sync + float(rng.normal(0, 5)), 1)

    for i in range(days - 1, -1, -1):
        day = today - timedelta(days=i)
        sync = float(np.clip(base_sync + rng.normal(0, 3), 30, 100))
        risk = float(np.clip(base_risk + rng.normal(0, 4), 0, 100))
        total_gates = 12
        critical = int(rng.integers(0, 3))
        warning  = int(rng.integers(1, 4))
        optimal  = max(0, total_gates - critical - warning)

        rows.append({
            "date":           day.isoformat(),
            "avg_sync_score": round(sync, 1),
            "avg_risk_score": round(risk, 1),
            "total_people":   int(rng.integers(3_000, 25_000)),
            "critical_gates": critical,
            "warning_gates":  warning,
            "optimal_gates":  optimal,
        })

        # Drift the base slowly
        base_sync = float(np.clip(base_sync + rng.normal(0, 0.5), 40, 95))
        base_risk = float(np.clip(100 - base_sync + rng.normal(0, 2), 0, 100))

    df = pd.DataFrame(rows)
    logger.debug("get_gate_performance_history: %d rows for '%s'.", len(df), station_name)
    return df
