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

# ================= KPIs (AIRPORT-SPECIFIC ONLY) =================
col1, col2, col3, col4 = st.columns(4)

busiest_airport_df = pd.read_sql(
    """
    SELECT
        a.iata_code,
        a.city,
        COUNT(f.flight_number) AS movements
    FROM airport a
    LEFT JOIN flights f
        ON a.iata_code IN (f.origin_iata, f.destination_iata)
    GROUP BY a.iata_code, a.city
    ORDER BY movements DESC
    LIMIT 1
    """,
    conn
)

if not busiest_airport_df.empty:
    busiest_airport = busiest_airport_df.iloc[0]["iata_code"]
else:
    busiest_airport = "N/A"


worst_delay_airport = pd.read_sql(
    """
    SELECT airport_iata,
           ROUND(100.0 * delayed_flights / total_flights, 2) delay_pct
    FROM airport_delays
    WHERE total_flights > 0
    ORDER BY delay_pct DESC
    LIMIT 1
    """,
    conn
)

avg_delay_airport = pd.read_sql(
    "SELECT ROUND(AVG(avg_delay_min),2) avg_delay FROM airport_delays",
    conn
)["avg_delay"][0]

zero_arrival_airports = pd.read_sql(
    """
    SELECT COUNT(*) cnt
    FROM airport a
    LEFT JOIN flights f ON a.iata_code = f.destination_iata
    WHERE f.flight_number IS NULL
    """,
    conn
)["cnt"][0]

col1.metric("Busiest Airport", busiest_airport["airport"][0])
col2.metric("Worst Delay Airport", worst_delay_airport["airport_iata"][0])
col3.metric("Avg Airport Delay (min)", avg_delay_airport)
col4.metric("Airports w/ No Arrivals", zero_arrival_airports)

# ================= TABS =================
tab1, tab2, tab3 = st.tabs(["🌍 Map", "📊 Airport Analysis", "📋 Airport Tables"])

# ======================================================
# TAB 1 : MAP (TRUE FLIGHT DENSITY)
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
            COUNT(f.flight_number) total_movements
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
        margin={"r":0,"t":40,"l":0,"b":0}
    )

    st.plotly_chart(fig, use_container_width=True)

# ======================================================
# TAB 2 : ANALYSIS
# ======================================================
with tab2:
    colA, colB = st.columns(2)

    # Top Airports by Movements
    top_airports_df = pd.read_sql(
        """
        SELECT origin_iata airport, COUNT(*) flights
        FROM flights
        GROUP BY origin_iata
        ORDER BY flights DESC
        LIMIT 10
        """,
        conn
    )

    with colA:
        fig = px.bar(
            top_airports_df,
            x="flights",
            y="airport",
            orientation="h",
            title="Top Airports by Outbound Flights"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Arrival vs Departure by Airport
    movement_df = pd.read_sql(
        """
        SELECT
            a.iata_code,
            SUM(CASE WHEN f.flight_type='departure' THEN 1 ELSE 0 END) departures,
            SUM(CASE WHEN f.flight_type='arrival' THEN 1 ELSE 0 END) arrivals
        FROM airport a
        LEFT JOIN flights f
            ON a.iata_code IN (f.origin_iata, f.destination_iata)
        GROUP BY a.iata_code
        """,
        conn
    )

    with colB:
        fig = px.bar(
            movement_df,
            x="iata_code",
            y=["departures", "arrivals"],
            barmode="group",
            title="Arrivals vs Departures by Airport"
        )
        st.plotly_chart(fig, use_container_width=True)

# ======================================================
# TAB 3 : TABLES
# ======================================================
with tab3:
    st.subheader("Airport Movement Summary")
    st.dataframe(movement_df, use_container_width=True)

    st.subheader("Airport Delay Metrics")
    delay_df = pd.read_sql(
        """
        SELECT airport_iata, avg_delay_min, median_delay_min, canceled_flights
        FROM airport_delays
        """,
        conn
    )
    st.dataframe(delay_df, use_container_width=True)
