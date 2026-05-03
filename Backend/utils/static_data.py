"""
utils/static_data.py  — FIXED
================================
get_leadership_data()  — each dict must have keys:
    name, role, img, desc
    (streamlit_app.py lines 5554-5565 access member['img'] and member['desc'])

get_tech_stack()  — must return a LIST of dicts, each with keys:
    layer, tech, detail
    (streamlit_app.py lines 5574-5581 iterate and access item['layer'],
     item['tech'], item['detail'])
"""

from __future__ import annotations


def get_leadership_data() -> list[dict]:
    """
    Return leadership team.  Every dict MUST contain:
        name (str), role (str), img (str URL), desc (str)
    """
    placeholder = "https://ui-avatars.com/api/?background=1e3a5f&color=fff&size=100&bold=true&name="

    return [
        {
            "name": "Dr. Anika Müller",
            "role": "Chief Executive Officer",
            "img":  placeholder + "AM",
            "desc": "20 years in rail infrastructure. Former VP at Siemens Mobility. "
                    "Passionate about merging safety engineering with data-driven operations.",
        },
        {
            "name": "Tobias Schreiber",
            "role": "Chief Technology Officer",
            "img":  placeholder + "TS",
            "desc": "Full-stack systems architect with deep expertise in IoT sensor networks "
                    "and real-time data pipelines for safety-critical environments.",
        },
        {
            "name": "Priya Venkataraman",
            "role": "Chief Operating Officer",
            "img":  placeholder + "PV",
            "desc": "Operations leader bridging Indian and European rail markets. "
                    "Specialist in large-scale infrastructure rollouts across 15+ cities.",
        },
        {
            "name": "Marcus Bauer",
            "role": "VP Product",
            "img":  placeholder + "MB",
            "desc": "Product strategist focused on human-centred design for industrial dashboards. "
                    "Translates complex telemetry data into actionable operator insights.",
        },
        {
            "name": "Sarah Fischer",
            "role": "Head of Data Science",
            "img":  placeholder + "SF",
            "desc": "ML researcher specialising in predictive maintenance models for "
                    "mechanical systems. PhD in Applied Statistics from TU Munich.",
        },
        {
            "name": "Arjun Nair",
            "role": "Head of Business Development",
            "img":  placeholder + "AN",
            "desc": "Leads partnerships with Deutsche Bahn, MVG, and Indian metro operators. "
                    "Expert in B2G contracts and public-sector procurement across DACH + South Asia.",
        },
    ]


def get_tech_stack() -> list[dict]:
    """
    Return technology stack.  Every dict MUST contain:
        layer (str), tech (str), detail (str)
    """
    return [
        {
            "layer":  "Frontend",
            "tech":   "Streamlit 1.35",
            "detail": "Interactive web dashboard with real-time Plotly charts and custom HTML/JS animations.",
        },
        {
            "layer":  "Visualisation",
            "tech":   "Plotly 5.x",
            "detail": "Interactive charts — bar, scatter, gauge, heatmap, pie, and waterfall plots.",
        },
        {
            "layer":  "Data Engine",
            "tech":   "Pandas 2.x + NumPy",
            "detail": "In-memory tabular data manipulation, aggregations, and synthetic telemetry generation.",
        },
        {
            "layer":  "Simulation",
            "tech":   "core.saas_simulator",
            "detail": "Custom SaaS financial model: 24-month P&L, headcount, LTV/CAC, and cohort churn.",
        },
        {
            "layer":  "Analytics",
            "tech":   "core.station_analytics",
            "detail": "Station-level KPIs, PSD door-cycle analytics, risk forecasting, and heatmaps.",
        },
        {
            "layer":  "Data Source",
            "tech":   "stations.csv",
            "detail": "Live gate telemetry: sensor temp, vibration, door state, passenger count per gate.",
        },
        {
            "layer":  "Infrastructure",
            "tech":   "Docker + GitHub Actions",
            "detail": "Containerised deployment with CI/CD pipeline; supports AWS ECS and Azure ACI.",
        },
        {
            "layer":  "Caching",
            "tech":   "@st.cache_data",
            "detail": "60 s TTL on live metrics; 3600 s TTL on forecast and heatmap computations.",
        },
        {
            "layer":  "Language",
            "tech":   "Python 3.11",
            "detail": "Type-annotated codebase with modular package structure (core/, data/, utils/).",
        },
    ]
