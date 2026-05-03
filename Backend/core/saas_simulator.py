"""
core/saas_simulator.py
======================
SaaS financial simulation engine.

Provides:
    SaaSModelConfig  – dataclass holding all model parameters
    SaaSSimulator    – runs the month-by-month simulation
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SaaSModelConfig:
    """All parameters that drive the SaaS simulation."""

    # --- Customer growth ---
    starting_customers: int = 50
    monthly_growth_rate: float = 0.20        # fraction, e.g. 0.20 = 20 %
    churn_rate: float = 0.05                 # monthly churn fraction

    # --- Pricing (per tier, per month) ---
    price_per_customer: float = 100.0        # blended / legacy field
    price_basic: float = 49.0
    price_pro: float = 149.0
    price_enterprise: float = 499.0

    # --- Costs ---
    fixed_costs: float = 5_000.0
    variable_cost_per_customer: float = 10.0
    cac_simplified: float = 150.0            # blended CAC

    # --- Headcount seeds ---
    initial_eng: int = 5
    initial_sales: int = 3
    initial_marketing: int = 2
    initial_cs: int = 2
    initial_ga: int = 2

    # --- Salary assumptions (annual, divided /12 internally) ---
    salary_eng: float = 120_000
    salary_sales: float = 80_000
    salary_marketing: float = 75_000
    salary_cs: float = 65_000
    salary_ga: float = 90_000

    # --- Tier mix (fractions, must sum ≤ 1; remainder → basic) ---
    pro_fraction: float = 0.30
    enterprise_fraction: float = 0.10

    # --- Expansion / contraction MRR rates ---
    expansion_rate: float = 0.02
    contraction_rate: float = 0.005

    # --- Misc ---
    seed: Optional[int] = 42


# ─────────────────────────────────────────────────────────────────────────────
# SIMULATOR
# ─────────────────────────────────────────────────────────────────────────────

class SaaSSimulator:
    """Month-by-month SaaS financial model."""

    def __init__(self, config: SaaSModelConfig) -> None:
        self.cfg = config
        if config.seed is not None:
            np.random.seed(config.seed)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, months: int = 24) -> pd.DataFrame:
        """Run the simulation for *months* periods and return a DataFrame."""
        cfg = self.cfg
        records = []

        # ── State ────────────────────────────────────────────────────────────
        total_customers = cfg.starting_customers
        cumulative_cash = 0.0

        # Headcount
        hc = {
            "GA":          cfg.initial_ga,
            "Engineering": cfg.initial_eng,
            "Marketing":   cfg.initial_marketing,
            "Sales":       cfg.initial_sales,
            "CS":          cfg.initial_cs,
        }

        prev_mrr = 0.0

        for month in range(1, months + 1):
            # ── Customer dynamics ─────────────────────────────────────────────
            churned      = max(0, round(total_customers * cfg.churn_rate))
            new_customers = max(0, round(total_customers * cfg.monthly_growth_rate))
            total_customers = max(0, total_customers - churned + new_customers)

            # Tier split
            n_enterprise = round(total_customers * cfg.enterprise_fraction)
            n_pro        = round(total_customers * cfg.pro_fraction)
            n_basic      = max(0, total_customers - n_enterprise - n_pro)

            # New enterprise wins / losses (simplified)
            new_enterprise_wins  = max(0, round(new_customers * cfg.enterprise_fraction))
            enterprise_upgrades  = max(0, round(n_pro * 0.02))
            lost_enterprise      = max(0, round(n_enterprise * cfg.churn_rate * 0.5))

            # ── Revenue ───────────────────────────────────────────────────────
            base_mrr = (
                n_basic      * cfg.price_basic
                + n_pro      * cfg.price_pro
                + n_enterprise * cfg.price_enterprise
            )
            expansion_mrr  = round(base_mrr * cfg.expansion_rate, 2)
            contraction_mrr = round(base_mrr * cfg.contraction_rate, 2)
            churn_mrr      = round(prev_mrr * cfg.churn_rate, 2)
            new_mrr        = round(new_customers * cfg.price_per_customer, 2)
            mrr            = round(base_mrr + expansion_mrr - contraction_mrr, 2)
            net_new_mrr    = round(mrr - prev_mrr, 2)
            arr            = round(mrr * 12, 2)
            mom_growth_pct = round((mrr / prev_mrr - 1) * 100, 2) if prev_mrr > 0 else 0.0
            revenue        = mrr

            # ── Headcount growth ──────────────────────────────────────────────
            hc = self._grow_headcount(hc, total_customers)

            # ── Salary costs ──────────────────────────────────────────────────
            sal = {
                "GA":          hc["GA"]          * cfg.salary_ga          / 12,
                "Engineering": hc["Engineering"] * cfg.salary_eng         / 12,
                "Marketing":   hc["Marketing"]   * cfg.salary_marketing   / 12,
                "Sales":       hc["Sales"]        * cfg.salary_sales      / 12,
                "CS":          hc["CS"]           * cfg.salary_cs         / 12,
            }
            total_salaries = sum(sal.values())

            # ── Cost structure (standard SaaS P&L) ───────────────────────────
            cogs        = round(total_customers * cfg.variable_cost_per_customer + revenue * 0.08, 2)
            gross_profit = round(revenue - cogs, 2)
            gross_margin = round((gross_profit / revenue * 100) if revenue > 0 else 0, 2)

            rd_cost  = round(sal["Engineering"] * 1.15 + revenue * 0.04, 2)
            sm_cost  = round((sal["Sales"] + sal["Marketing"]) * 1.20 + revenue * 0.05, 2)
            ga_cost  = round(sal["GA"] * 1.10 + cfg.fixed_costs, 2)
            cs_cost  = round(sal["CS"] * 1.10 + total_customers * 2, 2)

            total_opex = round(rd_cost + sm_cost + ga_cost + cs_cost, 2)
            ebit       = round(gross_profit - total_opex, 2)

            # ── Cash ──────────────────────────────────────────────────────────
            tax          = max(0.0, round(ebit * 0.21, 2))
            profit_loss  = round(ebit - tax, 2)
            cumulative_cash = round(cumulative_cash + profit_loss, 2)

            # ── Unit economics ────────────────────────────────────────────────
            cac = cfg.cac_simplified
            ltv_basic      = round((cfg.price_basic      / cfg.churn_rate) * (gross_margin / 100), 2)
            ltv_pro        = round((cfg.price_pro        / cfg.churn_rate) * (gross_margin / 100), 2)
            ltv_enterprise = round((cfg.price_enterprise / cfg.churn_rate) * (gross_margin / 100), 2)
            ltv_blended    = round((ltv_basic * n_basic + ltv_pro * n_pro + ltv_enterprise * n_enterprise)
                                   / max(total_customers, 1), 2)
            ltv_cac        = round(ltv_blended / cac, 2) if cac > 0 else 0

            cac_payback_basic      = round(cac / cfg.price_basic      if cfg.price_basic      > 0 else 0, 1)
            cac_payback_pro        = round(cac / cfg.price_pro        if cfg.price_pro        > 0 else 0, 1)
            cac_payback_enterprise = round(cac / cfg.price_enterprise if cfg.price_enterprise > 0 else 0, 1)

            sm_efficiency = round(net_new_mrr * 12 / sm_cost, 2) if sm_cost > 0 else 0

            records.append({
                # Time
                "Month": month,
                # Customers
                "Total_Customers":       total_customers,
                "New_Customers":         new_customers,
                "Churned_Customers":     churned,
                "Basic_Customers":       n_basic,
                "Pro_Customers":         n_pro,
                "Enterprise_Customers":  n_enterprise,
                "New_Enterprise_Wins":   new_enterprise_wins,
                "Enterprise_Upgrades":   enterprise_upgrades,
                "Lost_Enterprise":       lost_enterprise,
                # Revenue
                "MRR":            mrr,
                "ARR":            arr,
                "Revenue":        revenue,
                "Total_Revenue":  revenue,   # alias expected by visualize_dashboard_2
                "New_MRR":        new_mrr,
                "Expansion_MRR":  expansion_mrr,
                "Churn_MRR":      churn_mrr,
                "Net_New_MRR":    net_new_mrr,
                "MoM_Growth_%":   mom_growth_pct,
                # Margins
                "COGS":           cogs,
                "Gross_Profit":   gross_profit,
                "Gross_Margin_%": gross_margin,
                # Costs
                "RD_Cost":  rd_cost,
                "SM_Cost":  sm_cost,
                "GA_Cost":  ga_cost,
                "CS_Cost":  cs_cost,
                # Salaries
                "Salary_GA":          sal["GA"],
                "Salary_Engineering": sal["Engineering"],
                "Salary_Marketing":   sal["Marketing"],
                "Salary_Sales":       sal["Sales"],
                "Salary_CS":          sal["CS"],
                # Headcount
                "HC_GA":          hc["GA"],
                "HC_Engineering": hc["Engineering"],
                "HC_Marketing":   hc["Marketing"],
                "HC_Sales":       hc["Sales"],
                "HC_CS":          hc["CS"],
                "Total_Headcount": sum(hc.values()),
                # P&L
                "EBIT":           ebit,
                "Profit_Loss":    profit_loss,
                "Cumulative_Cash": cumulative_cash,
                # Unit economics
                "LTV_Blended":          ltv_blended,
                "LTV_CAC_Ratio":        ltv_cac,
                "CAC_Payback_Basic":    cac_payback_basic,
                "CAC_Payback_Pro":      cac_payback_pro,
                "CAC_Payback_Enterprise": cac_payback_enterprise,
                "SM_Efficiency":        sm_efficiency,
            })

            prev_mrr = mrr

        df = pd.DataFrame(records)
        logger.info("SaaSSimulator: completed %d-month simulation.", months)
        return df

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _grow_headcount(hc: dict, total_customers: int) -> dict:
        """Simple rule-based headcount scaling."""
        hc = dict(hc)  # copy
        thresholds = [100, 250, 500, 1000, 2000]
        additions  = [
            {"CS": 1},
            {"Sales": 1, "Engineering": 1},
            {"CS": 1, "Marketing": 1},
            {"Sales": 2, "Engineering": 2, "GA": 1},
            {"Sales": 2, "Engineering": 2, "CS": 2, "Marketing": 1},
        ]
        for thresh, add in zip(thresholds, additions):
            if total_customers >= thresh:
                for dept, n in add.items():
                    # Only add once per threshold crossing (check current level)
                    target = {
                        100:  {"CS": 3, "Sales": 3, "Engineering": 5, "Marketing": 2, "GA": 2},
                        250:  {"CS": 3, "Sales": 4, "Engineering": 6, "Marketing": 2, "GA": 2},
                        500:  {"CS": 4, "Sales": 4, "Engineering": 6, "Marketing": 3, "GA": 2},
                        1000: {"CS": 4, "Sales": 6, "Engineering": 8, "Marketing": 3, "GA": 3},
                        2000: {"CS": 6, "Sales": 8, "Engineering": 10, "Marketing": 4, "GA": 3},
                    }[thresh]
                    hc[dept] = max(hc[dept], target[dept])
        return hc