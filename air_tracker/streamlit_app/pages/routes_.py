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
st.title("🧭 Route Analysis")

# ================= KPIs =================
col1, col2, col3, col4 = st.columns(4)

route_kpis = pd.read_sql(
    """
    SELECT
        COUNT(DISTINCT origin_iata || '-' || destination_iata) AS total_routes,
        SUM(CASE WHEN o.country = d.country THEN 1 ELSE 0 END) AS domestic,
        SUM(CASE WHEN o.country != d.country THEN 1 ELSE 0 END) AS international
    FROM flights f
    JOIN airport o ON f.origin_iata = o.iata_code
    JOIN airport d ON f.destination_iata = d.iata_code
    """,
    conn
)

top_route = pd.read_sql(
    """
    SELECT o.city || ' → ' || d.city AS route
    FROM flights f
    JOIN airport o ON f.origin_iata = o.iata_code
    JOIN airport d ON f.destination_iata = d.iata_code
    GROUP BY route
    ORDER BY COUNT(*) DESC
    LIMIT 1
    """,
    conn
)["route"][0]

col1.metric("Unique Routes", route_kpis["total_routes"][0])
col2.metric("Top Route", top_route)
col3.metric("Domestic Routes", route_kpis["domestic"][0])
col4.metric("International Routes", route_kpis["international"][0])

# ================= CHARTS =================
colA, colB = st.columns(2)

# 1. Top City-Pair Routes
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
        title="Top 10 City-Pair Routes"
    )
    st.plotly_chart(fig, use_container_width=True)

# 2. Flights by Origin Country
country_df = pd.read_sql(
    """
    SELECT o.country, COUNT(*) AS flights
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

colC, colD = st.columns(2)

# 3. Domestic vs International Routes
dom_int_df = pd.read_sql(
    """
    SELECT
        CASE
            WHEN o.country = d.country THEN 'Domestic'
            ELSE 'International'
        END AS route_type,
        COUNT(*) AS flights
    FROM flights f
    JOIN airport o ON f.origin_iata = o.iata_code
    JOIN airport d ON f.destination_iata = d.iata_code
    GROUP BY route_type
    """,
    conn
)

with colC:
    fig = px.pie(
        dom_int_df,
        names="route_type",
        values="flights",
        hole=0.45,
        title="Domestic vs International Routes"
    )
    st.plotly_chart(fig, use_container_width=True)

# 4. Country-to-Country Flow
flow_df = pd.read_sql(
    """
    SELECT
        o.country AS origin_country,
        d.country AS destination_country,
        COUNT(*) AS flights
    FROM flights f
    JOIN airport o ON f.origin_iata = o.iata_code
    JOIN airport d ON f.destination_iata = d.iata_code
    GROUP BY origin_country, destination_country
    ORDER BY flights DESC
    """,
    conn
)

with colD:
    fig = px.treemap(
        flow_df,
        path=["origin_country", "destination_country"],
        values="flights",
        title="Country-to-Country Flight Flow",
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)
