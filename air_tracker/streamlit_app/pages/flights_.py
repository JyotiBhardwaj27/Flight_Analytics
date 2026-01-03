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
st.title("✈️ Flights – Operational Analysis")

# ================= KPIs (ONLY FLIGHT-SPECIFIC) =================
col1, col2, col3, col4 = st.columns(4)

arrivals = pd.read_sql(
    "SELECT COUNT(*) AS cnt FROM flights WHERE flight_type='arrival'", conn
)["cnt"][0]

departures = pd.read_sql(
    "SELECT COUNT(*) AS cnt FROM flights WHERE flight_type='departure'", conn
)["cnt"][0]

delayed = pd.read_sql(
    "SELECT COUNT(*) AS cnt FROM flights WHERE status='Delayed'", conn
)["cnt"][0]

cancelled = pd.read_sql(
    "SELECT COUNT(*) AS cnt FROM flights WHERE LOWER(status) IN ('cancelled','canceled')",
    conn
)["cnt"][0]

col1.metric("Arrivals", arrivals)
col2.metric("Departures", departures)
col3.metric("Delayed Flights", delayed)
col4.metric("Cancelled Flights", cancelled)

# ================= TABS =================
tab1, tab2, tab3 = st.tabs(
    ["📊 Flight Overview", "🧭 Operations Breakdown", "📋 Flights Table"]
)

# ======================================================
# TAB 1 : FLIGHT OVERVIEW
# ======================================================
with tab1:
    colA, colB = st.columns(2)

    # 1. Flight Status Distribution
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
            title="Overall Flight Status Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

    # 2. Status by Arrival vs Departure
    status_type_df = pd.read_sql(
        """
        SELECT flight_type, status, COUNT(*) AS flights
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

    # 3. Flights by Airline (Operational Load)
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

    # 4. Arrival vs Departure Volume
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
# TAB 2 : OPERATIONS BREAKDOWN (JOINS, NO REPEAT)
# ======================================================
with tab2:
    colA, colB = st.columns(2)

    # 1. Flights by Origin Country
    country_df = pd.read_sql(
        """
        SELECT o.country, COUNT(*) AS flights
        FROM flights f
        JOIN airport o
            ON f.origin_iata = o.iata_code
        GROUP BY o.country
        ORDER BY flights DESC
        """,
        conn
    )

    with colA:
        fig = px.pie(
            country_df,
            names="country",
            values="flights",
            title="Flights by Origin Country"
        )
        st.plotly_chart(fig, use_container_width=True)

    # 2. Airline-wise Flight Status (Treemap)
    airline_status_df = pd.read_sql(
        """
        SELECT airline_name, status, COUNT(*) AS flights
        FROM flights
        GROUP BY airline_name, status
        """,
        conn
    )

    with colB:
        fig = px.treemap(
            airline_status_df,
            path=["airline_name", "status"],
            values="flights",
            title="Airline-wise Flight Status Distribution",
            height=650
        )
        st.plotly_chart(fig, use_container_width=True)

# ======================================================
# TAB 3 : FLIGHTS TABLE (ONLY PLACE FOR RAW DATA)
# ======================================================
with tab3:
    st.subheader("🔎 Filter Flights")

    airlines = pd.read_sql(
        "SELECT DISTINCT airline_name FROM flights ORDER BY airline_name",
        conn
    )["airline_name"].dropna().tolist()

    statuses = pd.read_sql(
        "SELECT DISTINCT status FROM flights ORDER BY status",
        conn
    )["status"].dropna().tolist()

    colF1, colF2 = st.columns(2)
    selected_airline = colF1.selectbox("Airline", ["All"] + airlines)
    selected_status = colF2.selectbox("Status", ["All"] + statuses)

    base_query = """
    SELECT
        f.flight_number,
        f.airline_name,
        o.city AS origin_city,
        d.city AS destination_city,
        f.scheduled_time,
        f.status,
        f.flight_type
    FROM flights f
    LEFT JOIN airport o ON f.origin_iata = o.iata_code
    LEFT JOIN airport d ON f.destination_iata = d.iata_code
    WHERE 1=1
    """

    params = []

    if selected_airline != "All":
        base_query += " AND f.airline_name = ?"
        params.append(selected_airline)

    if selected_status != "All":
        base_query += " AND f.status = ?"
        params.append(selected_status)

    base_query += " ORDER BY f.scheduled_time DESC LIMIT 100"

    flights_table = pd.read_sql(base_query, conn, params=params)
    st.dataframe(flights_table, use_container_width=True)
