import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

def get_connection():
    return sqlite3.connect(
        "air_tracker/streamlit_app/database/air_tracker.db",
        check_same_thread=False
    )

conn = get_connection()
st.title("⏱️ Delay Analysis")

# ================= KPIs =================
col1, col2, col3, col4, col5 = st.columns(5)

delay_kpis = pd.read_sql(
    """
    SELECT
        ROUND(AVG(avg_delay_min),2) AS avg_delay,
        ROUND(AVG(median_delay_min),2) AS median_delay,
        ROUND(100.0 * SUM(delayed_flights) / SUM(total_flights), 2) AS delay_pct,
        ROUND(100.0 * SUM(canceled_flights) / SUM(total_flights), 2) AS cancel_pct
    FROM airport_delays
    """,
    conn
)

worst_airport = pd.read_sql(
    """
    SELECT airport_iata
    FROM airport_delays
    ORDER BY avg_delay_min DESC
    LIMIT 1
    """,
    conn
)["airport_iata"][0]

col1.metric("Avg Delay (min)", delay_kpis["avg_delay"][0])
col2.metric("Median Delay (min)", delay_kpis["median_delay"][0])
col3.metric("Delay %", delay_kpis["delay_pct"][0])
col4.metric("Cancellation %", delay_kpis["cancel_pct"][0])
col5.metric("Worst Delay Airport", worst_airport)

# ================= TABS =================
tab1, tab2 = st.tabs(["📊 Delay Insights", "📋 Delay Tables"])

# ======================================================
# TAB 1 : DELAY INSIGHTS
# ======================================================
with tab1:
    colA, colB = st.columns(2)

    # 1. Avg Delay by Airport
    avg_delay_df = pd.read_sql(
        """
        SELECT airport_iata, avg_delay_min
        FROM airport_delays
        ORDER BY avg_delay_min DESC
        """,
        conn
    )

    with colA:
        fig = px.bar(
            avg_delay_df,
            x="airport_iata",
            y="avg_delay_min",
            title="Average Delay by Airport",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)

    # 2. Delay % by Airport
    delay_pct_df = pd.read_sql(
        """
        SELECT
            airport_iata,
            ROUND(100.0 * delayed_flights / total_flights, 2) AS delay_pct
        FROM airport_delays
        WHERE total_flights > 0
        """,
        conn
    )

    with colB:
        fig = px.bar(
            delay_pct_df,
            x="airport_iata",
            y="delay_pct",
            title="Delay Percentage by Airport",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)

    colC, colD = st.columns(2)

    # 3. Delay Trend by Date
    trend_df = pd.read_sql(
        """
        SELECT delay_date, avg_delay_min
        FROM airport_delays
        ORDER BY delay_date
        """,
        conn
    )

    with colC:
        fig = px.line(
            trend_df,
            x="delay_date",
            y="avg_delay_min",
            markers=True,
            title="Delay Trend Over Time"
        )
        st.plotly_chart(fig, use_container_width=True)

    # 4. Delayed vs Cancelled Flights
    cancel_df = pd.read_sql(
        """
        SELECT
            airport_iata,
            delayed_flights,
            canceled_flights
        FROM airport_delays
        """,
        conn
    )

    with colD:
        fig = px.bar(
            cancel_df,
            x="airport_iata",
            y=["delayed_flights", "canceled_flights"],
            barmode="group",
            title="Delayed vs Cancelled Flights"
        )
        st.plotly_chart(fig, use_container_width=True)

# ======================================================
# TAB 2 : TABLES
# ======================================================
with tab2:
    st.subheader("Airport Delay Metrics")
    st.dataframe(avg_delay_df, use_container_width=True)
