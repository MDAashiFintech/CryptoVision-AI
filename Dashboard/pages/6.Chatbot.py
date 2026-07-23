import streamlit as st
import re
import time
import os

# --- IMPORT FIX FOR CLOUD ---
# We use this specific import to handle the Dashboard folder structure
try:
    from Dashboard.pages.FAQ import (
        load_all_data,
        load_and_process_all_metrics,
        get_model_leaderboard,
        plot_trend_chart,
        plot_moving_average_chart,
        get_top_correlations,
        get_forecasted_high_low,
        get_best_purchase_sale,
        get_group_prediction,
        get_confidence_level,
        fetch_top_stories,
        calculate_what_if,
        get_model_comparison,
    )
except ImportError:
    # Fallback for local development
    from pages.FAQ import (
        load_all_data,
        load_and_process_all_metrics,
        get_model_leaderboard,
        plot_trend_chart,
        plot_moving_average_chart,
        get_top_correlations,
        get_forecasted_high_low,
        get_best_purchase_sale,
        get_group_prediction,
        get_confidence_level,
        fetch_top_stories,
        calculate_what_if,
        get_model_comparison,
    )

# --- Page Configuration ---
# This MUST be the very first Streamlit command
st.set_page_config(
    page_title="Crypto Analytics Chatbot", page_icon="🤖", layout="centered"
)
st.title("🤖 Crypto Analytics Chatbot")

# --- Load all data ---
try:
    data_dict = load_all_data()
    all_metrics_df = load_and_process_all_metrics()
    main_df, rep_coins, all_coins, top_corr_df, latest_prices = (
        data_dict["main_df"],
        data_dict["rep_coins"],
        data_dict["all_coins"],
        data_dict["top_corr_df"],
        data_dict["latest_prices"],
    )
except Exception as e:
    st.error(f"Fatal Error loading data for Chatbot: {e}")
    st.info("Check if the Dashboard/assets/ folder contains all required CSV files.")
    st.stop()

# --- Feature Definitions ---
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

# --- Session State Management ---
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hi! I am your Crypto Analytics Assistant. How can I help you today?",
                "content_type": "text",
                "buttons": list(ASSESSMENT_QUESTIONS.keys()),
            }
        ]
    if "awaiting_controls" not in st.session_state:
        st.session_state.awaiting_controls = None
    if "last_used_coin" not in st.session_state:
        st.session_state.last_used_coin = None
    if "last_used_model" not in st.session_state:
        st.session_state.last_used_model = None
    if "what_if_step" not in st.session_state:
        st.session_state.what_if_step = 0
    if "what_if_data" not in st.session_state:
        st.session_state.what_if_data = {}

def reset_conversation():
    st.session_state.messages = []
    st.session_state.awaiting_controls = None
    initialize_session_state()
    st.rerun()

# --- Message Handling ---
def add_message(role, content, content_type="text", buttons=None):
    st.session_state.messages.append(
        {
            "role": role,
            "content": content,
            "content_type": content_type,
            "buttons": buttons,
        }
    )

def add_assistant_message(content, buttons=None):
    add_message("assistant", content, "text", buttons)

def add_user_message(content):
    add_message("user", content, "text")

# --- Main Logic ---
def process_user_input(prompt=None, button_label=None):
    user_text = button_label if button_label else prompt
    if not user_text:
        return
    add_user_message(user_text)
    user_text_lower = user_text.lower().strip()

    with st.spinner("Analyzing..."):
        time.sleep(0.3)
        st.session_state.awaiting_controls = None
        action_triggered = False

        if not action_triggered and user_text in ASSESSMENT_QUESTIONS:
            action = ASSESSMENT_QUESTIONS[user_text]
            action_triggered = True
            if action == "top_stories_action":
                stories = fetch_top_stories(rep_coins)
                add_assistant_message("Top stories:\n\n" + "\n\n".join([f"- {s}" for s in stories]) if stories else "No news available.")
                add_assistant_message("What's next?", buttons=list(ASSESSMENT_QUESTIONS.keys()))
            elif action == "model_comp_main":
                add_assistant_message("Choose a comparison type:", buttons=["Show Overall Winner", "Compare Specific Coin"])
            elif action == "what_if_controls":
                st.session_state.awaiting_controls = "what_if_controls"
                st.session_state.what_if_step = 1
                add_assistant_message("Which coin would you like to analyze for profit?")
            else:
                st.session_state.awaiting_controls = action
                add_assistant_message(f"Helper active for: **{user_text}**. Use the controls below.")

        if not action_triggered:
            if user_text == "Show Overall Winner":
                leaderboard, report = get_model_leaderboard(all_metrics_df)
                add_assistant_message(report)
                add_message("assistant", leaderboard, "dataframe")
                add_assistant_message("What's next?", buttons=["Back to Main Menu"])
                action_triggered = True
            elif user_text == "Compare Specific Coin":
                st.session_state.awaiting_controls = "model_comp_controls"
                add_assistant_message("Which coin would you like to compare?")
                action_triggered = True

        if not action_triggered:
            if "menu" in user_text_lower:
                add_assistant_message("Explore more:", buttons=list(ASSESSMENT_QUESTIONS.keys()))
            else:
                add_assistant_message("I'm not sure about that. Try one of these options:", buttons=list(ASSESSMENT_QUESTIONS.keys()))

# --- UI Rendering ---
def display_chat_history():
    for msg_index, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            content_type, content = msg.get("content_type", "text"), msg["content"]
            if content_type == "text":
                st.markdown(content)
            elif content_type == "plot":
                st.plotly_chart(content, use_container_width=True, key=f"chart_{msg_index}")
            elif content_type == "dataframe":
                st.dataframe(content, use_container_width=True, key=f"df_{msg_index}")
            
            if msg.get("buttons"):
                cols = st.columns(3)
                for i, label in enumerate(msg["buttons"]):
                    cols[i % 3].button(label, key=f"btn_{msg_index}_{i}", on_click=process_user_input, kwargs={"button_label": label})

def display_controls(control_type):
    st.markdown("---")
    st.subheader("Action Center")
    models = ["ARIMA", "PROPHET", "LSTM", "RF", "XGB"]

    if control_type == "trend_controls":
        coin = st.selectbox("Select Coin", all_coins)
        if st.button("Generate Chart"):
            fig, insight = plot_trend_chart(main_df, coin)
            add_message("assistant", fig, "plot")
            add_assistant_message(insight)
            st.session_state.awaiting_controls = None
            st.rerun()

    elif control_type == "high_low_controls":
        coin = st.selectbox("Select Coin", rep_coins)
        model = st.selectbox("Select Model", models)
        if st.button("Predict"):
            high, low, insight = get_forecasted_high_low(model, coin)
            if high:
                add_assistant_message(f"Forecast for {coin} ({model}):\n- High: ${high['price']:.2f}\n- Low: ${low['price']:.2f}")
                add_assistant_message(insight)
            st.session_state.awaiting_controls = None
            st.rerun()

# --- EXECUTION ---
initialize_session_state()
if prompt := st.chat_input("Ask a question..."):
    process_user_input(prompt=prompt)
display_chat_history()
if st.session_state.awaiting_controls:
    display_controls(st.session_state.awaiting_controls)