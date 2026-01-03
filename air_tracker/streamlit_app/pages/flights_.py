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

cancelled = pd.read_sql(
    "SELECT COUNT(*) AS cnt FROM flights WHERE LOWER(status) IN ('cancelled','canceled')",
    conn
)["cnt"][0]

col1.metric("Total Flights", total_flights)
col2.metric("Arrivals", arrivals)
col3.metric("Departures", departures)
col4.metric("Delayed Flights", delayed)
col5.metric("Cancelled Flights", cancelled)

# ================= TABS =================
tab1, tab2, tab3 = st.tabs(
    ["📊 Flight Overview", "🧭 Route & Geography", "✈️ Aircraft & Airline"]
)

# ======================================================
# TAB 1 : FLIGHT OVERVIEW
# ======================================================
with tab1:
    colA, colB = st.columns(2)

    # ---- Status Distribution ----
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

    # ---- Hourly Flight Trend ----
    hourly_df = pd.read_sql(
        """
        SELECT
            strftime('%H', scheduled_time) AS hour,
            COUNT(*) AS flights
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
            title="Hourly Flight Trend"
        )
        fig.update_layout(
            xaxis_title="Hour of Day",
            yaxis_title="Number of Flights"
        )
        st.plotly_chart(fig, use_container_width=True)

# ======================================================
# TAB 2 : ROUTE & GEOGRAPHY (JOINS WITH AIRPORT)
# ======================================================
with tab2:
    colA, colB = st.columns(2)

    # ---- Top Routes ----
    routes_df = pd.read_sql(
        """
        SELECT
            o.city || ' → ' || d.city AS route,
            COUNT(*) AS flights
        FROM flights f
        JOIN airport o ON f.origin_iata = o.iata_code
        JOIN airport d ON f.destination_iata = d.iata_code
        GROUP BY route
        ORDER BY flights DESC
        LIMIT 10
        """,
        conn
    )

    with colA:
        fig = px.bar(
            routes_df,
            x="flights",
            y="route",
            orientation="h",
            title="Top 10 Routes by Flights"
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---- Domestic vs International ----
    dom_int_df = pd.read_sql(
        """
        SELECT
            CASE
                WHEN o.country = d.country THEN 'Domestic'
                ELSE 'International'
            END AS flight_category,
            COUNT(*) AS flights
        FROM flights f
        JOIN airport o ON f.origin_iata = o.iata_code
        JOIN airport d ON f.destination_iata = d.iata_code
        GROUP BY flight_category
        """,
        conn
    )

    with colB:
        fig = px.pie(
            dom_int_df,
            names="flight_category",
            values="flights",
            hole=0.4,
            title="Domestic vs International Flights"
        )
        st.plotly_chart(fig, use_container_width=True)

# ======================================================
# TAB 3 : AIRCRAFT & AIRLINE (JOINS WITH AIRCRAFT)
# ======================================================
with tab3:
    colA, colB = st.columns(2)

    # ---- Flights per Aircraft Model ----
    aircraft_df = pd.read_sql(
        """
        SELECT
            ac.model,
            COUNT(*) AS flights
        FROM flights f
        JOIN aircraft ac
            ON f.aircraft_registration = ac.registration
        GROUP BY ac.model
        ORDER BY flights DESC
        LIMIT 10
        """,
        conn
    )

    with colA:
        fig = px.bar(
            aircraft_df,
            x="model",
            y="flights",
            title="Flights by Aircraft Model",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---- Airline vs Status Heatmap ----
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

    with colB:
        fig = px.density_heatmap(
            airline_status_df,
            x="status",
            y="airline_name",
            z="flights",
            color_continuous_scale="Blues",
            title="Airline vs Flight Status"
        )
        st.plotly_chart(fig, use_container_width=True)

# ================= FLIGHT TABLE =================
st.subheader("📋 Flights Table (Filterable)")

flights_table = pd.read_sql(
    """
    SELECT
        f.flight_number,
        f.airline_name,
        o.city AS origin_city,
        d.city AS destination_city,
        f.scheduled_time,
        f.status
    FROM flights f
    LEFT JOIN airport o ON f.origin_iata = o.iata_code
    LEFT JOIN airport d ON f.destination_iata = d.iata_code
    ORDER BY f.scheduled_time DESC
    LIMIT 50
    """,
    conn
)

st.dataframe(flights_table, use_container_width=True)
