import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="Market Terminal | CryptoVision AI", layout="wide")

# --- 2. THE UI "MAGIC" (Hides sidebar dots & applies dark theme) ---
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none !important;}
    .main { background-color: #0f172a; }
    .m-card {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 24px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .m-card:hover { transform: translateY(-5px); border-color: #3b82f6; }
    h1, h2, h3, p, span { color: #f8fafc !important; }
    .stCaption { color: #94a3b8 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA LOADING ---
@st.cache_data
def load_data():
    df = pd.read_csv("Dashboard/assets/crypto_enriched_ohlcv_cleaned_datasets.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    rep = pd.read_csv("Dashboard/assets/representative_coins.csv")
    return df, rep

try:
    data, rep_df = load_data()
    representatives = rep_df["Representative_Coin"].tolist()
except:
    st.error("Data Path Error.")
    st.stop()

rep_names = {"BETH-USD": "Beacon ETH", "BTC-USD": "Bitcoin", "ADA-USD": "Cardano", "BCH-USD": "Bitcoin Cash"}
coin_ids = {"BETH-USD": "beth", "BTC-USD": "bitcoin", "ADA-USD": "cardano", "BCH-USD": "bitcoin-cash"}

def get_live_prices(symbols):
    ids = [coin_ids[s] for s in symbols if s in coin_ids]
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies=usd&include_24hr_change=true"
    try:
        resp = requests.get(url, timeout=5).json()
        results = []
        for s in symbols:
            cid = coin_ids.get(s)
            if cid and cid in resp:
                # SAFETY: Using .get() with default values to prevent TypeErrors
                coin_data = resp[cid]
                results.append({
                    "symbol": s,
                    "price": float(coin_data.get("usd", 0)),
                    "change": float(coin_data.get("usd_24h_change", 0))
                })
        return results
    except: 
        return []

# --- 4. TERMINAL HEADER ---
c_head, c_btn = st.columns([4, 1])
with c_head:
    st.markdown("<h1 style='margin-bottom:0;'>Market Intelligence Terminal</h1>", unsafe_allow_html=True)
    st.caption(f"INSTITUTIONAL FEED • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

with c_btn:
    if st.button("⬅ Back to Home"):
        st.switch_page("app.py")

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. LIVE PRICE TICKER ---
live_data = get_live_prices(representatives)
if live_data:
    cols = st.columns(len(live_data))
    for i, coin in enumerate(live_data):
        # SAFETY: Check if change is a valid number before comparing
        change_val = coin.get('change', 0)
        color = "#22c55e" if change_val >= 0 else "#ef4444"
        
        cols[i].markdown(f"""
            <div class="m-card">
                <p style="color:#94a3b8; font-size:0.7rem; font-weight:bold; margin-bottom:5px;">{rep_names.get(coin['symbol'], 'ASSET').upper()}</p>
                <h2 style="margin:0; font-size:1.8rem;">${coin['price']:,.2f}</h2>
                <p style="color:{color}; font-weight:600; margin-top:5px;">{change_val:+.2f}%</p>
            </div>
        """, unsafe_allow_html=True)
else:
    st.warning("Live connection interrupted. Showing terminal defaults...")

st.markdown("<br><hr style='border-color:#334155;'><br>", unsafe_allow_html=True)

# --- 6. ASSET EXPLORER ---
st.markdown("### 📊 Asset Deep-Dive")
c1, c2 = st.columns([1, 3])

with c1:
    sel_coin = st.selectbox("Select Asset", sorted(data["Coin"].unique()))
    chart_type = st.radio("Metric", ["Price Trend", "Volume", "30-Day Moving Average"])
    
    cdf = data[data["Coin"] == sel_coin]
    ath = cdf["Close"].max()
    curr = cdf["Close"].iloc[-1]
    st.markdown(f"""
        <div style="background:#1e293b; padding:15px; border-radius:10px; border:1px solid #334155; margin-top:20px;">
            <p style="color:#94a3b8; font-size:0.8rem; margin:0;">All-Time High</p>
            <h4 style="margin:0; color:#3b82f6;">${ath:,.2f}</h4>
            <p style="color:#94a3b8; font-size:0.8rem; margin-top:10px;">Drawdown from Peak</p>
            <h4 style="margin:0; color:#ef4444;">-{((1 - curr/ath)*100):.1f}%</h4>
        </div>
    """, unsafe_allow_html=True)

with c2:
    if chart_type == "Price Trend":
        fig = px.line(cdf, x="Date", y="Close", color_discrete_sequence=['#3b82f6'])
    elif chart_type == "Volume":
        fig = px.bar(cdf, x="Date", y="Volume", color_discrete_sequence=['#1e293b'])
    else:
        cdf['SMA'] = cdf['Close'].rolling(30).mean()
        fig = px.line(cdf, x="Date", y=["Close", "SMA"], color_discrete_map={"Close": "#3b82f6", "SMA": "#f59e0b"})
    
    fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=450)
    st.plotly_chart(fig, use_container_width=True)