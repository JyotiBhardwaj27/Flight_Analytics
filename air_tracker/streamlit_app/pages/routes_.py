import streamlit as st
import pandas as pd
import sqlite3

def get_connection():
    return sqlite3.connect(
        "air_tracker/streamlit_app/database/air_tracker.db",
        check_same_thread=False
    )

conn = get_connection()
st.title("🧭 Route Leaderboards")

# ---------------- Busiest Routes ----------------
st.subheader("🔥 Busiest Routes (Most Flights)")

routes_df = pd.read_sql(
    """
    SELECT
        origin_iata || ' → ' || destination_iata AS route,
        COUNT(*) AS flights
    FROM flights
    GROUP BY route
    ORDER BY flights DESC
    """,
    conn
)

st.dataframe(routes_df, use_container_width=True)

# ---------------- Most Delayed Airports ----------------
st.subheader("⏱️ Most Delayed Airports")

delay_df = pd.read_sql(
    """
    SELECT airport_iata,
           ROUND(100.0 * delayed_flights / total_flights,2) AS delay_pct,
           avg_delay_min
    FROM airport_delays
    WHERE total_flights > 0
    ORDER BY delay_pct DESC
    """,
    conn
)

st.dataframe(delay_df, use_container_width=True)
