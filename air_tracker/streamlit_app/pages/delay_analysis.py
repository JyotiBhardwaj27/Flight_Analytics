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
st.title("⏱️ Delay Analysis")

# ======================================================
# KPIs (HIGH-LEVEL CONTEXT)
# ======================================================
kpi_df = pd.read_sql(
    """
    SELECT
        ROUND(AVG(avg_delay_min), 2) AS avg_delay,
        ROUND(100.0 * SUM(delayed_flights) / SUM(total_flights), 2) AS delay_pct,
        ROUND(100.0 * SUM(canceled_flights) / SUM(total_flights), 2) AS cancel_pct
    FROM airport_delays
    """,
    conn
)

col1, col2, col3 = st.columns(3)
col1.metric("Avg Delay (min)", kpi_df["avg_delay"][0])
col2.metric("Delayed Flights (%)", kpi_df["delay_pct"][0])
col3.metric("Cancelled Flights (%)", kpi_df["cancel_pct"][0])

# ================= TABS =================
tab1, tab2 = st.tabs(
    ["📊 Delay Insights", "📋 Delay Leaderboard"]
)

# ======================================================
# TAB 1 : DELAY INSIGHTS (MEANINGFUL CHARTS ONLY)
# ======================================================
with tab1:
    colA, colB = st.columns(2)

    # ---------------- 1. Delay Distribution ----------------
    delay_dist_df = pd.read_sql(
        """
        SELECT avg_delay_min
        FROM airport_delays
        WHERE avg_delay_min IS NOT NULL
        """,
        conn
    )

    with colA:
        fig = px.histogram(
            delay_dist_df,
            x="avg_delay_min",
            nbins=15,
            title="Distribution of Average Delay (Minutes)"
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---------------- 2. Delay Severity Buckets ----------------
    severity_df = pd.read_sql(
        """
        SELECT
            CASE
                WHEN avg_delay_min <= 15 THEN '0–15 min'
                WHEN avg_delay_min <= 30 THEN '15–30 min'
                WHEN avg_delay_min <= 60 THEN '30–60 min'
                ELSE '60+ min'
            END AS delay_bucket,
            COUNT(*) AS airports
        FROM airport_delays
        WHERE avg_delay_min IS NOT NULL
        GROUP BY delay_bucket
        """,
        conn
    )

    with colB:
        fig = px.pie(
            severity_df,
            names="delay_bucket",
            values="airports",
            hole=0.45,
            title="Delay Severity Share Across Airports"
        )
        st.plotly_chart(fig, use_container_width=True)

    colC, colD = st.columns(2)

    # ---------------- 3. Delay Contribution Share ----------------
    contribution_df = pd.read_sql(
        """
        SELECT
            airport_iata,
            delayed_flights
        FROM airport_delays
        WHERE delayed_flights > 0
        ORDER BY delayed_flights DESC
        LIMIT 8
        """,
        conn
    )

    with colC:
        fig = px.pie(
            contribution_df,
            names="airport_iata",
            values="delayed_flights",
            hole=0.45,
            title="Contribution to Total Delayed Flights (Top Airports)"
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---------------- 4. Delay Rate vs Traffic Volume ----------------
    bubble_df = pd.read_sql(
        """
        SELECT
            airport_iata,
            total_flights,
            delayed_flights,
            ROUND(100.0 * delayed_flights / total_flights, 2) AS delay_pct
        FROM airport_delays
        WHERE total_flights > 0
        """,
        conn
    )

    with colD:
        fig = px.scatter(
            bubble_df,
            x="total_flights",
            y="delay_pct",
            size="delayed_flights",
            hover_name="airport_iata",
            title="Delay Rate vs Traffic Volume",
            labels={
                "total_flights": "Total Flights",
                "delay_pct": "Delay Percentage"
            }
        )
        st.plotly_chart(fig, use_container_width=True)

# ======================================================
# TAB 2 : DELAY LEADERBOARD (TABLE — NO DUPLICATION)
# ======================================================
with tab2:
    st.subheader("🚨 Most Delayed Airports")

    delay_table = pd.read_sql(
        """
        SELECT
            airport_iata,
            total_flights,
            delayed_flights,
            canceled_flights,
            avg_delay_min,
            ROUND(100.0 * delayed_flights / total_flights, 2) AS delay_pct
        FROM airport_delays
        WHERE total_flights > 0
        ORDER BY delay_pct DESC
        """,
        conn
    )

    st.dataframe(delay_table, use_container_width=True)

    st.caption(
        "This table ranks airports by delay percentage and provides "
        "exact operational metrics for audit and comparison."
    )
