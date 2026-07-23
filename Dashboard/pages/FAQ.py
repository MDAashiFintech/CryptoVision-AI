import streamlit as st
from utils import load_all_data

# --- PAGE SETUP ---
st.set_page_config(page_title="FAQ", page_icon="❓", layout="wide")

st.title("❓ Frequently Asked Questions (FAQ)")
st.markdown("Find answers to common questions about the Crypto Analytics Hub and how to use its features.")
st.markdown("---")

# --- 1. General Questions ---
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
        The primary dataset is a cleaned and enriched collection of **daily OHLCV (Open, High, Low, Close, Volume)** data for numerous cryptocurrencies. Live price data is fetched in real-time from the CoinGecko API to provide the most current market snapshot.
    """)

# --- 2. Page-Specific Questions with Navigation ---
st.header("Navigating the Tools")

with st.expander("How do I use the main Dashboard?"):
    st.markdown("""
        The **Dashboard** is your main overview of the crypto market. It features:
        1.  **Live Price Cards** for key representative cryptocurrencies.
        2.  An **Explorer Tool** where you can select any coin and view various charts like price trends, volume, and candlestick patterns.
        3.  A **Price Performance** panel showing key metrics like 52-week highs/lows and all-time highs/lows.
        
        It's the best place to get a quick, at-a-glance view of the market.
    """)
    if st.button("Take me to the Dashboard", key="faq_dash_btn"):
        st.switch_page("pages/1.Dashboard.py")

with st.expander("How does the Forecast page work?"):
    st.markdown("""
        The **Forecast** page is where you can leverage the power of our machine learning models.
        1.  Use the **sidebar controls** to select a forecasting model (e.g., ARIMA, LSTM).
        2.  Choose a specific cryptocurrency you want to predict.
        3.  The page will display:
            - **Predicted High & Low prices** for the next 30 days.
            - An **interactive chart** comparing historical actuals vs. predictions.
            - **Key Performance Indicators (KPIs)** summarizing the model's accuracy and trading signals.
            - A **"What-If" calculator** to simulate hypothetical trades.
    """)
    if st.button("Take me to the Forecast Page", key="faq_forecast_btn"):
        st.switch_page("pages/4.Forecast.py")

with st.expander("What is the 'Model Comparison' page for?"):
    st.markdown("""
        This page provides a definitive answer to the question: **"Which model is the best?"**
        
        It analyzes the historical performance (MAPE, RMSE) of all our models (ARIMA, LSTM, RF, XGB, Prophet) and presents:
        1.  An **Overall Leaderboard** declaring the best model on average across all coins.
        2.  A **Deep Dive** section where you can select a specific coin and see which model performed best for it.
        
        Use this page to make data-driven decisions about which model to trust for your forecasts.
    """)
    if st.button("Take me to Model Comparison", key="faq_model_comp_btn"):
        st.switch_page("pages/5.Model_Comparison.py")

with st.expander("How do I use the Chatbot?"):
    st.markdown("""
        The **Chatbot** is the most interactive way to use this dashboard. Instead of clicking through menus, you can simply ask for what you need.
        
        1.  Start by clicking one of the main category buttons (e.g., "Find Correlations").
        2.  The bot will then ask you for the necessary inputs (like which coin to analyze).
        3.  After an analysis, the bot will remember the context and suggest intelligent **follow-up questions**.
        
        It's designed to feel like you're talking to a real financial analyst!
    """)
    if st.button("Talk to the Chatbot", key="faq_chatbot_btn"):
        st.switch_page("pages/6.Chatbot.py")

st.markdown("---")
st.info("If you have more questions, please refer to the project documentation.")