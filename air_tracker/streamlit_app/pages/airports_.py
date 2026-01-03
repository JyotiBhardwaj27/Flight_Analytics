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

# ================= KPIs =================
col1, col2, col3, col4, col5 = st.columns(5)

total_airports = pd.read_sql(
    "SELECT COUNT(*) AS cnt FROM airport", conn
)["cnt"][0]

busiest_departure = pd.read_sql(
    """
    SELECT origin_iata AS airport, COUNT(*) AS flights
    FROM flights
    WHERE flight_type = 'departure'
    GROUP BY origin_iata
    ORDER BY flights DESC
    LIMIT 1
    """,
    conn
)

busiest_arrival = pd.read_sql(
    """
    SELECT destination_iata AS airport, COUNT(*) AS flights
    FROM flights
    WHERE flight_type = 'arrival'
    GROUP BY destination_iata
    ORDER BY flights DESC
    LIMIT 1
    """,
    conn
)

avg_delay = pd.read_sql(
    "SELECT ROUND(AVG(avg_delay_min),2) AS avg_delay FROM airport_delays",
    conn
)["avg_delay"][0]

worst_airport = pd.read_sql(
    """
    SELECT airport_iata,
           ROUND(100.0 * delayed_flights / total_flights, 2) AS delay_pct
    FROM airport_delays
    WHERE total_flights > 0
    ORDER BY delay_pct DESC
    LIMIT 1
    """,
    conn
)

col1.metric("Total Airports", total_airports)
col2.metric("Busiest Departure", busiest_departure["airport"][0])
col3.metric("Busiest Arrival", busiest_arrival["airport"][0])
col4.metric("Avg Delay (min)", avg_delay)
col5.metric("Worst Delay Airport", worst_airport["airport_iata"][0])

# ================= TABS =================
tab1, tab2, tab3 = st.tabs(["🌍 Map", "📊 Airport Analysis", "🏢 Airport Detail"])

# ================= TAB 1 : MAP =================
with tab1:
    st.subheader("Flight Density by Airport (Arrivals + Departures)")

    map_df = pd.read_sql(
        """
        SELECT
            a.iata_code,
            a.name,
            a.city,
            a.latitude,
            a.longitude,
            SUM(
                CASE
                    WHEN f.origin_iata = a.iata_code THEN 1
                    WHEN f.destination_iata = a.iata_code THEN 1
                    ELSE 0
                END
            ) AS total_movements
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
        title="Airport Flight Density Map"
    )

    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r":0,"t":40,"l":0,"b":0}
    )

    st.plotly_chart(fig, use_container_width=True)

# ================= TAB 2 : ANALYSIS =================
with tab2:
    colA, colB = st.columns(2)

    outbound_df = pd.read_sql(
        """
        SELECT origin_iata, COUNT(*) AS outbound_flights
        FROM flights
        WHERE flight_type = 'departure'
        GROUP BY origin_iata
        ORDER BY outbound_flights DESC
        LIMIT 10
        """,
        conn
    )

    with colA:
        fig = px.bar(
            outbound_df,
            x="origin_iata",
            y="outbound_flights",
            title="Top 10 Airports by Departures",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)

    movement_df = pd.read_sql(
        """
        SELECT
            a.iata_code,
            SUM(CASE WHEN f.flight_type='departure' THEN 1 ELSE 0 END) AS departures,
            SUM(CASE WHEN f.flight_type='arrival' THEN 1 ELSE 0 END) AS arrivals
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
            title="Arrivals vs Departures by Airport",
            barmode="group"
        )
        st.plotly_chart(fig, use_container_width=True)

# ================= TAB 3 : AIRPORT DETAIL =================
with tab3:
    airport_list = pd.read_sql(
        "SELECT iata_code FROM airport ORDER BY iata_code", conn
    )["iata_code"].tolist()

    selected_airport = st.selectbox("Select Airport", airport_list)

    detail_df = pd.read_sql(
        f"""
        SELECT
            airline_name,
            COUNT(*) AS flights
        FROM flights
        WHERE origin_iata = '{selected_airport}'
           OR destination_iata = '{selected_airport}'
        GROUP BY airline_name
        ORDER BY flights DESC
        """,
        conn
    )

    st.write(f"### Airlines operating at {selected_airport}")
    st.dataframe(detail_df, use_container_width=True)
