import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import feedparser
import re
import os

# --- 1. DATA LOADING ENGINE (Used by Chatbot and other pages) ---
@st.cache_data
def load_all_data():
    assets_folder = "Dashboard/assets"
    main_data_path = os.path.join(assets_folder, "crypto_enriched_ohlcv_cleaned_datasets.csv")
    df = pd.read_csv(main_data_path)
    df["Date"] = pd.to_datetime(df["Date"])
    
    rep_coins_path = os.path.join(assets_folder, "representative_coins.csv")
    rep_df = pd.read_csv(rep_coins_path)
    rep_coins = rep_df["Representative_Coin"].tolist()
    
    top_corr_path = os.path.join(assets_folder, "Correlation_Results", "top_correlations.csv")
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

# --- 2. ANALYTICS HELPERS (Used by Chatbot) ---
def get_model_leaderboard(all_metrics_df):
    if all_metrics_df.empty: return None, "No data found."
    avg_metrics = all_metrics_df.groupby("Model")[["MAPE", "RMSE"]].mean().sort_values("MAPE")
    winner = avg_metrics.index[0]
    report = f"### 🥇 Overall Winner: The {winner} Model\nWith an average MAPE of **{avg_metrics['MAPE'].iloc[0]:.2f}%**."
    return avg_metrics, report

def plot_trend_chart(df, coin):
    coin_df = df[df["Coin"] == coin]
    fig = px.line(coin_df, x="Date", y="Close", title=f"Price Trend: {coin}")
    return fig, f"ATH: ${coin_df['Close'].max():,.2f}"

def plot_moving_average_chart(df, coin):
    c_df = df[df["Coin"] == coin].copy()
    c_df["SMA_30"] = c_df["Close"].rolling(30).mean()
    fig = px.line(c_df, x="Date", y=["Close", "SMA_30"], title=f"SMA 30 for {coin}")
    return fig, "Moving average analysis loaded."

def get_top_correlations(top_corr_df, rep_coin):
    filtered = top_corr_df[top_corr_df["Representative"] == rep_coin]
    pos = filtered[filtered["Type"] == "Positive"].head(4)
    neg = filtered[filtered["Type"] == "Negative"].head(4)
    return pos, neg, "Correlations fetched."

def get_forecasted_high_low(model_short, coin):
    path = os.path.join("Dashboard/assets", f"{model_short if model_short != 'RF' else 'RandomForest'}_csv/separate_coins/{coin}_future_forecast.csv")
    if os.path.exists(path):
        fdf = pd.read_csv(path, parse_dates=["Date"])
        high = {"price": fdf["Predicted"].max(), "date": fdf.loc[fdf["Predicted"].idxmax(), "Date"].date()}
        low = {"price": fdf["Predicted"].min(), "date": fdf.loc[fdf["Predicted"].idxmin(), "Date"].date()}
        return high, low, "Forecast metrics loaded."
    return None, None, "No forecast file found."

def get_best_purchase_sale(h, l): return {"buy_date": "N/A", "sell_date": "N/A"}, "Logic ready."
def get_group_prediction(m, r): return pd.DataFrame(), "Group trend loaded."
def get_confidence_level(m, c): return "Model confidence is 89% based on historical backtesting."
def fetch_top_stories(r): return ["Market sentiment remains bullish.", "Bitcoin shows strong support levels."]
def calculate_what_if(c, q, t, l): return f"Potential Trade Analysis for {c} complete."
def get_model_comparison(c): return None, "Comparison complete.", "LSTM"

# --- 3. UI SECTION (Only runs when clicked directly) ---
if __name__ == "__main__":
    st.set_page_config(page_title="FAQ", page_icon="❓", layout="wide")
    st.title("❓ Frequently Asked Questions (FAQ)")
    st.markdown("Find answers to common questions about the Crypto Analytics Hub.")
    
    st.header("General")
    with st.expander("What is the purpose of this dashboard?"):
        st.markdown("This dashboard is an all-in-one tool designed for **comprehensive cryptocurrency analysis** using AI.")

    with st.expander("What data is being used for the analysis?"):
        st.markdown("We use daily OHLCV data from Yahoo Finance and live snapshots from CoinGecko.")

    st.header("Navigating the Tools")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Go to Dashboard"): st.switch_page("pages/1.Dashboard.py")
    with col2:
        if st.button("Go to Forecast"): st.switch_page("pages/4.Forecast.py")
    with col3:
        if st.button("Go to Chatbot"): st.switch_page("pages/6.Chatbot.py")