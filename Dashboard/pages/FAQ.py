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

# PATH CONSTANTS
BASE_DASHBOARD = "Dashboard"
ASSETS_PATH = os.path.join(BASE_DASHBOARD, "assets")
DATA_PATH = "data"

st.title("❓ Frequently Asked Questions (FAQ)")
st.markdown("Find answers to common questions about the Crypto Analytics Hub.")

# --- NAVIGATION TABS ---
st.header("General & Navigating the Tools")
with st.expander("What is the purpose of this dashboard?"):
    st.write("This dashboard is an all-in-one tool designed for comprehensive cryptocurrency analysis using AI.")

# --- DATA LOADING FUNCTIONS (Used by other pages) ---
@st.cache_data
def load_all_data():
    main_data_path = os.path.join(ASSETS_PATH, "crypto_enriched_ohlcv_cleaned_datasets.csv")
    df = pd.read_csv(main_data_path)
    df["Date"] = pd.to_datetime(df["Date"])
    
    rep_df = pd.read_csv(os.path.join(ASSETS_PATH, "representative_coins.csv"))
    rep_coins = rep_df["Representative_Coin"].tolist()
    
    top_corr_path = os.path.join(ASSETS_PATH, "Correlation_Results", "top_correlations.csv")
    top_corr_df = pd.read_csv(top_corr_path)
    
    return {
        "main_df": df,
        "rep_coins": rep_coins,
        "all_coins": sorted(df["Coin"].unique()),
        "top_corr_df": top_corr_df,
        "latest_prices": df.groupby("Coin")["Close"].last().to_dict()
    }

@st.cache_data
def load_and_process_all_metrics():
    models = ["ARIMA", "PROPHET", "LSTM", "RF", "XGB"]
    all_metrics_dfs = []
    for model in models:
        folder_name = f"{model}_csv" if model != "RF" else "RandomForest_csv"
        file_name = f"{model.lower() if model != 'RF' else 'rf'}_metrics_summary.csv"
        metrics_file = os.path.join(ASSETS_PATH, folder_name, "separate_coins", file_name)
        
        if os.path.exists(metrics_file):
            m_df = pd.read_csv(metrics_file)
            m_df["Model"] = model
            all_metrics_dfs.append(m_df)
    
    if not all_metrics_dfs:
        return pd.DataFrame()
    return pd.concat(all_metrics_dfs, ignore_index=True)

# --- ANALYTICS HELPER FUNCTIONS ---
def get_model_leaderboard(all_metrics_df):
    if all_metrics_df.empty: return None, "No metrics data found."
    avg_metrics = all_metrics_df.groupby("Model")[["MAPE", "RMSE"]].mean().sort_values("MAPE")
    winner = avg_metrics.index[0]
    report = f"### 🥇 Overall Winner: The {winner} Model!"
    return avg_metrics, report

def plot_trend_chart(df, coin):
    coin_df = df[df["Coin"] == coin]
    fig = px.line(coin_df, x="Date", y="Close", title=f"Price Trend for {coin}")
    return fig, f"ATH: ${coin_df['Close'].max():,.2f}"

# (Keep your other helper functions like calculate_what_if, fetch_top_stories, etc.)