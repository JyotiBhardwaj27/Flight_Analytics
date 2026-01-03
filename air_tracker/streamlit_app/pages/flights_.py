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
col1, col2, col3, col4, col5 = st.columns(5)

total_flights = pd.read_sql("SELECT COUNT(*) cnt FROM flights", conn)["cnt"][0]
arrivals = pd.read_sql("SELECT COUNT(*) cnt FROM flights WHERE flight_type='arrival'", conn)["cnt"][0]
departures = pd.read_sql("SELECT COUNT(*) cnt FROM flights WHERE flight_type='departure'", conn)["cnt"][0]
delayed = pd.read_sql("SELECT COUNT(*) cnt FROM flights WHERE status='Delayed'", conn)["cnt"][0]
cancelled = pd.read_sql(
    "SELECT COUNT(*) cnt FROM flights WHERE LOWER(status) IN ('cancelled','canceled')",
    conn
)["cnt"][0]

col1.metric("Total Flights", total_flights)
col2.metric("Arrivals", arrivals)
col3.metric("Departures", departures)
col4.metric("Delayed", delayed)
col5.metric("Cancelled", cancelled)

# ================= TABS =================
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Overview", "🧭 Routes & Geography", "✈️ Airline & Aircraft", "📋 Flights Table"]
)

# ======================================================
# TAB 1 : OVERVIEW
# ======================================================
with tab1:
    colA, colB = st.columns(2)

    status_df = pd.read_sql(
        "SELECT status, COUNT(*) flights FROM flights GROUP BY status",
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

    hourly_df = pd.read_sql(
        """
        SELECT strftime('%H', scheduled_time) hour, COUNT(*) flights
        FROM flights
        WHERE scheduled_time IS NOT NULL
        GROUP BY hour
        ORDER BY hour
        """,
        conn
    )

    with colB:
        fig = px.line(
            hourly_df,
            x="hour",
            y="flights",
            markers=True,
            title="Hourly Flight Pattern"
        )
        st.plotly_chart(fig, use_container_width=True)

# ======================================================
# TAB 2 : ROUTES & GEOGRAPHY (DATA-REALISTIC)
# ======================================================
with tab2:
    colA, colB = st.columns(2)

    # 🔁 Replaced "Top 10 Routes" with Top Airports by Movements
    airport_movement_df = pd.read_sql(
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
            airport_movement_df,
            x="total_movements",
            y="iata_code",
            orientation="h",
            title="Top Airports by Total Movements"
        )
        st.plotly_chart(fig, use_container_width=True)

    # 🔁 Replaced Domestic vs International with Origin Country Distribution
    country_df = pd.read_sql(
        """
        SELECT
            o.country,
            COUNT(*) flights
        FROM flights f
        JOIN airport o ON f.origin_iata = o.iata_code
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

# ======================================================
# TAB 3 : AIRLINE & AIRCRAFT (TREEMAP INSTEAD OF HEATMAP)
# ======================================================
with tab3:
    colA, colB = st.columns(2)

    aircraft_df = pd.read_sql(
        """
        SELECT ac.model, COUNT(*) flights
        FROM flights f
        JOIN aircraft ac ON f.aircraft_registration = ac.registration
        GROUP BY ac.model
        ORDER BY flights DESC
        LIMIT 10
        """,
