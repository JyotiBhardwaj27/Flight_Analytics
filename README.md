✈️ Air Tracker – Aviation Analytics Platform

An end-to-end aviation data analytics web application built using Python, SQLite, SQL, and Streamlit.
The project extracts aviation data, stores it in a normalized SQL database, and visualizes operational insights through an interactive, multi-page Streamlit dashboard.

📌 Project Overview

The Air Tracker project focuses on analyzing aviation operations such as:

Airport information and connectivity

Flight movements and statuses

Aircraft metadata

Airport-level delay metrics

The application enables users to explore airport networks, analyze delays, filter flights, and identify busy routes, providing meaningful operational insights through interactive dashboards.

🎯 Objectives

Extract and structure aviation data efficiently

Design a normalized SQL database schema

Write optimized SQL queries for analytics

Build an interactive, user-friendly Streamlit application

Visualize trends, delays, and route performance

Demonstrate end-to-end data analytics workflow

🏗️ Project Architecture
air_tracker/
│
├── database/
│   └── air_tracker.db          # SQLite database
│
├── data/
│   └── *.csv                   # Raw / intermediate datasets
│
├── notebooks/
│   └── *.ipynb                 # Data exploration & validation
│
├── streamlit_app/
│   ├── app.py                  # Homepage dashboard
│   ├── db.py                   # Centralized DB connection
│   └── pages/
│       ├── 1_Flights.py        # Flight search & filters
│       ├── 2_Airports.py       # Airport details + map
│       ├── 3_Delay_Analysis.py # Delay analytics
│       └── 4_Routes.py         # Route leaderboards
│
├── README.md
└── requirements.txt

🗄️ Database Design

The project uses SQLite with a normalized relational schema.

Tables Overview
airport

Stores airport master data

IATA / ICAO codes

Location (latitude, longitude)

City, country, timezone

aircraft

Stores aircraft metadata

Registration

Model

Manufacturer

ICAO type code

flights

Stores operational flight records

Flight number

Airline

Origin & destination airports

Schedule & actual times

Status and flight type

airport_delays

Stores aggregated delay metrics

Total flights

Delayed flights

Average & median delay (minutes)

Cancellations

This separation ensures data integrity, scalability, and efficient querying.

📊 Key Features
🏠 Homepage Dashboard

Total number of airports

Total flights fetched

Average delay across airports

✈️ Flight Search & Filters

Search by flight number or airline

Filter by flight status

View real-time query results

🏢 Airport Details Viewer

Airport metadata (location, timezone)

Linked inbound and outbound flights

Interactive airport selection

🌍 Airport Map Visualization

Geospatial view of airports using latitude & longitude

Visual understanding of airport distribution

⏱️ Delay Analysis

Average & median delays by airport

Delay percentage calculation

Interactive charts for comparison

📍 Route Leaderboards

Busiest routes by flight count

Most delayed airports

🧠 Technologies Used

Python – Data processing and application logic

SQLite – Lightweight relational database

SQL – Analytical queries and aggregations

Pandas – Data manipulation

Streamlit – Interactive web application

Plotly – Charts and visualizations

🚀 How to Run the Application
1️⃣ Clone the Repository
git clone <your-repo-url>
cd air_tracker

2️⃣ Install Dependencies
pip3 install -r requirements.txt

3️⃣ Run Streamlit App
cd streamlit_app
python3 -m streamlit run app.py

4️⃣ Open in Browser
http://localhost:8501

📈 Evaluation Metrics Addressed

Data Extraction Accuracy – Clean ingestion and validation

SQL Database Design – Normalized schema with relationships

Query Efficiency – Optimized aggregation queries

Application Functionality – Multi-page interactive UI

Project Completeness – End-to-end pipeline

Error Handling – Schema mismatches and path resolution handled

Innovation – Geospatial mapping and route analytics

🧪 Error Handling & Robustness

Centralized database connection using absolute paths

Safe handling of missing or null values

Streamlit page isolation to prevent app-wide crashes

Debug-friendly architecture for scalability

📌 Key Learnings

Designing analytics-focused SQL schemas

Writing efficient SQL queries for business insights

Building modular, production-grade Streamlit applications

Handling real-world issues like path resolution and schema mismatches

Translating raw data into actionable insights

🔮 Future Enhancements

Airline-level performance KPIs

Date-range filters for time-series analysis

Route visualization with origin–destination paths

API-based live data ingestion

Deployment on Streamlit Cloud

👤 Author

Jyoti Bharadwaj
B.Tech (ECE) | Data Analytics Enthusiast
Skills: SQL, Python, Pandas, Streamlit, Data Visualization

📜 License

This project is for educational and portfolio purposes.
