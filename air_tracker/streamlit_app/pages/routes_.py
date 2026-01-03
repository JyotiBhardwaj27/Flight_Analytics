import streamlit as st
import pandas as pd
import sqlite3

# ---------------- DB CONNECTION ----------------
def get_connection():
    return sqlite3.connect(
        "air_tracker/streamlit_app/database/air_tracker.db",
        check_same_thread=False
    )

conn = get_connection()
st.title("🧭 Route Analysis")

# ================= TABS =================
tab1, tab2 = st.tabs(
    ["🔄 Route Directionality", "⏱️ Route Impact (Delays)"]
)

# ======================================================
# TAB 1 : ROUTE DIRECTIONALITY
# ======================================================
with tab1:
    st.subheader("🔄 Route Directionality (Origin → Destination)")

    direction_df = pd.read_sql(
        """
        SELECT
            origin_iata || ' → ' || destination_iata AS route,
            COUNT(*) AS flights
        FROM flights
        WHERE origin_iata IS NOT NULL
          AND destination_iata IS NOT NULL
        GROUP BY origin_iata, destination_iata
        ORDER BY flights DESC
        """,
        conn
    )

    if direction_df.empty:
        st.info(
            "No sufficient repeated routes available to analyse directionality."
        )
    else:
        st.dataframe(direction_df, use_container_width=True)

        st.caption(
            "This table shows directional traffic flows. "
            "It helps identify one-sided or dominant route patterns."
        )

# ======================================================
# TAB 2 : ROUTE IMPACT — DELAY LEADERBOARD
# ======================================================
with tab2:
    st.subheader("⏱️ Route Impact via Airport Delays")

    delay_df = pd.read_sql(
        """
        SELECT
            airport_iata,
            total_flights,
            delayed_flights,
            ROUND(100.0 * delayed_flights / total_flights, 2) AS delay_pct,
            avg_delay_min
        FROM airport_delays
        WHERE total_flights > 0
        ORDER BY delay_pct DESC
        """,
        conn
    )

    if delay_df.empty:
        st.info("No delay data available to assess route impact.")
    else:
        st.dataframe(delay_df, use_container_width=True)

        st.caption(
            "Airports ranked by delay percentage. "
            "These airports disproportionately affect route reliability."
        )
