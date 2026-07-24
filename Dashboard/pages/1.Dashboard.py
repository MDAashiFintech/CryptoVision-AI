import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- 1. PAGE CONFIG & GLOBAL THEME ---
st.set_page_config(page_title="Market Terminal | CryptoVision AI", layout="wide")

st.markdown("""
    <style>
    /* HIDE DEFAULT NAV */
    div[data-testid="stSidebarNav"] {display: none !important;}
    
    /* GLOBAL DARK THEME */
    .stApp { background-color: #020617; }
    [data-testid="stSidebar"] { background-color: #020617 !important; border-right: 1px solid #1e293b; }

    /* CARD STYLING */
    .m-card {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 25px;
        border-radius: 18px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .m-card:hover { border-color: #3b82f6; transform: translateY(-3px); }
    
    /* TITLES */
    h1, h2, h3 { color: #f8fafc !important; font-weight: 800 !important; }
    p, span, label { color: #cbd5e1 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. THE UNIFIED NAVIGATION SIDEBAR (Fixed with 9 items) ---
# --- THE PERMANENT NAVIGATION FIX ---
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
        # Change default_index for each page: Home=0, Dashboard=1, EDA=2, Group&Corr=3, etc.
        default_index=1, 
        styles={
            "container": {"background-color": "transparent"},
            "nav-link": {"color": "#cbd5e1", "font-size": "13px", "text-align": "left", "margin":"5px"},
            "nav-link-selected": {"background-color": "#2563eb", "color": "white"},
        }
    )

    # EXACT PATH LOGIC (Do not change filenames)
    if selected == "Home":
        st.switch_page("app.py")
    elif selected == "Market Terminal":
        st.switch_page("pages/1.Dashboard.py")
    elif selected == "Data Insights":
        st.switch_page("pages/2.EDA.py")
    elif selected == "Correlation & Groups":
        st.switch_page("pages/3.Correlation.py") # Ensure this matches the file name EXACTLY
    elif selected == "AI Forecasting":
        st.switch_page("pages/4.Forecast.py")
    elif selected == "Model Analytics":
        st.switch_page("pages/5.Model_Comparison.py")
    elif selected == "Chatbot":
        st.switch_page("pages/6.Chatbot.py")
    elif selected == "Market News":
        st.switch_page("pages/7.Top_Stories.py")
    elif selected == "FAQ":
        st.switch_page("pages/FAQ.py")

# --- 3. DATA LOADING & LOGIC ---
@st.cache_data
def load_data():
    df = pd.read_csv("Dashboard/assets/crypto_enriched_ohlcv_cleaned_datasets.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    rep = pd.read_csv("Dashboard/assets/representative_coins.csv")
    return df, rep

data, rep_df = load_data()
representatives = rep_df["Representative_Coin"].tolist()

def get_live_prices(symbols):
    coin_ids = {"BETH-USD": "beth", "BTC-USD": "bitcoin", "ADA-USD": "cardano", "BCH-USD": "bitcoin-cash"}
    ids = [coin_ids[s] for s in symbols if s in coin_ids]
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies=usd&include_24hr_change=true"
    try:
        resp = requests.get(url, timeout=5).json()
        return [{"s": s, "p": float(resp[coin_ids[s]]["usd"]), "c": float(resp[coin_ids[s]]["usd_24h_change"])} for s in symbols if coin_ids.get(s) in resp]
    except: return []

# --- 4. MAIN CONTENT ---
st.markdown("<h1 style='margin-bottom:0;'>Market Intelligence Terminal</h1>", unsafe_allow_html=True)
st.caption(f"INSTITUTIONAL FEED • {datetime.now().strftime('%H:%M:%S')} UTC")

# Live Metrics Row
live_data = get_live_prices(representatives)
if live_data:
    cols = st.columns(len(live_data))
    for i, coin in enumerate(live_data):
        color = "#22c55e" if coin['c'] >= 0 else "#ef4444"
        with cols[i]:
            st.markdown(f"""
                <div class="m-card">
                    <p style="color:#94a3b8; font-size:0.7rem; font-weight:bold;">{coin['s']}</p>
                    <h2 style="margin:0; font-size:1.6rem; color:white;">${coin['p']:,.2f}</h2>
                    <p style="color:{color}; font-weight:bold; margin-top:5px;">{coin['c']:+.2f}%</p>
                </div>
            """, unsafe_allow_html=True)

st.markdown("<br><hr style='border-color: #1e293b;'><br>", unsafe_allow_html=True)

# Main Dashboard Layout
col_chart, col_stats = st.columns([3, 1], gap="large")

with col_chart:
    st.markdown("### 📊 Interactive Asset Explorer")
    sel_coin = st.selectbox("Switch Perspective", sorted(data["Coin"].unique()))
    cdf = data[data["Coin"] == sel_coin]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=cdf["Date"], y=cdf["Close"], name="Price", line=dict(color='#3b82f6', width=2)))
    fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=450, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

with col_stats:
    st.markdown("### 📈 Risk Analysis")
    # Volatility Gauge
    vol = cdf["Close"].pct_change().std() * 100
    fig_g = go.Figure(go.Indicator(
        mode = "gauge+number", value = vol,
        gauge = {'axis': {'range': [None, 10]}, 'bar': {'color': "#3b82f6"}, 'steps': [{'range': [0, 5], 'color': "#1e293b"}]},
        title = {'text': "Volatility Index", 'font': {'size': 14}}
    ))
    fig_g.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=220, margin=dict(l=10,r=10,t=40,b=0))
    st.plotly_chart(fig_g, use_container_width=True)
    
    ath = cdf["Close"].max()
    curr = cdf["Close"].iloc[-1]
    st.markdown(f"""
        <div style="background:#1e293b; padding:20px; border-radius:15px; border:1px solid #334155;">
            <p style="margin:0; color:#94a3b8; font-size:0.75rem;">Peak Asset Value</p>
            <h3 style="margin:0; color:white;">${ath:,.2f}</h3>
            <hr style="border-color:#334155; margin:15px 0;">
            <p style="margin:0; color:#94a3b8; font-size:0.75rem;">Drawdown</p>
            <h3 style="margin:0; color:#ef4444;">-{((ath-curr)/ath*100):.1f}%</h3>
        </div>
    """, unsafe_allow_html=True)