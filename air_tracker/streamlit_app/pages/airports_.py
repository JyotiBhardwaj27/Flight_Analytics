import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

def get_connection():
    return sqlite3.connect("../database/air_tracker.db", check_same_thread=False)

tab1, tab2, tab3 = st.tabs(["🌍 Map", "🏢 Airport Details", "📊 Airport Analysis"])

conn = get_connection()
airport_df = pd.read_sql(
    """
    SELECT
        iata_code,
        name,
        city,
        country,
        latitude,
        longitude
    FROM airport
    WHERE latitude IS NOT NULL
      AND longitude IS NOT NULL
    """,
    conn
)

with tab1:
    st.subheader("Airport Locations Map")
    st.map(
        airport_df.rename(columns={"latitude": "lat", "longitude": "lon"})
    )

selected_airport = st.selectbox(
    "Select Airport",
    airport_df["iata_code"]
)
linked_flights = pd.read_sql(
    """
    SELECT *
    FROM flights
    WHERE origin_iata = ?
       OR destination_iata = ?
    """,
    conn,
    params=[selected_airport, selected_airport]
)
airport_info = pd.read_sql(
    "SELECT * FROM airport WHERE iata_code = ?",
    conn,
    params=[selected_airport]
)
with tab2:
    st.subheader("Airport Details")
    st.table(airport_info)
    st.dataframe(linked_flights)

airport_volume_df = pd.read_sql(
    """
    SELECT origin_iata, COUNT(*) AS flights
    FROM flights
    GROUP BY origin_iata
    ORDER BY flights DESC
    LIMIT 10
    """,
    conn
)

with tab3:
    fig = px.bar(
        airport_volume_df,
        x="origin_iata",
        y="flights",
        title="Top Airports by Outbound Flights"
    )
    st.plotly_chart(fig, use_container_width=True)


