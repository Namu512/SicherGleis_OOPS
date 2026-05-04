# SicherGleis Pro

A dual-purpose analytics platform combining **railway station gate monitoring** with a **SaaS financial simulation engine**, built with Python, Streamlit, and Plotly.

---

## Overview

### SicherGleis Pro — Railway Infrastructure Analytics
A real-time monitoring and analytics dashboard for railway station gates and platforms. Tracks gate sync scores, risk levels, passenger flow, maintenance status, and network health across multiple stations.

Key capabilities:
- Station-level and network-wide analytics
- PSD (Platform Screen Door) cycle analytics & temperature monitoring
- Maintenance forecasting with risk prediction
- Passenger heatmaps by hour and station
- Incident logging with severity filtering
- Gate performance history (30-day rolling KPIs)
- Energy consumption and rating tracking
- PDF report generation

### SaaS Financial Simulator
A month-by-month SaaS financial model that simulates MRR, churn, headcount scaling, unit economics (LTV/CAC), and cash flow. Supports scenario comparison and exports results to CSV and PNG charts.

Key metrics:
- MRR / ARR growth with tier-based pricing (Basic, Pro, Enterprise)
- Customer acquisition and churn dynamics
- Gross margin, EBIT, and cumulative cash
- CAC payback period and LTV/CAC ratios
- Sales & Marketing efficiency tracking
- Headcount scaling across departments (Engineering, Sales, Marketing, CS, G&A)
- Scenario comparison (e.g., Base Case vs. High Churn)

---

## Project Structure

```
SicherGleis_OOPS/
├── streamlit_app.py              # Main entry point — SicherGleis Pro dashboard
├── data_source.py                # Re-exports all data modules for the Streamlit app
├── requirements.txt              # Python dependencies
├── pytest.ini                    # Pytest configuration
│
├── Backend/
│   ├── app.py                   # CLI entry point + matplotlib visualisation
│   ├── dashboard.py             # SaaS simulator Streamlit dashboard + PDF reports
│   ├── core/
│   │   ├── saas_simulator.py    # SaaS simulation engine (config + simulator)
│   │   └── station_analytics.py # Station & network analytics engine
│   ├── data/
│   │   ├── loader.py           # Data loading (CSV or synthetic generation)
│   │   └── financial.py        # Financial model data bridge for Streamlit
│   ├── utils/
│   │   ├── gate_history.py     # 30-day gate performance history
│   │   └── static_data.py     # Leadership team & tech stack data
│   └── tests/
│       ├── conftest.py          # Shared test fixtures
│       ├── test_saas_simulator.py
│       ├── test_station_analytics.py
│       └── test_data_loader.py
│
└── report.md                    # Project report
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd SicherGleis_OOPS

# Create and activate a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Running the Apps

**SicherGleis Pro — Station Monitoring Dashboard:**
```bash
streamlit run streamlit_app.py
```

**SaaS Financial Simulator — Backend CLI:**
```bash
cd Backend
python app.py
```

**SaaS Financial Simulator — Streamlit Dashboard:**
```bash
cd Backend
streamlit run dashboard.py
```

---

## Dependencies

| Package       | Version   | Purpose                                 |
|---------------|-----------|-----------------------------------------|
| `streamlit`   | >= 1.57   | Interactive web dashboards               |
| `pandas`      | >= 3.0    | Data manipulation and analysis           |
| `numpy`       | >= 2.4    | Numerical computations                   |
| `plotly`      | >= 6.7    | Interactive charts and visualizations    |
| `matplotlib`  | >= 3.10   | Static plotting and chart generation     |
| `reportlab`   | >= 4.5    | PDF report generation                   |
| `openpyxl`   | >= 3.1    | Excel file support                      |
| `pytest`      | >= 9.0    | Testing framework                       |
| `pytest-cov`  | >= 7.1    | Test coverage reporting                  |
| `pytest-asyncio` | >= 1.3 | Async test support                      |

---

## Configuration

### SaaS Simulator Parameters

The simulator accepts a `SaaSModelConfig` with these key parameters:

| Parameter               | Default | Description                          |
|-------------------------|---------|--------------------------------------|
| `starting_customers`    | 50      | Initial customer count                 |
| `monthly_growth_rate`   | 0.20    | Monthly growth rate (20%)              |
| `churn_rate`            | 0.05    | Monthly churn rate (5%)               |
| `price_basic`           | $49     | Basic tier monthly price               |
| `price_pro`             | $149    | Pro tier monthly price                 |
| `price_enterprise`      | $499    | Enterprise tier monthly price          |
| `fixed_costs`           | $5,000  | Monthly fixed costs                    |
| `cac_simplified`        | $150    | Blended Customer Acquisition Cost      |

### Station Data

The app loads station data from `stations.csv`. If the file is not found, realistic synthetic data is auto-generated for these Munich stations:

München Hbf, München Ost, Marienplatz, Sendlinger Tor, Hauptbahnhof, Karlsplatz, Isartor, Rosenheimer Platz, Max-Weber-Platz, Münchner Freiheit

---

## Testing

```bash
pytest
```

With coverage:
```bash
pytest --cov=Backend
```

---

## Key Features

### Railway Analytics
- **Network Overview** — aggregate health score, sync/risk distribution, train type analysis
- **Station Detail** — per-station gate status, door cycles, temperature trends
- **Maintenance Forecasting** — predictive risk scoring for proactive maintenance
- **Passenger Analytics** — hourly heatmaps, occupancy rates, platform congestion
- **Incident Management** — severity-filtered log with temperature and vibration data
- **PDF Export** — one-click professional PDF reports

### Financial Simulation
- **Multi-scenario Simulation** — compare base case vs. high churn scenarios
- **12 Dashboard Charts** — MRR movements, growth %, headcount, EBIT, margins, LTV/CAC
- **CSV Export** — monthly breakdown exported for further analysis
- **PNG Chart Export** — publication-ready chart images
- **Unit Economics Tracking** — CAC payback period by tier, S&M efficiency

---

## Tech Stack

- **Language:** Python 3.11+
- **Frontend:** Streamlit (web dashboard), Plotly (interactive charts), Matplotlib (static charts)
- **Data:** Pandas, NumPy
- **Reporting:** ReportLab (PDF)
- **Testing:** pytest, pytest-cov
- **Architecture:** Modular — simulation engine, data loader, analytics, and UI layers are cleanly separated

---

## License

MIT License
