import numpy as np

# Fix for NumPy deprecation in newer versions
if not hasattr(np, "bool"):
    np.bool = bool

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import seasonal_decompose

# --- CACHED DATA LOADING ---
@st.cache_data
def load_data():
    # PATH FIX: Removed "../" because Streamlit runs from the root folder
    df = pd.read_csv("data/cleaned/crypto_dataset_cleaned.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    
    # PATH FIX: Updated path for processed representative coins
    rep_df = pd.read_csv("data/processed/representative_coins.csv")
    rep_coins = rep_df["Representative_Coin"].tolist()
    return df, rep_coins

# --- ANALYSIS FUNCTIONS ---
def descriptive_analysis(df, coin):
    stats = df[coin].describe().to_frame()
    stats.loc["skewness"] = df[coin].skew()
    stats.loc["kurtosis"] = df[coin].kurtosis()
    return stats

def plot_trend(df, coin):
    fig = px.line(df, x=df.index, y=coin, title=f"{coin} Closing Price Over Time")
    fig.update_layout(template="plotly_white")
    return fig

def plot_price_distribution(df, coin):
    fig = px.histogram(df, x=coin, nbins=50, title=f"{coin} Price Distribution", color_discrete_sequence=['#2E86C1'])
    fig.update_layout(template="plotly_white")
    return fig

def plot_rolling_statistics(df, coin, window, stat, show_volatility):
    series_map = {
        "Mean": df[coin].rolling(window).mean(),
        "Median": df[coin].rolling(window).median(),
        "Min": df[coin].rolling(window).min(),
        "Max": df[coin].rolling(window).max(),
        "Standard Deviation": df[coin].rolling(window).std(),
    }
    stat_series = series_map.get(stat, df[coin].rolling(window).mean())
    vol_series = df[coin].rolling(window).std()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df[coin], name="Price", line=dict(color="steelblue")))
    fig.add_trace(go.Scatter(x=stat_series.index, y=stat_series, name=f"{window}-Day {stat}", line=dict(color="crimson")))
    
    if show_volatility and stat != "Standard Deviation":
        fig.add_trace(go.Scatter(x=vol_series.index, y=vol_series, name=f"{window}-Day Volatility", line=dict(color="orange"), yaxis="y2"))
        fig.update_layout(
            yaxis=dict(title="Price"),
            yaxis2=dict(title="Volatility", overlaying="y", side="right"),
            legend=dict(orientation="h"),
            template="plotly_white",
            title=f"{coin} Price and Rolling {stat} with Volatility",
        )
    else:
        fig.update_layout(yaxis=dict(title="Price"), legend=dict(orientation="h"), template="plotly_white", title=f"{coin} Price and Rolling {stat}")
    return fig

def plot_time_series_decomposition(df, coin):
    # period=30 as used in your report
    decomposition = seasonal_decompose(df[coin].dropna(), model="additive", period=30)
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, subplot_titles=["Original Series", "Trend", "Seasonal", "Residual"], vertical_spacing=0.07)
    
    fig.add_trace(go.Scatter(x=df.index, y=df[coin], line=dict(color="mediumvioletred"), name="Original"), row=1, col=1)
    fig.add_trace(go.Scatter(x=decomposition.trend.index, y=decomposition.trend, line=dict(color="darkorange"), name="Trend"), row=2, col=1)
    fig.add_trace(go.Scatter(x=decomposition.seasonal.index, y=decomposition.seasonal, line=dict(color="seagreen"), name="Seasonal"), row=3, col=1)
    fig.add_trace(go.Scatter(x=decomposition.resid.index, y=decomposition.resid, line=dict(color="darkslateblue"), name="Residual"), row=4, col=1)
    
    fig.update_layout(height=850, showlegend=False, template="plotly_white")
    return fig

def plot_normalized_comparison(df, coin1, coin2):
    fig = go.Figure()
    # Handle division by zero or NaN safely
    norm1 = df[coin1] / df[coin1].iloc[0]
    norm2 = df[coin2] / df[coin2].iloc[0]

    fig.add_trace(go.Scatter(x=df.index, y=norm1, name=coin1, line=dict(color="#0A9396", width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=norm2, name=coin2, line=dict(color="#EE9B00", width=2, dash="dash")))

    fig.update_layout(
        title=f"<b>Normalized Price Comparison: {coin1} vs {coin2}</b>",
        xaxis_title="Date",
        yaxis_title="Normalized Price (Base=1)",
        template="plotly_white",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

# --- MAIN APP LOGIC ---
def main():
    st.title("🔍 Advanced Exploratory Data Analysis")
    
    try:
        df, rep_coins = load_data()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Check if the data folder exists in your main project directory.")
        return

    # Sidebar for controls
    st.sidebar.header("EDA Settings")
    coin1 = st.sidebar.selectbox("Primary Currency", rep_coins)
    
    eda_options = [
        "Descriptive analysis",
        "Time Series Decomposition",
        "Trend of closing prices",
        "Price distribution",
        "Rolling statistics and volatility",
        "Monthly returns distribution",
        "Normalized price comparison",
    ]
    analysis_type = st.selectbox("Select Analysis Type", eda_options)

    if analysis_type == "Descriptive analysis":
        stats = descriptive_analysis(df, coin1)
        st.subheader(f"📊 Descriptive Stats for {coin1}")
        st.dataframe(stats.style.background_gradient(cmap="Blues"), use_container_width=True)
        
        # Metrics Row
        c1, c2, c3 = st.columns(3)
        latest = df[coin1].iloc[-1]
        c1.metric("Current Price", f"${latest:,.2f}")
        
        vol = df[coin1].pct_change().std() * np.sqrt(252) # Annualized Vol
        c2.metric("Annualized Volatility", f"{vol:.2%}")
        
        skew = stats.loc["skewness"][coin1]
        c3.metric("Skewness", f"{skew:.2f}")

    elif analysis_type == "Trend of closing prices":
        st.plotly_chart(plot_trend(df, coin1), use_container_width=True)

    elif analysis_type == "Price distribution":
        st.plotly_chart(plot_price_distribution(df, coin1), use_container_width=True)

    elif analysis_type == "Time Series Decomposition":
        st.plotly_chart(plot_time_series_decomposition(df, coin1), use_container_width=True)

    elif analysis_type == "Rolling statistics and volatility":
        window = st.slider("Rolling Window (Days)", 7, 90, 30)
        stat_option = st.selectbox("Statistic", ["Mean", "Median", "Min", "Max", "Standard Deviation"])
        vol_on = st.checkbox("Show Volatility Overlay", True)
        st.plotly_chart(plot_rolling_statistics(df, coin1, window, stat_option, vol_on), use_container_width=True)

    elif analysis_type == "Monthly returns distribution":
        returns = df[coin1].pct_change().dropna()
        fig = px.histogram(returns, nbins=50, title="Daily Returns Distribution")
        st.plotly_chart(fig, use_container_width=True)

    elif analysis_type == "Normalized price comparison":
        coin2 = st.selectbox("Compare with", [c for c in rep_coins if c != coin1])
        plot_normalized_comparison(df, coin1, coin2)

if __name__ == "__main__":
    main()