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
st.title("🌍 Airports Analysis")

# ================= KPI: BUSIEST AIRPORT =================
busiest_airport_df = pd.read_sql(
    """
    SELECT
        a.iata_code AS airport,
        COUNT(f.flight_number) AS movements
    FROM airport a
    LEFT JOIN flights f
        ON a.iata_code IN (f.origin_iata, f.destination_iata)
    GROUP BY a.iata_code
    ORDER BY movements DESC
    LIMIT 1
    """,
    conn
)

if not busiest_airport_df.empty:
    busiest_airport = busiest_airport_df.iloc[0]["airport"]
    busiest_movements = busiest_airport_df.iloc[0]["movements"]
else:
    busiest_airport = "N/A"
    busiest_movements = 0

col1, col2 = st.columns(2)
col1.metric("Busiest Airport (Movements)", busiest_airport)
col2.metric("Total Movements", busiest_movements)

# ================= TABS =================
tab1, tab2, tab3 = st.tabs(
    ["🌍 Airport Map", "🏢 Airport Details", "📋 Airport Tables"]
)

# ======================================================
# TAB 1 : MAP — FLIGHT DENSITY
# ======================================================
with tab1:
    map_df = pd.read_sql(
        """
        SELECT
            a.iata_code,
            a.name,
            a.city,
            a.latitude,
            a.longitude,
            COUNT(f.flight_number) AS total_movements
        FROM airport a
        LEFT JOIN flights f
            ON a.iata_code IN (f.origin_iata, f.destination_iata)
        GROUP BY a.iata_code, a.name, a.city, a.latitude, a.longitude
        """,
        conn
    )

    fig = px.scatter_mapbox(
        map_df,
        lat="latitude",
        lon="longitude",
        size="total_movements",
        hover_name="name",
        hover_data=["iata_code", "city", "total_movements"],
        zoom=1.5,
        height=550,
        title="Airport Flight Density (Arrivals + Departures)"
    )

    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 40, "l": 0, "b": 0}
    )

    st.plotly_chart(fig, use_container_width=True)

# ======================================================
# TAB 2 : AIRPORT DETAILS VIEWER
# ======================================================
with tab2:
    airports_df = pd.read_sql(
        """
        SELECT iata_code, name, city, country, timezone
        FROM airport
        ORDER BY iata_code
        """,
        conn
    )

    selected_iata = st.selectbox(
        "Select Airport (IATA)",
        airports_df["iata_code"]
    )

    airport_info = airports_df[
        airports_df["iata_code"] == selected_iata
    ].iloc[0]

    colA, colB, colC = st.columns(3)
    colA.metric("City", airport_info["city"])
    colB.metric("Country", airport_info["country"])
    colC.metric("Timezone", airport_info["timezone"])

    st.subheader("✈️ Linked Flights")

    linked_flights = pd.read_sql(
        """
        SELECT
            flight_number,
            airline_name,
            origin_iata,
            destination_iata,
            status,
            flight_type
        FROM flights
        WHERE origin_iata = ? OR destination_iata = ?
        ORDER BY scheduled_time DESC
        LIMIT 50
        """,
        conn,
        params=[selected_iata, selected_iata]
    )

    st.dataframe(linked_flights, use_container_width=True)

# ======================================================
# TAB 3 : AIRPORT TABLES
# ======================================================
with tab3:
    st.subheader("Airport Movement Summary")

    movement_df = pd.read_sql(
        """
        SELECT
            a.iata_code,
            a.city,
            COUNT(f.flight_number) AS total_movements
        FROM airport a
        LEFT JOIN flights f
            ON a.iata_code IN (f.origin_iata, f.destination_iata)
        GROUP BY a.iata_code, a.city
        ORDER BY total_movements DESC
        """,
        conn
    )

    st.dataframe(movement_df, use_container_width=True)
