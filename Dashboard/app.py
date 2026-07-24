import streamlit as st
from streamlit_option_menu import option_menu
import base64

# --- PAGE CONFIG ---
st.set_page_config(page_title="CryptoVision AI", page_icon="📈", layout="wide")

# --- PREMIUM CSS INJECTION ---
st.markdown("""
    <style>
    /* Hide the default sidebar dots and navigation */
    div[data-testid="stSidebarNav"] {display: none;}
    
    /* Modern Font & Background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    /* Professional Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b;
    }

    /* Main Hero Styling */
    .hero-box {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 3rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 15px;
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.1);
        border-color: #3b82f6;
    }

    /* Custom Tech Tags */
    .badge {
        background: #1e293b;
        color: #3b82f6;
        padding: 5px 12px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.75rem;
        margin-right: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CUSTOM SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2091/2091665.png", width=80) # Modern AI Icon
    st.markdown("<h2 style='color: white; text-align: center;'>CryptoVision</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; text-align: center; font-size: 0.8rem;'>Fintech Prediction Engine v2.0</p>", unsafe_allow_html=True)
    st.write("---")
    
    # This is the "Option Menu" that makes it look like a real WebApp
    selected = option_menu(
        menu_title=None,
        options=["Home", "Market Dashboard", "Data Insights", "AI Forecasting", "Model Analytics", "Chatbot", "Market News", "FAQ"],
        icons=["house", "speedometer2", "search", "graph-up-arrow", "trophy", "robot", "newspaper", "question-circle"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#3b82f6", "font-size": "18px"}, 
            "nav-link": {"color": "white", "font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#1e293b"},
            "nav-link-selected": {"background-color": "#3b82f6"},
        }
    )
    
    # NAVIGATION LOGIC
    # These paths must match your actual filenames in the pages folder
    if selected == "Market Dashboard": st.switch_page("pages/1.Dashboard.py")
    if selected == "Data Insights": st.switch_page("pages/2.EDA.py")
    if selected == "AI Forecasting": st.switch_page("pages/4.Forecast.py")
    if selected == "Model Analytics": st.switch_page("pages/5.Model_Comparison.py")
    if selected == "Chatbot": st.switch_page("pages/6.Chatbot.py")
    if selected == "Market News": st.switch_page("pages/7.Top_Stories.py")
    if selected == "FAQ": st.switch_page("pages/FAQ.py")

# --- HOME PAGE CONTENT ---
if selected == "Home":
    st.markdown("""
        <div class="hero-box">
            <h1 style='font-weight: 800; font-size: 3.5rem;'>CRYPTOVISION AI</h1>
            <p style='font-size: 1.2rem; opacity: 0.9;'>Advanced Deep Learning & Market Intelligence for the Digital Asset Economy</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([3, 2], gap="large")
    
    with c1:
        st.markdown("### 🦾 The Prediction Engine")
        st.write("""
            Welcome to **CryptoVision AI**, a state-of-the-art analytics platform designed to solve the complexity of cryptocurrency market volatility. 
            Our system processes millions of data points across 30+ assets to provide real-time forecasting and behavioral clustering.
        """)
        
        st.markdown("""
            <div style="margin-top: 20px;">
                <span class="badge">DEEP LEARNING</span>
                <span class="badge">FINTECH</span>
                <span class="badge">REAL-TIME INFERENCE</span>
                <span class="badge">SCALABLE PIPELINE</span>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.image("https://images.unsplash.com/photo-1639762681485-074b7f938ba0?auto=format&fit=crop&w=800&q=80", use_container_width=True)

    st.write("---")
    
    # Capability Cards
    st.markdown("### 🚀 Platform Capabilities")
    cols = st.columns(3)
    
    with cols[0]:
        st.markdown("""<div class="glass-card">
            <h4 style="color: #3b82f6;">📉 Predictive Logic</h4>
            <p style="font-size: 0.9rem; color: #4b5563;">Leveraging LSTM Neural Networks and XGBoost for trend classification with sub-10% MAPE.</p>
        </div>""", unsafe_allow_html=True)
        
    with cols[1]:
        st.markdown("""<div class="glass-card">
            <h4 style="color: #3b82f6;">🤖 Conversational AI</h4>
            <p style="font-size: 0.9rem; color: #4b5563;">Proprietary NLP engine allowing for natural language queries of complex financial datasets.</p>
        </div>""", unsafe_allow_html=True)
        
    with cols[2]:
        st.markdown("""<div class="glass-card">
            <h4 style="color: #3b82f6;">🧬 PCA Clustering</h4>
            <p style="font-size: 0.9rem; color: #4b5563;">Automated asset archetyping using Principal Component Analysis for portfolio diversification.</p>
        </div>""", unsafe_allow_html=True)

    # Professional Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; color: #94a3b8; font-size: 0.8rem;'>Lead Developer: MD Aashif Ansari • MSc Applied AI & Data Science</div>", unsafe_allow_html=True)