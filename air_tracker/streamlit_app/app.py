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

st.set_page_config(page_title="Air Tracker", layout="wide")
st.title("✈️ Air Tracker – Overview")

conn = get_connection()

# ---------------- KPI METRICS ----------------
col1, col2, col3, col4, col5 = st.columns(5)

total_airports = pd.read_sql(
    "SELECT COUNT(*) AS cnt FROM airport", conn
)["cnt"][0]

total_flights = pd.read_sql(
    "SELECT COUNT(*) AS cnt FROM flights", conn
)["cnt"][0]

total_airlines = pd.read_sql(
    "SELECT COUNT(DISTINCT airline_name) AS cnt FROM flights", conn
)["cnt"][0]

delayed_flights = pd.read_sql(
    "SELECT COUNT(*) AS cnt FROM flights WHERE status='Delayed'", conn
)["cnt"][0]

avg_delay = pd.read_sql(
    "SELECT ROUND(AVG(avg_delay_min),2) AS avg_delay FROM airport_delays",
    conn
)["avg_delay"][0]

col1.metric("Total Airports", total_airports)
col2.metric("Total Flights", total_flights)
col3.metric("Active Airlines", total_airlines)
col4.metric("Delayed Flights", delayed_flights)
col5.metric("Avg Delay (min)", avg_delay)

# ---------------- DATA PREP ----------------
status_df = pd.read_sql(
    "SELECT status, COUNT(*) AS flight_count FROM flights GROUP BY status",
    conn
)

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

flight_type_df = pd.read_sql(
    """
    SELECT flight_type, COUNT(*) AS cnt
    FROM flights
    GROUP BY flight_type
    """,
    conn
)

hourly_flights_df = pd.read_sql(
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

# ---------------- TABS ----------------
tab1, tab2 = st.tabs(["📊 Overview Charts", "📋 Key Tables"])

# ================= TAB 1 : CHARTS =================
with tab1:

    colA, colB = st.columns(2)

    # ---- Flight Status Pie ----
    with colA:
        fig = px.pie(
            status_df,
            names="status",
            values="flight_count",
            title="Flight Status Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---- Arrival vs Departure ----
    with colB:
        fig = px.bar(
            flight_type_df,
            x="flight_type",
            y="cnt",
            title="Arrival vs Departure Flights",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)

    colC, colD = st.columns(2)

    # ---- Top Airlines Donut ----
    with colC:
        fig = px.pie(
            airline_df.head(5),
            names="airline_name",
            values="flights",
            hole=0.45,
            title="Top Airlines – Market Share"
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---- Flights Over Time (Hourly)----
    with colD:
        fig = px.line(
            hourly_flights_df,
            x="hour",
            y="flights",
            markers=True,
            title="Hourly Flight Trend"
       )
       st.plotly_chart(fig, use_container_width=True)
        fig.update_layout(
            xaxis_title="Hour of Day",
            yaxis_title="Number of Flights"
       )

       st.plotly_chart(fig, use_container_width=True)



# ================= TAB 2 : TABLES =================
with tab2:
    st.subheader("Flights by Status")
    st.dataframe(status_df, use_container_width=True)

    st.subheader("Top Airlines by Flight Count")
    st.dataframe(airline_df, use_container_width=True)


    st.subheader("Top Airlines")
    st.dataframe(airline_df)

