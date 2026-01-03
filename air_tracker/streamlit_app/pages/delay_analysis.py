import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

def get_connection():
    return sqlite3.connect(
        "air_tracker/streamlit_app/database/air_tracker.db",
        check_same_thread=False
    )

conn = get_connection()
st.title("⏱️ Delay Analysis")

# ---------------- KPIs ----------------
kpi_df = pd.read_sql(
    """
    SELECT
        ROUND(AVG(avg_delay_min),2) AS avg_delay,
        ROUND(100.0 * SUM(delayed_flights) / SUM(total_flights),2) AS delay_pct
    FROM airport_delays
    """,
    conn
)

col1, col2 = st.columns(2)
col1.metric("Avg Delay (min)", kpi_df["avg_delay"][0])
col2.metric("Delayed Flights (%)", kpi_df["delay_pct"][0])

# ---------------- Delay Charts ----------------
delay_df = pd.read_sql(
    """
    SELECT airport_iata, avg_delay_min,
           ROUND(100.0 * delayed_flights / total_flights,2) AS delay_pct
    FROM airport_delays
    WHERE total_flights > 0
    """,
    conn
)

colA, colB = st.columns(2)

with colA:
    fig = px.bar(
        delay_df,
        x="airport_iata",
        y="avg_delay_min",
        title="Average Delay by Airport",
        text_auto=True
    )
    st.plotly_chart(fig, use_container_width=True)

with colB:
    fig = px.bar(
        delay_df,
        x="airport_iata",
        y="delay_pct",
        title="Delay Percentage by Airport",
        text_auto=True
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Most Delayed Airports ----------------
st.subheader("🚨 Most Delayed Airports")

st.dataframe(
    delay_df.sort_values("delay_pct", ascending=False),
    use_container_width=True
)
