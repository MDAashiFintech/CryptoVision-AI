import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import feedparser
import re
import os

# --- PAGE SETUP ---
st.set_page_config(page_title="FAQ", page_icon="❓", layout="wide")

st.title("❓ Frequently Asked Questions (FAQ)")
st.markdown("Find answers to common questions about the Crypto Analytics Hub and how to use its features.")
st.markdown("---")

# --- General Questions ---
st.header("General")

with st.expander("What is the purpose of this dashboard?"):
    st.markdown("""
        This dashboard is an all-in-one tool designed for **comprehensive cryptocurrency analysis**. It provides:
        - **Live and historical price data** for a wide range of cryptocurrencies.
        - **Exploratory Data Analysis (EDA)** to understand trends, volatility, and distributions.
        - **Advanced forecasting** using multiple machine learning models (ARIMA, LSTM, etc.).
        - **Correlation and grouping analysis** to understand how different assets move together.
        - An **interactive chatbot** to guide you through these analyses conversationally.
    """)

with st.expander("What data is being used for the analysis?"):
    st.markdown("""
        The primary dataset is a cleaned and enriched collection of **daily OHLCV (Open, High, Low, Close, Volume)** data. 
        Live price data is fetched in real-time from the CoinGecko API.
    """)

# --- Navigation Section ---
st.header("Navigating the Tools")

with st.expander("How do I use the main Dashboard?"):
    st.markdown("""
        The **Dashboard** is your main overview. It features Live Price Cards and an Explorer Tool.
    """)
    if st.button("Take me to the Dashboard", key="faq_dash_btn"):
        st.switch_page("pages/1.Dashboard.py")

with st.expander("How does the Forecast page work?"):
    st.markdown("""
        The **Forecast** page is where you can leverage the power of our machine learning models like ARIMA and LSTM.
    """)
    if st.button("Take me to the Forecast Page", key="faq_forecast_btn"):
        st.switch_page("pages/4.Forecast.py")

with st.expander("What is the 'Model Comparison' page for?"):
    st.markdown("""
        This page provides a definitive answer to the question: **"Which model is the best?"**
    """)
    if st.button("Take me to Model Comparison", key="faq_model_comp_btn"):
        st.switch_page("pages/5.Model_Comparison.py")

with st.expander("How do I use the Chatbot?"):
    st.markdown("""
        The **Chatbot** is the most interactive way to use this dashboard. Simply ask for what you need!
    """)
    if st.button("Talk to the Chatbot", key="faq_chatbot_btn"):
        st.switch_page("pages/6.Chatbot.py")

st.markdown("---")
st.info("If you have more questions, please refer to the project documentation.")

# --- FIXED DATA LOADING ENGINE (Cloud Paths) ---
@st.cache_data
def load_all_data():
    # PATH FIX: Added Dashboard/ prefix
    assets_folder = "Dashboard/assets"
    df = pd.read_csv(os.path.join(assets_folder, "crypto_enriched_ohlcv_cleaned_datasets.csv"))
    df["Date"] = pd.to_datetime(df["Date"])
    rep_df = pd.read_csv(os.path.join(assets_folder, "representative_coins.csv"))
    rep_coins = rep_df["Representative_Coin"].tolist()
    top_corr_df = pd.read_csv(os.path.join(assets_folder, "Correlation_Results/top_correlations.csv"))
    return {
        "main_df": df,
        "rep_coins": rep_coins,
        "all_coins": sorted(df["Coin"].unique()),
        "top_corr_df": top_corr_df,
        "latest_prices": df.groupby("Coin")["Close"].last().to_dict()
    }

@st.cache_data
def load_and_process_all_metrics():
    # PATH FIX: Added Dashboard/ prefix
    assets_folder = "Dashboard/assets"
    models = ["ARIMA", "PROPHET", "LSTM", "RF", "XGB"]
    all_metrics_dfs = []
    for model in models:
        folder_name = f"{model}_csv" if model != "RF" else "RandomForest_csv"
        file_name = f"{model.lower() if model != 'RF' else 'rf'}_metrics_summary.csv"
        metrics_file = os.path.join(assets_folder, folder_name, "separate_coins", file_name)
        if os.path.exists(metrics_file):
            m_df = pd.read_csv(metrics_file)
            m_df["Model"] = model
            all_metrics_dfs.append(m_df)
    return pd.concat(all_metrics_dfs, ignore_index=True) if all_metrics_dfs else pd.DataFrame()

# --- ANALYTICS HELPERS (Keep these for other pages to use) ---
def get_model_leaderboard(all_metrics_df):
    if all_metrics_df.empty: return None, "No data found."
    avg_metrics = all_metrics_df.groupby("Model")[["MAPE", "RMSE"]].mean().sort_values("MAPE")
    winner = avg_metrics.index[0]
    report = f"### 🥇 Overall Winner: The {winner} Model"
    return avg_metrics, report

def fetch_top_stories(rep_coins):
    # This remains unchanged as it uses URLs
    return ["Latest stories loading..."]