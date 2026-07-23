import numpy as np

if not hasattr(np, "bool"):
    np.bool = bool

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import seasonal_decompose


def load_data():
    df = pd.read_csv("../data/cleaned/crypto_dataset_cleaned.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    rep_df = pd.read_csv("../data/processed/representative_coins.csv")
    rep_coins = rep_df["Representative_Coin"].tolist()
    return df, rep_coins


def descriptive_analysis(df, coin):
    stats = df[coin].describe().to_frame()
    stats.loc["skewness"] = df[coin].skew()
    stats.loc["kurtosis"] = df[coin].kurtosis()
    return stats


def plot_trend(df, coin):
    fig = px.line(df, x=df.index, y=coin, title=f"{coin} Closing Price Over Time")
    return fig


def plot_price_distribution(df, coin):
    fig = px.histogram(df, x=coin, nbins=50, title=f"{coin} Price Distribution")
    return fig


def plot_rolling_statistics(df, coin, window, stat, show_volatility):
    series_map = {
        "Mean": df[coin].rolling(window).mean(),
        "Median": df[coin].rolling(window).median(),
        "Min": df[coin].rolling(window).min(),
        "Max": df[coin].rolling(window).max(),
        "Standard Deviation": df[coin].rolling(window).std(),
    }
    stat_series = series_map.get(stat, df[coin].rolling(window).mean())
    vol_series = df[coin].rolling(window).std()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=df.index, y=df[coin], name="Price", line=dict(color="steelblue"))
    )
    fig.add_trace(
        go.Scatter(
            x=stat_series.index,
            y=stat_series,
            name=f"{window}-Day {stat}",
            line=dict(color="crimson"),
        )
    )
    if show_volatility and stat != "Standard Deviation":
        fig.add_trace(
            go.Scatter(
                x=vol_series.index,
                y=vol_series,
                name=f"{window}-Day Volatility",
                line=dict(color="orange"),
                yaxis="y2",
            )
        )
        fig.update_layout(
            yaxis=dict(title="Price"),
            yaxis2=dict(title="Volatility", overlaying="y", side="right"),
            legend=dict(orientation="h"),
            title=f"{coin} Price and Rolling {stat} with Volatility",
        )
    else:
        fig.update_layout(
            yaxis=dict(title="Price"),
            legend=dict(orientation="h"),
            title=f"{coin} Price and Rolling {stat}",
        )
    return fig


def plot_time_series_decomposition(df, coin):
    decomposition = seasonal_decompose(df[coin].dropna(), model="additive", period=30)
    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        subplot_titles=["Original Series", "Trend", "Seasonal", "Residual"],
        vertical_spacing=0.07,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df[coin], line=dict(color="mediumvioletred"), name="Original"
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=decomposition.trend.index,
            y=decomposition.trend,
            line=dict(color="darkorange"),
            name="Trend",
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=decomposition.seasonal.index,
            y=decomposition.seasonal,
            line=dict(color="seagreen"),
            name="Seasonal",
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=decomposition.resid.index,
            y=decomposition.resid,
            line=dict(color="darkslateblue"),
            name="Residual",
        ),
        row=4,
        col=1,
    )
    for i in range(1, 4):
        fig.update_xaxes(title_text="", row=i, col=1)
    fig.update_xaxes(title_text="Date", row=4, col=1)
    for i in range(1, 5):
        fig.update_yaxes(title_text="Value", row=i, col=1)
    fig.update_layout(height=850, showlegend=False)
    return fig


def plot_normalized_comparison(df, coin1, coin2):
    fig = go.Figure()
    color_map = {coin1: "#0A9396", coin2: "#EE9B00"}

    norm1 = df[coin1] / df[coin1].iloc[0]
    norm2 = df[coin2] / df[coin2].iloc[0]

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=norm1,
            name=coin1,
            line=dict(color=color_map[coin1], width=2),
            opacity=0.8,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=norm2,
            name=coin2,
            line=dict(color=color_map[coin2], width=2, dash="dash"),
            opacity=0.8,
        )
    )

    show_smooth = st.checkbox("Show 7-Day Rolling Average", value=True)
    if show_smooth:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=norm1.rolling(7).mean(),
                name=f"{coin1} 7D Avg",
                line=dict(color=color_map[coin1], width=1, dash="dot"),
                opacity=0.7,
                showlegend=True,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=norm2.rolling(7).mean(),
                name=f"{coin2} 7D Avg",
                line=dict(color=color_map[coin2], width=1, dash="dot"),
                opacity=0.7,
                showlegend=True,
            )
        )

    fig.update_layout(
        title=dict(
            text=f"<b>Normalized Price Comparison: {coin1} vs {coin2}</b>",
            x=0.02,
            xanchor="left",
        ),
        xaxis_title="Date",
        yaxis_title="Normalized Price (start=1)",
        legend=dict(orientation="h", x=0.5, y=1.1, xanchor="center"),
        hovermode="x unified",
        plot_bgcolor="#fafcff",
        xaxis=dict(
            rangeslider=dict(visible=True),
            showline=True,
            linewidth=1,
            linecolor="#bbb",
        ),
        yaxis=dict(showline=True, linewidth=1, linecolor="#bbb"),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.info(
        "Normalized price starts both series at 1 for comparison. Use the range slider below the chart to zoom in."
    )


def main():
    df, rep_coins = load_data()

    coin1 = st.selectbox("Select Primary Currency", rep_coins)

    eda_options = [
        "Descriptive analysis",
        "Time Series Decomposition",
        "Trend of closing prices",
        "Price distribution",
        "Rolling statistics and volatility",
        "Monthly returns distribution",
        "Autocorrelation (ACF/PACF)",
        "Correlation matrix",
        "Correlation scatter plot",
        "Normalized price comparison",
    ]
    analysis_type = st.selectbox("Select EDA Option", eda_options)

    needs_coin2 = analysis_type in [
        "Correlation scatter plot",
        "Normalized price comparison",
    ]
    coin2 = st.selectbox(
        "Select Secondary Currency (for comparison)",
        [c for c in rep_coins if c != coin1],
        disabled=not needs_coin2,
        help="Select for comparisons only",
    )

    if analysis_type == "Descriptive analysis":
        stats = descriptive_analysis(df, coin1)
        st.subheader(f"📊 Descriptive stats for {coin1}")
        st.dataframe(
            stats.style.background_gradient(cmap="Blues"), use_container_width=True
        )

        latest_price = df[coin1].iloc[-1]
        price_7d = df[coin1].iloc[-7] if len(df) > 7 else df[coin1].iloc[0]
        price_30d = df[coin1].iloc[-30] if len(df) > 30 else df[coin1].iloc[0]
        change_7d = (latest_price - price_7d) / price_7d * 100
        change_30d = (latest_price - price_30d) / price_30d * 100

        col1, col2, col3 = st.columns(3)
        col1.metric("Latest Price", f"${latest_price:,.2f}")
        col2.metric("7-Day Change", f"{change_7d:.2f}%")
        col3.metric("30-Day Change", f"{change_30d:.2f}%")

        vol = df[coin1].pct_change().rolling(30).std().iloc[-1]
        st.info(f"30-day Volatility: {vol:.2%}")

        insights = []
        insights.append(
            f"{coin1} has {'risen' if change_30d > 0 else 'fallen'} by {change_30d:.1f}% over past month."
        )
        insights.append("High volatility" if vol > 0.05 else "Low volatility")
        skew = stats.loc["skewness"][coin1]
        insights.append(
            "Right-skewed distribution" if skew > 0 else "Left-skewed distribution"
        )
        st.markdown("**Insights:**")
        for insight in insights:
            st.write(f"- {insight}")

    elif analysis_type == "Trend of closing prices":
        fig = plot_trend(df, coin1)
        st.subheader(f"{coin1} Closing Price Over Time")
        st.plotly_chart(fig, use_container_width=True)

    elif analysis_type == "Price distribution":
        fig = plot_price_distribution(df, coin1)
        st.subheader(f"Price Distribution of {coin1}")
        st.plotly_chart(fig, use_container_width=True)

    elif analysis_type == "Time Series Decomposition":
        st.subheader(f"{coin1} Time Series Decomposition")
        try:
            fig = plot_time_series_decomposition(df, coin1)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"An error occurred during decomposition: {e}")

    elif analysis_type == "Rolling statistics and volatility":
        st.header("Rolling Statistics Dashboard")
        col1, col2, col3 = st.columns(3)
        with col1:
            window = st.slider(
                "Rolling Window (days)", min_value=7, max_value=90, value=30
            )
        with col2:
            stat_option = st.selectbox(
                "Statistic",
                options=["Mean", "Median", "Min", "Max", "Standard Deviation"],
            )
        with col3:
            vol_option = st.checkbox("Show Volatility (Std Dev)", value=True)

        fig = plot_rolling_statistics(df, coin1, window, stat_option, vol_option)
        st.plotly_chart(fig, use_container_width=True)

    elif analysis_type == "Monthly returns distribution":
        monthly = df[[coin1]].resample("M").ffill()
        returns = monthly.pct_change().dropna()
        st.subheader(f"{coin1} Monthly Returns Distribution")

        fig = px.histogram(returns, x=coin1, nbins=30, title=f"{coin1} Monthly Returns")
        st.plotly_chart(fig, use_container_width=True)
        fig2 = px.bar(
            returns,
            x=returns.index,
            y=coin1,
            title=f"{coin1} Monthly Returns Over Time",
        )
        st.plotly_chart(fig2, use_container_width=True)

    elif analysis_type == "Autocorrelation (ACF/PACF)":
        returns = df[coin1].pct_change().dropna()
        acf_val = returns.autocorr(lag=1)
        st.subheader(f"{coin1} Autocorrelation (Lag 1)")
        st.write(f"Autocorrelation at lag 1: {acf_val:.4f}")
        st.line_chart(returns)
        st.info("Note: Full ACF/PACF plots not supported here.")

    elif analysis_type == "Correlation matrix":
        returns = df.pct_change().dropna()
        corr = returns[rep_coins].corr()
        st.subheader("Correlation Matrix")
        st.dataframe(corr.style.background_gradient(cmap="viridis"))

    elif analysis_type == "Correlation scatter plot" and coin2:
        returns = df[[coin1, coin2]].pct_change().dropna()
        fig = px.scatter(
            returns,
            x=coin1,
            y=coin2,
            title=f"{coin1} vs {coin2} Returns",
            labels={coin1: "Returns", coin2: "Returns"},
            color_discrete_sequence=["#374151"],
        )
        st.subheader(f"{coin1} vs {coin2} Correlation Scatter Plot")
        st.plotly_chart(fig, use_container_width=True)
        corr = returns[coin1].corr(returns[coin2])
        st.write(f"Pearson correlation coefficient: {corr:.4f}")

    elif analysis_type == "Normalized price comparison" and coin2:
        try:
            plot_normalized_comparison(df, coin1, coin2)
        except Exception as e:
            st.error(f"Error in Normalized Price Comparison: {e}")


if __name__ == "__main__":
    main()
