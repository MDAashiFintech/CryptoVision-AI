import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt


if not hasattr(np, "bool"):
    np.bool = bool

st.set_page_config(
    page_title="Crypto Group & Correlation", layout="wide", page_icon="📊"
)

st.title("📊 Representative Group & Correlation Dashboard")

# --- Load Data ---
try:
    # unchanged cleaned dataset path
    df = pd.read_csv("../data/cleaned/crypto_dataset_cleaned.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)

    # representatives and clusters path changed to your assets folder
    rep_df = pd.read_csv("assets/representative_coins.csv")
    clusters = rep_df["Cluster"].tolist()
    representatives = rep_df["Representative_Coin"].tolist()

    assignments_df = pd.read_csv("../data/processed/pca_clustered.csv")

    # Load saved correlation matrices from assets folder
    rep_corr_matrix = pd.read_csv(
        "assets/Correlation_Results/representative_correlation_matrix.csv", index_col=0
    )
    top_corr_df = pd.read_csv("assets/Correlation_Results/top_correlations.csv")

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --- Tabs for better UI ---
tabs = st.tabs(["Cluster Overview", "PCA Visualization", "Correlation Analysis"])

# ---------------- Cluster Overview ----------------
with tabs[0]:
    st.subheader("📋 Cluster Representatives")
    rep_table = rep_df.rename(columns={"Cluster": "Group"})
    st.dataframe(
        rep_table.style.background_gradient(cmap="Blues"), use_container_width=True
    )

    st.subheader("🗂️ Full Cluster Assignment (All Coins)")
    st.dataframe(
        assignments_df["Symbol Cluster PC1 PC2".split()]
        .sort_values(by="Cluster")
        .reset_index(drop=True)
        .style.background_gradient(cmap="viridis"),
        use_container_width=True,
    )

    st.download_button(
        "📥 Download All Cluster Assignments",
        data=assignments_df.to_csv(index=False).encode("utf-8"),
        file_name="all_cluster_assignments.csv",
        mime="text/csv",
    )

    # Group Drilldown
    st.subheader("🔍 Group Drilldown")
    group_choice = st.selectbox(
        "Select a Group", sorted(assignments_df["Cluster"].unique())
    )
    members_df = assignments_df[assignments_df["Cluster"] == group_choice]
    rep_coin = rep_table[rep_table["Group"] == group_choice][
        "Representative_Coin"
    ].values[0]
    st.markdown(f"**Group {group_choice} representative:** `{rep_coin}`")
    st.dataframe(
        members_df["Symbol PC1 PC2".split()]
        .reset_index(drop=True)
        .style.background_gradient(cmap="plasma"),
        use_container_width=True,
    )

    st.download_button(
        f"📥 Download Group {group_choice} Members",
        data=members_df.to_csv(index=False).encode("utf-8"),
        file_name=f"group_{group_choice}_members.csv",
        mime="text/csv",
    )


# ---------------- PCA Visualization ----------------
with tabs[1]:
    st.subheader("🖼️ PCA Scatterplot of Coins by Cluster")
    colors = ["#e377c2", "#17becf", "#bcbd22", "#7f7f7f", "#ff7f0e", "#2ca02c"]

    fig = go.Figure()
    for i in sorted(assignments_df["Cluster"].unique()):
        group_df = assignments_df[assignments_df["Cluster"] == i]
        fig.add_trace(
            go.Scatter(
                x=group_df["PC1"],
                y=group_df["PC2"],
                mode="markers",
                name=f"Group {i}",
                marker=dict(size=14, color=colors[i % len(colors)]),
                text=group_df["Symbol"],
                hovertemplate="Coin: %{text}<br>PC1: %{x:.2f}, PC2: %{y:.2f}",
            )
        )

    rep_points = assignments_df[assignments_df["Symbol"].isin(representatives)]
    fig.add_trace(
        go.Scatter(
            x=rep_points["PC1"],
            y=rep_points["PC2"],
            mode="markers+text",
            name="Representatives",
            marker=dict(
                size=24, symbol="star", color="gold", line=dict(width=2, color="black")
            ),
            text=rep_points["Symbol"],
            textposition="top right",
            hovertemplate="REP: %{text}<br>PC1: %{x:.2f}, PC2: %{y:.2f}",
        )
    )

    fig.update_layout(
        title="PCA Cluster Scatterplot (Coins by Cluster, Representatives Starred)",
        xaxis_title="PC1",
        yaxis_title="PC2",
        legend_title="Clusters",
        height=600,
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------------- Correlation Analysis ----------------
with tabs[2]:
    st.subheader("📈 Correlation Analysis")

    analysis_type = st.radio(
        "Select analysis:",
        [
            "Correlation heatmap (representatives)",
            "Top correlations for a representative",
            "Pairwise scatter plot",
        ],
    )

    if analysis_type == "Correlation heatmap (representatives)":
        fig = px.imshow(
            rep_corr_matrix,
            text_auto=True,
            color_continuous_scale="Viridis",
            aspect="auto",
            title="Correlation Heatmap (Daily Returns of Representatives)",
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- FIXED block ---
        sorted_corr = rep_corr_matrix.abs().unstack().sort_values(ascending=False)
        sorted_corr_filtered = sorted_corr[sorted_corr < 1]

        # Top correlation pair
        top_pair = sorted_corr_filtered.index[0]
        top_corr = float(sorted_corr_filtered.iloc[0])

        # Least correlation pair
        least_pair = sorted_corr_filtered.index[-1]
        least_corr = float(sorted_corr_filtered.iloc[-1])

        st.markdown(
            f"**Most correlated reps:** `{top_pair[0]} & {top_pair[1]}` (`{top_corr:.2f}`)"
        )
        st.markdown(
            f"**Least correlated reps:** `{least_pair[0]} & {least_pair[1]}` (`{least_corr:.2f}`)"
        )

        st.download_button(
            "📥 Download Rep Correlation Matrix",
            data=rep_corr_matrix.to_csv().encode("utf-8"),
            file_name="representative_correlation_matrix.csv",
            mime="text/csv",
        )

    elif analysis_type == "Top correlations for a representative":
        selected_rep = st.selectbox("Select representative", representatives)
        filtered_top_corr = top_corr_df[top_corr_df["Representative"] == selected_rep]

        positive_corr = (
            filtered_top_corr[filtered_top_corr["Type"] == "Positive"]
            .set_index("Coin")["Correlation"]
            .sort_values(ascending=False)
        )
        negative_corr = (
            filtered_top_corr[filtered_top_corr["Type"] == "Negative"]
            .set_index("Coin")["Correlation"]
            .sort_values(ascending=True)
        )

        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"Top Positive Correlations for {selected_rep}")
            st.dataframe(
                positive_corr.to_frame().style.background_gradient(cmap="Greens"),
                use_container_width=True,
            )
        with col2:
            st.subheader(f"Top Negative Correlations for {selected_rep}")
            st.dataframe(
                negative_corr.to_frame().style.background_gradient(cmap="Reds"),
                use_container_width=True,
            )

        plot_df = pd.DataFrame(
            {
                "Correlation": np.concatenate(
                    [positive_corr.values, negative_corr.values]
                ),
                "Coin": np.concatenate([positive_corr.index, negative_corr.index]),
                "Type": ["Positive"] * len(positive_corr)
                + ["Negative"] * len(negative_corr),
            }
        )
        fig = px.bar(
            plot_df,
            x="Coin",
            y="Correlation",
            color="Type",
            color_discrete_map={"Positive": "green", "Negative": "red"},
            range_y=[-1, 1],
            title=f"Top Correlations with {selected_rep}",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif analysis_type == "Pairwise scatter plot":
        coinA = st.selectbox("Select Coin A", df.columns)
        coinB = st.selectbox("Select Coin B", [c for c in df.columns if c != coinA])
        returns = df.pct_change().dropna()
        returns_pair = returns[[coinA, coinB]].dropna()
        fig = px.scatter(
            returns_pair,
            x=coinA,
            y=coinB,
            trendline=None,  # change to "ols" if you want regression line
            labels={coinA: f"{coinA} Returns", coinB: f"{coinB} Returns"},
            title=f"{coinA} vs {coinB} (Daily Returns Scatter Plot)",
        )
        st.plotly_chart(fig, use_container_width=True)
        corr_value = returns_pair[coinA].corr(returns_pair[coinB])
        st.markdown(f"**Pearson Correlation:** `{corr_value:.2f}`")

st.info(
    "This dashboard allows exploration of clusters, representatives, PCA plots, and correlations with interactive tables and downloads."
)
