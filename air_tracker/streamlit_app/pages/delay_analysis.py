# import streamlit as st
# import pandas as pd
# import sqlite3
# import plotly.express as px

# # ---------------- DB CONNECTION ----------------
# def get_connection():
#     return sqlite3.connect(
#         "air_tracker/streamlit_app/database/air_tracker.db",
#         check_same_thread=False
#     )

# conn = get_connection()
# st.title("⏱️ Delay Analysis")

# # ======================================================
# # KPIs (DELAY-SPECIFIC ONLY)
# # ======================================================
# kpi_df = pd.read_sql(
#     """
#     SELECT
#         ROUND(AVG(avg_delay_min), 2) AS avg_delay,
#         ROUND(AVG(median_delay_min), 2) AS median_delay,
#         ROUND(100.0 * SUM(delayed_flights) / SUM(total_flights), 2) AS delay_pct,
#         ROUND(100.0 * SUM(canceled_flights) / SUM(total_flights), 2) AS cancel_pct
#     FROM airport_delays
#     """,
#     conn
# )

# col1, col2, col3, col4 = st.columns(4)
# col1.metric("Avg Delay (min)", kpi_df["avg_delay"][0])
# col2.metric("Median Delay (min)", kpi_df["median_delay"][0])
# col3.metric("Delayed Flights (%)", kpi_df["delay_pct"][0])
# col4.metric("Cancelled Flights (%)", kpi_df["cancel_pct"][0])

# # ================= TABS =================
# tab1, tab2 = st.tabs(
#     ["📊 Delay Insights", "📋 Delay Leaderboards"]
# )

# # ======================================================
# # TAB 1 : DELAY INSIGHTS (CHARTS)
# # ======================================================
# with tab1:
#     colA, colB = st.columns(2)

#     # ---------------- Avg Delay by Airport ----------------
#     avg_delay_df = pd.read_sql(
#         """
#         SELECT airport_iata, avg_delay_min
#         FROM airport_delays
#         WHERE avg_delay_min IS NOT NULL
#         ORDER BY avg_delay_min DESC
#         """,
#         conn
#     )

#     with colA:
#         fig = px.bar(
#             avg_delay_df,
#             x="airport_iata",
#             y="avg_delay_min",
#             title="Average Delay by Airport",
#             text_auto=True
#         )
#         st.plotly_chart(fig, use_container_width=True)

#     # ---------------- Delay % by Airport ----------------
#     delay_pct_df = pd.read_sql(
#         """
#         SELECT
#             airport_iata,
#             ROUND(100.0 * delayed_flights / total_flights, 2) AS delay_pct
#         FROM airport_delays
#         WHERE total_flights > 0
#         ORDER BY delay_pct DESC
#         """,
#         conn
#     )

#     with colB:
#         fig = px.bar(
#             delay_pct_df,
#             x="airport_iata",
#             y="delay_pct",
#             title="Delay Percentage by Airport",
#             text_auto=True
#         )
#         st.plotly_chart(fig, use_container_width=True)

#     colC, colD = st.columns(2)

#     # ---------------- Delay Severity Buckets ----------------
#     severity_df = pd.read_sql(
#         """
#         SELECT
#             CASE
#                 WHEN avg_delay_min <= 15 THEN '0–15 min'
#                 WHEN avg_delay_min <= 30 THEN '15–30 min'
#                 WHEN avg_delay_min <= 60 THEN '30–60 min'
#                 ELSE '60+ min'
#             END AS delay_bucket,
#             COUNT(*) AS airports
#         FROM airport_delays
#         WHERE avg_delay_min IS NOT NULL
#         GROUP BY delay_bucket
#         ORDER BY airports DESC
#         """,
#         conn
#     )

#     with colC:
#         fig = px.bar(
#             severity_df,
#             x="delay_bucket",
#             y="airports",
#             title="Delay Severity Distribution (Airports)",
#             text_auto=True
#         )
#         st.plotly_chart(fig, use_container_width=True)

#     # ---------------- Delay Consistency (Avg vs Median) ----------------
#     consistency_df = pd.read_sql(
#         """
#         SELECT
#             airport_iata,
#             avg_delay_min,
#             median_delay_min
#         FROM airport_delays
#         WHERE avg_delay_min IS NOT NULL
#           AND median_delay_min IS NOT NULL
#         """,
#         conn
#     )

#     with colD:
#         fig = px.scatter(
#             consistency_df,
#             x="median_delay_min",
#             y="avg_delay_min",
#             text="airport_iata",
#             title="Delay Consistency (Median vs Average)"
#         )
#         st.plotly_chart(fig, use_container_width=True)

# # ======================================================
# # TAB 2 : DELAY LEADERBOARDS (TABLES)
# # ======================================================
# with tab2:
#     st.subheader("🚨 Most Delayed Airports")

#     delay_table = pd.read_sql(
#         """
#         SELECT
#             airport_iata,
#             avg_delay_min,
#             median_delay_min,
#             delayed_flights,
#             canceled_flights,
#             total_flights,
#             ROUND(100.0 * delayed_flights / total_flights, 2) AS delay_pct
#         FROM airport_delays
#         WHERE total_flights > 0
#         ORDER BY delay_pct DESC
#         """,
#         conn
#     )

#     if delay_table.empty:
#         st.info("No delay data available.")
#     else:
#         st.dataframe(delay_table, use_container_width=True)

#         st.caption(
#             "Airports ranked by delay percentage. "
#             "This helps identify consistently problematic locations."
#         )

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
# KPIs (DELAY-SPECIFIC ONLY)
# ======================================================
kpi_df = pd.read_sql(
    """
    SELECT
        ROUND(AVG(avg_delay_min), 2) AS avg_delay,
        ROUND(AVG(median_delay_min), 2) AS median_delay,
        ROUND(100.0 * SUM(delayed_flights) / SUM(total_flights), 2) AS delay_pct,
        ROUND(100.0 * SUM(canceled_flights) / SUM(total_flights), 2) AS cancel_pct
    FROM airport_delays
    """,
    conn
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Delay (min)", kpi_df["avg_delay"][0])
col2.metric("Median Delay (min)", kpi_df["median_delay"][0])
col3.metric("Delayed Flights (%)", kpi_df["delay_pct"][0])
col4.metric("Cancelled Flights (%)", kpi_df["cancel_pct"][0])

# ================= TABS =================
tab1, tab2 = st.tabs(
    ["📊 Delay Insights", "📋 Delay Leaderboard"]
)

# ======================================================
# TAB 1 : DELAY INSIGHTS (VISUALS)
# ======================================================
with tab1:
    colA, colB = st.columns(2)

    # ---------------- Delay Distribution (Histogram) ----------------
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

    # ---------------- Delay Severity Buckets (Donut) ----------------
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
            hole=0.4,
            title="Delay Severity Share Across Airports"
        )
        st.plotly_chart(fig, use_container_width=True)

    colC, colD = st.columns(2)

    # ---------------- Delay Consistency (Scatter) ----------------
    consistency_df = pd.read_sql(
        """
        SELECT
            airport_iata,
            avg_delay_min,
            median_delay_min
        FROM airport_delays
        WHERE avg_delay_min IS NOT NULL
          AND median_delay_min IS NOT NULL
        """,
        conn
    )

    with colC:
        fig = px.scatter(
            consistency_df,
            x="median_delay_min",
            y="avg_delay_min",
            text="airport_iata",
            title="Delay Consistency: Median vs Average Delay",
            labels={
                "median_delay_min": "Median Delay (min)",
                "avg_delay_min": "Average Delay (min)"
            }
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---------------- Top Delayed Airports (Horizontal Bar) ----------------
    top_delay_df = pd.read_sql(
        """
        SELECT
            airport_iata,
            ROUND(100.0 * delayed_flights / total_flights, 2) AS delay_pct
        FROM airport_delays
        WHERE total_flights > 0
        ORDER BY delay_pct DESC
        LIMIT 10
        """,
        conn
    )

    with colD:
        fig = px.bar(
            top_delay_df,
            x="delay_pct",
            y="airport_iata",
            orientation="h",
            title="Top Airports by Delay Percentage"
        )
        st.plotly_chart(fig, use_container_width=True)

# ======================================================
# TAB 2 : DELAY LEADERBOARD (TABLE)
# ======================================================
with tab2:
    st.subheader("🚨 Airport Delay Leaderboard")

    delay_table = pd.read_sql(
        """
        SELECT
            airport_iata,
            avg_delay_min,
            median_delay_min,
            delayed_flights,
            canceled_flights,
            total_flights,
            ROUND(100.0 * delayed_flights / total_flights, 2) AS delay_pct
        FROM airport_delays
        WHERE total_flights > 0
        ORDER BY delay_pct DESC
        """,
        conn
    )

    if delay_table.empty:
        st.info("No delay data available.")
    else:
        st.dataframe(delay_table, use_container_width=True)

        st.caption(
            "Airports ranked by delay percentage. "
            "This table highlights locations with consistently poor on-time performance."
        )

