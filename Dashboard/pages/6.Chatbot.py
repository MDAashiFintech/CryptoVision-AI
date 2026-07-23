import streamlit as st
import re
import time
import os
import sys

# --- 1. CLOUD PATH HACK ---
# This ensures Chatbot can import functions from FAQ.py on Streamlit Cloud
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
    st.error("Error: Could not link to the FAQ Analytics Engine. Check folder structure.")
    st.stop()

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Crypto Analytics Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 Crypto Analytics Chatbot")

# --- 3. DATA LOADING ---
try:
    data_dict = load_all_data()
    all_metrics_df = load_and_process_all_metrics()
    main_df, rep_coins, all_coins, top_corr_df, latest_prices = (
        data_dict["main_df"], data_dict["rep_coins"], data_dict["all_coins"],
        data_dict["top_corr_df"], data_dict["latest_prices"],
    )
except Exception as e:
    st.error(f"Data Loading Error: {e}")
    st.stop()

# --- 4. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm your Crypto AI Assistant. How can I help you?", "buttons": ["Show Price Chart", "Find Correlations", "Predict High/Low", "Compare Model Performance"]}]
if "awaiting_controls" not in st.session_state:
    st.session_state.awaiting_controls = None

# --- 5. LOGIC ---
def process_input(label=None):
    user_text = label if label else st.session_state.temp_input
    st.session_state.messages.append({"role": "user", "content": user_text})
    
    with st.spinner("Processing..."):
        time.sleep(0.5)
        if user_text == "Show Price Chart":
            st.session_state.awaiting_controls = "trend"
            st.session_state.messages.append({"role": "assistant", "content": "Which coin would you like to see?"})
        elif user_text == "Compare Model Performance":
            leaderboard, report = get_model_leaderboard(all_metrics_df)
            st.session_state.messages.append({"role": "assistant", "content": report})
            st.session_state.messages.append({"role": "assistant", "content": leaderboard, "type": "df"})
        else:
            st.session_state.messages.append({"role": "assistant", "content": "I'm ready to help! Please use the sidebar or menu options."})

# --- 6. UI RENDERING ---
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        if msg.get("type") == "df":
            st.dataframe(msg["content"], use_container_width=True)
        else:
            st.markdown(msg["content"])
        if msg.get("buttons"):
            cols = st.columns(len(msg["buttons"]))
            for j, b in enumerate(msg["buttons"]):
                cols[j].button(b, key=f"btn_{i}_{j}", on_click=process_input, args=(b,))

if prompt := st.chat_input("Type your question..."):
    st.session_state.temp_input = prompt
    process_input()

if st.session_state.awaiting_controls == "trend":
    st.markdown("---")
    c = st.selectbox("Select Coin", all_coins)
    if st.button("Generate Chart"):
        fig, insight = plot_trend_chart(main_df, c)
        st.plotly_chart(fig)
        st.session_state.awaiting_controls = None
        st.rerun()