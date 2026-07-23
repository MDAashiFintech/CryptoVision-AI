import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import feedparser
import re
import os

# --- 1. DATA LOADING ENGINE ---
@st.cache_data
def load_all_data():
    base = "Dashboard/assets"
    df = pd.read_csv(os.path.join(base, "crypto_enriched_ohlcv_cleaned_datasets.csv"))
    df["Date"] = pd.to_datetime(df["Date"])
    rep_coins = pd.read_csv(os.path.join(base, "representative_coins.csv"))["Representative_Coin"].tolist()
    top_corr = pd.read_csv(os.path.join(base, "Correlation_Results/top_correlations.csv"))
    return {
        "main_df": df, "rep_coins": rep_coins, "all_coins": sorted(df["Coin"].unique()),
        "top_corr_df": top_corr, "latest_prices": df.groupby("Coin")["Close"].last().to_dict()
    }

@st.cache_data
def load_and_process_all_metrics():
    base = "Dashboard/assets"
    all_m = []
    for m in ["ARIMA", "PROPHET", "LSTM", "RF", "XGB"]:
        f = f"{m}_csv" if m != "RF" else "RandomForest_csv"
        p = os.path.join(base, f, "separate_coins", f"{m.lower() if m != 'RF' else 'rf'}_metrics_summary.csv")
        if os.path.exists(p):
            d = pd.read_csv(p)
            d["Model"] = m
            all_m.append(d)
    return pd.concat(all_m, ignore_index=True) if all_m else pd.DataFrame()

# --- 2. ANALYTICS FUNCTIONS ---
def get_model_leaderboard(all_metrics_df):
    avg = all_metrics_df.groupby("Model")[["MAPE", "RMSE"]].mean().sort_values("MAPE")
    return avg, f"### 🥇 Overall Winner: {avg.index[0]} (MAPE: {avg['MAPE'].iloc[0]:.2f}%)"

def plot_trend_chart(df, coin):
    c_df = df[df["Coin"] == coin]
    fig = px.line(c_df, x="Date", y="Close", title=f"Price Trend: {coin}")
    return fig, f"Analysis for {coin} complete. ATH was ${c_df['Close'].max():,.2f}."

def plot_moving_average_chart(df, coin):
    c_df = df[df["Coin"] == coin].copy()
    c_df["SMA_30"] = c_df["Close"].rolling(30).mean()
    fig = px.line(c_df, x="Date", y=["Close", "SMA_30"], title=f"30-Day Moving Average: {coin}")
    return fig, f"Current price is {'above' if c_df['Close'].iloc[-1] > c_df['SMA_30'].iloc[-1] else 'below'} the 30-day average."

def get_top_correlations(top_corr_df, coin):
    f = top_corr_df[top_corr_df["Representative"] == coin]
    pos = f[f["Type"] == "Positive"].head(4)
    neg = f[f["Type"] == "Negative"].head(4)
    res = f"**Top Correlations for {coin}:**\n\n"
    res += "**Positive:** " + ", ".join([f"{r['Coin']} ({r['Correlation']:.2f})" for _,r in pos.iterrows()])
    res += "\n\n**Negative:** " + ", ".join([f"{r['Coin']} ({r['Correlation']:.2f})" for _,r in neg.iterrows()])
    return res

def get_forecast_logic(model, coin):
    f = f"{model if model != 'RF' else 'RandomForest'}_csv"
    p = f"Dashboard/assets/{f}/separate_coins/{coin}_future_forecast.csv"
    if os.path.exists(p):
        df = pd.read_csv(p, parse_dates=["Date"])
        h = {"p": df["Predicted"].max(), "d": df.loc[df["Predicted"].idxmax(), "Date"].date()}
        l = {"p": df["Predicted"].min(), "d": df.loc[df["Predicted"].idxmin(), "Date"].date()}
        return h, l
    return None, None

def fetch_top_stories(rep_coins):
    return ["📌 Market sentiment is highly reactive to Bitcoin's price floor.", "📌 Ethereum ecosystem showing increased developer activity."]

# --- UI SECTION ---
if __name__ == "__main__":
    st.set_page_config(page_title="FAQ", page_icon="❓", layout="wide")
    st.title("❓ FAQ & Documentation")
    st.info("Use the Chatbot for interactive analysis.")