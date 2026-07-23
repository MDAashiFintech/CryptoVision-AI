# import streamlit as st
# import re
# import time
# from pages.analysis_functions import (
#     load_all_data,
#     plot_trend_chart,
#     plot_moving_average_chart,
#     get_top_correlations,
#     get_forecasted_high_low,
#     get_best_purchase_sale,
#     get_group_prediction,
#     get_confidence_level,
#     fetch_top_stories,
#     calculate_what_if,
#     get_model_comparison,
# )

# # --- Page Configuration ---
# st.set_page_config(
#     page_title="Crypto Analytics Chatbot", page_icon="🤖", layout="centered"
# )
# st.title("🤖 Crypto Analytics Chatbot")

# # --- Load all data ---
# try:
#     data_dict = load_all_data()
#     main_df, rep_coins, all_coins, top_corr_df, latest_prices = (
#         data_dict["main_df"],
#         data_dict["rep_coins"],
#         data_dict["all_coins"],
#         data_dict["top_corr_df"],
#         data_dict["latest_prices"],
#     )
# except FileNotFoundError as e:
#     st.error(
#         "Fatal Error: A required data file was not found. Please check your `assets` folder at the project root."
#     )
#     st.error(e)
#     st.stop()

# # --- Feature Definitions ---
# ASSESSMENT_QUESTIONS = {
#     "Show Price Chart": "trend_controls",
#     "Find Correlations": "correlation_controls",
#     "Show Moving Average": "ma_controls",
#     "Predict High/Low": "high_low_controls",
#     "Best Time to Purchase/Sell": "best_time_controls",
#     "Predict Group Trend": "group_pred_controls",
#     "Get Model Confidence": "confidence_controls",
#     "Display Top Stories": "top_stories_action",
#     "Analyze Potential Profit": "what_if_controls",
#     "Compare Model Performance": "model_comp_controls",
# }


# # --- Session State Management ---
# def initialize_session_state():
#     if "messages" not in st.session_state:
#         st.session_state.messages = [
#             {
#                 "role": "assistant",
#                 "content": "Hi! I am your Crypto Analytics Assistant. How can I help you?",
#                 "content_type": "text",
#                 "buttons": list(ASSESSMENT_QUESTIONS.keys()),
#             }
#         ]
#     if "awaiting_controls" not in st.session_state:
#         st.session_state.awaiting_controls = None
#     if "last_used_coin" not in st.session_state:
#         st.session_state.last_used_coin = None
#     if "last_used_model" not in st.session_state:
#         st.session_state.last_used_model = None


# def reset_conversation():
#     initialize_session_state()
#     st.rerun()


# # --- Message & Content Handling ---
# def add_message(role, content, content_type="text", buttons=None):
#     st.session_state.messages.append(
#         {
#             "role": role,
#             "content": content,
#             "content_type": content_type,
#             "buttons": buttons,
#         }
#     )


# def add_assistant_message(content, buttons=None):
#     add_message("assistant", content, "text", buttons)


# def add_user_message(content):
#     add_message("user", content, "text")


# # --- Main Logic ---
# def process_user_input(prompt=None, button_label=None):
#     user_text = button_label if button_label else prompt
#     if not user_text:
#         return
#     add_user_message(user_text)
#     user_text_lower = user_text.lower().strip()

#     with st.spinner("Thinking..."):
#         time.sleep(0.5)
#         st.session_state.awaiting_controls = None

#         # --- THIS IS THE NEW, ENHANCED INTENT RECOGNITION ---
#         action_triggered = False

#         # 1. Check for contextual follow-up questions first
#         if " for " in user_text:
#             parts = user_text.split(" for ")
#             action_phrase = parts[0].strip()
#             coin_entity = parts[1].strip()

#             # Map action phrase to a control type
#             if "moving average" in action_phrase.lower():
#                 st.session_state.awaiting_controls = "ma_controls"
#             elif "predict high/low" in action_phrase.lower():
#                 st.session_state.awaiting_controls = "high_low_controls"
#             # Add more elifs here for other contextual actions if needed

#             if st.session_state.awaiting_controls:
#                 st.session_state.last_used_coin = coin_entity
#                 add_assistant_message(
#                     f"Okay, I will help you with: **{action_phrase} for {coin_entity}**. Please use the controls below."
#                 )
#                 action_triggered = True

#         # 2. Check for main assessment questions if no follow-up was triggered
#         if not action_triggered and user_text in ASSESSMENT_QUESTIONS:
#             action = ASSESSMENT_QUESTIONS[user_text]
#             if action == "top_stories_action":
#                 with st.spinner("Fetching latest news..."):
#                     stories = fetch_top_stories(rep_coins)
#                     if stories:
#                         news_response = "Here are the top stories:\n\n" + "\n\n".join(
#                             [f"- {s}" for s in stories]
#                         )
#                         add_assistant_message(news_response)
#                 add_assistant_message(
#                     "What would you like to do next?",
#                     buttons=list(ASSESSMENT_QUESTIONS.keys()),
#                 )
#             else:
#                 st.session_state.awaiting_controls = action
#                 add_assistant_message(
#                     f"Okay, I will help you with: **{user_text}**. Please use the controls below."
#                 )
#             action_triggered = True

#         # 3. Check for simple commands if still no action
#         if not action_triggered:
#             if "start over" in user_text_lower or "reset" in user_text_lower:
#                 reset_conversation()
#             elif "thanks" in user_text_lower or "thank you" in user_text_lower:
#                 add_assistant_message(
#                     "You're welcome! How else can I help?",
#                     buttons=list(ASSESSMENT_QUESTIONS.keys()),
#                 )
#             elif "main menu" in user_text_lower:
#                 add_assistant_message(
#                     "Okay, what would you like to explore from the main menu?",
#                     buttons=list(ASSESSMENT_QUESTIONS.keys()),
#                 )
#             else:
#                 add_assistant_message(
#                     "I'm sorry, I didn't recognize that command. Please choose from one of the available options.",
#                     buttons=list(ASSESSMENT_QUESTIONS.keys()),
#                 )


# # --- UI Rendering ---
# def display_chat_history():
#     for msg_index, msg in enumerate(st.session_state.messages):
#         with st.chat_message(msg["role"]):
#             content_type, content = msg.get("content_type", "text"), msg["content"]
#             if content_type == "text":
#                 st.markdown(content)
#             elif content_type == "plot":
#                 st.plotly_chart(
#                     content, use_container_width=True, key=f"chart_{msg_index}"
#                 )
#             elif content_type == "dataframe":
#                 st.dataframe(content, use_container_width=True, key=f"df_{msg_index}")
#             if msg.get("buttons"):
#                 num_buttons = len(msg["buttons"])
#                 cols_per_row = 3 if num_buttons > 2 else num_buttons
#                 rows_of_cols = [
#                     st.columns(cols_per_row)
#                     for _ in range((num_buttons + cols_per_row - 1) // cols_per_row)
#                 ]
#                 for i, label in enumerate(msg["buttons"]):
#                     button_key = f"btn_{msg_index}_{i}_{label}"
#                     row, col = i // cols_per_row, i % cols_per_row
#                     rows_of_cols[row][col].button(
#                         label,
#                         key=button_key,
#                         on_click=process_user_input,
#                         kwargs={"button_label": label},
#                     )


# def display_controls(control_type):
#     st.markdown("---")
#     st.subheader("Analysis Controls")
#     models = ["ARIMA", "PROPHET", "LSTM", "RF", "XGB"]

#     def handle_rerun(coin=None, model=None):
#         if coin:
#             st.session_state.last_used_coin = coin
#         if model:
#             st.session_state.last_used_model = model

#         follow_up_buttons = []
#         if coin:
#             follow_up_buttons.append(f"Show Moving Average for {coin}")
#             follow_up_buttons.append(f"Predict High/Low for {coin}")
#         follow_up_buttons.append("Back to Main Menu")

#         add_assistant_message(
#             "Analysis complete. What would you like to do next?",
#             buttons=follow_up_buttons,
#         )
#         st.session_state.awaiting_controls = None
#         st.rerun()

#     # --- THIS IS THE NEW, ROBUST DEFAULT INDEX LOGIC ---
#     def get_default_index(options_list):
#         last_coin = st.session_state.last_used_coin
#         if last_coin and last_coin in options_list:
#             return options_list.index(last_coin)
#         return 0  # Safely default to the first item if not found

#     # --- Control Blocks with the fix applied ---
#     if control_type == "trend_controls":
#         coin = st.selectbox(
#             "Select Cryptocurrency",
#             options=all_coins,
#             index=get_default_index(all_coins),
#         )
#         if st.button("Generate Chart"):
#             fig, insight = plot_trend_chart(main_df, coin)
#             add_message("assistant", fig, "plot")
#             add_assistant_message(insight)
#             handle_rerun(coin=coin)

#     elif control_type == "ma_controls":
#         coin = st.selectbox(
#             "Select Cryptocurrency",
#             options=all_coins,
#             index=get_default_index(all_coins),
#         )
#         if st.button("Generate Chart"):
#             fig, insight = plot_moving_average_chart(main_df, coin)
#             add_message("assistant", fig, "plot")
#             add_assistant_message(insight)
#             handle_rerun(coin=coin)

#     elif control_type == "correlation_controls":
#         coin = st.selectbox(
#             "Select Representative Coin",
#             options=rep_coins,
#             index=get_default_index(rep_coins),
#         )
#         if st.button("Find Correlations"):
#             pos, neg, insight = get_top_correlations(top_corr_df, coin)
#             response = f"For **{coin}**, here are the top correlated coins:\n\n**Top 4 Positive:**\n"
#             for _, r in pos.iterrows():
#                 response += f"- {r['Coin']} ({r['Correlation']:.2f})\n"
#             response += "\n**Top 4 Negative:**\n"
#             for _, r in neg.iterrows():
#                 response += f"- {r['Coin']} ({r['Correlation']:.2f})\n"
#             add_assistant_message(response)
#             add_assistant_message(insight)
#             handle_rerun(coin=coin)

#     elif control_type == "high_low_controls":
#         model = st.selectbox("Select Model", options=models)
#         coin = st.selectbox(
#             "Select Representative Coin",
#             options=rep_coins,
#             index=get_default_index(rep_coins),
#         )
#         if st.button("Predict"):
#             high, low, insight = get_forecasted_high_low(model, coin)
#             if high and low:
#                 response = f"Using the **{model}** model for **{coin}**, I predict:\n- **Future High:** ${high['price']:.2f} around {high['date']}\n- **Future Low:** ${low['price']:.2f} around {low['date']}"
#                 add_assistant_message(response)
#                 add_assistant_message(insight)
#             else:
#                 add_assistant_message(
#                     f"Sorry, I couldn't find forecast data for {coin} with the {model} model."
#                 )
#             handle_rerun(coin=coin, model=model)

#     elif control_type == "best_time_controls":
#         model = st.selectbox("Select Model", options=models)
#         coin = st.selectbox(
#             "Select Representative Coin",
#             options=rep_coins,
#             index=get_default_index(rep_coins),
#         )
#         if st.button("Suggest Strategy"):
#             high, low, _ = get_forecasted_high_low(model, coin)
#             suggestion, insight = get_best_purchase_sale(high, low)
#             if isinstance(suggestion, dict):
#                 response = f"Based on the **{model}** forecast for **{coin}**:\n- **Suggested Purchase:** Around {suggestion['buy_date']} at ~${suggestion['buy_price']:.2f}\n- **Suggested Sale:** Around {suggestion['sell_date']} at ~${suggestion['sell_price']:.2f}\n- **Anticipated Profit:** **${suggestion['profit_per_coin']:.2f} per coin**."
#                 add_assistant_message(response)
#                 add_assistant_message(insight)
#             else:
#                 add_assistant_message(
#                     suggestion if suggestion else "Could not generate a suggestion."
#                 )
#             handle_rerun(coin=coin, model=model)

#     elif control_type == "group_pred_controls":
#         model = st.selectbox("Select Model", options=models)
#         if st.button("Predict Group Trend"):
#             pred_df, insight = get_group_prediction(model, rep_coins)
#             add_assistant_message(
#                 f"Here is the 30-day trend prediction for all representative coins using the **{model}** model:"
#             )
#             add_message("assistant", pred_df, "dataframe")
#             add_assistant_message(insight)
#             handle_rerun(model=model)

#     elif control_type == "confidence_controls":
#         model = st.selectbox("Select Model", options=models)
#         coin = st.selectbox(
#             "Select Representative Coin",
#             options=rep_coins,
#             index=get_default_index(rep_coins),
#         )
#         if st.button("Get Confidence Level"):
#             add_assistant_message(get_confidence_level(model, coin))
#             handle_rerun(coin=coin, model=model)

#     elif control_type == "what_if_controls":
#         coin = st.selectbox(
#             "Select Cryptocurrency",
#             options=all_coins,
#             index=get_default_index(all_coins),
#         )
#         quantity = st.number_input(
#             "Enter quantity of coins:", min_value=0.01, value=1.0, step=0.1
#         )
#         target_price = st.number_input(
#             "Enter your target sell price ($):",
#             min_value=0.01,
#             value=latest_prices.get(coin, 1000.0) * 1.1,
#         )
#         if st.button("Analyze Trade"):
#             add_assistant_message(
#                 calculate_what_if(coin, quantity, target_price, latest_prices)
#             )
#             handle_rerun(coin=coin)

#     elif control_type == "model_comp_controls":
#         coin = st.selectbox(
#             "Select Representative Coin to Compare Models",
#             options=rep_coins,
#             index=get_default_index(rep_coins),
#         )
#         if st.button("Compare Models"):
#             fig, insight = get_model_comparison(coin)
#             if fig:
#                 add_assistant_message(
#                     f"Here is a performance comparison of all models for **{coin}**:"
#                 )
#                 add_message("assistant", fig, "plot")
#                 add_assistant_message(insight)
#             else:
#                 add_assistant_message(insight)
#             handle_rerun(coin=coin)


# # --- Main App Execution Flow ---
# initialize_session_state()

# if prompt := st.chat_input("Your message"):
#     process_user_input(prompt=prompt)

# display_chat_history()

# if st.session_state.awaiting_controls:
#     display_controls(st.session_state.awaiting_controls)

# pages/1_🤖_Chatbot.py

import streamlit as st
import re
import time
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
except FileNotFoundError as e:
    st.error(
        f"Fatal Error: A required data file was not found. Please check your `assets` folder. Error: {e}"
    )
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
    "Compare Model Performance": "model_comp_main",  # This now leads to a sub-menu
}


# --- Session State Management ---
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hi! I am your Crypto Analytics Assistant. How can I help you?",
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

    with st.spinner("Thinking..."):
        time.sleep(0.5)
        st.session_state.awaiting_controls = None
        action_triggered = False

        # 1. Check for CONTEXTUAL follow-up questions first
        if " for " in user_text:
            parts = user_text.split(" for ")
            action_phrase = parts[0].strip()
            entity = parts[1].strip()

            # Find the matching action from our main dictionary
            for main_action_key, control_key in ASSESSMENT_QUESTIONS.items():
                if main_action_key.lower() in action_phrase.lower():
                    st.session_state.last_used_coin = entity
                    st.session_state.awaiting_controls = control_key
                    add_assistant_message(
                        f"Okay, setting up: **{main_action_key} for {entity}**. Please use the controls below."
                    )
                    action_triggered = True
                    break

            # Special case for "Forecast with MODEL for COIN"
            if "Forecast with" in action_phrase:
                model_entity = action_phrase.replace("Forecast with", "").strip()
                st.session_state.last_used_coin = entity
                st.session_state.last_used_model = model_entity
                st.session_state.awaiting_controls = "high_low_controls"
                add_assistant_message(
                    f"Okay, setting up a **High/Low Forecast** for **{entity}** using the **{model_entity}** model. Please confirm below."
                )
                action_triggered = True

        # 2. Check for main assessment questions if no follow-up was triggered
        if not action_triggered and user_text in ASSESSMENT_QUESTIONS:
            action = ASSESSMENT_QUESTIONS[user_text]
            action_triggered = True
            if action == "top_stories_action":
                stories = fetch_top_stories(rep_coins)
                add_assistant_message(
                    "Here are the top stories:\n\n"
                    + "\n\n".join([f"- {s}" for s in stories])
                    if stories
                    else "Sorry, I couldn't fetch news."
                )
                add_assistant_message(
                    "What would you like to do next?",
                    buttons=list(ASSESSMENT_QUESTIONS.keys()),
                )
            elif action == "model_comp_main":
                add_assistant_message(
                    "Great! Do you want to see the overall best model, or compare performance for a specific coin?",
                    buttons=["Show Overall Winner", "Compare for a Specific Coin"],
                )
            elif action == "what_if_controls":
                st.session_state.awaiting_controls = "what_if_controls"
                st.session_state.what_if_step = 1
                st.session_state.what_if_data = {}
                add_assistant_message(
                    "Great! Let's analyze a potential trade. First, which coin are you thinking of?"
                )
            else:
                st.session_state.awaiting_controls = action
                add_assistant_message(
                    f"Okay, I will help with: **{user_text}**. Please use the controls below."
                )

        # 3. Check for Model Comparison sub-menu options
        if not action_triggered:
            if user_text == "Show Overall Winner":
                leaderboard, report = get_model_leaderboard(all_metrics_df)
                add_assistant_message(report)
                add_message("assistant", leaderboard, "dataframe")
                add_assistant_message(
                    "What would you like to do next?",
                    buttons=["Compare for a Specific Coin", "Back to Main Menu"],
                )
                action_triggered = True
            elif user_text == "Compare for a Specific Coin":
                st.session_state.awaiting_controls = "model_comp_controls"
                add_assistant_message(
                    "Which representative coin would you like to compare the models for?"
                )
                action_triggered = True

        # 4. Check for simple commands if still no action
        if not action_triggered:
            if "start over" in user_text_lower:
                reset_conversation()
            elif "main menu" in user_text_lower:
                add_assistant_message(
                    "What would you like to explore?",
                    buttons=list(ASSESSMENT_QUESTIONS.keys()),
                )
            else:
                add_assistant_message(
                    "I'm sorry, I don't recognize that command. Please choose from the options.",
                    buttons=list(ASSESSMENT_QUESTIONS.keys()),
                )


# --- UI Rendering ---
def display_chat_history():
    for msg_index, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            content_type, content = msg.get("content_type", "text"), msg["content"]
            if content_type == "text":
                st.markdown(content)
            elif content_type == "plot":
                st.plotly_chart(
                    content, use_container_width=True, key=f"chart_{msg_index}"
                )
            elif content_type == "dataframe":
                st.dataframe(content, use_container_width=True, key=f"df_{msg_index}")
            if msg.get("buttons"):
                num_buttons, cols_per_row = len(msg["buttons"]), (
                    3 if len(msg["buttons"]) > 2 else len(msg["buttons"])
                )
                if cols_per_row > 0:
                    rows_of_cols = [
                        st.columns(cols_per_row)
                        for _ in range((num_buttons + cols_per_row - 1) // cols_per_row)
                    ]
                    for i, label in enumerate(msg["buttons"]):
                        button_key = f"btn_{msg_index}_{i}_{label}"
                        row, col = i // cols_per_row, i % cols_per_row
                        rows_of_cols[row][col].button(
                            label,
                            key=button_key,
                            on_click=process_user_input,
                            kwargs={"button_label": label},
                        )


def display_controls(control_type):
    st.markdown("---")
    st.subheader("Analysis Controls")
    models = ["ARIMA", "PROPHET", "LSTM", "RF", "XGB"]

    def handle_rerun(coin=None, model=None, best_model_for_coin=None):
        if coin:
            st.session_state.last_used_coin = coin
        if model:
            st.session_state.last_used_model = model
        follow_up_buttons = []
        if best_model_for_coin and coin:
            follow_up_buttons.append(f"Forecast with {best_model_for_coin} for {coin}")
        if coin:
            follow_up_buttons.append(f"Show Moving Average for {coin}")
        follow_up_buttons.append("Show Overall Winner")
        follow_up_buttons.append("Back to Main Menu")
        add_assistant_message(
            "Analysis complete. What would you like to do next?",
            buttons=follow_up_buttons,
        )
        st.session_state.awaiting_controls = None
        st.rerun()

    def get_default_index(options_list, for_coin=True):
        item = (
            st.session_state.last_used_coin
            if for_coin
            else st.session_state.last_used_model
        )
        return options_list.index(item) if item and item in options_list else 0

    # Consolidate standard controls
    is_standard_control = control_type not in [
        "what_if_controls",
        "model_comp_controls",
        "group_pred_controls",
    ]

    if is_standard_control:
        coin_options = (
            rep_coins
            if control_type
            in [
                "correlation_controls",
                "high_low_controls",
                "best_time_controls",
                "confidence_controls",
            ]
            else all_coins
        )
        coin = st.selectbox(
            "Select Cryptocurrency",
            options=coin_options,
            index=get_default_index(coin_options),
        )
        model = None
        if control_type in [
            "high_low_controls",
            "best_time_controls",
            "confidence_controls",
        ]:
            model = st.selectbox(
                "Select Model",
                options=models,
                index=get_default_index(models, for_coin=False),
            )

        if st.button("Generate Analysis"):
            if control_type == "trend_controls":
                fig, insight = plot_trend_chart(main_df, coin)
                add_message("assistant", fig, "plot")
                add_assistant_message(insight)
                handle_rerun(coin=coin)
            elif control_type == "ma_controls":
                fig, insight = plot_moving_average_chart(main_df, coin)
                add_message("assistant", fig, "plot")
                add_assistant_message(insight)
                handle_rerun(coin=coin)
            elif control_type == "correlation_controls":
                pos, neg, insight = get_top_correlations(top_corr_df, coin)
                response = (
                    f"For **{coin}**, here are the top correlated coins:\n\n**Top 4 Positive:**\n"
                    + "".join(
                        [
                            f"- {r['Coin']} ({r['Correlation']:.2f})\n"
                            for _, r in pos.iterrows()
                        ]
                    )
                )
                response += "\n**Top 4 Negative:**\n" + "".join(
                    [
                        f"- {r['Coin']} ({r['Correlation']:.2f})\n"
                        for _, r in neg.iterrows()
                    ]
                )
                add_assistant_message(response)
                add_assistant_message(insight)
                handle_rerun(coin=coin)
            elif control_type == "high_low_controls":
                high, low, insight = get_forecasted_high_low(model, coin)
                if high and low:
                    response = f"Using the **{model}** model for **{coin}**, I predict:\n- **Future High:** ${high['price']:.2f} around {high['date']}\n- **Future Low:** ${low['price']:.2f} around {low['date']}"
                    add_assistant_message(response)
                    add_assistant_message(insight)
                else:
                    add_assistant_message(f"Sorry, couldn't find forecast data.")
                handle_rerun(coin=coin, model=model)
            elif control_type == "best_time_controls":
                high, low, _ = get_forecasted_high_low(model, coin)
                suggestion, insight = get_best_purchase_sale(high, low)
                if isinstance(suggestion, dict):
                    response = f"Based on the **{model}** forecast for **{coin}**:\n- **Suggested Purchase:** Around {suggestion['buy_date']} at ~${suggestion['buy_price']:.2f}\n- **Suggested Sale:** Around {suggestion['sell_date']} at ~${suggestion['sell_price']:.2f}\n- **Anticipated Profit:** **${suggestion['profit_per_coin']:.2f} per coin**."
                    add_assistant_message(response)
                    add_assistant_message(insight)
                else:
                    add_assistant_message(
                        suggestion or "Could not generate suggestion."
                    )
                handle_rerun(coin=coin, model=model)
            elif control_type == "confidence_controls":
                add_assistant_message(get_confidence_level(model, coin))
                handle_rerun(coin=coin, model=model)

    elif control_type == "what_if_controls":
        if st.session_state.what_if_step == 1:
            coin = st.selectbox(
                "Select Cryptocurrency",
                options=all_coins,
                index=get_default_index(all_coins),
            )
            if st.button("Next: Set Quantity"):
                st.session_state.what_if_data["coin"] = coin
                st.session_state.what_if_step = 2
                add_user_message(f"Selected coin: {coin}")
                add_assistant_message(f"Okay, **{coin}**. How many coins?")
                st.rerun()
        elif st.session_state.what_if_step == 2:
            quantity = st.number_input(
                "Enter quantity:", min_value=0.01, value=1.0, step=0.1
            )
            if st.button("Next: Set Target Price"):
                st.session_state.what_if_data["quantity"] = quantity
                st.session_state.what_if_step = 3
                add_user_message(f"Quantity: {quantity}")
                add_assistant_message(
                    f"Got it, **{quantity}** coins. What is your target sell price ($)?"
                )
                st.rerun()
        elif st.session_state.what_if_step == 3:
            coin = st.session_state.what_if_data["coin"]
            target_price = st.number_input(
                "Enter target price ($):",
                min_value=0.01,
                value=latest_prices.get(coin, 1.0) * 1.1,
            )
            if st.button("Analyze Trade"):
                st.session_state.what_if_data["target_price"] = target_price
                add_user_message(f"Target Price: ${target_price:,.2f}")
                result = calculate_what_if(
                    coin,
                    st.session_state.what_if_data["quantity"],
                    target_price,
                    latest_prices,
                )
                add_assistant_message(result)
                st.session_state.what_if_step = 0
                st.session_state.what_if_data = {}
                handle_rerun(coin=coin)

    elif control_type == "group_pred_controls":
        model = st.selectbox(
            "Select Model",
            options=models,
            index=get_default_index(models, for_coin=False),
        )
        if st.button("Predict Group Trend"):
            pred_df, insight = get_group_prediction(model, rep_coins)
            add_assistant_message(
                f"Here is the 30-day trend prediction for all representative coins using the **{model}** model:"
            )
            add_message("assistant", pred_df, "dataframe")
            add_assistant_message(insight)
            handle_rerun(model=model)

    elif control_type == "model_comp_controls":
        coin = st.selectbox(
            "Select Representative Coin",
            options=rep_coins,
            index=get_default_index(rep_coins),
        )
        if st.button("Compare Models"):
            fig, insight, best_model = get_model_comparison(coin)
            if fig:
                add_assistant_message(
                    f"Here is the performance comparison for **{coin}**:"
                )
                add_message("assistant", fig, "plot")
                add_assistant_message(insight)
            else:
                add_assistant_message(insight)
            handle_rerun(coin=coin, best_model_for_coin=best_model)


# --- Main App Execution Flow ---
initialize_session_state()
if prompt := st.chat_input("Your message"):
    process_user_input(prompt=prompt)
display_chat_history()
if st.session_state.awaiting_controls:
    display_controls(st.session_state.awaiting_controls)
