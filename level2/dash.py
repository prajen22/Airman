import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
# Global constants
# ============================================================

CSV_PATH = Path("level2_telemetry.csv")
REFRESH_SEC = 1.0   # dashboard refresh rate

# ============================================================
# Custom CSS – Professional GCS Style
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
# Helper UI functions
# ============================================================

def metric_card(label, value, unit=""):
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
# Header
# ============================================================

st.title("🛩️ AHRS Ground Control Station")
st.caption("Level-2 Telemetry • Attitude Estimation • Flight-Style Monitoring")

st.markdown("---")

# ============================================================
# Main dashboard loop
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
    # Top status bar
    # ========================================================

    status_col, info_col = st.columns([2, 3])

    with status_col:
        st.markdown("### 🟢 System Status")
        st.markdown("**Telemetry:** Active")
        st.markdown("**Checksum:** CRC16-CCITT")
        st.markdown("**Update Rate:** 20 Hz")

    with info_col:
        st.markdown("### 📋 Frame Info")
        st.markdown(f"**Last Timestamp:** `{int(latest['timestamp_ms'])} ms`")
        st.markdown(f"**Samples Logged:** `{len(df)}`")
        st.markdown("**Mode:** Level-2 AHRS")

    st.markdown("---")

    # ========================================================
    # Metric cards (Attitude + Environment)
    # ========================================================

    st.markdown('<div class="section-title">Attitude & Environment</div>', unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        metric_card("Roll", f"{latest['roll']:.2f}", "°")
    with c2:
        metric_card("Pitch", f"{latest['pitch']:.2f}", "°")
    with c3:
        metric_card("Heading", f"{latest['heading']:.2f}", "°")
    with c4:
        metric_card("Altitude", f"{latest['altitude']:.2f}", " m")
    with c5:
        metric_card("Temperature", f"{latest['temperature']:.2f}", " °C")

    st.markdown("---")

    # ========================================================
    # Charts section (clean grid)
    # ========================================================

    st.markdown('<div class="section-title">Attitude Time Series</div>', unsafe_allow_html=True)

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.plotly_chart(
            make_plot(df, "roll", "Roll vs Time", "Degrees"),
            width="stretch"
        )
        st.plotly_chart(
            make_plot(df, "pitch", "Pitch vs Time", "Degrees"),
            width="stretch"
        )

    with chart_col2:
        st.plotly_chart(
            make_plot(df, "heading", "Heading vs Time", "Degrees"),
            width="stretch"
        )

    st.markdown(
        '<div class="subtle">Dashboard refreshes automatically. Data source: CSV flight log.</div>',
        unsafe_allow_html=True
    )

    time.sleep(REFRESH_SEC)
    st.rerun()
