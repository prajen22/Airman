"""
dash.py

AIRMAN – Level 2 AHRS Ground Control Station
-------------------------------------------

This Streamlit application acts as a lightweight Ground Control Station (GCS)
for the Level-2 AHRS telemetry system.

Core Responsibilities:
- Read validated telemetry data from a CSV flight log
- Display real-time attitude and environmental metrics
- Visualize roll, pitch, and heading trends over time

Optional Bonus Feature:
- 3D attitude cube visualization that rotates with roll, pitch, and heading

Design Philosophy:
- Clear separation of concerns (logging vs visualization)
- File-based telemetry source to mimic real flight logs
- UI inspired by aerospace / robotics ground stations
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from pathlib import Path
import time

# ============================================================
# Page configuration
# ============================================================

st.set_page_config(
    page_title="AHRS Ground Control Station",
    layout="wide"
)

# ============================================================
# Global configuration
# ============================================================

CSV_PATH = Path("level2_telemetry.csv")
REFRESH_SEC = 1.0   # UI refresh rate (not telemetry rate)

# ============================================================
# Custom CSS – Professional GCS Styling
# ============================================================

st.markdown("""
<style>
body {
    background-color: #0b0f19;
}
.section-title {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 8px;
}
.metric-card {
    background-color: #111827;
    padding: 18px;
    border-radius: 14px;
    text-align: center;
    box-shadow: 0 6px 16px rgba(0,0,0,0.45);
}
.metric-label {
    font-size: 13px;
    color: #9ca3af;
}
.metric-value {
    font-size: 30px;
    font-weight: 700;
    color: #22d3ee;
}
.subtle {
    color: #9ca3af;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# Helper UI components
# ============================================================

def metric_card(label, value, unit=""):
    """Render a single metric card (cockpit-style)."""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}{unit}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def make_plot(df, y_col, title, y_label):
    """Generate a Plotly time-series plot."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["timestamp_ms"],
            y=df[y_col],
            mode="lines",
            line=dict(width=2)
        )
    )
    fig.update_layout(
        title=title,
        height=300,
        margin=dict(l=30, r=30, t=45, b=30),
        xaxis_title="Time (ms)",
        yaxis_title=y_label,
        template="plotly_dark"
    )
    return fig

# ============================================================
# 3D Attitude Cube Helpers (Bonus Feature)
# ============================================================

def rotation_matrix(roll, pitch, yaw):
    """Create rotation matrix from roll, pitch, yaw (degrees)."""
    r, p, y = np.deg2rad([roll, pitch, yaw])

    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(r), -np.sin(r)],
        [0, np.sin(r),  np.cos(r)]
    ])
    Ry = np.array([
        [ np.cos(p), 0, np.sin(p)],
        [0, 1, 0],
        [-np.sin(p), 0, np.cos(p)]
    ])
    Rz = np.array([
        [np.cos(y), -np.sin(y), 0],
        [np.sin(y),  np.cos(y), 0],
        [0, 0, 1]
    ])

    return Rz @ Ry @ Rx

def make_attitude_cube(roll, pitch, yaw):
    """Create a 3D rotating cube representing attitude."""
    vertices = np.array([
        [-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],
        [-1,-1, 1],[1,-1, 1],[1,1, 1],[-1,1, 1]
    ])
    edges = [
        (0,1),(1,2),(2,3),(3,0),
        (4,5),(5,6),(6,7),(7,4),
        (0,4),(1,5),(2,6),(3,7)
    ]

    R = rotation_matrix(roll, pitch, yaw)
    rotated = vertices @ R.T

    fig = go.Figure()
    for e in edges:
        fig.add_trace(go.Scatter3d(
            x=[rotated[e[0],0], rotated[e[1],0]],
            y=[rotated[e[0],1], rotated[e[1],1]],
            z=[rotated[e[0],2], rotated[e[1],2]],
            mode="lines",
            line=dict(color="cyan", width=6)
        ))

    fig.update_layout(
        title="3D Attitude Visualization (Bonus)",
        height=420,
        scene=dict(
            xaxis=dict(range=[-2,2], visible=False),
            yaxis=dict(range=[-2,2], visible=False),
            zaxis=dict(range=[-2,2], visible=False),
            aspectmode="cube"
        ),
        template="plotly_dark"
    )
    return fig

# ============================================================
# Dashboard Header
# ============================================================

st.title("🛩️ AHRS Ground Control Station")
st.caption("Level-2 Telemetry • Attitude Estimation • Flight-Style Monitoring")
st.markdown("---")

# ============================================================
# Main Dashboard Loop
# ============================================================

while True:

    if not CSV_PATH.exists():
        st.warning("⏳ Waiting for telemetry logger to create CSV file...")
        time.sleep(REFRESH_SEC)
        st.rerun()

    df = pd.read_csv(CSV_PATH)
    if df.empty:
        st.info("📡 Telemetry stream detected, waiting for data...")
        time.sleep(REFRESH_SEC)
        st.rerun()

    latest = df.iloc[-1]

    # ========================================================
    # Status Section
    # ========================================================

    s1, s2 = st.columns([2, 3])
    with s1:
        st.markdown("### 🟢 System Status")
        st.markdown("**Telemetry:** Active")
        st.markdown("**Checksum:** CRC16-CCITT")
        st.markdown("**Update Rate:** 20 Hz")

    with s2:
        st.markdown("### 📋 Frame Info")
        st.markdown(f"**Last Timestamp:** `{int(latest['timestamp_ms'])} ms`")
        st.markdown(f"**Samples Logged:** `{len(df)}`")
        st.markdown("**Mode:** Level-2 AHRS")

    st.markdown("---")

    # ========================================================
    # Metric Cards
    # ========================================================

    st.markdown('<div class="section-title">Attitude & Environment</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1: metric_card("Roll", f"{latest['roll']:.2f}", "°")
    with c2: metric_card("Pitch", f"{latest['pitch']:.2f}", "°")
    with c3: metric_card("Heading", f"{latest['heading']:.2f}", "°")
    with c4: metric_card("Altitude", f"{latest['altitude']:.2f}", " m")
    with c5: metric_card("Temperature", f"{latest['temperature']:.2f}", " °C")

    st.markdown("---")

    # ========================================================
    # Charts + 3D Cube
    # ========================================================

    left, right = st.columns([2, 1])

    with left:
        st.plotly_chart(make_plot(df, "roll", "Roll vs Time", "Degrees"), width="stretch")
        st.plotly_chart(make_plot(df, "pitch", "Pitch vs Time", "Degrees"), width="stretch")
        st.plotly_chart(make_plot(df, "heading", "Heading vs Time", "Degrees"), width="stretch")

    with right:
        st.plotly_chart(
            make_attitude_cube(
                latest["roll"],
                latest["pitch"],
                latest["heading"]
            ),
            width="stretch"
        )

    st.markdown(
        '<div class="subtle">'
        'Dashboard refreshes automatically. '
        'Data source: CSV flight log.'
        '</div>',
        unsafe_allow_html=True
    )

    time.sleep(REFRESH_SEC)
    st.rerun()

