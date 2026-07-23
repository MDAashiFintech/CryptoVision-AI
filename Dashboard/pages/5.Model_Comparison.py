# pages/2_🏆_Model_Comparison.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pages.FAQ import load_and_process_all_metrics, load_all_data
import os

st.set_page_config(page_title="Model Comparison", page_icon="🏆", layout="wide")

st.title("🏆 Model Performance Comparison")
st.markdown(
    "An objective, data-driven look at which forecasting model performed best across various metrics and cryptocurrencies."
)

# --- Load Data ---
try:
    all_metrics_df = load_and_process_all_metrics()
    data_dict = load_all_data()
    rep_coins = data_dict["rep_coins"]
except Exception as e:
    st.error(
        f"Failed to load necessary data. Please check your `assets` folder and file structures. Error: {e}"
    )
    st.stop()

if all_metrics_df.empty:
    st.error(
        "No model metrics could be loaded. Please ensure your `assets` folder contains the correct `_metrics_summary.csv` files for each model."
    )
    st.stop()

# --- Section 1: The Leaderboard ---
st.header("🥇 Overall Model Leaderboard")
st.markdown(
    "Models are ranked by their average **MAPE (Mean Absolute Percentage Error)** across all representative coins. **Lower is better.**"
)

# Calculate average metrics
avg_metrics = (
    all_metrics_df.groupby("Model")[["MAPE", "RMSE", "MAE"]].mean().sort_values("MAPE")
)
winner = avg_metrics.index[0]
winner_mape = avg_metrics["MAPE"].iloc[0]

# Display the winner prominently
st.success(f"**Overall Winner: The {winner} Model**")
st.markdown(
    f"The **{winner}** model achieved the lowest average prediction error with a MAPE of **{winner_mape:.2f}%**, making it the most consistently accurate model across the board."
)

# Display top 3 as KPI cards
st.subheader("Top 3 Performers")
cols = st.columns(3)
colors = ["#FFD700", "#C0C0C0", "#CD7F32"]  # Gold, Silver, Bronze

for i in range(min(3, len(avg_metrics))):
    model_name = avg_metrics.index[i]
    mape_val = avg_metrics["MAPE"].iloc[i]
    with cols[i]:
        st.markdown(
            f"""
            <div style="border: 2px solid {colors[i]}; border-radius: 10px; padding: 20px; text-align: center;">
                <h3 style="margin: 0; color: {colors[i]};">#{i+1} {model_name}</h3>
                <p style="font-size: 1.2em; margin-top: 10px;">Avg. MAPE: <strong>{mape_val:.2f}%</strong></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Display the full leaderboard table
st.subheader("Full Leaderboard Details")
st.dataframe(
    avg_metrics.style.background_gradient(cmap="Greens_r", subset=["MAPE"]).format(
        "{:.2f}"
    )
)

st.markdown("---")

# --- Section 2: Deep Dive by Cryptocurrency ---
st.header("🔍 Deep Dive by Cryptocurrency")
selected_coin = st.selectbox(
    "Select a Representative Coin to analyze model performance:", options=rep_coins
)

if selected_coin:
    coin_metrics_df = all_metrics_df[all_metrics_df["Coin"] == selected_coin].set_index(
        "Model"
    )

    st.subheader(f"Performance Metrics for {selected_coin}")
    st.dataframe(
        coin_metrics_df[["RMSE", "MAE", "MAPE", "R2"]]
        .style.background_gradient(cmap="Greens_r", subset=["MAPE"])
        .format("{:.2f}")
    )

    # --- Visual Forecast Comparison Chart ---
    st.subheader(f"Visual Forecast Comparison on Test Data for {selected_coin}")

    with st.spinner(f"Loading all model forecasts for {selected_coin}..."):
        fig = go.Figure()
        actual_added = False

        for model in ["ARIMA", "PROPHET", "LSTM", "RF", "XGB"]:
            folder_name = f"{model}_csv" if model != "RF" else "RandomForest_csv"
            test_file = os.path.join(
                "assets",
                folder_name,
                "separate_coins",
                f"{selected_coin}_test_forecast.csv",
            )

            if os.path.exists(test_file):
                test_df = pd.read_csv(test_file, parse_dates=["Date"])
                if not actual_added and "Actual" in test_df.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=test_df["Date"],
                            y=test_df["Actual"],
                            mode="lines",
                            name="Actual Price",
                            line=dict(color="black", width=3),
                        )
                    )
                    actual_added = True

                if "Predicted" in test_df.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=test_df["Date"],
                            y=test_df["Predicted"],
                            mode="lines",
                            name=f"{model} Predicted",
                            line=dict(dash="dot"),
                        )
                    )

        if not actual_added:
            st.warning(
                "Could not load any forecast data to display the visual comparison chart."
            )
        else:
            fig.update_layout(
                title=f"Actual vs. Predicted Prices from All Models for {selected_coin}",
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                legend_title="Models",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.info(
                "This chart plots the test data predictions from all available models against the actual price. The line that 'hugs' the black 'Actual Price' line most closely is the best performer."
            )

st.markdown("---")

# --- Section 3: Metric-by-Metric Breakdown ---
with st.expander("📊 See Metric-by-Metric Breakdown Across All Coins"):
    metric_to_compare = st.selectbox(
        "Select a metric to compare:", ["MAPE", "RMSE", "MAE", "R2"]
    )

    fig = px.bar(
        all_metrics_df,
        x="Coin",
        y=metric_to_compare,
        color="Model",
        barmode="group",
        title=f"Model Comparison for {metric_to_compare}",
        labels={"value": metric_to_compare, "Coin": "Cryptocurrency"},
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- Section 4: Final Verdict ---
st.header("📜 Final Verdict")
st.info(
    f"""
    Based on a comprehensive analysis of all performance metrics, the **{winner} model** stands out as the **overall best performer** for this forecasting task. 
    
    - It demonstrated the **lowest average error rates (MAPE)**, indicating the highest predictive accuracy across the entire set of representative cryptocurrencies.
    - While performance for individual coins can vary (as seen in the 'Deep Dive' section), the **{winner} model** provides the most reliable and robust starting point for forecasting.
    
    For any serious trading strategy, it is recommended to consult the 'Deep Dive' section to confirm the best-performing model for the specific cryptocurrency of interest.
    """
)
