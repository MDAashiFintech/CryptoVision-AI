import numpy as np
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import seasonal_decompose

# Fix for NumPy deprecation
if not hasattr(np, "bool"):
    np.bool = bool

# --- 1. PAGE CONFIG & THEME ---
st.set_page_config(page_title="Data Insights | CryptoVision AI", layout="wide")

st.markdown("""
    <style>
    /* HIDE DEFAULT NAV */
    div[data-testid="stSidebarNav"] {display: none !important;}
    
    /* GLOBAL DARK THEME */
    .stApp { background-color: #020617; }
    [data-testid="stSidebar"] { background-color: #020617 !important; border-right: 1px solid #1e293b; }

    /* CARD STYLING */
    .stat-card {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 10px;
    }
    
    /* TITLES */
    h1, h2, h3 { color: #f8fafc !important; font-weight: 800 !important; }
    p, span, label { color: #cbd5e1 !important; }
    
    /* DATAFRAME OVERRIDE */
    .stDataFrame { border: 1px solid #334155; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. UNIFIED NAVIGATION SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding-bottom: 20px;">
            <img src="https://cdn-icons-png.flaticon.com/512/2091/2091665.png" width="70" style="filter: drop-shadow(0 0 8px #3b82f6);">
            <h2 style='color: white; margin-top: 10px; font-size: 1.5rem;'>CryptoVision</h2>
        </div>
    """, unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=["Home", "Market Terminal", "Data Insights", "Correlation & Groups", "AI Forecasting", "Model Analytics", "Chatbot", "Market News", "FAQ"],
        icons=["house", "grid-1x2", "search", "diagram-3", "graph-up", "award", "robot", "rss", "info-circle"],
        default_index=2, # Current page index
        styles={
            "container": {"background-color": "transparent"},
            "nav-link": {"color": "#cbd5e1", "font-size": "13px", "text-align": "left", "margin":"5px"},
            "nav-link-selected": {"background-color": "#2563eb", "color": "white"},
        }
    )

    if selected == "Home": st.switch_page("app.py")
    if selected == "Market Terminal": st.switch_page("pages/1.Dashboard.py")
    if selected == "Correlation & Groups": st.switch_page("pages/3.Group_&_Correlation.py")
    if selected == "AI Forecasting": st.switch_page("pages/4.Forecast.py")
    if selected == "Model Analytics": st.switch_page("pages/5.Model_Comparison.py")
    if selected == "Chatbot": st.switch_page("pages/6.Chatbot.py")
    if selected == "Market News": st.switch_page("pages/7.Top_Stories.py")
    if selected == "FAQ": st.switch_page("pages/FAQ.py")

# --- 3. DATA LOADING ---
@st.cache_data
def load_data():
    # Corrected Cloud Paths
    df = pd.read_csv("data/cleaned/crypto_dataset_cleaned.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    rep_df = pd.read_csv("data/processed/representative_coins.csv")
    return df, rep_df["Representative_Coin"].tolist()

# --- 4. ANALYSIS FUNCTIONS (Optimized for Dark Theme) ---
def plot_trend(df, coin):
    fig = px.line(df, x=df.index, y=coin, title=f"{coin} Historical Trajectory")
    fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig

def plot_price_distribution(df, coin):
    fig = px.histogram(df, x=coin, nbins=50, title=f"{coin} Distribution Analysis", color_discrete_sequence=['#3b82f6'])
    fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig

def plot_time_series_decomposition(df, coin):
    decomposition = seasonal_decompose(df[coin].dropna(), model="additive", period=30)
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.07,
                        subplot_titles=["Original", "Trend", "Seasonality", "Residuals"])
    
    fig.add_trace(go.Scatter(x=df.index, y=df[coin], name="Raw", line=dict(color="#3b82f6")), row=1, col=1)
    fig.add_trace(go.Scatter(x=decomposition.trend.index, y=decomposition.trend, name="Trend", line=dict(color="#f59e0b")), row=2, col=1)
    fig.add_trace(go.Scatter(x=decomposition.seasonal.index, y=decomposition.seasonal, name="Seasonal", line=dict(color="#10b981")), row=3, col=1)
    fig.add_trace(go.Scatter(x=decomposition.resid.index, y=decomposition.resid, name="Resid", line=dict(color="#ef4444")), row=4, col=1)
    
    fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=800, showlegend=False)
    return fig

# --- 5. MAIN UI ---
def main():
    st.markdown("<h1 style='font-size: 2.5rem;'>Data Insights Engine</h1>", unsafe_allow_html=True)
    st.caption("Quantitative Exploratory Analytics & Time-Series Decomposition")
    
    try:
        df, rep_coins = load_data()
    except Exception as e:
        st.error(f"Initialization Failed: {e}")
        return

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Selection Row
    col_sel1, col_sel2 = st.columns([1, 1])
    with col_sel1:
        coin1 = st.selectbox("Primary Asset Focus", rep_coins)
    with col_sel2:
        eda_options = [
            "Statistical Profile",
            "Time Series Decomposition",
            "Price Action & Returns",
            "Indexed Comparison"
        ]
        analysis_type = st.selectbox("Intelligence Module", eda_options)

    st.markdown("---")

    if analysis_type == "Statistical Profile":
        c1, c2 = st.columns([1, 2], gap="large")
        with c1:
            st.markdown("### 📋 Descriptive Stats")
            stats = df[coin1].describe().to_frame()
            st.dataframe(stats.style.background_gradient(cmap="Blues"), use_container_width=True)
        with c2:
            st.markdown("### 📈 Real-time Context")
            latest = df[coin1].iloc[-1]
            vol = df[coin1].pct_change().std() * np.sqrt(252)
            
            m1, m2 = st.columns(2)
            m1.metric("Latest Close", f"${latest:,.2f}")
            m2.metric("Ann. Volatility", f"{vol:.2%}")
            st.info(f"Insight: The return profile for {coin1} indicates institutional-level volatility levels.")

    elif analysis_type == "Price Action & Returns":
        t1, t2 = st.tabs(["Trend Line", "Return Distribution"])
        with t1: st.plotly_chart(plot_trend(df, coin1), use_container_width=True)
        with t2: st.plotly_chart(plot_price_distribution(df, coin1), use_container_width=True)

    elif analysis_type == "Time Series Decomposition":
        st.plotly_chart(plot_time_series_decomposition(df, coin1), use_container_width=True)

    elif analysis_type == "Indexed Comparison":
        coin2 = st.selectbox("Compare with Benchmark", [c for c in rep_coins if c != coin1])
        norm1 = df[coin1] / df[coin1].iloc[0]
        norm2 = df[coin2] / df[coin2].iloc[0]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=norm1, name=coin1, line=dict(color="#3b82f6")))
        fig.add_trace(go.Scatter(x=df.index, y=norm2, name=coin2, line=dict(color="#f59e0b", dash="dot")))
        fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', title="Normalized Performance (Base=1)")
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()