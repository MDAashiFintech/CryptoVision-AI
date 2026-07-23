import streamlit as st
import time
from utils import (
    load_all_data, load_and_process_all_metrics, get_model_leaderboard,
    plot_trend_chart, get_top_correlations, get_forecast_logic
)

st.set_page_config(page_title="Crypto AI Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 Crypto Analytics Assistant")

# Load Data from Utils
try:
    data = load_all_data()
    metrics = load_and_process_all_metrics()
except Exception as e:
    st.error(f"Data loading failed: {e}")
    st.stop()

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I am your AI Assistant. How can I help you?", "type": "text", "buttons": ["Show Price Chart", "Find Correlations", "Predict High/Low", "Analyze Profit", "Model Leaderboard"]}]
if "active_tool" not in st.session_state: st.session_state.active_tool = None

def add_msg(role, content, type="text"):
    st.session_state.messages.append({"role": role, "content": content, "type": type})

def process_btn(label):
    add_msg("user", label)
    st.session_state.active_tool = label
    if label == "Model Leaderboard":
        df, report = get_model_leaderboard(metrics)
        add_msg("assistant", report)
        add_msg("assistant", df, "df")
        st.session_state.active_tool = None
    else:
        add_msg("assistant", f"I'm ready for **{label}**. Use the controls below.")

# Render Chat
for i, m in enumerate(st.session_state.messages):
    with st.chat_message(m["role"]):
        if m["type"] == "text": st.markdown(m["content"])
        elif m["type"] == "plot": st.plotly_chart(m["content"], use_container_width=True)
        elif m["type"] == "df": st.dataframe(m["content"], use_container_width=True)
        
        if "buttons" in m:
            cols = st.columns(len(m["buttons"]))
            for j, btn in enumerate(m["buttons"]):
                cols[j].button(btn, key=f"chatbtn_{i}_{j}", on_click=process_btn, args=(btn,))

# Dynamic Controls
if st.session_state.active_tool:
    st.markdown("---")
    t = st.session_state.active_tool
    if t == "Show Price Chart":
        c = st.selectbox("Select Coin", data["all_coins"])
        if st.button("View Trend"):
            fig, insight = plot_trend_chart(data["main_df"], c)
            add_msg("assistant", fig, "plot")
            add_msg("assistant", insight)
            st.session_state.active_tool = None
            st.rerun()
    
    elif t == "Predict High/Low":
        c = st.selectbox("Coin", data["rep_coins"])
        m = st.selectbox("Model", ["LSTM", "XGB", "ARIMA"])
        if st.button("Run Prediction"):
            h, l = get_forecast_logic(m, c)
            if h: add_msg("assistant", f"Forecast for {c}: High ${h['p']:,.2f}, Low ${l['p']:,.2f}")
            else: add_msg("assistant", "No data found for this coin/model.")
            st.session_state.active_tool = None
            st.rerun()

    elif t == "Find Correlations":
        c = st.selectbox("Target Asset", data["rep_coins"])
        if st.button("Check Correlation"):
            add_msg("assistant", get_top_correlations(data["top_corr_df"], c))
            st.session_state.active_tool = None
            st.rerun()

    elif t == "Analyze Profit":
        c = st.selectbox("Select Asset", data["all_coins"])
        q = st.number_input("Quantity", 1.0)
        p = st.number_input("Target Price ($)", value=data["latest_prices"].get(c, 1.0)*1.1)
        if st.button("Calculate"):
            diff = (p - data["latest_prices"].get(c, 0)) * q
            add_msg("assistant", f"Analysis for **{c}**: Potential profit of **${diff:,.2f}**.")
            st.session_state.active_tool = None
            st.rerun()

if prompt := st.chat_input("Ask about the market..."):
    add_msg("user", prompt)
    add_msg("assistant", "I work best with the menu buttons above. Please select a specific analysis!")
    st.rerun()