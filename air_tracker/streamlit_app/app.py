import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# ---------------- DB CONNECTION ----------------
def get_connection():
    return sqlite3.connect(
        "air_tracker/streamlit_app/database/air_tracker.db",
        check_same_thread=False
    )

conn = get_connection()

st.set_page_config(page_title="Dashboard Overview", layout="wide")
st.title("✈️ Flight Analytics – Overview")

# ================= KPIs (GLOBAL ONLY) =================
col1, col2, col3, col4, col5 = st.columns(5)

total_airports = pd.read_sql(
    "SELECT COUNT(*) cnt FROM airport", conn
)["cnt"][0]

total_flights = pd.read_sql(
    "SELECT COUNT(*) cnt FROM flights", conn
)["cnt"][0]

active_airlines = pd.read_sql(
    "SELECT COUNT(DISTINCT airline_name) cnt FROM flights", conn
)["cnt"][0]

avg_delay = pd.read_sql(
    "SELECT ROUND(AVG(avg_delay_min),2) avg_delay FROM airport_delays",
    conn
)["avg_delay"][0]

delayed_pct = pd.read_sql(
    """
    SELECT ROUND(
        100.0 * SUM(CASE WHEN status='Delayed' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS delay_pct
    FROM flights
    """,
    conn
)["delay_pct"][0]

col1.metric("Total Airports", total_airports)
col2.metric("Total Flights", total_flights)
col3.metric("Active Airlines", active_airlines)
col4.metric("Avg Delay (min)", avg_delay)
col5.metric("Delayed Flights (%)", delayed_pct)

# ================= CHARTS =================
tab1, tab2 = st.tabs(["📊 Overview Charts", "📋 Summary Tables"])

with tab1:
    colA, colB = st.columns(2)

    # 1. Flight Status Distribution (ONLY HERE)
    status_df = pd.read_sql(
        "SELECT status, COUNT(*) flights FROM flights GROUP BY status",
        conn
    )

    with colA:
        fig = px.pie(
            status_df,
            names="status",
            values="flights",
            title="Flight Status Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

    # 2. Arrival vs Departure Share
    movement_df = pd.read_sql(
        "SELECT flight_type, COUNT(*) flights FROM flights GROUP BY flight_type",
        conn
    )

    with colB:
        fig = px.pie(
            movement_df,
            names="flight_type",
            values="flights",
            hole=0.45,
            title="Arrival vs Departure Share"
        )
        st.plotly_chart(fig, use_container_width=True)

    # 3. Top 5 Airlines (EXECUTIVE VIEW)
    airline_df = pd.read_sql(
        """
        SELECT airline_name, COUNT(*) flights
        FROM flights
        GROUP BY airline_name
        ORDER BY flights DESC
        LIMIT 5
        """,
        conn
    )

    fig = px.bar(
        airline_df,
        x="airline_name",
        y="flights",
        title="Top 5 Airlines by Flights",
        text_auto=True
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Top Airlines Summary")
    st.dataframe(airline_df, use_container_width=True)
