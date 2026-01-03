# ✈️ Air Tracker – Aviation Analytics Dashboard

An end-to-end Aviation Data Analytics Web Application built using Python, SQL (SQLite), and Streamlit.  
This project demonstrates the complete analytics lifecycle — from data extraction and database design to optimized SQL querying and interactive visualization.

---

## 📌 Project Overview

Air Tracker analyzes aviation operations data to provide insights into:

- Airports and their geographical distribution
- Flight operations and statuses
- Airline activity and route density
- Airport-level delay and cancellation patterns

The application enables users to explore flight data, analyze delays, visualize airport networks, and identify busy routes through a multi-page interactive dashboard.

---

## 🎯 Objectives

- Extract and structure aviation data accurately
- Design a normalized SQL database schema
- Write efficient SQL queries for analytics
- Build a multi-page Streamlit dashboard
- Visualize trends, distributions, and relationships
- Deliver a complete end-to-end analytics solution

---

## 🏗️ Project Architecture

<p align="center">
  <img src="air_tracker/assets/architecture.png" width="700">
</p>


## 🗄️ Database Design

The project uses SQLite with a normalized relational schema.

### Tables

airport  
- Airport master data  
- IATA / ICAO codes  
- City, country, continent  
- Latitude, longitude, timezone  

aircraft  
- Aircraft registration  
- Manufacturer and model  
- ICAO type code  

flights  
- Flight number  
- Airline name  
- Origin and destination airports  
- Scheduled and actual times  
- Flight status and type  

airport_delays  
- Total flights  
- Delayed flights  
- Average and median delay (minutes)  
- Cancelled flights  

This design avoids redundancy and supports efficient analytics.

---

## 📊 Application Features

### Homepage – Executive Dashboard
- Total number of airports
- Total flights fetched
- Average delay across airports
- Flight status distribution (Pie / Bar charts)
- Top airlines by flight volume

### Flights Page
- Search by airline or flight number
- Filter by flight status
- Flights table with live SQL queries
- Airline distribution and origin-airport analysis

### Airports Page
- Interactive airport map (latitude & longitude)
- Airport details viewer
- Linked inbound and outbound flights
- Airport traffic ranking charts

### Delay Analysis Page
- Average vs median delay comparison
- Delay percentage by airport
- Cancelled flights analysis
- Histograms, scatter plots, and box plots

### Routes Page
- Busiest routes by flight count
- Route traffic heatmap
- Most delayed airports

---

## 📈 Visualizations Used

- Bar charts
- Pie and donut charts
- Histograms
- Scatter plots
- Box plots
- Heatmaps
- Geospatial maps

Charts were selected based on business questions rather than using a single chart type everywhere.

---

## 🧠 Technologies Used

- Python
- SQLite and SQL
- Pandas
- Streamlit
- Plotly Express

---

## 🚀 How to Run the Application

1. Clone the repository  
git clone <repository-url>  
cd air_tracker  

2. Install dependencies  
pip install -r requirements.txt  

3. Run Streamlit app  
cd streamlit_app  
python3 -m streamlit run app.py  

4. Open in browser  
http://localhost:8501  

---

## 📦 requirements.txt

streamlit>=1.30.0  
pandas>=2.0.0  
plotly>=5.15.0  

---

## 🧪 Error Handling & Robustness

- Centralized database connection using absolute paths
- Schema validation during development
- Graceful handling of missing or null values
- Streamlit page isolation to prevent app-wide crashes

---

## 📌 Key Learnings

- Designing analytics-focused SQL schemas
- Writing optimized SQL queries for insights
- Building modular multi-page Streamlit applications
- Handling real-world issues such as schema mismatches and file paths
- Translating raw data into actionable insights

---

## 🔮 Future Enhancements

- Airline-level performance KPIs
- Date-range based trend analysis
- Route flow visualization on maps
- Live API-based data ingestion
- Deployment on Streamlit Cloud

---

## 👤 Author

Jyoti Bharadwaj  
B.Tech (ECE) | Data Analytics Enthusiast  
Skills: SQL, Python, Pandas, Streamlit, Data Visualization

---

## 📜 License

This project is for educational and portfolio purposes.
