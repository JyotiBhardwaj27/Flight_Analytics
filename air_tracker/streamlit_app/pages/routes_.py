import sqlite3

def get_connection():
    return sqlite3.connect("air_tracker/streamlit_app/database/air_tracker.db", check_same_thread=False)

import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📍 Route Leaderboards")

conn = get_connection()
tab1, tab2 = st.tabs(["📋 Route Tables", "📊 Route Charts"])

routes_df = pd.read_sql(
    """
    SELECT origin_iata, destination_iata, COUNT(*) AS flights
    FROM flights
    GROUP BY origin_iata, destination_iata
    ORDER BY flights DESC
    LIMIT 10
    """,
    conn
)




delayed_df = pd.read_sql(
    """
    SELECT airport_iata, avg_delay_min
    FROM airport_delays
    ORDER BY avg_delay_min DESC
    LIMIT 10
    """,
    conn
)
with tab1:
    st.subheader("Busiest Routes")
    st.dataframe(routes_df)
    st.subheader("Most Delayed Airports")
    st.dataframe(delayed_df)



heat_df = pd.read_sql(
    """
    SELECT
        origin_iata,
        destination_iata,
        COUNT(*) AS flights
    FROM flights
    GROUP BY origin_iata, destination_iata
    """,
    conn
)

with tab2:
    fig = px.density_heatmap(
        heat_df,
        x="origin_iata",
        y="destination_iata",
        z="flights",
        title="Route Traffic Heatmap"
    )
    st.plotly_chart(fig, use_container_width=True)

