import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pages.FAQ import load_and_process_all_metrics, load_all_data
import os

st.set_page_config(page_title="Model Comparison", page_icon="🏆", layout="wide")

st.title("🏆 Model Performance Comparison")
st.markdown("An objective look at which AI architecture performed best.")

# --- Load Data ---
try:
    all_metrics_df = load_and_process_all_metrics()
    data_dict = load_all_data()
    rep_coins = data_dict["rep_coins"]
except Exception as e:
    st.error(f"Failed to load metrics. Ensure assets are in 'Dashboard/assets/'. Error: {e}")
    st.stop()

# --- Section 1: The Leaderboard ---
st.header("🥇 Overall Model Leaderboard")
if not all_metrics_df.empty:
    avg_metrics = all_metrics_df.groupby("Model")[["MAPE", "RMSE", "MAE"]].mean().sort_values("MAPE")
    winner = avg_metrics.index[0]
    st.success(f"**Overall Winner: The {winner} Model** with {avg_metrics['MAPE'].iloc[0]:.2f}% MAPE")
    
    st.dataframe(avg_metrics.style.background_gradient(cmap="Greens_r"), use_container_width=True)

# --- Section 2: Deep Dive ---
st.header("🔍 Deep Dive by Cryptocurrency")
selected_coin = st.selectbox("Select Coin:", options=rep_coins)

if selected_coin:
    st.subheader(f"Visual Comparison for {selected_coin}")
    fig = go.Figure()
    actual_added = False

    for model in ["ARIMA", "PROPHET", "LSTM", "RF", "XGB"]:
        folder = f"{model}_csv" if model != "RF" else "RandomForest_csv"
        # CLOUD PATH FIX
        test_file = os.path.join("Dashboard", "assets", folder, "separate_coins", f"{selected_coin}_test_forecast.csv")

        if os.path.exists(test_file):
            test_df = pd.read_csv(test_file, parse_dates=["Date"])
            if not actual_added:
                fig.add_trace(go.Scatter(x=test_df["Date"], y=test_df["Actual"], name="Actual Price", line=dict(color="black", width=2.5)))
                actual_added = True
            fig.add_trace(go.Scatter(x=test_df["Date"], y=test_df["Predicted"], name=f"{model} Pred", line=dict(dash="dot")))

    st.plotly_chart(fig, use_container_width=True)