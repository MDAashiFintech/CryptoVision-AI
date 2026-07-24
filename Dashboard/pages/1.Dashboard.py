import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- 1. GLOBAL UI FIX (Add this to every page to hide dots) ---
st.set_page_config(page_title="Market Terminal | CryptoVision AI", layout="wide")

st.markdown("""
    <style>
    /* Hide default sidebar navigation dots */
    div[data-testid="stSidebarNav"] {display: none;}
    
    /* Dark Theme Base */
    .main {
        background-color: #0f172a;
    }
    
    /* Sleek Metric Cards */
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        transition: border-color 0.3s;
    }
    .metric-card:hover {
        border-color: #3b82f6;
    }
    
    /* Price Performance Box */
    .stats-box {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #334155;
    }
    
    /* Header Styling */
    h1, h2, h3 {
        color: #f8fafc !important;
        font-weight: 800 !important;
    }
    .stCaption {
        color: #94a3b8 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGIC & DATA ---
@st.cache_data
def load_base_data():
    df = pd.read_csv("Dashboard/assets/crypto_enriched_ohlcv_cleaned_datasets.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    rep = pd.read_csv("Dashboard/assets/representative_coins.csv")
    return df, rep

try:
    data, rep_df = load_base_data()
    representatives = rep_df["Representative_Coin"].tolist()
except Exception as e:
    st.error("Data integrity error. Check asset paths.")
    st.stop()

rep_names = {"BETH-USD": "Beacon ETH", "BTC-USD": "Bitcoin", "ADA-USD": "Cardano", "BCH-USD": "Bitcoin Cash"}
coin_ids = {"BETH-USD": "beth", "BTC-USD": "bitcoin", "ADA-USD": "cardano", "BCH-USD": "bitcoin-cash"}

def get_live_prices(symbols):
    ids = [coin_ids[s] for s in symbols if s in coin_ids]
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies=usd&include_24hr_change=true"
    try:
        resp = requests.get(url).json()
        results = []
        for s in symbols:
            cid = coin_ids.get(s)
            if cid in resp:
                results.append({
                    "symbol": s,
                    "name": rep_names.get(s, s),
                    "price": resp[cid]["usd"],
                    "change": resp[cid].get("usd_24h_change", 0)
                })
        return results
    except: return []

# --- 3. HEADER ---
col_h1, col_h2 = st.columns([2, 1])
with col_h1:
    st.title("Market Intelligence Terminal")
    st.caption(f"Real-time institutional feed • Last update: {datetime.now().strftime('%H:%M:%S')}")

# --- 4. LIVE PRICE TRACKER ---
st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
live_prices = get_live_prices(representatives)
cols = st.columns(len(representatives))

for i, coin in enumerate(live_prices):
    price = f"${coin['price']:,.2f}" if coin['price'] > 0 else "FETCHING..."
    change_val = coin['change']
    color = "#22c55e" if change_val >= 0 else "#ef4444"
    
    cols[i].markdown(f"""
        <div class="metric-card">
            <p style="color: #94a3b8; font-size: 0.8rem; font-weight: 700; margin-bottom: 5px;">{coin['name'].upper()}</p>
            <p style="font-size: 1.8rem; font-weight: 800; margin: 0;">{price}</p>
            <p style="color: {color}; font-size: 1rem; font-weight: 600;">{change_val:+.2f}%</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- 5. INTERACTIVE EXPLORER ---
st.subheader("Asset Deep-Dive")
c1, c2 = st.columns([1, 2])
with c1:
    selected_coin = st.selectbox("Select Asset", sorted(data["Coin"].unique()))
with c2:
    chart_type = st.select_slider("Select Visualization", options=["Trend", "30-Day SMA", "Volume", "Candlestick"])

coin_df = data[data["Coin"] == selected_coin]

if not coin_df.empty:
    col_stats, col_chart = st.columns([1, 3], gap="large")
    
    with col_stats:
        # Calculate Metrics
        close = coin_df["Close"]
        ath = close.max()
        atl = close.min()
        curr = close.iloc[-1]
        
        st.markdown(f"""
            <div class="stats-box">
                <h4 style="margin-top:0; color:#3b82f6;">Performance Summary</h4>
                <div style="display:flex; justify-content:space-between; margin:10px 0;">
                    <span style="color:#94a3b8;">All-Time High</span>
                    <span style="font-weight:700; color:#f8fafc;">${ath:,.2f}</span>
                </div>
                <div style="display:flex; justify-content:space-between; margin:10px 0;">
                    <span style="color:#94a3b8;">All-Time Low</span>
                    <span style="font-weight:700; color:#f8fafc;">${atl:,.2f}</span>
                </div>
                <hr style="border-color:#334155;">
                <p style="color:#94a3b8; font-size:0.8rem;">The asset is currently trading at <b>{((curr/ath)*100):.1f}%</b> of its peak value.</p>
            </div>
        """, unsafe_allow_html=True)

    with col_chart:
        if chart_type == "Trend":
            fig = px.line(coin_df, x="Date", y="Close", color_discrete_sequence=['#3b82f6'])
        elif chart_type == "30-Day SMA":
            coin_df['SMA'] = coin_df['Close'].rolling(30).mean()
            fig = px.line(coin_df, x="Date", y=["Close", "SMA"], color_discrete_map={"Close": "#3b82f6", "SMA": "#f59e0b"})
        elif chart_type == "Volume":
            fig = px.bar(coin_df, x="Date", y="Volume", color_discrete_sequence=['#1e293b'])
        else: # Candlestick
            fig = go.Figure(data=[go.Candlestick(x=coin_df['Date'], open=coin_df['Open'], high=coin_df['High'], low=coin_df['Low'], close=coin_df['Close'])])
        
        fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=0, b=0), height=400)
        st.plotly_chart(fig, use_container_width=True)

# --- 6. FOOTER DISCLAIMER ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("Terminal Data Source: Yahoo Finance & CoinGecko Public API. For analytical purposes only.")