import streamlit as st
import base64
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="CryptoVision AI | Fintech Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS FOR PROFESSIONAL LOOK ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stHeader {
        background: transparent;
    }
    .gradient-text {
        background: -webkit-linear-gradient(left, #1E3A8A, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
    }
    .hero-container {
        padding: 2rem 0rem;
        text-align: center;
    }
    .feature-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #3B82F6;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        height: 250px;
        transition: transform 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-5px);
    }
    .tech-tag {
        display: inline-block;
        background: #E0E7FF;
        color: #1E40AF;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 2px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# --- HERO SECTION ---
st.markdown("""
    <div class="hero-container">
        <h1 class="gradient-text">CryptoVision AI</h1>
        <p style='color: #4B5563; font-size: 1.2rem; font-weight: 400;'>
            Next-Generation Fintech Intelligence & Predictive Modeling Platform
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- CORE VALUE PROPOSITION ---
col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.markdown("### 🧠 Intelligent Market Forecasting")
    st.write("""
        **CryptoVision AI** is a professional-grade fintech platform that bridges the gap between raw blockchain data and actionable financial intelligence. 
        By utilizing a high-performance Machine Learning pipeline, the system analyzes market archetypes, volatility patterns, and price momentum across 30+ major assets.
    """)
    
    st.write("""
        This platform demonstrates the end-to-end deployment of **Deep Learning (LSTM)** and **Ensemble methods**, 
        designed for low-latency inference and high-accuracy forecasting in volatile environments.
    """)

    st.markdown("#### 🛠️ Tech Stack & Engineering")
    tags = ["Python", "TensorFlow", "Scikit-Learn", "Streamlit", "XGBoost", "Prophet", "Plotly", "REST APIs", "PCA"]
    tag_html = "".join([f'<span class="tech-tag">{t}</span>' for t in tags])
    st.markdown(tag_html, unsafe_allow_html=True)

with col2:
    # Professional image related to data/tech
    st.image(
        "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2070&auto=format&fit=crop",
        caption="Real-time Data Processing & Prediction Engine",
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- PROFESSIONAL FEATURE CARDS ---
st.markdown("### 🚀 Platform Capabilities")
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
        <div class="feature-card">
            <h4 style="color: #1E3A8A;">🤖 Natural Language Querying</h4>
            <p style="color: #4B5563; font-size: 0.9rem;">
                Integrated AI Assistant designed to process complex financial queries. 
                Move from static menus to natural language exploration of correlations, trends, and forecasts.
            </p>
        </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
        <div class="feature-card">
            <h4 style="color: #1E3A8A;">📈 Multi-Model Architectures</h4>
            <p style="color: #4B5563; font-size: 0.9rem;">
                Comparison engine featuring <b>LSTM Neural Networks</b> for sequential data, 
                <b>XGBoost</b> for trend detection, and <b>Prophet</b> for seasonal decomposition.
            </p>
        </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
        <div class="feature-card">
            <h4 style="color: #1E3A8A;">🏆 Performance Benchmarking</h4>
            <p style="color: #4B5563; font-size: 0.9rem;">
                Objective statistical evaluation using <b>MAPE, RMSE, and R²</b> metrics. 
                Identify the optimal model for specific asset classes through rigorous backtesting.
            </p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# --- FOOTER / AUTHOR ---
st.markdown("---")
footer_col1, footer_col2 = st.columns(2)
with footer_col1:
    st.markdown(f"**Lead AI Engineer:** MD Aashif Ansari")
    st.markdown("*MSc Applied AI & Data Science*")
with footer_col2:
    st.markdown("<div style='text-align: right;'>© 2024 CryptoVision AI | Deployed on Streamlit Cloud</div>", unsafe_allow_html=True)

# --- SIDEBAR MESSAGE ---
st.sidebar.info("Navigate via the sidebar to explore the platform's analytical tools.")