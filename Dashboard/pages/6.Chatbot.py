import streamlit as st
import time
import os
import sys

# --- 1. CLOUD PATH HACK ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import FAQ
    from FAQ import (
        load_all_data, load_and_process_all_metrics, get_model_leaderboard,
        plot_trend_chart, plot_moving_average_chart, get_top_correlations,
        get_forecast_logic, fetch_top_stories
    )
except ImportError:
    st.error("Engine failure. Restarting...")
    st.stop()

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Crypto AI Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 Crypto Analytics Assistant")

# --- 3. DATA LOADING ---
data = load_all_data()
metrics = load_and_process_all_metrics()

# --- 4. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I am your Crypto AI Assistant. Choose an analysis to begin:", "type": "text", "buttons": ["Show Price Chart", "Find Correlations", "Predict High/Low", "Analyze Potential Profit", "Compare Model Performance"]}]
if "active_tool" not in st.session_state: st.session_state.active_tool = None
if "step" not in st.session_state: st.session_state.step = 0

def add_msg(role, content, type="text"):
    st.session_state.messages.append({"role": role, "content": content, "type": type})

def process_btn(label):
    add_msg("user", label)
    st.session_state.active_tool = label
    if label == "Compare Model Performance":
        df, report = get_model_leaderboard(metrics)
        add_msg("assistant", report)
        add_msg("assistant", df, "df")
        st.session_state.active_tool = None
    elif label == "Analyze Potential Profit":
        st.session_state.step = 1
        add_msg("assistant", "Great! Which coin are you interested in?")
    else:
        add_msg("assistant", f"I'm ready to help with **{label}**. Please use the controls below.")

# --- 5. UI DISPLAY ---
for i, m in enumerate(st.session_state.messages):
    with st.chat_message(m["role"]):
        if m["type"] == "text": st.markdown(m["content"])
        elif m["type"] == "plot": st.plotly_chart(m["content"], use_container_width=True)
        elif m["type"] == "df": st.dataframe(m["content"], use_container_width=True)
        
        if "buttons" in m:
            cols = st.columns(3)
            for j, btn in enumerate(m["buttons"]):
                cols[j % 3].button(btn, key=f"b_{i}_{j}", on_click=process_btn, args=(btn,))

# --- 6. DYNAMIC CONTROLS ---
if st.session_state.active_tool:
    st.markdown("---")
    tool = st.session_state.active_tool
    
    if tool == "Show Price Chart":
        c = st.selectbox("Select Coin", data["all_coins"])
        if st.button("Generate Trend"):
            fig, insight = plot_trend_chart(data["main_df"], c)
            add_msg("assistant", fig, "plot")
            add_msg("assistant", insight)
            st.session_state.active_tool = None
            st.rerun()

    elif tool == "Predict High/Low":
        c = st.selectbox("Currency", data["rep_coins"])
        m = st.selectbox("Model", ["LSTM", "XGB", "ARIMA", "PROPHET"])
        if st.button("Run Forecast"):
            h, l = get_forecast_logic(m, c)
            if h:
                res = f"**Forecast for {c} ({m}):**\n- High: `${h['p']:,.2f}` on {h['d']}\n- Low: `${l['p']:,.2f}` on {l['d']}"
                add_msg("assistant", res)
            else: add_msg("assistant", "Data not found.")
            st.session_state.active_tool = None
            st.rerun()

    elif tool == "Find Correlations":
        c = st.selectbox("Target Coin", data["rep_coins"])
        if st.button("Calculate Correlations"):
            add_msg("assistant", get_top_correlations(data["top_corr_df"], c))
            st.session_state.active_tool = None
            st.rerun()

    elif tool == "Analyze Potential Profit":
        c = st.selectbox("Choose Asset", data["all_coins"])
        q = st.number_input("Quantity", min_value=0.1, value=1.0)
        t = st.number_input("Target Sell Price ($)", value=data["latest_prices"].get(c, 1.0) * 1.1)
        if st.button("Calculate Profit"):
            curr = data["latest_prices"].get(c, 0)
            profit = (t - curr) * q
            add_msg("assistant", f"Buying **{q} {c}** now and selling at **${t:,.2f}** would result in a profit/loss of: **${profit:,.2f}**")
            st.session_state.active_tool = None
            st.rerun()

if prompt := st.chat_input("Ask a question..."):
    add_msg("user", prompt)
    add_msg("assistant", "I'm focusing on the menu options right now. Please select one of the analysis buttons to proceed!")
    st.rerun()