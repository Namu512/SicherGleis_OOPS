"""
app.py  (REFACTORED)
====================
SaaS Financial Model – CLI entry point and visualisation layer.

Core simulation logic has been moved to:
    core/saas_simulator.py   →  SaaSModelConfig, SaaSSimulator

Matplotlib visualisation helpers are kept here to avoid touching
dashboard.py's import surface.
"""

import logging
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

from Backend.core.saas_simulator import SaaSModelConfig, SaaSSimulator  # noqa: F401 (re-exported for dashboard.py)

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# SIMULATION RUNNER  (thin wrapper kept for backward compatibility)
# ─────────────────────────────────────────────────────────────────────────────

def run_simulation(config: SaaSModelConfig, months: int = 24) -> pd.DataFrame:
    """
    Simulate SaaS metrics over ``months`` periods.

    Delegates to :class:`~core.saas_simulator.SaaSSimulator`.

    Parameters
    ----------
    config : SaaSModelConfig
    months : int

    Returns
    -------
    pd.DataFrame
    """
    try:
        df = SaaSSimulator(config).run(months=months)
        logger.info("Simulation completed: %d months.", months)
        return df
    except Exception as exc:
        logger.error("Simulation failed: %s", exc)
        raise


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def fmt_currency(ax, axis: str = "y") -> None:
    formatter = mticker.FuncFormatter(lambda x, _: f"${x:,.0f}")
    if axis == "y":
        ax.yaxis.set_major_formatter(formatter)
    else:
        ax.xaxis.set_major_formatter(formatter)


# ─────────────────────────────────────────────────────────────────────────────
# VISUALISATION — kept identical to original for dashboard.py compatibility
# ─────────────────────────────────────────────────────────────────────────────

def visualize_results(df: pd.DataFrame, title_suffix: str = "") -> None:
    """Original 3-chart overview figure."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    ax = axes[0]
    ax.plot(df['Month'], df['Total_Customers'], marker='o', color='tab:blue', label='Total Customers')
    ax.bar(df['Month'], df['New_Customers'], color='tab:green', alpha=0.3, label='New Customers')
    ax.set_title('Customer Growth'); ax.set_xlabel('Month'); ax.set_ylabel('Customers')
    ax.legend(); ax.grid(True, linestyle='--', alpha=0.6)

    ax = axes[1]
    ax.plot(df['Month'], df['MRR'], marker='s', color='tab:orange')
    ax.set_title('MRR Growth'); ax.set_xlabel('Month'); ax.set_ylabel('MRR ($)')
    ax.grid(True, linestyle='--', alpha=0.6); fmt_currency(ax)

    ax = axes[2]
    ax.plot(df['Month'], df['Profit_Loss'], marker='x', color='tab:red', label='Monthly P&L')
    ax.plot(df['Month'], df['Cumulative_Cash'], marker='.', linewidth=2, color='tab:purple', label='Cumulative Cash')
    ax.axhline(0, color='black', linewidth=1)
    ax.set_title('Profit & Cash Flow'); ax.set_xlabel('Month'); ax.set_ylabel('Amount ($)')
    ax.legend(); ax.grid(True, linestyle='--', alpha=0.6)

    fig.suptitle(f'SaaS Financial Simulation Results {title_suffix}', fontsize=16)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    filename = f"saas_simulation_{title_suffix.replace(' ', '_').replace('(','').replace(')','').lower()}.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    logger.info("[CHART] Saved: %s", filename)
    plt.close()


def visualize_dashboard_1(df: pd.DataFrame, title_suffix: str = "") -> None:
    """Dashboard 1: Revenue & Cost Detail."""
    fig, axes = plt.subplots(2, 3, figsize=(22, 12))
    fig.suptitle(f'SaaS Dashboard 1 — Revenue & Cost Detail {title_suffix}', fontsize=15, fontweight='bold')
    months = df["Month"]

    ax = axes[0, 0]
    ax.bar(months, df["New_MRR"],       label="New MRR",        color="#2ecc71", alpha=0.85)
    ax.bar(months, df["Expansion_MRR"], label="Expansion MRR",  color="#a9dfbf", alpha=0.85, bottom=df["New_MRR"])
    ax.bar(months, df["Churn_MRR"],     label="Churn MRR",      color="#e74c3c", alpha=0.85)
    ax.plot(months, df["Net_New_MRR"],  label="Net New MRR",    color="#2980b9", linewidth=2, marker='o', markersize=4)
    ax.set_title("MRR Movements"); ax.set_xlabel("Month"); ax.set_ylabel("MRR ($)")
    ax.legend(fontsize=7); ax.grid(True, linestyle='--', alpha=0.5); fmt_currency(ax)

    ax = axes[0, 1]; ax2 = ax.twinx()
    ax.bar(months, df["Net_New_MRR"], label="Net New MRR", color="#27ae60", alpha=0.8)
    ax2.plot(months, df["MoM_Growth_%"], color="#2980b9", linewidth=2, marker='s', markersize=4, label="MoM growth %")
    ax.set_title("MRR Growth"); ax.set_xlabel("Month"); ax.set_ylabel("Net New MRR ($)"); ax2.set_ylabel("MoM Growth %")
    fmt_currency(ax); ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}%"))
    lines1, lab1 = ax.get_legend_handles_labels(); lines2, lab2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, lab1 + lab2, fontsize=7); ax.grid(True, linestyle='--', alpha=0.5)

    ax = axes[0, 2]
    ax.bar(months, df["New_Enterprise_Wins"],  label="New Enterprise", color="#2ecc71", alpha=0.85)
    ax.bar(months, df["Enterprise_Upgrades"],  label="Upgrades from Pro", color="#a9cce3", alpha=0.85, bottom=df["New_Enterprise_Wins"])
    ax.bar(months, -df["Lost_Enterprise"],     label="Lost",           color="#e74c3c", alpha=0.85)
    ax.axhline(0, color='black', linewidth=0.8)
    ax.set_title("Enterprise Customer Wins/Losses"); ax.set_xlabel("Month"); ax.set_ylabel("Customers")
    ax.legend(fontsize=7); ax.grid(True, linestyle='--', alpha=0.5)

    ax = axes[1, 0]
    ax.stackplot(months, df["COGS"], df["RD_Cost"], df["SM_Cost"], df["GA_Cost"], df["CS_Cost"],
                 labels=["CoGS", "R&D", "S&M", "G&A", "CS"],
                 colors=["#5dade2", "#a9cce3", "#f9e79f", "#f0b27a", "#d2b4de"], alpha=0.85)
    ax.set_title("Monthly Costs by P&L Category"); ax.set_xlabel("Month"); ax.set_ylabel("Cost ($)")
    ax.legend(fontsize=7, loc='upper left'); ax.grid(True, linestyle='--', alpha=0.5); fmt_currency(ax)

    ax = axes[1, 1]
    ax.stackplot(months, df["COGS"], df["RD_Cost"], df["SM_Cost"], df["GA_Cost"], df["CS_Cost"],
                 labels=["CoGS", "R&D", "Sales & Marketing", "G&A", "Customer Success"],
                 colors=["#117a65", "#1a5276", "#7d6608", "#784212", "#4a235a"], alpha=0.75)
    ax.set_title("Monthly Costs by Category"); ax.set_xlabel("Month"); ax.set_ylabel("Cost ($)")
    ax.legend(fontsize=7, loc='upper left'); ax.grid(True, linestyle='--', alpha=0.5); fmt_currency(ax)

    ax = axes[1, 2]
    ax.stackplot(months, df["Salary_GA"], df["Salary_Engineering"], df["Salary_Marketing"],
                 df["Salary_Sales"], df["Salary_CS"],
                 labels=["G&A", "Engineering", "Marketing", "Sales", "CS"],
                 colors=["#5dade2", "#f0b27a", "#a9dfbf", "#f9e79f", "#d2b4de"], alpha=0.85)
    ax.set_title("Monthly Salaries by Department"); ax.set_xlabel("Month"); ax.set_ylabel("Salary Cost ($)")
    ax.legend(fontsize=7, loc='upper left'); ax.grid(True, linestyle='--', alpha=0.5); fmt_currency(ax)

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    filename = f"saas_dashboard1_{title_suffix.replace(' ', '_').replace('(','').replace(')','').lower()}.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    logger.info("[CHART] Saved: %s", filename)
    plt.close()


def visualize_dashboard_2(df: pd.DataFrame, title_suffix: str = "") -> None:
    """Dashboard 2: Efficiency & Growth Metrics."""
    fig = plt.figure(figsize=(22, 12))
    fig.suptitle(f'SaaS Dashboard 2 — Efficiency & Growth Metrics {title_suffix}', fontsize=15, fontweight='bold')
    months = df["Month"]

    ax1 = fig.add_subplot(2, 3, 1)
    ax1.stackplot(months, df["COGS"], df["RD_Cost"], df["SM_Cost"], df["GA_Cost"], df["CS_Cost"],
                  labels=["CoGS", "R&D", "S&M", "G&A", "CS"],
                  colors=["#f0b27a", "#a9dfbf", "#aed6f1", "#d2b4de", "#f9e79f"], alpha=0.8)
    ax1.plot(months, df["Total_Revenue"], color="#27ae60", linewidth=2.5, label="Revenues")
    ax1.plot(months, df["EBIT"], color="#2980b9", linewidth=2, label="EBIT", linestyle='--')
    ax1.axhline(0, color='black', linewidth=0.8)
    ax1.set_title("Revenues, Costs & EBIT"); ax1.set_xlabel("Month"); ax1.set_ylabel("Amount ($)")
    ax1.legend(fontsize=7, loc='upper left'); ax1.grid(True, linestyle='--', alpha=0.5); fmt_currency(ax1)

    ax2 = fig.add_subplot(2, 3, 2)
    ax2.plot(months, df["Gross_Margin_%"], color="#2980b9", linewidth=2, marker='o', markersize=4)
    ax2.fill_between(months, df["Gross_Margin_%"], alpha=0.15, color="#2980b9")
    ax2.set_title("Gross Profit Margin"); ax2.set_xlabel("Month"); ax2.set_ylabel("Gross Margin %")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax2.set_ylim(0, 100); ax2.grid(True, linestyle='--', alpha=0.5)

    ax3 = fig.add_subplot(2, 3, 3)
    ax3.stackplot(months, df["HC_GA"], df["HC_Engineering"], df["HC_Marketing"],
                  df["HC_Sales"], df["HC_CS"],
                  labels=["G&A", "Engineering", "Marketing", "Sales", "CS"],
                  colors=["#5dade2", "#f0b27a", "#a9dfbf", "#f9e79f", "#d2b4de"], alpha=0.85)
    ax3.set_title("Headcount by Department"); ax3.set_xlabel("Month"); ax3.set_ylabel("Headcount")
    ax3.legend(fontsize=7, loc='upper left'); ax3.grid(True, linestyle='--', alpha=0.5)

    ax4 = fig.add_subplot(2, 3, 4)
    ax4.plot(months, df["SM_Efficiency"], color="#2980b9", linewidth=2.5, marker='o', markersize=4)
    ax4.fill_between(months, df["SM_Efficiency"], alpha=0.12, color="#2980b9")
    ax4.axhline(1.0, color='red', linestyle='--', linewidth=1, label="1.0x (break-even)")
    ax4.set_title("Sales & Marketing Efficiency"); ax4.set_xlabel("Month"); ax4.set_ylabel("Efficiency Ratio")
    ax4.legend(fontsize=7); ax4.grid(True, linestyle='--', alpha=0.5)

    ax5 = fig.add_subplot(2, 3, 5)
    ax5.plot(months, df["CAC_Payback_Basic"],      color="#8e44ad", linewidth=2, marker='o', markersize=4, label="Basic")
    ax5.plot(months, df["CAC_Payback_Pro"],        color="#2980b9", linewidth=2, marker='s', markersize=4, label="Pro")
    ax5.plot(months, df["CAC_Payback_Enterprise"], color="#27ae60", linewidth=2, marker='^', markersize=4, label="Enterprise")
    ax5.set_title("CAC Payback Time — by Pricing Plan"); ax5.set_xlabel("Month"); ax5.set_ylabel("Months to Payback")
    ax5.legend(fontsize=7); ax5.grid(True, linestyle='--', alpha=0.5)

    ax6 = fig.add_subplot(2, 3, 6)
    ax6.plot(months, df["LTV_CAC_Ratio"], color="#e67e22", linewidth=2.5, marker='D', markersize=4)
    ax6.axhline(3.0, color='green', linestyle='--', linewidth=1.2, label="3x (benchmark)")
    ax6.fill_between(months, df["LTV_CAC_Ratio"], 3.0,
                     where=(df["LTV_CAC_Ratio"] >= 3.0), alpha=0.15, color='green', label="Above 3x")
    ax6.fill_between(months, df["LTV_CAC_Ratio"], 3.0,
                     where=(df["LTV_CAC_Ratio"] < 3.0), alpha=0.15, color='red',   label="Below 3x")
    ax6.set_title("LTV / CAC Ratio"); ax6.set_xlabel("Month"); ax6.set_ylabel("LTV:CAC")
    ax6.legend(fontsize=7); ax6.grid(True, linestyle='--', alpha=0.5)

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    filename = f"saas_dashboard2_{title_suffix.replace(' ', '_').replace('(','').replace(')','').lower()}.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    logger.info("[CHART] Saved: %s", filename)
    plt.close()


def visualize_comparison(df_base: pd.DataFrame, df_churn: pd.DataFrame) -> None:
    """Scenario comparison: Base vs High Churn."""
    fig, axes = plt.subplots(2, 3, figsize=(22, 12))
    fig.suptitle("Scenario Comparison: Base Case vs High Churn", fontsize=15, fontweight='bold')
    months = df_base["Month"]
    comparisons = [
        (axes[0, 0], "MRR",             "MRR ($)",             "MRR Growth"),
        (axes[0, 1], "Total_Customers", "Customers",           "Total Customers"),
        (axes[0, 2], "Cumulative_Cash", "Cumulative Cash ($)", "Cumulative Cash"),
        (axes[1, 0], "Gross_Margin_%",  "Gross Margin %",      "Gross Margin"),
        (axes[1, 1], "SM_Efficiency",   "S&M Efficiency",      "S&M Efficiency"),
        (axes[1, 2], "EBIT",            "EBIT ($)",            "EBIT"),
    ]
    for ax, col, ylabel, title in comparisons:
        ax.plot(months, df_base[col],  linewidth=2, marker='o', markersize=3,
                color="#2980b9", label="Base Case (5% churn)")
        ax.plot(months, df_churn[col], linewidth=2, marker='s', markersize=3,
                color="#e74c3c", label="High Churn (10% churn)", linestyle='--')
        ax.set_title(title); ax.set_xlabel("Month"); ax.set_ylabel(ylabel)
        ax.legend(fontsize=8); ax.grid(True, linestyle='--', alpha=0.5)
        if "$" in ylabel:
            fmt_currency(ax)
        if "%" in ylabel:
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}%"))

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    filename = "saas_scenario_comparison.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    logger.info("[CHART] Saved: %s", filename)
    plt.close()


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY PRINT
# ─────────────────────────────────────────────────────────────────────────────

def log_summary(df: pd.DataFrame, config: SaaSModelConfig) -> None:
    """Log a concise financial summary via the logging module."""
    logger.info("=" * 50)
    logger.info("FINANCIAL SIMULATION SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Assumptions: Start={config.starting_customers}, "
                f"Growth={config.monthly_growth_rate * 100}%, "
                f"Churn={config.churn_rate * 100}%")
    logger.info(f"Price: ${config.price_per_customer:,.0f}, "
                f"Fixed Costs: ${config.fixed_costs:,}")
    logger.info("-" * 50)

    breakeven_month = df[df["Cumulative_Cash"] >= 0]["Month"].min()
    if pd.notna(breakeven_month):
        logger.info("[OK]    Break-even Month   : Month %d", int(breakeven_month))
    else:
        logger.info("[ERROR] Break-even         : Not reached within %d months", len(df))

    final = df.iloc[-1]
    logger.info("[MRR]   Final MRR          : $%s", f"{final['MRR']:,.0f}")
    logger.info("[ARR]   Final ARR          : $%s", f"{final['ARR']:,.0f}")
    logger.info("[USERS] Final Customers    : %d", int(final['Total_Customers']))
    logger.info("[CASH]  Final Cum. Cash    : $%s", f"{final['Cumulative_Cash']:,.0f}")
    logger.info("[MARGIN]Final Gross Margin : %.1f%%", final['Gross_Margin_%'])
    logger.info("[HC]    Final Headcount    : %d", int(final['Total_Headcount']))
    logger.info("[LTV]   LTV/CAC Ratio      : %.2fx", final['LTV_CAC_Ratio'])

    total_lost   = df["Churned_Customers"].sum()
    total_gained = df["New_Customers"].sum()
    logger.info("[WARN]  Total Churned      : %d (%.1f%% of gains)",
                int(total_lost), (total_lost / total_gained) * 100)
    logger.info("=" * 50)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """CLI entry point for the SaaS simulation."""
    logger.info("Running Scenario A: Base Case…")
    config_base = SaaSModelConfig(
        starting_customers=50,
        monthly_growth_rate=0.20,
        churn_rate=0.05,
        price_per_customer=100,
        fixed_costs=5000,
        variable_cost_per_customer=10,
        cac_simplified=150,
        initial_eng=5, initial_sales=3, initial_marketing=2, initial_cs=2, initial_ga=2,
    )
    df_base = run_simulation(config_base, months=24)
    log_summary(df_base, config_base)
    visualize_results(df_base,     title_suffix="(Base Case)")
    visualize_dashboard_1(df_base, title_suffix="(Base Case)")
    visualize_dashboard_2(df_base, title_suffix="(Base Case)")
    df_base.to_csv("simulation_results_base.csv", index=False)
    logger.info("[CSV] Saved: simulation_results_base.csv")

    logger.info("Running Scenario B: High Churn Analysis…")
    config_high_churn = SaaSModelConfig(
        starting_customers=50,
        monthly_growth_rate=0.20,
        churn_rate=0.10,
        price_per_customer=100,
        fixed_costs=5000,
        variable_cost_per_customer=10,
        cac_simplified=150,
        initial_eng=5, initial_sales=3, initial_marketing=2, initial_cs=2, initial_ga=2,
    )
    df_churn = run_simulation(config_high_churn, months=24)
    log_summary(df_churn, config_high_churn)
    visualize_results(df_churn,     title_suffix="(High Churn Scenario)")
    visualize_dashboard_1(df_churn, title_suffix="(High Churn Scenario)")
    visualize_dashboard_2(df_churn, title_suffix="(High Churn Scenario)")
    df_churn.to_csv("simulation_results_high_churn.csv", index=False)
    logger.info("[CSV] Saved: simulation_results_high_churn.csv")

    logger.info("Generating scenario comparison chart…")
    visualize_comparison(df_base, df_churn)
    logger.info("[DONE] All files generated successfully.")


if __name__ == "__main__":
    main()