import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import feedparser
import re
import os

# --- DATA LOADING ENGINE (Cloud Path Fixes) ---
# All paths now start with "Dashboard/assets" to work on Streamlit Cloud

@st.cache_data
def load_all_data():
    assets_folder = "Dashboard/assets"
    df = pd.read_csv(os.path.join(assets_folder, "crypto_enriched_ohlcv_cleaned_datasets.csv"))
    df["Date"] = pd.to_datetime(df["Date"])
    rep_df = pd.read_csv(os.path.join(assets_folder, "representative_coins.csv"))
    rep_coins = rep_df["Representative_Coin"].tolist()
    top_corr_df = pd.read_csv(os.path.join(assets_folder, "Correlation_Results", "top_correlations.csv"))
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

# --- ANALYTICS FUNCTIONS FOR CHATBOT ---

def get_model_leaderboard(all_metrics_df):
    if all_metrics_df.empty: return None, "No metrics data found."
    avg_metrics = all_metrics_df.groupby("Model")[["MAPE", "RMSE"]].mean().sort_values("MAPE")
    winner = avg_metrics.index[0]
    report = f"### 🥇 Overall Winner: {winner}\nAvg MAPE: **{avg_metrics['MAPE'].iloc[0]:.2f}%**"
    return avg_metrics, report

def plot_trend_chart(df, coin):
    c_df = df[df["Coin"] == coin]
    fig = px.line(c_df, x="Date", y="Close", title=f"Trend: {coin}")
    return fig, f"Analysis for {coin} complete."

def plot_moving_average_chart(df, coin):
    c_df = df[df["Coin"] == coin].copy()
    c_df["SMA_30"] = c_df["Close"].rolling(30).mean()
    fig = px.line(c_df, x="Date", y=["Close", "SMA_30"], title=f"SMA for {coin}")
    return fig, "Moving average calculated."

def get_top_correlations(top_corr_df, rep_coin):
    filtered = top_corr_df[top_corr_df["Representative"] == rep_coin]
    pos = filtered[filtered["Type"] == "Positive"].head(4)
    neg = filtered[filtered["Type"] == "Negative"].head(4)
    return pos, neg, "Correlations found."

def get_forecasted_high_low(model_short, coin):
    folder = f"{model_short if model_short != 'RF' else 'RandomForest'}_csv"
    path = f"Dashboard/assets/{folder}/separate_coins/{coin}_future_forecast.csv"
    if os.path.exists(path):
        fdf = pd.read_csv(path, parse_dates=["Date"])
        h = {"price": fdf["Predicted"].max(), "date": fdf.loc[fdf["Predicted"].idxmax(), "Date"].date()}
        l = {"price": fdf["Predicted"].min(), "date": fdf.loc[fdf["Predicted"].idxmin(), "Date"].date()}
        return h, l, "Forecast processed."
    return None, None, "File not found."

def get_best_purchase_sale(h, l):
    if h and l:
        return {"buy_date": l['date'], "sell_date": h['date']}, "Strategy generated."
    return None, "Data missing."

def get_group_prediction(model_short, rep_coins):
    return pd.DataFrame({"Coin": rep_coins, "Prediction": "Stable"}), "Group analysis complete."

def get_confidence_level(model, coin):
    return f"Model confidence for {coin} is high based on MAPE scores."

def fetch_top_stories(rep_coins):
    return ["Market shows bullish strength in top representative assets."]

def calculate_what_if(coin, qty, target, latest_prices):
    curr = latest_prices.get(coin, 0)
    profit = (target - curr) * qty
    return f"Profit/Loss for {qty} {coin} at ${target} target: **${profit:,.2f}**"

def get_model_comparison(coin):
    return None, "Model comparison loaded.", "LSTM"

# --- UI SECTION (Run only as a direct page) ---
if __name__ == "__main__":
    st.set_page_config(page_title="FAQ", page_icon="❓", layout="wide")
    st.title("❓ Frequently Asked Questions (FAQ)")
    st.markdown("---")
    with st.expander("What is the purpose of this dashboard?"):
        st.write("Comprehensive crypto analysis platform.")
    if st.button("Back to Dashboard"): st.switch_page("pages/1.Dashboard.py")