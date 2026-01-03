
import streamlit as st
import pandas as pd
import plotly.express as px

import sqlite3

def get_connection():
    return sqlite3.connect("../database/air_tracker.db", check_same_thread=False)

st.title("⏱ Delay Analysis")

conn = get_connection()
tab1, tab2 = st.tabs(["📋 Delay Metrics", "📊 Delay Insights"])

delay_df = pd.read_sql(
    """
    SELECT
        airport_iata,
        avg_delay_min,
        median_delay_min,
        ROUND(
            CAST(delayed_flights AS REAL) / total_flights * 100, 2
        ) AS delay_percentage
    FROM airport_delays
    """,
    conn
)
with tab1:
    st.dataframe(delay_df)

with tab2:
    fig = px.bar(
        delay_df,
        x="airport_iata",
        y=["avg_delay_min", "median_delay_min"],
        barmode="group",
        title="Average vs Median Delay"
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = px.histogram(
        delay_df,
        x="avg_delay_min",
        title="Delay Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)
    fig = px.bar(
        delay_df,
        x="airport_iata",
        y="avg_delay_min",
        title="Average Delay by Airport (minutes)"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Delay Percentage
    fig = px.bar(
        delay_df,
        x="airport_iata",
        y="delay_percentage",
        title="Delay Percentage by Airport"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Cancelled Flights
    cancel_df = pd.read_sql(
        "SELECT airport_iata, canceled_flights FROM airport_delays",
        conn
    )

    fig = px.bar(cancel_df, x="airport_iata", y="canceled_flights",
                 title="Cancelled Flights by Airport")
    st.plotly_chart(fig, use_container_width=True)



