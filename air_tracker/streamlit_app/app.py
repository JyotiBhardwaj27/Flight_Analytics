import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

def get_connection():
    return sqlite3.connect("air_tracker/streamlit_app/database/air_tracker.db", check_same_thread=False)

st.set_page_config(page_title="Air Tracker", layout="wide")
st.title("✈️ Air Tracker – Overview")

conn = get_connection()

col1, col2, col3 = st.columns(3)

total_airports = pd.read_sql(
    "SELECT COUNT(*) AS cnt FROM airport", conn
)["cnt"][0]

total_flights = pd.read_sql(
    "SELECT COUNT(*) AS cnt FROM flights", conn
)["cnt"][0]

avg_delay = pd.read_sql(
    "SELECT ROUND(AVG(avg_delay_min),2) AS avg_delay FROM airport_delays",
    conn
)["avg_delay"][0]

col1.metric("Total Airports", total_airports)
col2.metric("Total Flights", total_flights)
col3.metric("Avg Delay (min)", avg_delay)

status_df = pd.read_sql(
    "SELECT status, COUNT(*) AS flight_count FROM flights GROUP BY status",
    conn
)


tab1, tab2 = st.tabs(["📊 Overview Charts", "📋 Key Tables"])
with tab1:
    # Flight Status Pie Chart
    fig = px.pie(
        status_df,
        names="status",
        values="flight_count",
        title="Flight Status Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)
    airline_df = pd.read_sql(
    """
    SELECT airline_name, COUNT(*) AS flights
    FROM flights
    GROUP BY airline_name
    ORDER BY flights DESC
    LIMIT 10
    """,
    conn
    )

    # Top Airlines Donut Chart
    fig = px.pie(
        airline_df.head(5),
        names="airline_name",
        values="flights",
        hole=0.4,
        title="Top Airlines Market Share"
    )
    st.plotly_chart(fig, use_container_width=True)


with tab2:
    st.subheader("Flights by Status")
    st.dataframe(status_df)

    st.subheader("Top Airlines")
    st.dataframe(airline_df)

