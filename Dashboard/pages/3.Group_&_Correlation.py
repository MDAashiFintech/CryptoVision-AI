import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Fix for NumPy version differences
if not hasattr(np, "bool"):
    np.bool = bool

st.set_page_config(
    page_title="Crypto Group & Correlation", layout="wide", page_icon="📊"
)

st.title("📊 Representative Group & Correlation Dashboard")

# --- CACHED DATA LOADING ---
@st.cache_data
def load_correlation_data():
    # PATH FIXES: Removed "../" and added "Dashboard/" where needed
    df = pd.read_csv("data/cleaned/crypto_dataset_cleaned.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)

    rep_df = pd.read_csv("Dashboard/assets/representative_coins.csv")
    
    assignments_df = pd.read_csv("data/processed/pca_clustered.csv")

    rep_corr_matrix = pd.read_csv(
        "Dashboard/assets/Correlation_Results/representative_correlation_matrix.csv", index_col=0
    )
    
    top_corr_df = pd.read_csv("Dashboard/assets/Correlation_Results/top_correlations.csv")
    
    return df, rep_df, assignments_df, rep_corr_matrix, top_corr_df

# --- EXECUTE LOADING ---
try:
    df, rep_df, assignments_df, rep_corr_matrix, top_corr_df = load_correlation_data()
    representatives = rep_df["Representative_Coin"].tolist()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Ensure you are running the app from the root directory and file paths are correct.")
    st.stop()

# --- TABS ---
tabs = st.tabs(["Cluster Overview", "PCA Visualization", "Correlation Analysis"])

# ---------------- Cluster Overview ----------------
with tabs[0]:
    st.subheader("📋 Cluster Representatives")
    rep_table = rep_df.rename(columns={"Cluster": "Group"})
    st.dataframe(rep_table.style.background_gradient(cmap="Blues"), use_container_width=True)

    st.subheader("🗂️ Full Cluster Assignment (All Coins)")
    st.dataframe(
        assignments_df["Symbol Cluster PC1 PC2".split()]
        .sort_values(by="Cluster")
        .reset_index(drop=True)
        .style.background_gradient(cmap="viridis"),
        use_container_width=True,
    )

    # Group Drilldown
    st.subheader("🔍 Group Drilldown")
    group_choice = st.selectbox("Select a Group", sorted(assignments_df["Cluster"].unique()))
    members_df = assignments_df[assignments_df["Cluster"] == group_choice]
    
    # Safely get representative coin
    rep_row = rep_table[rep_table["Group"] == group_choice]
    if not rep_row.empty:
        rep_coin = rep_row["Representative_Coin"].values[0]
        st.markdown(f"**Group {group_choice} representative:** `{rep_coin}`")
    
    st.dataframe(
        members_df["Symbol PC1 PC2".split()]
        .reset_index(drop=True)
        .style.background_gradient(cmap="plasma"),
        use_container_width=True,
    )

# ---------------- PCA Visualization ----------------
with tabs[1]:
    st.subheader("🖼️ PCA Scatterplot of Coins by Cluster")
    colors = ["#e377c2", "#17becf", "#bcbd22", "#7f7f7f", "#ff7f0e", "#2ca02c"]

    fig = go.Figure()
    for i in sorted(assignments_df["Cluster"].unique()):
        group_df = assignments_df[assignments_df["Cluster"] == i]
        fig.add_trace(go.Scatter(
            x=group_df["PC1"], y=group_df["PC2"],
            mode="markers", name=f"Group {i}",
            marker=dict(size=14, color=colors[i % len(colors)]),
            text=group_df["Symbol"],
            hovertemplate="Coin: %{text}<br>PC1: %{x:.2f}, PC2: %{y:.2f}"
        ))

    # Highlight representatives with stars
    rep_points = assignments_df[assignments_df["Symbol"].isin(representatives)]
    fig.add_trace(go.Scatter(
        x=rep_points["PC1"], y=rep_points["PC2"],
        mode="markers+text", name="Representatives",
        marker=dict(size=24, symbol="star", color="gold", line=dict(width=2, color="black")),
        text=rep_points["Symbol"], textposition="top right"
    ))

    fig.update_layout(title="PCA Cluster Scatterplot", xaxis_title="PC1", yaxis_title="PC2", template="plotly_white", height=600)
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Correlation Analysis ----------------
with tabs[2]:
    st.subheader("📈 Correlation Analysis")
    analysis_type = st.radio("Select analysis:", ["Heatmap", "Top correlations", "Pairwise scatter"])

    if analysis_type == "Heatmap":
        fig = px.imshow(rep_corr_matrix, text_auto=True, color_continuous_scale="Viridis", title="Representative Correlation Heatmap")
        st.plotly_chart(fig, use_container_width=True)

    elif analysis_type == "Top correlations":
        selected_rep = st.selectbox("Select representative", representatives)
        filtered = top_corr_df[top_corr_df["Representative"] == selected_rep]
        
        c1, c2 = st.columns(2)
        with c1:
            st.write("Positive Correlations")
            st.dataframe(filtered[filtered["Type"] == "Positive"].sort_values("Correlation", ascending=False), use_container_width=True)
        with c2:
            st.write("Negative Correlations")
            st.dataframe(filtered[filtered["Type"] == "Negative"].sort_values("Correlation", ascending=True), use_container_width=True)

    elif analysis_type == "Pairwise scatter":
        coinA = st.selectbox("Select Coin A", df.columns)
        coinB = st.selectbox("Select Coin B", [c for c in df.columns if c != coinA])
        returns = df.pct_change().dropna()
        fig = px.scatter(returns, x=coinA, y=coinB, title=f"{coinA} vs {coinB} Daily Returns")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"**Correlation Coefficient:** `{returns[coinA].corr(returns[coinB]):.2f}`")

st.info("Dashboard successfully loaded from root path.")