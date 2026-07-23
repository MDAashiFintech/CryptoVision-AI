import streamlit as st
from utils import load_all_data # Import from root utils

st.set_page_config(page_title="FAQ", page_icon="❓", layout="wide")

st.title("❓ Frequently Asked Questions")
st.markdown("Find answers to common questions about the platform.")
st.markdown("---")

with st.expander("What is the purpose of this dashboard?"):
    st.write("An all-in-one AI tool for cryptocurrency analysis and forecasting.")

with st.expander("What data is being used?"):
    st.write("Cleaned daily OHLCV data and live snapshots from CoinGecko.")

st.header("Navigating the Tools")
col1, col2 = st.columns(2)
with col1:
    if st.button("Open Main Dashboard"): st.switch_page("pages/1.Dashboard.py")
with col2:
    if st.button("Talk to AI Chatbot"): st.switch_page("pages/6.Chatbot.py")