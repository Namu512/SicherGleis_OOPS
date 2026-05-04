import sys
from pathlib import Path
import pandas as pd
import pytest

# Add Backend/ to sys.path so core/, data/, utils/ are importable
_backend_dir = str(Path(__file__).resolve().parent.parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

# Also add project root for data_source.py imports
_project_root = str(Path(__file__).resolve().parent.parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import os
os.chdir(_backend_dir)  # Ensure cwd is Backend/ for relative imports

from core.saas_simulator import SaaSModelConfig, SaaSSimulator
from core.station_analytics import StationAnalytics, NetworkAnalytics


@pytest.fixture
def saas_config():
    return SaaSModelConfig(
        starting_customers=100,
        monthly_growth_rate=0.15,
        churn_rate=0.05,
        price_per_customer=50,
        fixed_costs=10000,
        variable_cost_per_customer=10,
        cac_simplified=150,
        seed=42,
    )


@pytest.fixture
def saas_simulator(saas_config):
    return SaaSSimulator(saas_config)


@pytest.fixture
def sample_station_df():
    return pd.DataFrame({
        "station": ["München Hbf", "München Hbf", "Marienplatz", "Sendlinger Tor", "Marienplatz"],
        "gate_id": ["MU-H-G01", "MU-H-G02", "MA-R-G01", "SE-L-G01", "MA-R-G02"],
        "sync_score": [95.0, 88.0, 76.0, 45.0, 92.0],
        "risk_score": [10.0, 25.0, 40.0, 70.0, 15.0],
        "people": [500, 300, 250, 80, 400],
        "maintenance_status": ["OPTIMAL", "OPTIMAL", "WARNING", "CRITICAL", "OPTIMAL"],
        "door_state": ["open", "closed", "open", "jammed", "open"],
        "train_type": ["S-Bahn", "U-Bahn", "S-Bahn", "Tram", "U-Bahn"],
        "operator": ["DB", "DB", "MVG", "MVG", "MVG"],
        "platform": [1, 1, 2, 3, 2],
        "power_consumption": [15.0, 14.5, 13.0, 18.0, 12.0],
        "energy_rating": ["A+", "A", "B", "C", "A"],
        "delay": [0, 2, -1, 5, 0],
        "connection_line": ["S1", "S1", "U3", "U6", "U3"],
        "occupancy_rate": [0.625, 0.375, 0.3125, 0.1, 0.5],
        "last_maintenance": ["2024-01-15", "2024-02-10", "2024-03-01", "2023-12-20", "2024-01-28"],
        "signal_status": ["OK", "OK", "OK", "FAULT", "OK"],
        "sensor_temp": [25.0, 26.0, 24.5, 28.0, 25.5],
        "sensor_vib": [0.3, 0.25, 0.2, 0.6, 0.15],
    })


@pytest.fixture
def empty_df():
    return pd.DataFrame()


@pytest.fixture
def network_df(sample_station_df):
    df = sample_station_df.copy()
    # Add a few more rows for different stations
    extra = pd.DataFrame({
        "station": ["Karlsplatz", "Isartor", "München Hbf"],
        "gate_id": ["KA-G01", "IS-G01", "MU-H-G03"],
        "sync_score": [82.0, 91.0, 78.0],
        "risk_score": [30.0, 18.0, 35.0],
        "people": [200, 350, 600],
        "maintenance_status": ["OPTIMAL", "OPTIMAL", "WARNING"],
        "door_state": ["open", "open", "closed"],
        "train_type": ["U-Bahn", "S-Bahn", "ICE"],
        "operator": ["MVG", "DB", "DB"],
        "platform": [4, 5, 1],
        "power_consumption": [13.0, 14.0, 16.0],
        "energy_rating": ["A", "A+", "B"],
        "delay": [1, 0, 3],
        "connection_line": ["U2", "S4", "ICE"],
        "occupancy_rate": [0.25, 0.4375, 0.75],
        "last_maintenance": ["2024-02-15", "2024-03-10", "2024-01-05"],
        "signal_status": ["OK", "OK", "OK"],
        "sensor_temp": [24.0, 25.5, 27.0],
        "sensor_vib": [0.2, 0.18, 0.35],
    })
    return pd.concat([df, extra], ignore_index=True)
