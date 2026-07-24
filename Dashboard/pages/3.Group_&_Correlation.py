import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Fix for NumPy version differences
if not hasattr(np, "bool"):
    np.bool = bool

# --- 1. PAGE CONFIG & GLOBAL THEME ---
st.set_page_config(page_title="Market Clusters | CryptoVision AI", layout="wide")

st.markdown("""
    <style>
    /* HIDE DEFAULT NAV */
    div[data-testid="stSidebarNav"] {display: none !important;}
    
    /* GLOBAL DARK THEME */
    .stApp { background-color: #020617; }
    [data-testid="stSidebar"] { background-color: #020617 !important; border-right: 1px solid #1e293b; }

    /* CUSTOM CARD STYLING */
    .info-card {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    
    /* TITLES & TEXT */
    h1, h2, h3 { color: #f8fafc !important; font-weight: 800 !important; }
    p, span, label { color: #cbd5e1 !important; }
    
    /* DATAFRAME OVERRIDE */
    .stDataFrame { border: 1px solid #334155; border-radius: 10px; }
    
    /* TABS STYLING */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. UNIFIED NAVIGATION SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding-bottom: 20px;">
            <img src="https://cdn-icons-png.flaticon.com/512/2091/2091665.png" width="70" style="filter: drop-shadow(0 0 8px #3b82f6);">
            <h2 style='color: white; margin-top: 10px; font-size: 1.5rem;'>CryptoVision</h2>
        </div>
    """, unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=["Home", "Market Dashboard", "Data Insights", "AI Forecasting", "Model Analytics", "Chatbot", "Market News", "FAQ"],
        icons=["house", "grid-1x2", "search", "graph-up", "award", "robot", "rss", "info-circle"],
        default_index=3, # Correlation Index
        styles={
            "container": {"background-color": "transparent"},
            "nav-link": {"color": "#cbd5e1", "font-size": "14px", "text-align": "left", "margin":"5px"},
            "nav-link-selected": {"background-color": "#2563eb", "color": "white"},
        }
    )

    if selected == "Home": st.switch_page("app.py")
    if selected == "Market Dashboard": st.switch_page("pages/1.Dashboard.py")
    if selected == "Data Insights": st.switch_page("pages/2.EDA.py")
    if selected == "AI Forecasting": st.switch_page("pages/4.Forecast.py")
    if selected == "Model Analytics": st.switch_page("pages/5.Model_Comparison.py")
    if selected == "Chatbot": st.switch_page("pages/6.Chatbot.py")
    if selected == "Market News": st.switch_page("pages/7.Top_Stories.py")
    if selected == "FAQ": st.switch_page("pages/FAQ.py")

# --- 3. DATA ENGINE ---
@st.cache_data
def load_correlation_data():
    df = pd.read_csv("data/cleaned/crypto_dataset_cleaned.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    rep_df = pd.read_csv("Dashboard/assets/representative_coins.csv")
    assignments_df = pd.read_csv("data/processed/pca_clustered.csv")
    rep_corr_matrix = pd.read_csv("Dashboard/assets/Correlation_Results/representative_correlation_matrix.csv", index_col=0)
    top_corr_df = pd.read_csv("Dashboard/assets/Correlation_Results/top_correlations.csv")
    return df, rep_df, assignments_df, rep_corr_matrix, top_corr_df

try:
    df, rep_df, assignments_df, rep_corr_matrix, top_corr_df = load_correlation_data()
    representatives = rep_df["Representative_Coin"].tolist()
except Exception as e:
    st.error(f"System Load Error: {e}")
    st.stop()

# --- 4. MAIN CONTENT ---
st.markdown("<h1 style='font-size: 2.5rem;'>Behavioral Analytics & Clustering</h1>", unsafe_allow_html=True)
st.caption("Principal Component Analysis & Inter-Asset Correlation Matrices")

tabs = st.tabs(["📊 Cluster Overview", "🧬 PCA Visualization", "🔗 Correlation Analysis"])

# ---------------- Tab 1: Cluster Overview ----------------
with tabs[0]:
    st.markdown("### Asset Groups by Market Archetype")
    st.write("The system categorizes 30+ assets into 4 primary behavioral groups based on price velocity and volatility profiles.")
    
    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        st.markdown("#### Primary Archetypes")
        rep_table = rep_df.rename(columns={"Cluster": "Group ID"})
        st.dataframe(rep_table.style.background_gradient(cmap="Blues"), use_container_width=True)
    
    with col2:
        st.markdown("#### Group Drilldown")
        g_choice = st.selectbox("Select a behavioral group to view members", sorted(assignments_df["Cluster"].unique()))
        members = assignments_df[assignments_df["Cluster"] == g_choice][["Symbol", "PC1", "PC2"]]
        st.dataframe(members.reset_index(drop=True).style.background_gradient(cmap="viridis"), use_container_width=True)

# ---------------- Tab 2: PCA Visualization ----------------
with tabs[1]:
    st.markdown("### Latent Feature Scatterplot")
    st.info("This chart visualizes the mathematical 'distance' between assets using PCA. Coins that are closer together share similar market behaviors.")
    
    colors = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6"]
    fig = go.Figure()
    
    for i in sorted(assignments_df["Cluster"].unique()):
        g_df = assignments_df[assignments_df["Cluster"] == i]
        fig.add_trace(go.Scatter(
            x=g_df["PC1"], y=g_df["PC2"],
            mode="markers", name=f"Group {i}",
            marker=dict(size=12, color=colors[i % len(colors)], line=dict(width=1, color="white")),
            text=g_df["Symbol"], hovertemplate="<b>%{text}</b><br>PC1: %{x:.2f}<br>PC2: %{y:.2f}"
        ))

    # Star the representatives
    rep_pts = assignments_df[assignments_df["Symbol"].isin(representatives)]
    fig.add_trace(go.Scatter(
        x=rep_pts["PC1"], y=rep_pts["PC2"],
        mode="markers+text", name="Archetypes",
        marker=dict(size=22, symbol="star", color="gold", line=dict(width=2, color="#020617")),
        text=rep_pts["Symbol"], textposition="top center"
    ))

    fig.update_layout(
        template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        height=600, margin=dict(l=0,r=0,t=20,b=0), xaxis_title="Principal Component 1", yaxis_title="Principal Component 2"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Tab 3: Correlation Analysis ----------------
with tabs[2]:
    st.markdown("### Inter-Asset Multi-Correlation Matrix")
    
    c_type = st.segmented_control("Analysis Layer", options=["Archetype Heatmap", "Asset Pairwise Scatter"], default="Archetype Heatmap")

    if c_type == "Archetype Heatmap":
        fig = px.imshow(
            rep_corr_matrix, text_auto=".2f",
            color_continuous_scale="Viridis",
            title="Correlation Coefficient Matrix (Returns)"
        )
        fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance Insight
        st.markdown("""
            <div class="info-card">
                <p style="margin:0; font-size:0.9rem; font-weight:600; color:#3b82f6;">INSIGHT</p>
                <p style="margin:0; font-size:0.85rem;">High correlation (close to 1.0) suggests these assets move in lockstep. 
                For portfolio diversification, investors typically seek assets in different clusters with low correlation scores.</p>
            </div>
        """, unsafe_allow_html=True)

    else:
        c1, c2 = st.columns(2)
        with c1: coinA = st.selectbox("Asset A", df.columns)
        with c2: coinB = st.selectbox("Asset B", [c for c in df.columns if c != coinA])
        
        rets = df[[coinA, coinB]].pct_change().dropna()
        fig = px.scatter(rets, x=coinA, y=coinB, trendline="ols", trendline_color_override="red")
        fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Pearson Correlation", f"{rets[coinA].corr(rets[coinB]):.3f}")

# --- FOOTER ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #475569; font-size: 10px;'>UNSUPERVISED LEARNING MODULE • CRYPTOVISION AI • DEPLOYED ON STREAMLIT CLOUD</div>", unsafe_allow_html=True)