import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import seasonal_decompose
import feedparser
import re
import os

st.set_page_config(page_title="FAQ", page_icon="❓", layout="wide")

st.title("❓ Frequently Asked Questions (FAQ)")
st.markdown(
    "Find answers to common questions about the Crypto Analytics Hub and how to use its features."
)

st.markdown("---")

# --- General Questions ---
st.header("General")

with st.expander("What is the purpose of this dashboard?"):
    st.markdown(
        """
        This dashboard is an all-in-one tool designed for **comprehensive cryptocurrency analysis**. It provides:
        - **Live and historical price data** for a wide range of cryptocurrencies.
        - **Exploratory Data Analysis (EDA)** to understand trends, volatility, and distributions.
        - **Advanced forecasting** using multiple machine learning models (ARIMA, LSTM, etc.).
        - **Correlation and grouping analysis** to understand how different assets move together.
        - An **interactive chatbot** to guide you through these analyses conversationally.
    """
    )

with st.expander("What data is being used for the analysis?"):
    st.markdown(
        """
        The primary dataset is a cleaned and enriched collection of **daily OHLCV (Open, High, Low, Close, Volume)** data for numerous cryptocurrencies. Live price data is fetched in real-time from the CoinGecko API to provide the most current market snapshot.
    """
    )

# --- Page-Specific Questions with Navigation ---
st.header("Navigating the Tools")

with st.expander("How do I use the main Dashboard?"):
    st.markdown(
        """
        The **Dashboard** is your main overview of the crypto market. It features:
        1.  **Live Price Cards** for key representative cryptocurrencies.
        2.  An **Explorer Tool** where you can select any coin and view various charts like price trends, volume, and candlestick patterns.
        3.  A **Price Performance** panel showing key metrics like 52-week highs/lows and all-time highs/lows.
        
        It's the best place to get a quick, at-a-glance view of the market.
    """
    )
    if st.button("Take me to the Dashboard", key="faq_dash_btn"):
        # IMPORTANT: The path must be relative to the root 'Dashboard' directory.
        # Ensure your Dashboard page file is named '1_📊_Dashboard.py' or update the path.
        st.switch_page("pages/1.Dashboard.py")

with st.expander("How does the Forecast page work?"):
    st.markdown(
        """
        The **Forecast** page is where you can leverage the power of our machine learning models.
        1.  Use the **sidebar controls** to select a forecasting model (e.g., ARIMA, LSTM).
        2.  Choose a specific cryptocurrency you want to predict.
        3.  The page will display:
            - **Predicted High & Low prices** for the next 30 days.
            - An **interactive chart** comparing historical actuals vs. predictions.
            - **Key Performance Indicators (KPIs)** summarizing the model's accuracy and trading signals.
            - A **"What-If" calculator** to simulate hypothetical trades.
    """
    )
    if st.button("Take me to the Forecast Page", key="faq_forecast_btn"):
        st.switch_page(
            "pages/3.Forecast.py"
        )  # Assumes your Forecast page is named this

with st.expander("What is the 'Model Comparison' page for?"):
    st.markdown(
        """
        This page provides a definitive answer to the question: **"Which model is the best?"**
        
        It analyzes the historical performance (MAPE, RMSE) of all our models (ARIMA, LSTM, RF, XGB, Prophet) and presents:
        1.  An **Overall Leaderboard** declaring the best model on average across all coins.
        2.  A **Deep Dive** section where you can select a specific coin and see which model performed best for it.
        
        Use this page to make data-driven decisions about which model to trust for your forecasts.
    """
    )
    if st.button("Take me to Model Comparison", key="faq_model_comp_btn"):
        st.switch_page(
            "pages/5.Model_Comparison.py"
        )  # Assumes your comparison page is named this

with st.expander("How do I use the Chatbot?"):
    st.markdown(
        """
        The **Chatbot** is the most interactive way to use this dashboard. Instead of clicking through menus, you can simply ask for what you need.
        
        1.  Start by clicking one of the main category buttons (e.g., "Find Correlations").
        2.  The bot will then ask you for the necessary inputs (like which coin to analyze).
        3.  After an analysis, the bot will remember the context and suggest intelligent **follow-up questions**.
        
        It's designed to feel like you're talking to a real financial analyst!
    """
    )
    if st.button("Talk to the Chatbot", key="faq_chatbot_btn"):
        st.switch_page("pages/6.Chatbot.py")  # Assumes your chatbot is named this

st.markdown("---")
st.info("If you have more questions, please refer to the project documentation.")


# --- Unified Data Loading ---
@st.cache_data
def load_all_data():
    assets_folder = "assets"
    main_data_path = os.path.join(
        assets_folder, "crypto_enriched_ohlcv_cleaned_datasets.csv"
    )
    df = pd.read_csv(main_data_path)
    df["Date"] = pd.to_datetime(df["Date"])
    rep_coins_path = os.path.join(assets_folder, "representative_coins.csv")
    rep_df = pd.read_csv(rep_coins_path)
    rep_coins = rep_df["Representative_Coin"].tolist()
    top_corr_path = os.path.join(
        assets_folder, "Correlation_Results", "top_correlations.csv"
    )
    top_corr_df = pd.read_csv(top_corr_path)
    all_coins_list = sorted(df["Coin"].unique())
    latest_prices = df.groupby("Coin")["Close"].last().to_dict()
    return {
        "main_df": df,
        "rep_coins": rep_coins,
        "all_coins": all_coins_list,
        "top_corr_df": top_corr_df,
        "latest_prices": latest_prices,
    }


@st.cache_data
def load_and_process_all_metrics():
    assets_folder, models = "assets", ["ARIMA", "PROPHET", "LSTM", "RF", "XGB"]
    all_metrics_dfs = []
    for model in models:
        folder_name = f"{model}_csv" if model != "RF" else "RandomForest_csv"
        file_name = f"{model.lower()}_metrics_summary.csv"
        metrics_file = os.path.join(
            assets_folder, folder_name, "separate_coins", file_name
        )
        if os.path.exists(metrics_file):
            try:
                metrics_df = pd.read_csv(metrics_file)
                metrics_df["Model"] = model
                all_metrics_dfs.append(metrics_df)
            except Exception as e:
                print(f"Could not process metrics file: {metrics_file}. Error: {e}")
    if not all_metrics_dfs:
        return pd.DataFrame()
    combined_df = pd.concat(all_metrics_dfs, ignore_index=True)
    for col in ["RMSE", "MAE", "MAPE", "R2"]:
        if col in combined_df.columns:
            combined_df[col] = pd.to_numeric(combined_df[col], errors="coerce")
    return combined_df


# --- NEW FUNCTION FOR THE LEADERBOARD ---
def get_model_leaderboard(all_metrics_df):
    if all_metrics_df.empty:
        return None, "No metrics data was found to generate a leaderboard."

    avg_metrics = (
        all_metrics_df.groupby("Model")[["MAPE", "RMSE"]].mean().sort_values("MAPE")
    )
    winner = avg_metrics.index[0]
    winner_mape = avg_metrics["MAPE"].iloc[0]

    report = f"### 🥇 Overall Model Leaderboard\nBased on the average **MAPE** (Mean Absolute Percentage Error) across all coins, the winner is...\n\n"
    report += f"## **The {winner} Model!**\nWith an average error of only **{winner_mape:.2f}%**, it stands out as the most consistently accurate model."

    return avg_metrics, report


# --- ALL OTHER FUNCTIONS FROM PREVIOUS STEP ARE INCLUDED BELOW ---
# (The code is identical, just included here for completeness)
def plot_trend_chart(df, coin):
    coin_df = df[df["Coin"] == coin]
    fig = px.line(coin_df, x="Date", y="Close", title=f"Price Trend for {coin}")
    ath_price, ath_date = (
        coin_df["Close"].max(),
        coin_df["Date"][coin_df["Close"].idxmax()],
    )
    atl_price, atl_date = (
        coin_df["Close"].min(),
        coin_df["Date"][coin_df["Close"].idxmin()],
    )
    fig.add_annotation(
        x=ath_date,
        y=ath_price,
        text=f"ATH: ${ath_price:,.2f}",
        showarrow=True,
        arrowhead=1,
        ax=0,
        ay=-40,
        bgcolor="rgba(40,167,69,0.8)",
        font=dict(color="white"),
    )
    fig.add_annotation(
        x=atl_date,
        y=atl_price,
        text=f"ATL: ${atl_price:,.2f}",
        showarrow=True,
        arrowhead=1,
        ax=0,
        ay=40,
        bgcolor="rgba(220,53,69,0.8)",
        font=dict(color="white"),
    )
    change_30d = (
        (coin_df["Close"].iloc[-1] / coin_df["Close"].iloc[-31] - 1) * 100
        if len(coin_df) > 30
        else None
    )
    insight = (
        f"The All-Time High for {coin} was ${ath_price:,.2f}. Over the last 30 days of available data, the price has changed by {change_30d:.2f}%."
        if change_30d
        else f"The All-Time High for {coin} was ${ath_price:,.2f}."
    )
    return fig, insight


def plot_moving_average_chart(df, coin):
    coin_df = df[df["Coin"] == coin].copy()
    coin_df["SMA_30"] = coin_df["Close"].rolling(30).mean()
    coin_df["SMA_90"] = coin_df["Close"].rolling(90).mean()
    latest_price, latest_sma30 = coin_df["Close"].iloc[-1], coin_df["SMA_30"].iloc[-1]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=coin_df["Date"], y=coin_df["Close"], mode="lines", name="Price")
    )
    fig.add_trace(
        go.Scatter(
            x=coin_df["Date"],
            y=coin_df["SMA_30"],
            mode="lines",
            name="30-Day SMA",
            line=dict(color="orange"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=coin_df["Date"],
            y=coin_df["SMA_90"],
            mode="lines",
            name="90-Day SMA",
            line=dict(color="purple", dash="dot"),
        )
    )
    fig.update_layout(
        title=f"Moving Averages for {coin}",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    insight = f"Insight: The current price of ${latest_price:,.2f} is **{'above' if latest_price > latest_sma30 else 'below'}** its 30-day moving average (${latest_sma30:,.2f}), which can be a {'bullish' if latest_price > latest_sma30 else 'bearish'} signal."
    return fig, insight


def get_top_correlations(top_corr_df, rep_coin):
    filtered = top_corr_df[top_corr_df["Representative"] == rep_coin]
    positive, negative = filtered[filtered["Type"] == "Positive"].head(4), filtered[
        filtered["Type"] == "Negative"
    ].head(4)
    if not positive.empty:
        top_pos_coin, top_pos_val = (
            positive["Coin"].iloc[0],
            positive["Correlation"].iloc[0],
        )
        insight = f"Insight: {rep_coin} shows a strong positive correlation with **{top_pos_coin}** ({top_pos_val:.2f}), suggesting they often move in the same direction."
    else:
        insight = "No significant positive correlations found."
    return positive, negative, insight


def get_forecasted_high_low(model_short, coin):
    assets_folder = "assets"
    folder_name = f"{model_short}_csv" if model_short != "RF" else "RandomForest_csv"
    base_path = os.path.join(assets_folder, folder_name, "separate_coins")
    future_file = os.path.join(base_path, f"{coin}_future_forecast.csv")
    if not os.path.exists(future_file):
        return None, None, None
    future_df = pd.read_csv(future_file, parse_dates=["Date"])
    high_idx, low_idx = future_df["Predicted"].idxmax(), future_df["Predicted"].idxmin()
    high_info = {
        "date": future_df.loc[high_idx, "Date"].date(),
        "price": future_df.loc[high_idx, "Predicted"],
    }
    low_info = {
        "date": future_df.loc[low_idx, "Date"].date(),
        "price": future_df.loc[low_idx, "Predicted"],
    }
    spread = (high_info["price"] - low_info["price"]) / low_info["price"] * 100
    insight = f"Insight: The model predicts a **{spread:.2f}%** price range between the future low and high, indicating its volatility forecast."
    return high_info, low_info, insight


def get_best_purchase_sale(high_info, low_info):
    if not high_info or not low_info:
        return None, None
    if high_info["date"] > low_info["date"]:
        profit = high_info["price"] - low_info["price"]
        suggestion = {
            "buy_date": low_info["date"],
            "buy_price": low_info["price"],
            "sell_date": high_info["date"],
            "sell_price": high_info["price"],
            "profit_per_coin": profit,
        }
        insight = f"Insight: This strategy yields a potential profit of **${profit:,.2f} per coin**, based on the model's forecast."
        return suggestion, insight
    else:
        suggestion = "The predicted high occurs before the predicted low, suggesting a downward trend where a simple buy-low-sell-high strategy is not profitable in this forecast period."
        insight = "Insight: The model predicts a bearish trend for the forecast period, as the lowest point comes after the highest point."
        return suggestion, insight


def get_group_prediction(model_short, rep_coins):
    coin_trends, assets_folder = [], "assets"
    folder_name = f"{model_short}_csv" if model_short != "RF" else "RandomForest_csv"
    trend_base_path = os.path.join(assets_folder, folder_name, "separate_coins")
    if not os.path.exists(trend_base_path):
        return pd.DataFrame(), None
    for rep_coin in rep_coins:
        ffile = os.path.join(trend_base_path, f"{rep_coin}_future_forecast.csv")
        try:
            fdf = pd.read_csv(ffile, parse_dates=["Date"])
            if len(fdf) >= 30:
                p_start, p_end = fdf.loc[0, "Predicted"], fdf.loc[29, "Predicted"]
                state = "Up" if p_end > p_start else "Down"
                coin_trends.append({"Coin": rep_coin, "30-Day Prediction": state})
        except Exception:
            coin_trends.append({"Coin": rep_coin, "30-Day Prediction": "No Data"})
    df = pd.DataFrame(coin_trends)
    num_up = (df["30-Day Prediction"] == "Up").sum()
    total = len(df)
    insight = f"Insight: The overall market state appears {'Bullish' if num_up > total/2 else 'Bearish'}, with **{num_up} out of {total}** representative coins predicted to rise."
    return df, insight


def calculate_what_if(coin, quantity, target_price, latest_prices):
    current_price = latest_prices.get(coin)
    if current_price is None:
        return "Could not retrieve the latest price for this coin."
    profit = (target_price - current_price) * quantity
    return f"Based on a current price of **${current_price:,.2f}** for {coin}, a hypothetical trade of **{quantity}** coins to a target of **${target_price:,.2f}** would result in a potential profit/loss of **${profit:,.2f}**."


def get_model_comparison(coin):
    all_metrics_df = load_and_process_all_metrics()
    if all_metrics_df.empty:
        return None, "No performance metrics found."

    coin_metrics_df = all_metrics_df[all_metrics_df["Coin"] == coin].set_index("Model")
    if coin_metrics_df.empty:
        return None, f"No performance metrics found for {coin}."

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("MAPE (%) - Lower is Better", "RMSE - Lower is Better"),
    )
    fig.add_trace(
        go.Bar(x=coin_metrics_df.index, y=coin_metrics_df["MAPE"], name="MAPE"),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(x=coin_metrics_df.index, y=coin_metrics_df["RMSE"], name="RMSE"),
        row=1,
        col=2,
    )
    fig.update_layout(
        title_text=f"Model Performance Comparison for {coin}", showlegend=False
    )

    best_mape_model = coin_metrics_df["MAPE"].idxmin()
    insight = f"Insight: For **{coin}**, the **{best_mape_model}** model appears to be the most accurate, as it has the lowest MAPE (Mean Absolute Percentage Error)."
    return fig, insight, best_mape_model


def get_confidence_level(model_short, coin):
    all_metrics_df = load_and_process_all_metrics()
    if all_metrics_df.empty:
        return "Metrics data could not be loaded."

    model_metrics = all_metrics_df[
        (all_metrics_df["Model"] == model_short) & (all_metrics_df["Coin"] == coin)
    ]
    if not model_metrics.empty:
        mape = model_metrics.iloc[0].get("MAPE")
        if pd.notna(mape):
            accuracy = 100 - mape
            return f"The **{model_short}** model's average accuracy for **{coin}** is **{accuracy:.2f}%** (based on a MAPE of {mape:.2f}%)."
    return f"Confidence level data not found for {coin} with the {model_short} model."


def fetch_top_stories(rep_coins):
    rss_urls = [
        "https://cryptonews.com/news/feed",
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://news.bitcoin.com/feed/",
    ]
    filter_coins = [c.split("-")[0].upper() for c in rep_coins]
    entries = []
    for url in rss_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            combined_text = (entry.title + " " + entry.get("summary", "")).upper()
            if any(coin in combined_text for coin in filter_coins):
                summary = re.sub(r"<[^>]+>", "", entry.get("summary", ""))
                summary = re.sub(
                    r"The post .+? appeared first on .+", "", summary
                ).strip()
                summary = (summary[:150] + "...") if len(summary) > 150 else summary
                entries.append(
                    f"**{entry.title}**: {summary} [Read More]({entry.link})"
                )
    return entries[:5]
