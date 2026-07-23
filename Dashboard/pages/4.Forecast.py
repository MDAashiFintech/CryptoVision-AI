# import streamlit as st
# import pandas as pd
# import numpy as np
# import plotly.graph_objs as go
# import os
# import base64


# def image_to_base64(img_path):
#     with open(img_path, "rb") as img_file:
#         return base64.b64encode(img_file.read()).decode()


# MODEL_NAMES = {
#     "ARIMA": "ARIMA (Auto-Regressive Integrated Moving Average)",
#     "LSTM": "LSTM (Long Short-Term Memory Neural Net)",
#     "RF": "Random Forest",
#     "XGB": "XGBoost (Extreme Gradient Boosting)",
#     "PROPHET": "Prophet (Facebook Prophet)",
# }

# COIN_INFO = {
#     "BTC-USD": ("Bitcoin", "₿"),
#     "BCH-USD": ("Bitcoin Cash", "🪙"),
#     "ADA-USD": ("Cardano", "₳"),
#     "BETH-USD": ("Beacon ETH", "⚡"),
#     "LINK-USD": ("Chainlink", "🔗"),
#     "STETH-USD": ("Staked ETH", "🦄"),
# }

# PNG_PATHS = {
#     "BTC-USD": "assets/BTC.png",
#     "BCH-USD": "assets/BCH.png",
#     "ADA-USD": "assets/ADA.png",
#     "STETH-USD": "assets/STETH.png",
#     "BETH-USD": "assets/BETH.png",
#     "LINK-USD": "assets/LINK.png",
# }

# CARD_ICONS = {
#     "signal": "assets/signal.png",
#     "performance": "assets/chart.png",
#     "summary": "assets/summary.png",
# }

# st.title("Forecast: Crypto Price Prediction")
# st.markdown("---")

# assets_folder = "assets"
# arima_base_path = os.path.join(assets_folder, "Arima_csv", "separate_coins")
# prophet_base_path = os.path.join(assets_folder, "Prophet_csv", "separate_coins")
# lstm_base_path = os.path.join(assets_folder, "LSTM_csv", "separate_coins")
# rf_base_path = os.path.join(assets_folder, "RandomForest_csv", "separate_coins")
# xgb_base_path = os.path.join(assets_folder, "XGBoost_csv", "separate_coins")
# rep_coins_path = os.path.join(assets_folder, "representative_coins.csv")

# metrics_arima_file = os.path.join(arima_base_path, "arima_metrics_summary.csv")
# metrics_prophet_file = os.path.join(prophet_base_path, "prophet_metrics_summary.csv")
# metrics_lstm_file = os.path.join(lstm_base_path, "lstm_metrics_summary.csv")
# metrics_rf_file = os.path.join(rf_base_path, "rf_metrics_summary.csv")
# metrics_xgb_file = os.path.join(xgb_base_path, "xgb_metrics_summary.csv")

# rep_df = pd.read_csv(rep_coins_path)
# rep_coins = rep_df["Representative_Coin"].tolist()
# COINS = rep_coins

# MODELS = [MODEL_NAMES.get(k, k) for k in MODEL_NAMES.keys()]
# model_full = st.selectbox("Choose a model", MODELS)
# coin = st.selectbox("Choose a currency", COINS)


# def model_shortname(fullname):
#     for k, v in MODEL_NAMES.items():
#         if fullname.startswith(v):
#             return k
#     if fullname in MODEL_NAMES.values():
#         for k, v in MODEL_NAMES.items():
#             if fullname == v:
#                 return k
#     return fullname


# model_short = model_shortname(model_full)


# def check_and_rename(df, expected_cols):
#     df_cols_lower = [c.lower() for c in df.columns]
#     rename_map = {}
#     for col in expected_cols:
#         if col not in df.columns:
#             if col.lower() in df_cols_lower:
#                 matched_col = df.columns[df_cols_lower.index(col.lower())]
#                 rename_map[matched_col] = col
#             else:
#                 df[col] = pd.NA
#     if rename_map:
#         df.rename(columns=rename_map, inplace=True)
#     return df


# # ----------- MARKET STATE / TREND PREDICTION (NEW SECTION) -----------
# st.markdown("## 🟢 Market State Prediction (Trend for All Representatives)")
# ms_col1, ms_col2 = st.columns([2, 5])

# # Trend window selector
# with ms_col1:
#     trend_days_options = {"1 Week": 7, "15 Days": 15, "1 Month/30 Days": 30}
#     trend_days_label = st.selectbox(
#         "Select forecast window for state prediction:",
#         list(trend_days_options.keys()),
#         index=2,
#         key="market_state_window",
#     )
#     trend_n_days = trend_days_options[trend_days_label]

# # Identify base path for all coins' forecast of selected model
# if model_short == "ARIMA":
#     trend_base_path = arima_base_path
# elif model_short == "PROPHET":
#     trend_base_path = prophet_base_path
# elif model_short == "LSTM":
#     trend_base_path = lstm_base_path
# elif model_short == "RF":
#     trend_base_path = rf_base_path
# elif model_short == "XGB":
#     trend_base_path = xgb_base_path
# else:
#     trend_base_path = None

# coin_trends = []

# if trend_base_path is not None:
#     for rep_coin in rep_coins:
#         ffile = os.path.join(trend_base_path, f"{rep_coin}_future_forecast.csv")
#         try:
#             fdf = pd.read_csv(ffile, parse_dates=["Date"])
#             fdf = check_and_rename(fdf, ["Date", "Predicted", "Signal"])
#             if len(fdf) >= trend_n_days:
#                 p_start = fdf.loc[0, "Predicted"]
#                 p_end = fdf.loc[trend_n_days - 1, "Predicted"]
#                 pct_change = (
#                     ((p_end - p_start) / abs(p_start)) * 100 if p_start != 0 else np.nan
#                 )
#                 state = (
#                     "Bullish"
#                     if pct_change > 0
#                     else "Bearish" if pct_change < 0 else "Neutral"
#                 )
#                 coin_trends.append(
#                     {
#                         "Coin": rep_coin,
#                         "Start Price": round(p_start, 4),
#                         "End Price": round(p_end, 4),
#                         "Percent Change (%)": round(pct_change, 2),
#                         "State": state,
#                     }
#                 )
#             else:
#                 coin_trends.append(
#                     {
#                         "Coin": rep_coin,
#                         "Start Price": np.nan,
#                         "End Price": np.nan,
#                         "Percent Change (%)": np.nan,
#                         "State": "No Data",
#                     }
#                 )
#         except Exception:
#             coin_trends.append(
#                 {
#                     "Coin": rep_coin,
#                     "Start Price": np.nan,
#                     "End Price": np.nan,
#                     "Percent Change (%)": np.nan,
#                     "State": "No Data",
#                 }
#             )

# trend_df = pd.DataFrame(coin_trends)
# with ms_col2:
#     st.dataframe(
#         trend_df.style.background_gradient(
#             cmap="RdYlGn", subset=["Percent Change (%)"]
#         ),
#         use_container_width=True,
#     )

# n_bullish = (trend_df["State"] == "Bullish").sum()
# n_bearish = (trend_df["State"] == "Bearish").sum()
# n_neutral = (trend_df["State"] == "Neutral").sum()
# n_total = len(trend_df)

# if n_bullish > n_bearish:
#     market_msg = f"🟩 <b>Portfolio Market State:</b> <span style='color:#16A085'>Bullish</span> ({n_bullish} / {n_total} coins forecasted to rise)"
# elif n_bearish > n_bullish:
#     market_msg = f"🟥 <b>Portfolio Market State:</b> <span style='color:#C0392B'>Bearish</span> ({n_bearish} / {n_total} coins forecasted to fall)"
# else:
#     market_msg = f"🟨 <b>Portfolio Market State:</b> <span style='color:#F1C40F'>Mixed or Neutral</span>"

# st.markdown(
#     f"<div style='font-size:1.15em;margin-top:-10px;'>{market_msg}</div>",
#     unsafe_allow_html=True,
# )
# st.markdown("---")
# # ------------------------------------------------------------------

# # ---- SINGLE CURRENCY FORECAST DETAIL (unchanged below) -----------

# metrics_row = None

# if model_short == "ARIMA":
#     base_path = arima_base_path
#     metrics_file = metrics_arima_file
# elif model_short == "PROPHET":
#     base_path = prophet_base_path
#     metrics_file = metrics_prophet_file
# elif model_short == "LSTM":
#     base_path = lstm_base_path
#     metrics_file = metrics_lstm_file
# elif model_short == "RF":
#     base_path = rf_base_path
#     metrics_file = metrics_rf_file
# elif model_short == "XGB":
#     base_path = xgb_base_path
#     metrics_file = metrics_xgb_file
# else:
#     base_path = None
#     metrics_file = None

# if base_path:
#     hist_file = os.path.join(base_path, f"{coin}_historical_forecast.csv")
#     test_file = os.path.join(base_path, f"{coin}_test_forecast.csv")
#     future_file = os.path.join(base_path, f"{coin}_future_forecast.csv")

#     if (
#         os.path.exists(hist_file)
#         and os.path.exists(test_file)
#         and os.path.exists(future_file)
#     ):
#         hist_df = pd.read_csv(hist_file, parse_dates=["Date"])
#         hist_df = check_and_rename(hist_df, ["Date", "Actual", "Predicted", "Signal"])

#         test_df = pd.read_csv(test_file, parse_dates=["Date"])
#         test_df = check_and_rename(test_df, ["Date", "Actual", "Predicted", "Signal"])

#         future_df = pd.read_csv(future_file, parse_dates=["Date"])
#         future_df = check_and_rename(future_df, ["Date", "Predicted", "Signal"])
#         if "Actual" not in future_df.columns:
#             future_df["Actual"] = pd.NA

#         # --- Forecasted High/Low display for all models ---
#         high_idx = future_df["Predicted"].idxmax()
#         low_idx = future_df["Predicted"].idxmin()

#         high_date = future_df.loc[high_idx, "Date"].date()
#         high_price = future_df.loc[high_idx, "Predicted"]

#         low_date = future_df.loc[low_idx, "Date"].date()
#         low_price = future_df.loc[low_idx, "Predicted"]

#         st.info(
#             f"**{model_short} Model Forecasted HIGH:** ${high_price:.2f} on {high_date}"
#         )
#         st.info(
#             f"**{model_short} Model Forecasted LOW:** ${low_price:.2f} on {low_date}"
#         )

#     else:
#         st.error(f"{model_short} forecast files for selected coin not found.")
#         st.stop()

#     if metrics_file and os.path.exists(metrics_file):
#         metrics_df = pd.read_csv(metrics_file)
#         if coin in metrics_df["Coin"].values:
#             metrics_row = metrics_df[metrics_df["Coin"] == coin].iloc[0]

#     dff = pd.concat(
#         [
#             hist_df.loc[:, ["Date", "Actual", "Predicted", "Signal"]],
#             test_df.loc[:, ["Date", "Actual", "Predicted", "Signal"]],
#         ],
#         ignore_index=True,
#     )
#     future_df = future_df.loc[:, ["Date", "Actual", "Predicted", "Signal"]]
#     dff = pd.concat([dff, future_df], ignore_index=True)
# else:
#     dff = pd.DataFrame()

# if not dff.empty:
#     st.markdown("### Chart Options")
#     show_future = st.checkbox(f"Show {model_short} Future 30-Day Forecast", value=False)

#     if not show_future:
#         date_options = {"1D": 1, "1W": 7, "1M/30D": 30, "All": None}
#         date_selected = st.radio(
#             "Filter date range:", list(date_options.keys()), index=3, horizontal=True
#         )
#         max_date = dff["Date"].max()
#         if date_options[date_selected]:
#             min_date = max_date - pd.Timedelta(days=date_options[date_selected] - 1)
#             chart_df = dff[dff["Date"] >= min_date].copy()
#         else:
#             chart_df = dff.copy()

#         chart_df["Short_MA"] = (
#             chart_df["Actual"].rolling(window=7, min_periods=1).mean()
#         )
#         chart_df["Long_MA"] = (
#             chart_df["Actual"].rolling(window=30, min_periods=1).mean()
#         )

#         buy_mask = chart_df["Signal"].str.lower() == "buy"
#         sell_mask = chart_df["Signal"].str.lower() == "sell"

#         fig = go.Figure()
#         fig.add_trace(
#             go.Scatter(
#                 x=chart_df["Date"],
#                 y=chart_df["Actual"],
#                 mode="lines",
#                 name="Actual Price",
#                 line=dict(color="blue"),
#             )
#         )
#         fig.add_trace(
#             go.Scatter(
#                 x=chart_df["Date"],
#                 y=chart_df["Predicted"],
#                 mode="lines",
#                 name="Predicted Price",
#                 line=dict(color="orange", dash="dash"),
#             )
#         )
#         fig.add_trace(
#             go.Scatter(
#                 x=chart_df["Date"],
#                 y=chart_df["Short_MA"],
#                 mode="lines",
#                 name="Short-term MA",
#                 line=dict(color="purple", dash="dot"),
#             )
#         )
#         fig.add_trace(
#             go.Scatter(
#                 x=chart_df["Date"],
#                 y=chart_df["Long_MA"],
#                 mode="lines",
#                 name="Long-term MA",
#                 line=dict(color="orange", dash="dot"),
#             )
#         )
#         fig.add_trace(
#             go.Scatter(
#                 x=chart_df["Date"][buy_mask],
#                 y=chart_df["Actual"][buy_mask],
#                 mode="markers",
#                 name="Buy Signal",
#                 marker=dict(color="green", size=10, symbol="circle"),
#             )
#         )
#         fig.add_trace(
#             go.Scatter(
#                 x=chart_df["Date"][sell_mask],
#                 y=chart_df["Actual"][sell_mask],
#                 mode="markers",
#                 name="Sell Signal",
#                 marker=dict(color="red", size=10, symbol="circle"),
#             )
#         )
#     else:
#         future_options = {"1 Week": 7, "15 Days": 15, "1 Month/30 Days": 30}
#         future_period_selected = st.radio(
#             "Show future forecast for:",
#             list(future_options.keys()),
#             index=2,
#             horizontal=True,
#         )
#         future_days = future_options[future_period_selected]

#         last_actual_date = dff["Date"][dff["Actual"].notna()].max()
#         chart_df = dff[dff["Date"] <= last_actual_date].copy()
#         future_df_chart = dff[
#             (dff["Date"] > last_actual_date)
#             & (dff["Date"] <= last_actual_date + pd.Timedelta(days=future_days))
#         ].copy()
#         chart_df["Short_MA"] = (
#             chart_df["Actual"].rolling(window=7, min_periods=1).mean()
#         )
#         chart_df["Long_MA"] = (
#             chart_df["Actual"].rolling(window=30, min_periods=1).mean()
#         )
#         buy_mask = chart_df["Signal"].str.lower() == "buy"
#         sell_mask = chart_df["Signal"].str.lower() == "sell"

#         fig = go.Figure()
#         fig.add_trace(
#             go.Scatter(
#                 x=chart_df["Date"],
#                 y=chart_df["Actual"],
#                 mode="lines",
#                 name="Actual Price",
#                 line=dict(color="blue"),
#             )
#         )
#         fig.add_trace(
#             go.Scatter(
#                 x=future_df_chart["Date"],
#                 y=future_df_chart["Predicted"],
#                 mode="lines",
#                 name="Future Forecast",
#                 line=dict(color="green", dash="dot"),
#                 fill="tozeroy",
#                 fillcolor="rgba(0,200,0,0.1)",
#             )
#         )
#         fig.add_trace(
#             go.Scatter(
#                 x=chart_df["Date"],
#                 y=chart_df["Short_MA"],
#                 mode="lines",
#                 name="Short-term MA",
#                 line=dict(color="purple", dash="dot"),
#             )
#         )
#         fig.add_trace(
#             go.Scatter(
#                 x=chart_df["Date"],
#                 y=chart_df["Long_MA"],
#                 mode="lines",
#                 name="Long-term MA",
#                 line=dict(color="orange", dash="dash"),
#             )
#         )
#         fig.add_trace(
#             go.Scatter(
#                 x=chart_df["Date"][buy_mask],
#                 y=chart_df["Actual"][buy_mask],
#                 mode="markers",
#                 name="Buy Signal",
#                 marker=dict(color="green", size=10, symbol="circle"),
#             )
#         )
#         fig.add_trace(
#             go.Scatter(
#                 x=chart_df["Date"][sell_mask],
#                 y=chart_df["Actual"][sell_mask],
#                 mode="markers",
#                 name="Sell Signal",
#                 marker=dict(color="red", size=10, symbol="circle"),
#             )
#         )

#     fig.update_layout(
#         title=f"{MODEL_NAMES.get(model_short, model_short)} Forecast for {COIN_INFO.get(coin, (coin, ''))[0]}",
#         xaxis=dict(type="date"),
#         yaxis_title="Price",
#         legend=dict(orientation="h", x=0.01, y=1.13),
#     )
#     st.plotly_chart(fig, use_container_width=True)

#     # # ---------- Scenario Analysis / What If? Section ---------------
#     st.markdown("## Scenario Analysis - What If?")
#     quantity = st.number_input("Enter quantity of coins:", min_value=0.0, value=1.0)
#     valid_actuals = chart_df["Actual"].dropna()
#     current_price = valid_actuals.iloc[-1] if not valid_actuals.empty else None

#     if current_price is None:
#         st.warning("Current price data unavailable for scenario analysis.")
#     else:
#         target_price = st.number_input(
#             "Enter hypothetical target sell price ($):",
#             min_value=0.0,
#             value=float(current_price),
#         )
#         potential_profit = (target_price - current_price) * quantity
#         profit_color = "#27ae60" if potential_profit >= 0 else "#c0392b"
#         st.markdown(
#             f"""
#             <div style="background:#e7f5e6; border-radius:10px; padding:15px; max-width:400px;">
#                 <h4>Potential Profit/Loss</h4>
#                 <p style="font-size:1.5em; color:{profit_color}; font-weight:bold;">
#                     ${potential_profit:,.2f}
#                 </p>
#                 <p>Based on buying {quantity} coins at current price ${current_price:,.2f} and selling at target price ${target_price:,.2f}.</p>
#             </div>
#             """,
#             unsafe_allow_html=True,
#         )

#     # # ---------------------- End What-If Section -------------------

#     buy_count = buy_mask.sum()
#     sell_count = sell_mask.sum()
#     last_buy_date = (
#         chart_df["Date"][buy_mask].max().strftime("%Y-%m-%d") if buy_count > 0 else "-"
#     )
#     last_sell_date = (
#         chart_df["Date"][sell_mask].max().strftime("%Y-%m-%d")
#         if sell_count > 0
#         else "-"
#     )
#     signal_icon_b64 = image_to_base64(CARD_ICONS["signal"])
#     signal_card_html = f"""
#     <div style="background-color:#e8f7ef;border-radius:10px;padding:18px 24px;margin-bottom:18px;box-shadow:0 2px 8px #eee9;">
#         <div style="display:flex;align-items:center;margin-bottom:8px;">
#             <img src="data:image/png;base64,{signal_icon_b64}" style="height:28px;width:28px;margin-right:12px;">
#             <span style="font-size:1.13em;font-weight:600;">Signal Summary</span>
#         </div>
#         <div>
#             <ul style="list-style-type:none;padding-left:0;margin-top:8px;">
#                 <li><strong>Buys:</strong> <span style='color:#207850;'>{buy_count}</span> &nbsp; | &nbsp; <strong>Latest Buy:</strong> {last_buy_date}</li>
#                 <li><strong>Sells:</strong> <span style='color:#c81d1d;'>{sell_count}</span> &nbsp; | &nbsp; <strong>Latest Sell:</strong> {last_sell_date}</li>
#             </ul>
#         </div>
#     </div>
#     """
#     st.markdown(signal_card_html, unsafe_allow_html=True)

#     performance_icon_b64 = image_to_base64(CARD_ICONS["performance"])
#     perf_card_style = "background-color:#f9f9fc;border-radius:10px;padding:18px 24px;margin-bottom:18px;box-shadow:0 2px 8px #8883;"

#     if metrics_row is not None:
#         rmse = metrics_row.get("RMSE", None)
#         mae = metrics_row.get("MAE", None)
#         r2 = metrics_row.get("R2", None)
#         mape = metrics_row.get("MAPE", None)
#         performance_card_html = f"""
#         <div style="{perf_card_style}">
#             <div style="display:flex;align-items:center;margin-bottom:8px;">
#                 <img src="data:image/png;base64,{performance_icon_b64}" style="height:28px;width:28px;margin-right:12px;">
#                 <span style="font-size:1.13em;font-weight:600;">Model Performance</span>
#             </div>
#             <ul style='list-style-type:none;padding-left:0;margin-top:8px;'>
#                 <li><strong>RMSE:</strong> {rmse:.2f}</li>
#                 <li><strong>MAE:</strong> {mae:.2f}</li>
#                 <li><strong>MAPE:</strong> {mape:.2f}%</li>
#                 <li><strong>R²:</strong> {r2:.2f}</li>
#             </ul>
#         </div>
#         """
#     else:
#         performance_card_html = f"""
#         <div style="{perf_card_style}">
#             <em>Metrics not found for this coin/model.</em>
#         </div>
#         """
#     st.markdown(performance_card_html, unsafe_allow_html=True)

#     summary_icon_b64 = image_to_base64(CARD_ICONS["summary"])
#     summary_card_style = "background-color:#fffcee;border-radius:10px;padding:18px 24px;margin-bottom:18px;box-shadow:0 2px 8px #ddd6;"

#     if metrics_row is not None:
#         summary_text = (
#             f"The {MODEL_NAMES.get(model_short, model_short)} model for {COIN_INFO.get(coin, (coin, ''))[0]} achieved "
#             f"RMSE of {rmse:.2f}, MAE of {mae:.2f}, MAPE of {mape:.2f}%, R² of {r2:.2f}. "
#             f"Lower RMSE and MAE indicate higher accuracy. R² closer to 1 suggests excellent fit. "
#             f"MAPE under 20% is generally good for financial forecasts."
#         )
#     else:
#         summary_text = "No metrics available for this model & currency."

#     summary_card_html = f"""
#     <div style="{summary_card_style}">
#         <div style="display:flex;align-items:center;margin-bottom:8px;">
#             <img src="data:image/png;base64,{summary_icon_b64}" style="height:28px;width:28px;margin-right:12px;">
#             <span style="font-size:1.13em;font-weight:600;">Executive Summary</span>
#         </div>
#         <div style='margin-top:6px;'>{summary_text}</div>
#     </div>
#     """
#     st.markdown(summary_card_html, unsafe_allow_html=True)

#     st.markdown("---")
#     st.markdown("### Detailed Results")
#     st.dataframe(
#         chart_df[["Date", "Actual", "Predicted", "Short_MA", "Long_MA", "Signal"]]
#     )
#     st.markdown("---")
#     st.markdown("### Download Forecast Data")
#     csv_data = chart_df.to_csv(index=False, encoding="utf-8")
#     st.download_button(
#         "Download results as CSV",
#         csv_data,
#         f"{model_full}_{coin}_forecast.csv",
#         "text/csv",
#     )
# else:
#     st.error("No results found for selected model/currency.")

# pages/Forecast.py

# pages/Forecast.py

# pages/Forecast.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import os
import base64

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Crypto Forecast", page_icon="📈", layout="wide")


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
PNG_PATHS = {
    "BTC-USD": "assets/BTC.png",
    "BCH-USD": "assets/BCH.png",
    "ADA-USD": "assets/ADA.png",
    "STETH-USD": "assets/STETH.png",
    "BETH-USD": "assets/BETH.png",
    "LINK-USD": "assets/LINK.png",
}
CARD_ICONS = {
    "signal": "assets/signal.png",
    "performance": "assets/chart.png",
    "summary": "assets/summary.png",
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


# --- NEW: Signal Filtering Algorithm ---
def filter_significant_signals(df, window_size=5):
    """
    Identifies only the most significant buy/sell signals.
    A buy signal is significant if it's the lowest actual price in a rolling window.
    A sell signal is significant if it's the highest actual price in a rolling window.
    """
    df["is_buy"] = df["Signal"].str.lower() == "buy"
    df["is_sell"] = df["Signal"].str.lower() == "sell"

    df["rolling_min"] = df["Actual"].rolling(window=window_size, center=True).min()
    df["rolling_max"] = df["Actual"].rolling(window=window_size, center=True).max()

    significant_buys = df[(df["is_buy"]) & (df["Actual"] == df["rolling_min"])]
    significant_sells = df[(df["is_sell"]) & (df["Actual"] == df["rolling_max"])]

    return significant_buys, significant_sells


# --- DATA LOADING ---
assets_folder = "assets"
try:
    rep_df = pd.read_csv(os.path.join(assets_folder, "representative_coins.csv"))
    rep_coins = rep_df["Representative_Coin"].tolist()
except FileNotFoundError:
    st.error("`representative_coins.csv` not found in `assets` folder.")
    st.stop()

# --- SIDEBAR CONTROLS ---
st.sidebar.title("Forecasting Controls")
st.sidebar.markdown("Select a model and cryptocurrency to generate a forecast.")
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
st.markdown(
    f"Using the **{model_full}** model to predict future price movements and generate trading signals."
)

# --- DATA PATHS & FILE LOADING ---
base_path_map = {
    "ARIMA": os.path.join(assets_folder, "Arima_csv", "separate_coins"),
    "PROPHET": os.path.join(assets_folder, "Prophet_csv", "separate_coins"),
    "LSTM": os.path.join(assets_folder, "LSTM_csv", "separate_coins"),
    "RF": os.path.join(assets_folder, "RandomForest_csv", "separate_coins"),
    "XGB": os.path.join(assets_folder, "XGBoost_csv", "separate_coins"),
}
base_path = base_path_map.get(model_short)
metrics_file = (
    os.path.join(base_path, f"{model_short.lower()}_metrics_summary.csv")
    if base_path
    else None
)
if not base_path:
    st.error("Selected model path not found.")
    st.stop()
try:
    hist_df = pd.read_csv(
        os.path.join(base_path, f"{coin}_historical_forecast.csv"), parse_dates=["Date"]
    )
    test_df = pd.read_csv(
        os.path.join(base_path, f"{coin}_test_forecast.csv"), parse_dates=["Date"]
    )
    future_df = pd.read_csv(
        os.path.join(base_path, f"{coin}_future_forecast.csv"), parse_dates=["Date"]
    )
except FileNotFoundError:
    st.error(
        f"Forecast data for **{coin}** with the **{model_short}** model not found."
    )
    st.stop()
dff = pd.concat([hist_df, test_df, future_df], ignore_index=True)
dff = check_and_rename(dff, ["Date", "Actual", "Predicted", "Signal"])

# --- KEY METRICS ---
st.markdown("---")
col1, col2 = st.columns(2)
high_price, high_date = future_df["Predicted"].max(), future_df.loc[
    future_df["Predicted"].idxmax(), "Date"
].strftime("%Y-%m-%d")
low_price, low_date = future_df["Predicted"].min(), future_df.loc[
    future_df["Predicted"].idxmin(), "Date"
].strftime("%Y-%m-%d")
with col1:
    st.markdown(
        f"""<div style="background-color:#E8F8F5;border-left:5px solid #1ABC9C;border-radius:5px;padding:20px;"><h4 style="margin:0;color:#1ABC9C;">Predicted High 🔼</h4><p style="font-size:2em;font-weight:bold;margin:10px 0;">${high_price:,.2f}</p><p style="margin:0;color:#555;">Around: <strong>{high_date}</strong></p></div>""",
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f"""<div style="background-color:#FDEDEC;border-left:5px solid #E74C3C;border-radius:5px;padding:20px;"><h4 style="margin:0;color:#E74C3C;">Predicted Low 🔽</h4><p style="font-size:2em;font-weight:bold;margin:10px 0;">${low_price:,.2f}</p><p style="margin:0;color:#555;">Around: <strong>{low_date}</strong></p></div>""",
        unsafe_allow_html=True,
    )

# --- MAIN CHARTING AREA ---
st.markdown("---")
st.subheader("Interactive Forecast Chart")
chart_options_cols = st.columns([2, 3])
with chart_options_cols[0]:
    show_future = st.toggle("Show Future 30-Day Forecast", value=False)
with chart_options_cols[1]:
    if show_future:
        future_options = {"1 Week": 7, "15 Days": 15, "1 Month": 30}
        future_period_selected = st.radio(
            "Future Window:", list(future_options.keys()), index=2, horizontal=True
        )
        future_days = future_options[future_period_selected]
    else:
        date_options = {
            "1 Week": 7,
            "1 Month": 30,
            "6 Months": 180,
            "All History": None,
        }
        date_selected = st.radio(
            "Historical Window:", list(date_options.keys()), index=1, horizontal=True
        )

fig = go.Figure()
if show_future:
    last_actual_date = dff["Date"][dff["Actual"].notna()].max()
    chart_df = dff[dff["Date"] <= last_actual_date]
    future_df_chart = dff[
        (dff["Date"] > last_actual_date)
        & (dff["Date"] <= last_actual_date + pd.Timedelta(days=future_days))
    ]
    fig.add_trace(
        go.Scatter(
            x=chart_df["Date"],
            y=chart_df["Actual"],
            mode="lines",
            name="Actual Price",
            line=dict(color="#3498DB", width=2.5),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=future_df_chart["Date"],
            y=future_df_chart["Predicted"],
            mode="lines",
            name="Future Forecast",
            line=dict(color="#2ECC71", dash="dot", width=2.5),
            fill="tozeroy",
            fillcolor="rgba(46, 204, 113, 0.1)",
        )
    )
else:
    chart_df = dff[dff["Actual"].notna()].copy()
    if date_options[date_selected]:
        min_date = chart_df["Date"].max() - pd.Timedelta(
            days=date_options[date_selected]
        )
        chart_df = chart_df[chart_df["Date"] >= min_date]
    chart_df["Short_MA"] = chart_df["Actual"].rolling(window=7, min_periods=1).mean()
    chart_df["Long_MA"] = chart_df["Actual"].rolling(window=30, min_periods=1).mean()
    fig.add_trace(
        go.Scatter(
            x=chart_df["Date"],
            y=chart_df["Actual"],
            mode="lines",
            name="Actual Price",
            line=dict(color="#3498DB", width=2),
        )
    )
    # FIX: Ensure Predicted Price is always drawn in historical view
    fig.add_trace(
        go.Scatter(
            x=chart_df["Date"],
            y=chart_df["Predicted"],
            mode="lines",
            name="Predicted Price",
            line=dict(color="#E67E22", dash="dash", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=chart_df["Date"],
            y=chart_df["Short_MA"],
            mode="lines",
            name="7-Day MA",
            line=dict(color="purple", dash="dot", width=1.5),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=chart_df["Date"],
            y=chart_df["Long_MA"],
            mode="lines",
            name="30-Day MA",
            line=dict(color="grey", dash="longdash", width=1.5),
        )
    )

# FIX: Filter signals for clarity
significant_buys, significant_sells = filter_significant_signals(dff.copy())
fig.add_trace(
    go.Scatter(
        x=significant_buys["Date"],
        y=significant_buys["Actual"],
        mode="markers",
        name="Significant Buy",
        marker=dict(
            color="#27AE60",
            size=10,
            symbol="triangle-up",
            line=dict(width=1, color="DarkSlateGrey"),
        ),
    )
)
fig.add_trace(
    go.Scatter(
        x=significant_sells["Date"],
        y=significant_sells["Actual"],
        mode="markers",
        name="Significant Sell",
        marker=dict(
            color="#C0392B",
            size=10,
            symbol="triangle-down",
            line=dict(width=1, color="DarkSlateGrey"),
        ),
    )
)

fig.update_layout(
    title=f"Forecast vs. Actual Price for {coin}",
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig, use_container_width=True)

# --- KPI CARDS SECTION ---
st.markdown("---")
st.subheader("Model Insights & Performance")
kpi_cols = st.columns(3)

# KPI 1: Signal Summary
with kpi_cols[0]:
    buy_count, sell_count = len(significant_buys), len(significant_sells)
    last_buy_date = (
        significant_buys["Date"].max().strftime("%Y-%m-%d") if buy_count > 0 else "-"
    )
    last_sell_date = (
        significant_sells["Date"].max().strftime("%Y-%m-%d") if sell_count > 0 else "-"
    )
    signal_icon_b64 = image_to_base64(CARD_ICONS.get("signal"))
    st.markdown(
        f"""<div style="background-color:#e8f7ef;border-radius:10px;padding:20px;height:100%;"><div style="display:flex;align-items:center;margin-bottom:12px;"><img src="data:image/png;base64,{signal_icon_b64}" style="height:28px;margin-right:12px;"><span style="font-size:1.1em;font-weight:600;">Significant Signals</span></div><p style="margin:4px 0;"><strong>Buys:</strong> <span style='color:#207850;'>{buy_count}</span> | Latest: {last_buy_date}</p><p style="margin:4px 0;"><strong>Sells:</strong> <span style='color:#c81d1d;'>{sell_count}</span> | Latest: {last_sell_date}</p></div>""",
        unsafe_allow_html=True,
    )

# KPI 2: Model Performance
with kpi_cols[1]:
    performance_icon_b64 = image_to_base64(CARD_ICONS.get("performance"))
    st.markdown(
        f"""<div style="background-color:#f4f6f8;border-radius:10px;padding:20px;height:100%;"><div style="display:flex;align-items:center;margin-bottom:12px;"><img src="data:image/png;base64,{performance_icon_b64}" style="height:28px;margin-right:12px;"><span style="font-size:1.1em;font-weight:600;">Model Performance</span></div>""",
        unsafe_allow_html=True,
    )
    try:
        metrics_df = pd.read_csv(metrics_file)
        metrics_row = metrics_df[metrics_df["Coin"] == coin].iloc[0]
        st.markdown(
            f"""<p style="margin:4px 0;"><strong>RMSE:</strong> {metrics_row.get('RMSE', 'N/A'):.2f}</p><p style="margin:4px 0;"><strong>MAPE:</strong> {metrics_row.get('MAPE', 'N/A'):.2f}%</p><p style="margin:4px 0;"><strong>R²:</strong> {metrics_row.get('R2', 'N/A'):.2f}</p>""",
            unsafe_allow_html=True,
        )
    except:
        st.markdown("<p><em>Metrics not available.</em></p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# KPI 3: Executive Summary
with kpi_cols[2]:
    summary_icon_b64 = image_to_base64(CARD_ICONS.get("summary"))
    summary_text = "No metrics for this model/currency."
    try:
        if "metrics_row" in locals():
            summary_text = f"The **{model_short}** model for **{coin_name}** has a MAPE of **{metrics_row.get('MAPE', 'N/A'):.2f}%**. Lower values are better, with MAPE under 20% generally good for financial forecasts."
    except:
        pass
    st.markdown(
        f"""<div style="background-color:#fffcee;border-radius:10px;padding:20px;height:100%;"><div style="display:flex;align-items:center;margin-bottom:12px;"><img src="data:image/png;base64,{summary_icon_b64}" style="height:28px;margin-right:12px;"><span style="font-size:1.1em;font-weight:600;">Executive Summary</span></div><p style='margin-top:8px;'>{summary_text}</p></div>""",
        unsafe_allow_html=True,
    )

# --- TABBED INTERFACE ---
st.markdown("---")
tab1, tab2, tab3 = st.tabs(
    ["📊 Market State Prediction", "💡 What-If Scenario Analysis", "📄 Detailed Data"]
)

with tab1:
    st.subheader("Portfolio Market State Prediction")
    trend_days_options = {"1 Week": 7, "15 Days": 15, "1 Month": 30}
    trend_days_label = st.selectbox(
        "Select forecast window:", list(trend_days_options.keys()), index=2
    )
    trend_n_days = trend_days_options[trend_days_label]
    coin_trends = []
    for rep_coin in rep_coins:
        ffile = os.path.join(base_path, f"{rep_coin}_future_forecast.csv")
        try:
            fdf = pd.read_csv(ffile, parse_dates=["Date"])
            if len(fdf) >= trend_n_days:
                p_start, p_end = (
                    fdf.loc[0, "Predicted"],
                    fdf.loc[trend_n_days - 1, "Predicted"],
                )
                pct_change = (
                    ((p_end - p_start) / abs(p_start)) * 100 if p_start != 0 else 0
                )
                state = (
                    "Bullish 🟢"
                    if pct_change > 0
                    else "Bearish 🔴" if pct_change < 0 else "Neutral 🟡"
                )
                coin_trends.append(
                    {
                        "Coin": rep_coin,
                        "Predicted Change": f"{pct_change:.2f}%",
                        "State": state,
                    }
                )
        except:
            coin_trends.append(
                {"Coin": rep_coin, "Predicted Change": "N/A", "State": "No Data"}
            )
    trend_df = pd.DataFrame(coin_trends)
    st.dataframe(trend_df, use_container_width=True)

with tab2:
    # FIX: New beautiful and functional What-If section
    st.subheader("Hypothetical Trade Calculator")
    if "trade_result" not in st.session_state:
        st.session_state.trade_result = ""

    def calculate_trade():
        qty = st.session_state.what_if_qty
        target = st.session_state.what_if_target
        current_p = dff["Actual"].dropna().iloc[-1]
        profit = (target - current_p) * qty
        profit_color = "#27AE60" if profit >= 0 else "#C0392B"
        st.session_state.trade_result = f"""<div style="background-color:#F4F6F8;border-radius:10px;padding:20px;text-align:center;margin-top:20px;"><h4 style="margin-bottom:10px;">Potential Profit / Loss</h4><p style="font-size:2.5em;color:{profit_color};font-weight:bold;">${profit:,.2f}</p><p>Based on buying {qty} {coin} at current price of ${current_p:,.2f} and selling at ${target:,.2f}.</p></div>"""

    current_price = dff["Actual"].dropna().iloc[-1]
    if current_price:
        with st.container(border=True):
            form_cols = st.columns([2, 2, 1])
            form_cols[0].number_input(
                "Enter quantity to trade:",
                min_value=0.01,
                value=1.0,
                step=0.1,
                key="what_if_qty",
            )
            form_cols[1].number_input(
                "Enter target sell price ($):",
                min_value=0.01,
                value=float(current_price * 1.1),
                key="what_if_target",
            )
            form_cols[2].markdown(
                "<div style='margin-top:28px'></div>", unsafe_allow_html=True
            )
            form_cols[2].button(
                "Calculate", on_click=calculate_trade, use_container_width=True
            )
            if st.session_state.trade_result:
                st.markdown(st.session_state.trade_result, unsafe_allow_html=True)
    else:
        st.warning("Current price data unavailable.")

with tab3:
    st.subheader(f"Raw Forecast Data for {coin}")
    st.dataframe(dff.tail(100))
    csv_data = dff.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Full Data as CSV",
        csv_data,
        f"{model_short}_{coin}_full_forecast.csv",
        "text/csv",
    )
