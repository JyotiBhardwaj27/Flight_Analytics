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
    SELECT origin_iata, COUNT(*) AS flights
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
    SELECT destination_iata, COUNT(*) AS flights
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

if not busiest_departure.empty:
    col2.metric(
        "Busiest Departure",
        busiest_departure["origin_iata"][0],
        f'{busiest_departure["flights"][0]} flights'
    )

if not busiest_arrival.empty:
    col3.metric(
        "Busiest Arrival",
        busiest_arrival["destination_iata"][0],
        f'{busiest_arrival["flights"][0]} flights'
    )

col4.metric("Avg Delay (min)", avg_delay)

if not worst_airport.empty:
    col5.metric(
        "Worst Delay Airport",
        worst_airport["airport_iata"][0],
        f'{worst_airport["delay_pct"][0]} %'
    )

# ================= MAP DATA =================
map_df = pd.read_sql(
    """
    SELECT 
        a.iata_code,
        a.name,
        a.city,
        a.latitude,
        a.longitude,
        COUNT(f.flight_number) AS total_flights
    FROM airport a
    LEFT JOIN flights f
        ON a.iata_code = f.origin_iata
    GROUP BY a.iata_code, a.name, a.city, a.latitude, a.longitude
    """,
    conn
)

st.subheader("🌍 Airport Flight Density Map")

fig = px.scatter_mapbox(
    map_df,
    lat="latitude",
    lon="longitude",
    size="total_flights",
    hover_name="name",
    hover_data=["iata_code", "city", "total_flights"],
    zoom=2,
    height=500,
    title="Airport-wise Flight Volume"
)

fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r":0,"t":40,"l":0,"b":0}
)

st.plotly_chart(fig, use_container_width=True)

# ================= CHARTS =================
colA, colB = st.columns(2)

# ---- Outbound Flights per Airport ----
outbound_df = pd.read_sql(
    """
    SELECT 
        origin_iata,
        COUNT(*) AS outbound_flights
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
        title="Top 10 Airports by Outbound Flights",
        text_auto=True
    )
    st.plotly_chart(fig, use_container_width=True)

# ---- Arrival vs Departure per Airport ----
movement_df = pd.read_sql(
    """
    SELECT
        origin_iata AS airport,
        SUM(CASE WHEN flight_type = 'departure' THEN 1 ELSE 0 END) AS departures,
        SUM(CASE WHEN flight_type = 'arrival' THEN 1 ELSE 0 END) AS arrivals
    FROM flights
    GROUP BY origin_iata
    """,
    conn
)

with colB:
    fig = px.bar(
        movement_df.head(10),
        x="airport",
        y=["departures", "arrivals"],
        title="Arrival vs Departure (Top Airports)",
        barmode="group"
    )
    st.plotly_chart(fig, use_container_width=True)

# ================= AIRPORT DETAIL =================
st.subheader("🏢 Airport Detail View")

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
