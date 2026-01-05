# 🎬 Netflix Content Intelligence Platform

🔗 **Live App:**  
https://netflix-content-intelligence.streamlit.app/

---

## 🎯 Project Overview

The **Netflix Content Intelligence Platform** is an interactive, data-driven analytics dashboard built to explore, analyze, and evaluate movie content using real-world data from **The Movie Database (TMDB)**.

This project is designed as a **decision-support and exploration tool** for content analysts, strategists, and data enthusiasts—transforming raw entertainment data into **actionable insights** through rich visualizations, statistical analysis, and opportunity mapping.

The platform demonstrates how **data analytics, visualization, and product thinking** can be combined into a professional, end-to-end application.

---

## 🧠 What This Platform Does

The app guides users through a structured analytical journey across multiple dashboards:

| Dashboard | Purpose | Key Question Answered |
|---------|--------|----------------------|
| **Content Universe** | Market overview | What content exists and how does it perform? |
| **Performance Deep Dive** | Statistical analysis | What drives popularity and engagement? |
| **Market Opportunities** | Opportunity discovery | Where is there white space to invest? |
| **Recommendation Copilot** | Scenario testing | How might a new content profile perform? |
| **Predictive Forecasting** | Trend intuition | What patterns emerge over time? |
| **Head-to-Head Comparison** | Decision support | Which option performs better? |

Each section builds logically on the previous one, simulating how analytics supports real business decisions.

---

## 📊 Key Features

### 1️⃣ Content Universe – Market Landscape
- Explore movies by **genre, release year, popularity, and ratings**
- Identify top performers using a **composite Netflix Score**
- Visualize quality vs reach using interactive scatter plots
- Poster-based browsing for intuitive exploration

### 2️⃣ Performance Deep Dive – Analytical Insights
- Correlation analysis between popularity, votes, ratings, and engagement
- **Anomaly detection** to surface outlier titles
- Engagement proxy calculations using vote count + rating signals
- Seasonality analysis by release month

### 3️⃣ Market Opportunities – White Space Analysis
- Genre-level aggregation and normalization
- Identify **underserved vs oversaturated genres**
- Interactive market maps using performance vs volume axes
- Auto-generated **investment memos** for top opportunities

### 4️⃣ Recommendation Copilot – Scenario Simulation
- Simulate content profiles using:
  - Genre
  - Budget level
  - Release window
- Predict relative popularity and risk level
- Compare profiles against historically similar titles

### 5️⃣ Predictive Forecasting (Exploratory)
- Lightweight trend analysis by time window
- Momentum and engagement pattern exploration
- Designed as a foundation for future ML forecasting extensions

### 6️⃣ Head-to-Head Comparison
- Compare two genres or content profiles side-by-side
- Evaluate differences across performance metrics
- Designed for final decision support and presentation use

---

## 🛠️ Tech Stack

| Layer | Technology |
|-----|-----------|
| Frontend | Streamlit |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly |
| API | TMDB API |
| Styling | Custom CSS (Netflix-inspired dark theme) |
| Deployment | Streamlit Cloud |
| Version Control | GitHub |

---

## 🧮 Core Metrics & Logic

- **Netflix Score (Composite Signal)**   Netflix Score = Popularity + Vote Average + log(Vote Count)
- **Engagement Proxy**  Engagement = 0.65 × log(Votes) + 0.35 × Rating
- **Opportunity Score**
- Combines normalized performance, quality, popularity, and competition
- Penalizes oversaturated genres
- Rewards high-performance, low-volume segments

All scoring logic is **transparent and explainable**, making the app suitable for demos and interviews.

---

## 📈 Visualization Highlights

- Interactive scatter plots with anomaly highlighting
- Market quadrant bubble charts for opportunity discovery
- Correlation heatmaps
- Time-based trend lines
- Poster-based grids for intuitive browsing

Each visualization is paired with **interpretation text**, focusing on *what the data means*, not just what it shows.

---

## 🔐 API & Secrets Management

This app uses the **TMDB API**.  
The API key is stored securely using **Streamlit Secrets** and is **never committed to GitHub**.

Example secret format:
```toml
TMDB_API_KEY = "your_api_key_here"

⸻

## 🚀 How to Run Locally
# Clone the repository
git clone https://github.com/vaishrao2601/Netflix-Content-Intelligence.git
cd Netflix-Content-Intelligence

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py






Built by Vaishnavi Srinivas
Data • Analytics • Product Thinking 🎬
