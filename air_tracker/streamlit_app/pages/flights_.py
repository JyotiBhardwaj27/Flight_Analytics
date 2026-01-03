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
st.title("✈️ Flights Analysis")

# ================= KPIs =================
col1, col2, col3, col4 = st.columns(4)

total_flights = pd.read_sql(
    "SELECT COUNT(*) AS cnt FROM flights", conn
)["cnt"][0]

arrivals = pd.read_sql(
    "SELECT COUNT(*) AS cnt FROM flights WHERE flight_type='arrival'", conn
)["cnt"][0]

departures = pd.read_sql(
    "SELECT COUNT(*) AS cnt FROM flights WHERE flight_type='departure'", conn
)["cnt"][0]

delayed = pd.read_sql(
    "SELECT COUNT(*) AS cnt FROM flights WHERE status='Delayed'", conn
)["cnt"][0]

col1.metric("Total Flights", total_flights)
col2.metric("Arrivals", arrivals)
col3.metric("Departures", departures)
col4.metric("Delayed Flights", delayed)

# ================= TABS =================
tab1, tab2 = st.tabs(["📊 Flight Overview", "🧭 Routes & Operations"])

# ======================================================
# TAB 1 : FLIGHT OVERVIEW
# ======================================================
with tab1:
    colA, colB = st.columns(2)

    # ---- 1. Flight Status Distribution ----
    status_df = pd.read_sql(
        """
        SELECT status, COUNT(*) AS flights
        FROM flights
        GROUP BY status
        """,
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

    # ---- 2. Status by Arrival vs Departure ----
    status_type_df = pd.read_sql(
        """
        SELECT
            flight_type,
            status,
            COUNT(*) AS flights
        FROM flights
        GROUP BY flight_type, status
        """,
        conn
    )

    with colB:
        fig = px.bar(
            status_type_df,
            x="flight_type",
            y="flights",
            color="status",
            barmode="group",
            title="Flight Status by Arrival vs Departure"
        )
        st.plotly_chart(fig, use_container_width=True)

    colC, colD = st.columns(2)

    # ---- 3. Flights by Airline ----
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

    with colC:
        fig = px.bar(
            airline_df,
            x="airline_name",
            y="flights",
            title="Flights by Airline",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---- 4. Arrival vs Departure Volume ----
    movement_df = pd.read_sql(
        """
        SELECT flight_type, COUNT(*) AS flights
        FROM flights
        GROUP BY flight_type
        """,
        conn
    )

    with colD:
        fig = px.bar(
            movement_df,
            x="flight_type",
            y="flights",
            title="Arrival vs Departure Volume",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)

# ======================================================
# TAB 2 : ROUTES & OPERATIONS (JOIN-BASED)
# ======================================================
with tab2:
    colA, colB = st.columns(2)

    # ---- 1. Top Airports by Total Movements ----
    airport_df = pd.read_sql(
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
        LIMIT 10
        """,
        conn
    )

    with colA:
        fig = px.bar(
            airport_df,
            x="total_movements",
            y="iata_code",
            orientation="h",
            title="Top Airports by Total Movements"
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---- 2. Flights by Origin Country ----
    country_df = pd.read_sql(
        """
        SELECT
            o.country,
            COUNT(*) AS flights
        FROM flights f
        JOIN airport o
            ON f.origin_iata = o.iata_code
        GROUP BY o.country
        ORDER BY flights DESC
        """,
        conn
    )

    with colB:
        fig = px.pie(
            country_df,
            names="country",
            values="flights",
            title="Flights by Origin Country"
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---- 3. Airline-wise Flight Status (Treemap) ----
    airline_status_df = pd.read_sql(
        """
        SELECT
            airline_name,
            status,
            COUNT(*) AS flights
        FROM flights
        GROUP BY airline_name, status
        """,
        conn
    )

    fig = px.treemap(
        airline_status_df,
        path=["airline_name", "status"],
        values="flights",
        title="Airline-wise Flight Status Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)
