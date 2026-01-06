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
st.title("🛩️ Aircraft Utilization")

# ======================================================
# KPIs
# ======================================================
total_aircraft = pd.read_sql(
    "SELECT COUNT(*) cnt FROM aircraft",
    conn
)["cnt"][0]

assigned_aircraft = pd.read_sql(
    """
    SELECT COUNT(DISTINCT aircraft_registration) cnt
    FROM flights
    WHERE aircraft_registration IS NOT NULL
    """,
    conn
)["cnt"][0]

unassigned_aircraft = total_aircraft - assigned_aircraft

avg_flights_per_aircraft = pd.read_sql(
    """
    SELECT ROUND(
        CAST(COUNT(*) AS FLOAT) / COUNT(DISTINCT aircraft_registration),
        2
    ) AS avg_flights
    FROM flights
    WHERE aircraft_registration IS NOT NULL
    """,
    conn
)["avg_flights"][0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Aircraft", total_aircraft)
col2.metric("Aircraft Assigned", assigned_aircraft)
col3.metric("Unassigned Aircraft", max(unassigned_aircraft, 0))
col4.metric("Avg Flights / Aircraft", avg_flights_per_aircraft)

# ======================================================
# TABS
# ======================================================
tab1, tab2 = st.tabs(["📊 Aircraft Analysis", "📋 Aircraft Tables"])

# ======================================================
# TAB 1 : CHARTS
# ======================================================
with tab1:
    colA, colB = st.columns(2)

    # ---------------- Flights per Aircraft Model ----------------
    model_df = pd.read_sql(
        """
        SELECT
            a.model,
            COUNT(f.flight_number) AS flights
        FROM aircraft a
        LEFT JOIN flights f
            ON a.registration = f.aircraft_registration
        GROUP BY a.model
        ORDER BY flights DESC
        """,
        conn
    )

    with colA:
        fig = px.bar(
            model_df,
            x="model",
            y="flights",
            title="Flights per Aircraft Model",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---------------- Top Aircraft by Flights ----------------
    top_aircraft_df = pd.read_sql(
        """
        SELECT
            aircraft_registration,
            COUNT(*) AS flights
        FROM flights
        WHERE aircraft_registration IS NOT NULL
        GROUP BY aircraft_registration
        ORDER BY flights DESC
        LIMIT 10
        """,
        conn
    )

    with colB:
        fig = px.bar(
            top_aircraft_df,
            x="flights",
            y="aircraft_registration",
            orientation="h",
            title="Top Aircraft by Number of Flights"
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---------------- Assignment Status ----------------
    assign_df = pd.DataFrame({
        "status": ["Assigned", "Unassigned"],
        "count": [assigned_aircraft, max(unassigned_aircraft, 0)]
    })

    fig = px.pie(
        assign_df,
        names="status",
        values="count",
        hole=0.4,
        title="Aircraft Assignment Status"
    )

    st.plotly_chart(fig, use_container_width=True)

# ======================================================
# TAB 2 : TABLES
# ======================================================
with tab2:
    st.subheader("Aircraft Utilization Table")

    aircraft_table = pd.read_sql(
        """
        SELECT
            a.registration,
            a.model,
            COUNT(f.flight_number) AS flights_assigned
        FROM aircraft a
        LEFT JOIN flights f
            ON a.registration = f.aircraft_registration
        GROUP BY a.registration, a.model
        ORDER BY flights_assigned DESC
        """,
        conn
    )

    st.dataframe(aircraft_table, use_container_width=True)
