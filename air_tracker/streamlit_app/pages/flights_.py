
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

def get_connection():
    return sqlite3.connect("air_tracker/streamlit_app/database/air_tracker.db", check_same_thread=False)


st.title("✈️ Flight Search & Filters")

conn = get_connection()

st.sidebar.header("Filters")

airline = st.sidebar.text_input("Airline")
flight_no = st.sidebar.text_input("Flight Number")
status = st.sidebar.selectbox(
    "Status",
    ["All"] + pd.read_sql(
        "SELECT DISTINCT status FROM flights", conn
    )["status"].dropna().tolist()
)
query = "SELECT * FROM flights WHERE 1=1"
params = []

if airline:
    query += " AND airline_name LIKE ?"
    params.append(f"%{airline}%")

if flight_no:
    query += " AND flight_number LIKE ?"
    params.append(f"%{flight_no}%")

if status != "All":
    query += " AND status = ?"
    params.append(status)

df = pd.read_sql(query, conn, params=params)


# Flights by Airline
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

# Flights by Origin Airport
origin_df = pd.read_sql(
    """
    SELECT origin_iata, COUNT(*) AS flights
    FROM flights
    GROUP BY origin_iata
    ORDER BY flights DESC
    LIMIT 10
    """,
    conn
)

tab1, tab2 = st.tabs(["✈️ Flights Table", "📊 Flight Analysis"])
with tab1:
    st.dataframe(df)
with tab2:
    fig = px.histogram(
        airline_df,
        x="flights",
        title="Distribution of Flights Across Airlines"
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(
        origin_df,
        x="origin_iata",
        y="flights",
        title="Top Origin Airports"
    )
    st.plotly_chart(fig, use_container_width=True)

query = "SELECT * FROM flights WHERE 1=1"
params = []

if airline:
    query += " AND airline_name LIKE ?"
    params.append(f"%{airline}%")

if flight_no:
    query += " AND flight_number LIKE ?"
    params.append(f"%{flight_no}%")

if status != "All":
    query += " AND status = ?"
    params.append(status)



