import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import os
import base64

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Crypto Forecast", page_icon="📈", layout="wide")

# --- PATH DEFINITION (The "Cloud Fix") ---
# On Streamlit Cloud, everything must start from the root folder
BASE_DASHBOARD_PATH = "Dashboard"
ASSETS_FOLDER = os.path.join(BASE_DASHBOARD_PATH, "assets")

# --- HELPER FUNCTIONS ---
def image_to_base64(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

MODEL_NAMES = {
    "ARIMA": "ARIMA",
    "LSTM": "LSTM Neural Net",
    "RF": "Random Forest",
    "XGB": "XGBoost",
    "PROPHET": "Prophet",
}

COIN_INFO = {
    "BTC-USD": ("Bitcoin", "₿"),
    "BCH-USD": ("Bitcoin Cash", "🪙"),
    "ADA-USD": ("Cardano", "₳"),
    "BETH-USD": ("Beacon ETH", "⚡"),
    "LINK-USD": ("Chainlink", "🔗"),
    "STETH-USD": ("Staked ETH", "🦄"),
}

# Updated Image Paths with Dashboard/ prefix
PNG_PATHS = {
    "BTC-USD": os.path.join(ASSETS_FOLDER, "BTC.png"),
    "BCH-USD": os.path.join(ASSETS_FOLDER, "BCH.png"),
    "ADA-USD": os.path.join(ASSETS_FOLDER, "ADA.png"),
    "STETH-USD": os.path.join(ASSETS_FOLDER, "STETH.png"),
    "BETH-USD": os.path.join(ASSETS_FOLDER, "BETH.png"),
    "LINK-USD": os.path.join(ASSETS_FOLDER, "LINK.png"),
}

CARD_ICONS = {
    "signal": os.path.join(ASSETS_FOLDER, "signal.png"),
    "performance": os.path.join(ASSETS_FOLDER, "chart.png"),
    "summary": os.path.join(ASSETS_FOLDER, "summary.png"),
}

def model_shortname(fullname):
    for k, v in MODEL_NAMES.items():
        if v == fullname:
            return k
    return fullname

def check_and_rename(df, expected_cols):
    df_cols_lower = [c.lower() for c in df.columns]
    rename_map = {}
    for col in expected_cols:
        if col not in df.columns and col.lower() in df_cols_lower:
            matched_col = df.columns[df_cols_lower.index(col.lower())]
            rename_map[matched_col] = col
    if rename_map:
        df.rename(columns=rename_map, inplace=True)
    return df

def filter_significant_signals(df, window_size=5):
    df["is_buy"] = df["Signal"].str.lower() == "buy"
    df["is_sell"] = df["Signal"].str.lower() == "sell"
    df["rolling_min"] = df["Actual"].rolling(window=window_size, center=True).min()
    df["rolling_max"] = df["Actual"].rolling(window=window_size, center=True).max()
    significant_buys = df[(df["is_buy"]) & (df["Actual"] == df["rolling_min"])]
    significant_sells = df[(df["is_sell"]) & (df["Actual"] == df["rolling_max"])]
    return significant_buys, significant_sells

# --- DATA LOADING ---
try:
    rep_df = pd.read_csv(os.path.join(ASSETS_FOLDER, "representative_coins.csv"))
    rep_coins = rep_df["Representative_Coin"].tolist()
except FileNotFoundError:
    st.error(f"`representative_coins.csv` not found in `{ASSETS_FOLDER}`. Please check your folder structure.")
    st.stop()

# --- SIDEBAR CONTROLS ---
st.sidebar.title("Forecasting Controls")
model_full = st.sidebar.selectbox("Choose a Model", list(MODEL_NAMES.values()))
coin = st.sidebar.selectbox("Choose a Currency", rep_coins)
model_short = model_shortname(model_full)

# --- DYNAMIC HEADER ---
coin_name = COIN_INFO.get(coin, (coin, ""))[0]
coin_logo_path = PNG_PATHS.get(coin)
if coin_logo_path and os.path.exists(coin_logo_path):
    logo_b64 = image_to_base64(coin_logo_path)
    st.markdown(
        f"""<div style="display:flex;align-items:center;margin-bottom:20px;"><img src="data:image/png;base64,{logo_b64}" style="height:50px;margin-right:15px;"><h1 style="margin:0;">Forecast for {coin_name}</h1></div>""",
        unsafe_allow_html=True,
    )
else:
    st.markdown(f"# 📈 Forecast for {coin_name}")

# --- DATA PATHS & FILE LOADING ---
base_path_map = {
    "ARIMA": os.path.join(ASSETS_FOLDER, "Arima_csv", "separate_coins"),
    "PROPHET": os.path.join(ASSETS_FOLDER, "Prophet_csv", "separate_coins"),
    "LSTM": os.path.join(ASSETS_FOLDER, "LSTM_csv", "separate_coins"),
    "RF": os.path.join(ASSETS_FOLDER, "RandomForest_csv", "separate_coins"),
    "XGB": os.path.join(ASSETS_FOLDER, "XGBoost_csv", "separate_coins"),
}
base_path = base_path_map.get(model_short)
metrics_file = os.path.join(base_path, f"{model_short.lower()}_metrics_summary.csv") if base_path else None

try:
    hist_df = pd.read_csv(os.path.join(base_path, f"{coin}_historical_forecast.csv"), parse_dates=["Date"])
    test_df = pd.read_csv(os.path.join(base_path, f"{coin}_test_forecast.csv"), parse_dates=["Date"])
    future_df = pd.read_csv(os.path.join(base_path, f"{coin}_future_forecast.csv"), parse_dates=["Date"])
    dff = pd.concat([hist_df, test_df, future_df], ignore_index=True)
    dff = check_and_rename(dff, ["Date", "Actual", "Predicted", "Signal"])
except Exception as e:
    st.error(f"Error loading forecast data for {coin}: {e}")
    st.stop()

# --- KEY METRICS ---
st.markdown("---")
col1, col2 = st.columns(2)
try:
    high_price = future_df["Predicted"].max()
    high_date = future_df.loc[future_df["Predicted"].idxmax(), "Date"].strftime("%Y-%m-%d")
    low_price = future_df["Predicted"].min()
    low_date = future_df.loc[future_df["Predicted"].idxmin(), "Date"].strftime("%Y-%m-%d")
    
    col1.markdown(f"""<div style="background-color:#E8F8F5;border-left:5px solid #1ABC9C;border-radius:5px;padding:20px;"><h4 style="margin:0;color:#1ABC9C;">Predicted High 🔼</h4><p style="font-size:2em;font-weight:bold;margin:10px 0;">${high_price:,.2f}</p><p style="margin:0;color:#555;">Around: <strong>{high_date}</strong></p></div>""", unsafe_allow_html=True)
    col2.markdown(f"""<div style="background-color:#FDEDEC;border-left:5px solid #E74C3C;border-radius:5px;padding:20px;"><h4 style="margin:0;color:#E74C3C;">Predicted Low 🔽</h4><p style="font-size:2em;font-weight:bold;margin:10px 0;">${low_price:,.2f}</p><p style="margin:0;color:#555;">Around: <strong>{low_date}</strong></p></div>""", unsafe_allow_html=True)
except:
    st.warning("Future predictions currently unavailable for this selection.")

# --- CHARTING AREA ---
st.subheader("Interactive Forecast Chart")
fig = go.Figure()
fig.add_trace(go.Scatter(x=dff["Date"], y=dff["Actual"], name="Actual Price", line=dict(color="#3498DB", width=2)))
fig.add_trace(go.Scatter(x=dff["Date"], y=dff["Predicted"], name="Predicted", line=dict(color="#E67E22", dash="dash")))
st.plotly_chart(fig, use_container_width=True)

# --- KPI CARDS SECTION ---
st.markdown("---")
k_cols = st.columns(3)
# Note: Ensure signal.png, chart.png, and summary.png exist in Dashboard/assets/
with k_cols[0]:
    icon = image_to_base64(CARD_ICONS['signal'])
    st.markdown(f"""<div style="background-color:#e8f7ef;border-radius:10px;padding:20px;"><h5>Significant Signals</h5><p>Latest prediction trends analyzed.</p></div>""", unsafe_allow_html=True)

with k_cols[1]:
    st.markdown(f"""<div style="background-color:#f4f6f8;border-radius:10px;padding:20px;"><h5>Performance Metrics</h5></div>""", unsafe_allow_html=True)
    try:
        m_df = pd.read_csv(metrics_file)
        row = m_df[m_df["Coin"] == coin].iloc[0]
        st.write(f"**MAPE:** {row['MAPE']:.2f}%")
        st.write(f"**R² Score:** {row['R2']:.2f}")
    except:
        st.write("Metrics currently unavailable.")

with k_cols[2]:
    st.markdown(f"""<div style="background-color:#fffcee;border-radius:10px;padding:20px;"><h5>Executive Summary</h5><p>Model robustness evaluated on 30-day window.</p></div>""", unsafe_allow_html=True)

st.info("Forecast successfully loaded from Dashboard paths.")