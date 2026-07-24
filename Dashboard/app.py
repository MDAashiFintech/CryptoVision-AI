import streamlit as st
from streamlit_option_menu import option_menu
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="CryptoVision AI | Institutional Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ADVANCED CSS FOR POLISHED UI ---
st.markdown("""
    <style>
    /* Hide default Streamlit navigation */
    div[data-testid="stSidebarNav"] {display: none;}
    
    /* Overall Background and Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    .main {
        background-color: #0f172a;
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar Refinement */
    [data-testid="stSidebar"] {
        background-color: #020617 !important;
        border-right: 1px solid #1e293b;
        min-width: 260px !important;
    }

    /* Hero Section - Fixed height and centering */
    .hero-section {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        padding: 50px 30px;
        border-radius: 24px;
        color: white;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* Modern Badge/Tag Styling */
    .tech-badge {
        display: inline-block;
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        padding: 6px 15px;
        border-radius: 100px;
        font-weight: 600;
        font-size: 0.75rem;
        margin: 5px;
        border: 1px solid rgba(96, 165, 250, 0.2);
        letter-spacing: 0.5px;
    }

    /* Enhanced Capability Cards */
    .cap-card {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 30px;
        border-radius: 20px;
        height: 100%;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .cap-card:hover {
        transform: translateY(-10px);
        border-color: #3b82f6;
        box-shadow: 0 15px 30px rgba(0,0,0,0.4);
        background: #1e293b;
    }

    /* Section Headings */
    .section-title {
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 20px;
    }
    
    /* Footer */
    .footer-text {
        color: #64748b;
        font-size: 0.85rem;
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        border-top: 1px solid #1e293b;
    }
    </style>
""", unsafe_allow_html=True)

# --- CUSTOM SIDEBAR ---
with st.sidebar:
    # Top Branding
    st.markdown("""
        <div style="text-align: center; padding: 20px 0px;">
            <img src="https://cdn-icons-png.flaticon.com/512/2091/2091665.png" width="80" style="filter: drop-shadow(0 0 10px #3b82f6);">
            <h2 style='color: white; margin-top: 15px; font-weight: 800; letter-spacing: -1px;'>CryptoVision</h2>
            <p style='color: #94a3b8; font-size: 0.75rem; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;'>Intelligence Engine v2.0</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 10px 0px;'></div>", unsafe_allow_html=True)

    # Navigation Menu with FIXED Contrast
    selected = option_menu(
        menu_title=None,
        options=["Home", "Market Dashboard", "Data Insights", "AI Forecasting", "Model Analytics", "Chatbot", "Market News", "FAQ"],
        icons=["house", "grid-1x2", "search", "graph-up", "award", "robot", "rss", "info-circle"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5px", "background-color": "transparent"},
            "icon": {"color": "#60a5fa", "font-size": "18px"}, 
            "nav-link": {
                "color": "#cbd5e1", # Lighter grey/white for high visibility
                "font-size": "14px", 
                "text-align": "left", 
                "margin":"5px", 
                "font-weight": "500",
                "--hover-color": "#1e293b"
            },
            "nav-link-selected": {
                "background-color": "#2563eb",
                "color": "white",
                "font-weight": "700"
            },
        }
    )
    
    st.markdown("<div style='position: fixed; bottom: 20px; left: 20px; color: #475569; font-size: 10px;'>DEVELOPED BY MD AASHIF ANSARI</div>", unsafe_allow_html=True)

# --- NAVIGATION LOGIC ---
if selected == "Market Dashboard": st.switch_page("pages/1.Dashboard.py")
if selected == "Data Insights": st.switch_page("pages/2.EDA.py")
if selected == "AI Forecasting": st.switch_page("pages/4.Forecast.py")
if selected == "Model Analytics": st.switch_page("pages/5.Model_Comparison.py")
if selected == "Chatbot": st.switch_page("pages/6.Chatbot.py")
if selected == "Market News": st.switch_page("pages/7.Top_Stories.py")
if selected == "FAQ": st.switch_page("pages/FAQ.py")

# --- HOME PAGE CONTENT ---
if selected == "Home":
    # 1. Fixed Hero Section
    st.markdown("""
        <div class="hero-section">
            <h1 style='font-weight: 800; font-size: 3.8rem; margin: 0; letter-spacing: -2px;'>CRYPTOVISION AI</h1>
            <p style='font-size: 1.25rem; font-weight: 300; opacity: 0.95; max-width: 800px; margin: 15px auto;'>
                Precision Data Science & Multi-Architecture Deep Learning for the Global Digital Economy.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 2. Main Narrative
    col1, col2 = st.columns([3, 2], gap="large")
    
    with col1:
        st.markdown("<h2 class='section-title'>🦾 The Intelligence Core</h2>", unsafe_allow_html=True)
        st.write("""
            **CryptoVision AI** is a professional-grade fintech ecosystem designed to navigate the high-volatility 
            landscape of digital assets. By processing high-fidelity OHLCV data through a sophisticated 
            **Machine Learning pipeline**, the platform delivers institutional-level insights.
        """)
        
        st.write("""
            Our architecture integrates **Long Short-Term Memory (LSTM)** neural networks and 
            **Gradient Boosted Trees** to identify non-linear market patterns and momentum shifts 
            before they materialize in price action.
        """)
        
        st.markdown("""
            <div style="margin-top: 25px;">
                <span class="tech-badge">NEURAL NETWORKS</span>
                <span class="tech-badge">ENSEMBLE LEARNING</span>
                <span class="tech-badge">TIME-SERIES EDA</span>
                <span class="tech-badge">NLP CHATBOT</span>
                <span class="tech-badge">FINTECH API</span>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.image("https://images.unsplash.com/photo-1639762681485-074b7f938ba0?auto=format&fit=crop&w=800&q=80", use_container_width=True)

    st.markdown("<br><hr style='border-color: #1e293b;'><br>", unsafe_allow_html=True)
    
    # 3. Enhanced Capability Cards
    st.markdown("<h2 class='section-title'>🚀 Platform Capabilities</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="medium")
    
    with c1:
        st.markdown("""<div class="cap-card">
            <div style="font-size: 30px; margin-bottom: 10px;">📉</div>
            <h4 style="color: #60a5fa; margin-bottom: 10px;">Predictive Analytics</h4>
            <p style="font-size: 0.85rem; color: #94a3b8; line-height: 1.6;">
                Advanced forecasting using LSTM and XGBoost, optimized via hyperparameter tuning to achieve sub-10% MAPE on major assets.
            </p>
        </div>""", unsafe_allow_html=True)
        
    with c2:
        st.markdown("""<div class="cap-card">
            <div style="font-size: 30px; margin-bottom: 10px;">🤖</div>
            <h4 style="color: #60a5fa; margin-bottom: 10px;">Conversational AI</h4>
            <p style="font-size: 0.85rem; color: #94a3b8; line-height: 1.6;">
                An integrated NLP layer designed for financial queries, enabling interactive exploration of correlations and trends.
            </p>
        </div>""", unsafe_allow_html=True)
        
    with c3:
        st.markdown("""<div class="cap-card">
            <div style="font-size: 30px; margin-bottom: 10px;">🧬</div>
            <h4 style="color: #60a5fa; margin-bottom: 10px;">Market Clustering</h4>
            <p style="font-size: 0.85rem; color: #94a3b8; line-height: 1.6;">
                Unsupervised learning utilizing Principal Component Analysis (PCA) to categorize assets into behavioral archetypes.
            </p>
        </div>""", unsafe_allow_html=True)

    # 4. Final Footer
    st.markdown(f"""
        <div class="footer-text">
            <b>Project Classification:</b> Professional AI Portfolio Platform<br>
            Solent University MSc Applied AI & Data Science Graduation Project • MD Aashif Ansari © 2024
        </div>
    """, unsafe_allow_html=True)