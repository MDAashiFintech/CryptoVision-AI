import streamlit as st
import re
import time
import os
import sys

# --- CLOUD PATH HACK ---
# This allows Chatbot to import functions from FAQ.py on Streamlit Cloud
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    import FAQ
    from FAQ import (
        load_all_data, load_and_process_all_metrics, get_model_leaderboard,
        plot_trend_chart, plot_moving_average_chart, get_top_correlations,
        get_forecasted_high_low, get_best_purchase_sale, get_group_prediction,
        get_confidence_level, fetch_top_stories, calculate_what_if, get_model_comparison,
    )
except ImportError:
    st.error("Engine Link Failure. Ensure Dashboard/pages/FAQ.py exists.")
    st.stop()

# --- Page Configuration ---
st.set_page_config(page_title="Crypto Analytics Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 Crypto Analytics Chatbot")

# --- Load all data ---
try:
    data_dict = load_all_data()
    all_metrics_df = load_and_process_all_metrics()
    main_df, rep_coins, all_coins, top_corr_df, latest_prices = (
        data_dict["main_df"], data_dict["rep_coins"], data_dict["all_coins"],
        data_dict["top_corr_df"], data_dict["latest_prices"],
    )
except Exception as e:
    st.error(f"Data Load Error: {e}")
    st.stop()

# --- FEATURE & SESSION SETUP ---
ASSESSMENT_QUESTIONS = {
    "Show Price Chart": "trend_controls",
    "Find Correlations": "correlation_controls",
    "Show Moving Average": "ma_controls",
    "Predict High/Low": "high_low_controls",
    "Best Time to Purchase/Sell": "best_time_controls",
    "Predict Group Trend": "group_pred_controls",
    "Get Model Confidence": "confidence_controls",
    "Display Top Stories": "top_stories_action",
    "Analyze Potential Profit": "what_if_controls",
    "Compare Model Performance": "model_comp_main",
}

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I am your Crypto AI Assistant. How can I help you?", "buttons": list(ASSESSMENT_QUESTIONS.keys())}]
if "awaiting_controls" not in st.session_state: st.session_state.awaiting_controls = None
if "what_if_step" not in st.session_state: st.session_state.what_if_step = 0
if "what_if_data" not in st.session_state: st.session_state.what_if_data = {}

# --- CORE CHAT LOGIC ---
def process_user_input(prompt=None, button_label=None):
    user_text = button_label if button_label else prompt
    if not user_text: return
    st.session_state.messages.append({"role": "user", "content": user_text})
    
    with st.spinner("Processing..."):
        time.sleep(0.3)
        st.session_state.awaiting_controls = None
        
        if user_text in ASSESSMENT_QUESTIONS:
            action = ASSESSMENT_QUESTIONS[user_text]
            if action == "top_stories_action":
                stories = fetch_top_stories(rep_coins)
                st.session_state.messages.append({"role": "assistant", "content": "\n".join(stories)})
            elif action == "what_if_controls":
                st.session_state.awaiting_controls = "what_if_controls"
                st.session_state.what_if_step = 1
                st.session_state.messages.append({"role": "assistant", "content": "Which coin for the trade?"})
            else:
                st.session_state.awaiting_controls = action
                st.session_state.messages.append({"role": "assistant", "content": f"Select inputs for **{user_text}** below."})
        elif user_text == "Show Overall Winner":
            leaderboard, report = get_model_leaderboard(all_metrics_df)
            st.session_state.messages.append({"role": "assistant", "content": report})
            st.session_state.messages.append({"role": "assistant", "content": leaderboard, "type": "df"})

# --- UI DISPLAY ---
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        if msg.get("type") == "df": st.dataframe(msg["content"], use_container_width=True)
        else: st.markdown(msg["content"])
        if msg.get("buttons"):
            cols = st.columns(3)
            for j, btn in enumerate(msg["buttons"]):
                cols[j % 3].button(btn, key=f"b_{i}_{j}", on_click=process_user_input, args=(btn,))

if prompt := st.chat_input("Type your question..."):
    process_user_input(prompt=prompt)

# --- DYNAMIC CONTROL PANEL ---
if st.session_state.awaiting_controls:
    st.markdown("---")
    ctrl = st.session_state.awaiting_controls
    if ctrl == "trend_controls":
        c = st.selectbox("Select Coin", all_coins)
        if st.button("Generate Chart"):
            fig, insight = plot_trend_chart(main_df, c)
            st.session_state.messages.append({"role": "assistant", "content": fig, "type": "plot"})
            st.session_state.awaiting_controls = None
            st.rerun()
    elif ctrl == "high_low_controls":
        c = st.selectbox("Select Coin", rep_coins)
        m = st.selectbox("Select Model", ["ARIMA", "PROPHET", "LSTM", "RF", "XGB"])
        if st.button("Run Prediction"):
            h, l, insight = get_forecasted_high_low(m, c)
            st.session_state.messages.append({"role": "assistant", "content": f"Results for {c}: High: ${h['price']:.2f}, Low: ${l['price']:.2f}"})
            st.session_state.awaiting_controls = None
            st.rerun()