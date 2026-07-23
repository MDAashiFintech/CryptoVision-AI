# app.py (Your main Welcome Page)

import streamlit as st
import base64
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Crypto Analytics Hub | Home",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- STYLING ---
# You can add custom CSS to a file named style.css in your root directory
# For now, we'll use markdown for some inline styling.

# --- WELCOME PAGE LAYOUT ---


# A little function to load images as base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


# Main header with a cool gradient text effect (optional, but looks nice)
st.markdown(
    """
    <style>
    .gradient-text {
        background: -webkit-linear-gradient(left, #00C4FF, #33FF7A);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    </style>
    <div style="text-align: center;">
        <h1>💸 Welcome to the <span class="gradient-text">Crypto Analytics Hub!</span></h1>
    </div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    "<h4 style='text-align: center; color: #888;'>Your All-in-One Crypto Analysis and Forecasting Tool</h4>",
    unsafe_allow_html=True,
)
st.markdown("---")


# --- TWO-COLUMN LAYOUT: PROJECT INFO & VISUAL ---
col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.header("📖 About This Project")
    st.markdown(
        """
        This dashboard is a comprehensive tool developed as part of an academic assessment for **Solent University**.
        It leverages historical cryptocurrency data and multiple machine learning models to provide deep insights,
        accurate forecasts, and actionable analytics.

        Our goal is to create an intuitive, data-driven platform that empowers users to explore market trends,
        compare model performance, and interact with complex data through a conversational AI assistant.
        """
    )

    st.subheader("🧑‍💻 Author")
    st.markdown(
        """
        - **Aashif Ansari**
        """
    )

    # Solent University Logo
    st.markdown(
        """
        <div style="display: flex; align-items: center; margin-top: 20px;">
            <p style="margin-right: 10px; font-weight: bold;">University:</p>
            <img src="https://www.solent.ac.uk/UI/images/logo-horizontal-2022.svg" alt="Solent University Logo" width="200">
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    # You can replace this URL with a local image if you prefer
    st.image(
        "https://images.unsplash.com/photo-1640286599025-31293a8470b8?q=80&w=1932&auto=format&fit=crop",
        caption="Data-driven insights into the world of crypto.",
    )

st.markdown("---")

# --- FEATURE HIGHLIGHTS IN CARDS ---
st.header("🚀 Key Features")
feat_col1, feat_col2, feat_col3 = st.columns(3, gap="medium")

with feat_col1:
    st.markdown(
        """
        <div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; border: 1px solid #cce7ff; height: 100%;">
            <h4 style="color: #007bff;">🤖 Interactive Chatbot</h4>
            <p>Engage in a natural conversation to perform complex analyses. Ask for forecasts, correlations, and insights without navigating menus.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with feat_col2:
    st.markdown(
        """
        <div style="background-color: #f0fff0; padding: 20px; border-radius: 10px; border: 1px solid #cce7cc; height: 100%;">
            <h4 style="color: #28a745;">📈 Multi-Model Forecasting</h4>
            <p>Leverage five distinct machine learning models (ARIMA, LSTM, Prophet, RF, XGB) to predict future price highs and lows.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with feat_col3:
    st.markdown(
        """
        <div style="background-color: #fffaf0; padding: 20px; border-radius: 10px; border: 1px solid #ffe7cc; height: 100%;">
            <h4 style="color: #fd7e14;">🏆 Model Performance Hub</h4>
            <p>Objectively compare all forecasting models on key metrics like MAPE and RMSE to identify the best performer for your chosen cryptocurrency.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- CALL TO ACTION ---
st.sidebar.success("Select a tool from the sidebar to begin analyzing!")
