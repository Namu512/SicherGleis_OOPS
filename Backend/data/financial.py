"""
data/financial.py  — FIXED
============================
get_financial_model_data() accepts every keyword argument that
streamlit_app.py passes, and uses a path-safe import so it works
regardless of whether Python's cwd is the project root or Backend/.
"""

from __future__ import annotations

import logging
import os
import sys

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)

# ── Path fix: ensure Backend/ is on sys.path so `core` is always findable ──
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)


@st.cache_data(ttl=3600, show_spinner=False)
def get_financial_model_data(
    months: int = 24,
    starting_customers: int = 50,
    monthly_growth_rate: float = 0.20,
    churn_rate: float = 0.05,
    price_per_customer: float = 100.0,
    fixed_costs: float = 5_000.0,
    variable_cost_per_customer: float = 10.0,
    cac_simplified: float = 150.0,
    churn_rate_high: float | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Run the SaaS simulation for two scenarios and return
    (df_base, df_churn) — both plain DataFrames.

    Parameters mirror every kwarg that streamlit_app.py passes at line 5126.
    churn_rate_high defaults to churn_rate * 2 when not supplied.
    """
    from core.saas_simulator import SaaSModelConfig, SaaSSimulator

    if churn_rate_high is None:
        churn_rate_high = churn_rate * 2.0

    cfg_base = SaaSModelConfig(
        starting_customers=int(starting_customers),
        monthly_growth_rate=float(monthly_growth_rate),
        churn_rate=float(churn_rate),
        price_per_customer=float(price_per_customer),
        fixed_costs=float(fixed_costs),
        variable_cost_per_customer=float(variable_cost_per_customer),
        cac_simplified=float(cac_simplified),
    )

    cfg_churn = SaaSModelConfig(
        starting_customers=int(starting_customers),
        monthly_growth_rate=float(monthly_growth_rate),
        churn_rate=float(churn_rate_high),
        price_per_customer=float(price_per_customer),
        fixed_costs=float(fixed_costs),
        variable_cost_per_customer=float(variable_cost_per_customer),
        cac_simplified=float(cac_simplified),
    )

    df_base  = SaaSSimulator(cfg_base).run(months=int(months))
    df_churn = SaaSSimulator(cfg_churn).run(months=int(months))

    logger.info(
        "get_financial_model_data: %d months | base churn=%.1f%% | high churn=%.1f%%",
        months, churn_rate * 100, churn_rate_high * 100,
    )
    return df_base, df_churn