import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- 1. PAGE CONFIG & THEME OVERRIDE ---
st.set_page_config(page_title="Intelligence Terminal", layout="wide")

# CSS to force dark mode and hide default navigation
st.markdown("""
    <style>
    /* HIDE DEFAULT NAV */
    [data-testid="stSidebarNav"] {display: none !important;}
    
    /* FORCE DARK BACKGROUND */
    .stApp { background-color: #020617; }
    
    /* TERMINAL CARDS */
    .metric-container {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* HEADERS */
    h1, h2, h3 { color: #f8fafc !important; font-weight: 800 !important; }
    .stText, p, span, label { color: #cbd5e1 !important; }
    
    /* CUSTOM SCROLLBAR */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #020617; }
    ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
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
    st.error("Infrastructure Error: Link to Assets folder broken.")
    st.stop()

def get_live_prices(symbols):
    coin_ids = {"BETH-USD": "beth", "BTC-USD": "bitcoin", "ADA-USD": "cardano", "BCH-USD": "bitcoin-cash"}
    ids = [coin_ids[s] for s in symbols if s in coin_ids]
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies=usd&include_24hr_change=true"
    try:
        resp = requests.get(url, timeout=5).json()
        results = []
        for s in symbols:
            cid = coin_ids.get(s)
            if cid in resp:
                results.append({
                    "symbol": s,
                    "price": float(resp[cid].get("usd", 0)),
                    "change": float(resp[cid].get("usd_24h_change", 0))
                })
        return results
    except: return []

# --- 3. SIDEBAR (MATCHING HOME PAGE) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>CryptoVision</h2>", unsafe_allow_html=True)
    st.write("---")
    if st.button("🏠 Return to Overview", use_container_width=True):
        st.switch_page("app.py")
    st.info("Institutional Grade Market Intelligence Feed.")

# --- 4. HEADER & TOP METRICS ---
st.markdown("<h1 style='font-size: 2.5rem;'>Market Intelligence Terminal</h1>", unsafe_allow_html=True)
st.caption(f"LIVE DATA STREAM • REFRESHED AT {datetime.now().strftime('%H:%M:%S')} UTC")

# Horizontal Price Ticker
live_data = get_live_prices(representatives)
if live_data:
    cols = st.columns(len(live_data))
    for i, coin in enumerate(live_data):
        color = "#22c55e" if coin['change'] >= 0 else "#ef4444"
        with cols[i]:
            st.markdown(f"""
                <div class="metric-container">
                    <p style="color:#94a3b8; font-size:0.7rem; font-weight:bold; letter-spacing:1px;">{coin['symbol']}</p>
                    <h2 style="margin:0; font-size:1.8rem; color:white;">${coin['price']:,.2f}</h2>
                    <p style="color:{color}; font-weight:bold; margin-top:5px;">{coin['change']:+.2f}%</p>
                </div>
            """, unsafe_allow_html=True)
else:
    st.warning("External API Rate Limit Reached. Showing cached indicators.")

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. MARKET ANALYSIS SECTION ---
col_main, col_side = st.columns([3, 1], gap="large")

with col_main:
    st.markdown("### 📊 Interactive Analysis")
    selected_coin = st.selectbox("Switch Perspective", sorted(data["Coin"].unique()))
    
    cdf = data[data["Coin"] == selected_coin]
    
    # Advanced Technical Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=cdf["Date"], y=cdf["Close"], name="Price", line=dict(color='#3b82f6', width=2)))
    fig.add_trace(go.Scatter(x=cdf["Date"], y=cdf["Close"].rolling(30).mean(), name="30D SMA", line=dict(color='#f59e0b', width=1, dash='dot')))
    
    fig.update_layout(
        template="plotly_dark", 
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#1e293b"),
        margin=dict(l=0, r=0, t=20, b=0),
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)

with col_side:
    st.markdown("### 📈 Insights")
    
    # Calculate Drawdown
    ath = cdf["Close"].max()
    curr = cdf["Close"].iloc[-1]
    drawdown = ((ath - curr) / ath) * 100
    
    # Sentiment Gauge (New Content)
    st.markdown("""<p style="font-size:0.8rem; font-weight:bold; color:#94a3b8;">VOLATILITY SCORE</p>""", unsafe_allow_html=True)
    volatility = cdf["Close"].pct_change().std() * 100
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = volatility,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Volatility Index", 'font': {'size': 14}},
        gauge = {
            'axis': {'range': [None, 10], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#3b82f6"},
            'steps': [
                {'range': [0, 3], 'color': "#1e293b"},
                {'range': [3, 7], 'color': "#334155"}],
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 8}
        }
    ))
    fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white", 'family': "Inter"}, height=250, margin=dict(l=20, r=20, t=50, b=0))
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Asset Stats Card
    st.markdown(f"""
        <div style="background:#1e293b; padding:20px; border-radius:15px; border:1px solid #334155;">
            <p style="margin:0; color:#94a3b8; font-size:0.75rem;">Peak Asset Value</p>
            <h3 style="margin:0; color:#f8fafc;">${ath:,.2f}</h3>
            <hr style="border-color:#334155; margin:15px 0;">
            <p style="margin:0; color:#94a3b8; font-size:0.75rem;">Current Drawdown</p>
            <h3 style="margin:0; color:#ef4444;">-{drawdown:.1f}%</h3>
        </div>
    """, unsafe_allow_html=True)

# --- 6. FOOTER ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #475569; font-size: 10px;'>PROPRIETARY ANALYTICS ENGINE • CRYPTOVISION AI V2.0</div>", unsafe_allow_html=True)