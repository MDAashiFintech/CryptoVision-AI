# import streamlit as st
# import pandas as pd
# import requests
# from datetime import datetime
# import plotly.express as px
# import plotly.graph_objects as go
# import numpy as np
# import feedparser
# import re


# # --- PAGE SETUP ---
# st.set_page_config(page_title="Crypto Dashboard", layout="wide", page_icon="💸")
# st.markdown(
#     "<h1 style='text-align:center;color:#2E86C1'>💸 Crypto Dashboard</h1>",
#     unsafe_allow_html=True,
# )
# st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# # --- LOAD REPRESENTATIVES ---
# rep_df = pd.read_csv("Dashboard/assets/representative_coins.csv")
# representatives = rep_df["Representative_Coin"].tolist()
# rep_names = {
#     "BETH-USD": "Beacon ETH",
#     "BTC-USD": "Bitcoin",
#     "ADA-USD": "Cardano",
#     "BCH-USD": "Bitcoin Cash",
# }
# coin_ids = {
#     "BETH-USD": "beth",
#     "BTC-USD": "bitcoin",
#     "ADA-USD": "cardano",
#     "BCH-USD": "bitcoin-cash",
# }


# # --- Live Prices ---
# def get_live_prices(symbols):
#     ids = [coin_ids[s] for s in symbols if s in coin_ids]
#     url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies=usd&include_24hr_change=true"
#     resp = requests.get(url).json()
#     results = []
#     for s in symbols:
#         cid = coin_ids.get(s)
#         if cid in resp:
#             results.append(
#                 {
#                     "symbol": s,
#                     "name": rep_names.get(s, cid.replace("-", " ").title()),
#                     "price": resp[cid]["usd"],
#                     "change": resp[cid].get("usd_24h_change", 0),
#                 }
#             )
#     return results


# st.header("⚡ Live Prices for Representatives")
# live_prices = get_live_prices(representatives)
# cols = st.columns(len(representatives))
# for i, coin in enumerate(live_prices):
#     price = f"${coin['price']:,.2f}"
#     change = coin["change"]
#     # Ensure 'change' is a number before formatting
# try:
#     # Convert to float just in case it's a string
#     val = float(change)
#     delta = f"{val:+.2f}%"
# except (ValueError, TypeError, NameError):
#     # If data is missing, show N/A instead of crashing
#     delta = "N/A"
#     cols[i].markdown(
#         f"""<div style='background:#f4f6f8; border-radius:12px; padding:16px; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.08)'>
#             <h3 style='color:#2E86C1'>{coin['name']}</h3>
#             <p style='font-size:2em; font-weight:700; margin:0'>{price}</p>
#             <p style='color:{"#27ae60" if change>=0 else "#c0392b"}; font-size:1.3em; margin-bottom:6px;'>{delta}</p>
#             <span style='color:#888;'>Symbol: {coin['symbol']}</span>
#         </div>""",
#         unsafe_allow_html=True,
#     )
# st.markdown("---")

# # --- Load data for All Coins ---
# data = pd.read_csv("Dashboard/assets/crypto_enriched_ohlcv_cleaned_datasets.csv")
# data["Date"] = pd.to_datetime(data["Date"])
# all_coins = sorted(data["Coin"].unique())

# # --- Crypto Explorer ---
# st.subheader("Explore Cryptocurrencies")
# col1, col2 = st.columns(2)
# with col1:
#     selected_coin = st.selectbox("Select Cryptocurrency", all_coins)
# with col2:
#     chart_type = st.selectbox(
#         "Select Chart",
#         ["Closing Trend", "Histogram", "30-day SMA", "Candlestick", "Volume"],
#     )

# coin_df = data[data["Coin"] == selected_coin]
# if not coin_df.empty:
#     dates = coin_df["Date"]
#     close = coin_df["Close"]

#     # Added price performance panel and adjusted plotting into columns
#     col_stats, col_chart = st.columns([2, 7])

#     # Calculate price performance metrics
#     last_year_mask = coin_df["Date"] >= dates.max() - pd.Timedelta(days=365)
#     last_year = coin_df[last_year_mask]
#     low_52w = last_year["Close"].min() if not last_year.empty else close.min()
#     high_52w = last_year["Close"].max() if not last_year.empty else close.max()

#     ath = close.max()
#     ath_date = dates.iloc[np.argmax(close)]
#     atl = close.min()
#     atl_date = dates.iloc[np.argmin(close)]

#     now_price = close.iloc[-1]
#     pct_from_atl = ((now_price - atl) / atl) * 100 if atl != 0 else None

#     with col_stats:
#         st.markdown(
#             f"""
#             <div style="background-color:#F8F9F9;padding:18px;border-radius:12px;box-shadow:0 2px 10px rgba(44,62,80,0.08)">
#             <h4 style="color:#2D3436;margin-bottom:14px;">Price performance</h4>
#             <div style="display:flex;justify-content:space-between;">
#                 <span><b>Low (52w)</b></span>
#                 <span style="color:#c0392b">${low_52w:,.2f}</span>
#             </div>
#             <div style="display:flex;justify-content:space-between;">
#                 <span><b>High (52w)</b></span>
#                 <span style="color:#27ae60">${high_52w:,.2f}</span>
#             </div>
#             <hr>
#             <div>
#                 <span><b>All-time high</b></span><br>
#                 <span style="font-size:1.15em;color:#117A65">${ath:,.2f}</span>
#                 <span style="font-size:0.9em;color:#888;">&nbsp;{ath_date.strftime('%b %d, %Y')}</span>
#             </div>
#             <div>
#                 <span><b>All-time low</b></span><br>
#                 <span style="font-size:1.15em;color:#c0392b">${atl:,.5f}</span>
#                 <span style="font-size:0.9em;color:#888;">&nbsp;{atl_date.strftime('%b %d, %Y')}</span>
#             </div>
#             <div>
#                 <span><b>Growth from ATL:</b> <span style="color:#27ae60">{f"+{pct_from_atl:,.2f}%" if pct_from_atl is not None else ""}</span></span>
#             </div>
#             </div>
#             """,
#             unsafe_allow_html=True,
#         )
#     with col_chart:
#         if chart_type == "Closing Trend":
#             fig = px.line(
#                 coin_df, x="Date", y="Close", title=f"{selected_coin} Closing Trend"
#             )
#         elif chart_type == "Histogram":
#             fig = px.histogram(
#                 coin_df,
#                 x="Close",
#                 nbins=50,
#                 title=f"{selected_coin} Closing Price Distribution",
#             )
#         elif chart_type == "30-day SMA":
#             sma = close.rolling(30).mean()
#             fig = px.line(coin_df, x="Date", y=sma, title=f"{selected_coin} 30-day SMA")
#         elif chart_type == "Candlestick":
#             fig = go.Figure(
#                 data=[
#                     go.Candlestick(
#                         x=coin_df["Date"],
#                         open=coin_df["Open"],
#                         high=coin_df["High"],
#                         low=coin_df["Low"],
#                         close=coin_df["Close"],
#                     )
#                 ]
#             )
#             fig.update_layout(
#                 title=f"{selected_coin} Candlestick Chart",
#                 xaxis_rangeslider_visible=False,
#             )
#         elif chart_type == "Volume":
#             fig = px.bar(
#                 coin_df, x="Date", y="Volume", title=f"{selected_coin} Volume Chart"
#             )
#         st.plotly_chart(fig, use_container_width=True)
# else:
#     st.warning("No data for selected coin.")


# # --- Analytics Cards ---
# st.header("Analytics & Tools")

# if st.button("📊Data Exploration", key="btn_data_exploration"):
#     st.switch_page("pages/2.EDA.py")

# if st.button("🔗Correlation", key="btn_correlation"):
#     st.switch_page("pages/3.Group_&_Correlation.py")

# if st.button("📈 Prediction", key="btn_prediction"):
#     st.switch_page("pages/4.Forecast.py")

# if st.button("📰 News & Sentiment", key="btn_news"):
#     st.switch_page("pages/7.Top_Stories.py")
# st.markdown("---")

# # --- Crypto News RSS Feed ---
# st.subheader("📰 Latest Crypto News")

# rss_urls = [
#     "https://cryptonews.com/news/feed",
#     "https://www.coindesk.com/arc/outboundfeeds/rss/",
#     "https://news.bitcoin.com/feed/",
# ]

# all_coins_upper = sorted(set([c.split("-")[0].upper() for c in data["Coin"].unique()]))
# rep_coins_simple = [c.split("-")[0].upper() for c in representatives]

# selected_filter = st.radio(
#     "Filter news for:",
#     ["All 30 Cryptocurrencies", "4 Representatives"],
#     horizontal=True,
# )

# filter_coins = (
#     rep_coins_simple if selected_filter == "4 Representatives" else all_coins_upper
# )


# @st.cache_data(ttl=600)
# def fetch_news(filter_coins):
#     entries = []
#     for url in rss_urls:
#         feed = feedparser.parse(url)
#         for entry in feed.entries:
#             combined_text = (entry.title + " " + entry.get("summary", "")).upper()
#             if any(coin in combined_text for coin in filter_coins):
#                 image_url = None
#                 # 1. media_content
#                 if "media_content" in entry:
#                     mc = entry.media_content
#                     if isinstance(mc, list) and len(mc) > 0 and "url" in mc[0]:
#                         image_url = mc[0]["url"]
#                     elif isinstance(mc, dict) and "url" in mc:
#                         image_url = mc["url"]
#                 # 2. media_thumbnail
#                 elif "media_thumbnail" in entry:
#                     mt = entry.media_thumbnail
#                     if isinstance(mt, list) and len(mt) > 0 and "url" in mt[0]:
#                         image_url = mt[0]["url"]
#                 # 3. image in links
#                 elif "links" in entry:
#                     for link in entry.links:
#                         if link.get("type", "").startswith("image"):
#                             image_url = link["href"]
#                             break
#                 # 4. image in summary (HTML <img src="...">)
#                 if not image_url:
#                     matches = re.findall(
#                         r'<img[^>]+src="([^">]+)"', entry.get("summary", "")
#                     )
#                     if matches:
#                         image_url = matches[0]
#                 # 5. fallback
#                 if not image_url:
#                     image_url = "https://cryptologos.cc/logos/all-crypto-logos.png"

#                 # Clean up summary (remove 'The post ... appeared first on ...')
#                 summary = entry.get("summary", "")
#                 summary = re.sub(
#                     r"The post .+? appeared first on .+?(\.|\.\.\.|!| )*",
#                     "",
#                     summary,
#                 ).strip()
#                 if len(summary) > 200:
#                     summary = summary[:200] + "..."

#                 entries.append(
#                     {
#                         "title": entry.title,
#                         "link": entry.link,
#                         "published": entry.get("published", "No date"),
#                         "summary": summary,
#                         "image": image_url,
#                     }
#                 )
#     return entries


# news = fetch_news(filter_coins)

# max_display = 8  # number of news articles to show
# card_style = """
#     background-color: #f9fafb;
#     border-radius: 12px;
#     box-shadow: 0 2px 10px rgba(44,62,80,0.07);
#     padding: 15px 20px;
#     margin-bottom: 20px;
#     display: flex;
#     align-items: flex-start;
# """

# scrollable_div = """
# <div style='max-height:460px; overflow-y:auto;'>
# """

# st.markdown(scrollable_div, unsafe_allow_html=True)

# if news:
#     for article in news[:max_display]:
#         st.markdown(
#             f"""
#         <div style="{card_style}">
#             <img src="{article['image']}" style="width:110px; height:75px; object-fit:cover; border-radius:8px; margin-right:16px;">
#             <div style="flex:1;">
#                 <div style="font-size:1.05em; font-weight:bold; margin-bottom:6px;">{article['title']}</div>
#                 <div style="color:#444; font-size:0.95em; margin-bottom:8px;">{article['summary']}</div>
#                 <a href="{article['link']}" target="_blank" style="color:#2E86C1; font-weight:600; text-decoration:none;">
#                     Read More &rarr;
#                 </a>
#                 <div style="font-size:0.85em; color:#888; margin-top:5px;">{article['published']}</div>
#             </div>
#         </div>
#         """,
#             unsafe_allow_html=True,
#         )
# else:
#     st.info("No recent news articles found for the selected filter.")

# st.markdown("</div>", unsafe_allow_html=True)

#______________________________________
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import feedparser
import re

# --- PAGE SETUP ---
st.set_page_config(page_title="Crypto Dashboard", layout="wide", page_icon="💸")
st.markdown(
    "<h1 style='text-align:center;color:#2E86C1'>💸 Crypto Dashboard</h1>",
    unsafe_allow_html=True,
)
st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# --- LOAD REPRESENTATIVES ---
# Fixed Path: Added Dashboard/
rep_df = pd.read_csv("Dashboard/assets/representative_coins.csv")
representatives = rep_df["Representative_Coin"].tolist()
rep_names = {
    "BETH-USD": "Beacon ETH",
    "BTC-USD": "Bitcoin",
    "ADA-USD": "Cardano",
    "BCH-USD": "Bitcoin Cash",
}
coin_ids = {
    "BETH-USD": "beth",
    "BTC-USD": "bitcoin",
    "ADA-USD": "cardano",
    "BCH-USD": "bitcoin-cash",
}

# --- Live Prices ---
def get_live_prices(symbols):
    ids = [coin_ids[s] for s in symbols if s in coin_ids]
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies=usd&include_24hr_change=true"
    try:
        resp = requests.get(url).json()
        results = []
        for s in symbols:
            cid = coin_ids.get(s)
            if cid in resp:
                results.append(
                    {
                        "symbol": s,
                        "name": rep_names.get(s, cid.replace("-", " ").title()),
                        "price": resp[cid]["usd"],
                        "change": resp[cid].get("usd_24h_change", 0),
                    }
                )
        return results
    except:
        return []

st.header("⚡ Live Prices for Representatives")
live_prices = get_live_prices(representatives)
cols = st.columns(len(representatives))

# --- FIXED LOOP AND INDENTATION ---
for i, coin in enumerate(live_prices):
    price = f"${coin['price']:,.2f}"
    change = coin["change"]
    
    # Check data quality before showing
    try:
        val = float(change)
        delta = f"{val:+.2f}%"
    except:
        val = 0
        delta = "N/A"

    # Now show the card inside the loop
    cols[i].markdown(
        f"""<div style='background:#f4f6f8; border-radius:12px; padding:16px; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.08)'>
            <h3 style='color:#2E86C1'>{coin['name']}</h3>
            <p style='font-size:2em; font-weight:700; margin:0'>{price}</p>
            <p style='color:{"#27ae60" if val>=0 else "#c0392b"}; font-size:1.3em; margin-bottom:6px;'>{delta}</p>
            <span style='color:#888;'>Symbol: {coin['symbol']}</span>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("---")

# --- Load data for All Coins ---
# Fixed Path: Added Dashboard/
data = pd.read_csv("Dashboard/assets/crypto_enriched_ohlcv_cleaned_datasets.csv")
data["Date"] = pd.to_datetime(data["Date"])
all_coins = sorted(data["Coin"].unique())

# --- Crypto Explorer ---
st.subheader("Explore Cryptocurrencies")
col1, col2 = st.columns(2)
with col1:
    selected_coin = st.selectbox("Select Cryptocurrency", all_coins)
with col2:
    chart_type = st.selectbox(
        "Select Chart",
        ["Closing Trend", "Histogram", "30-day SMA", "Candlestick", "Volume"],
    )

coin_df = data[data["Coin"] == selected_coin]
if not coin_df.empty:
    dates = coin_df["Date"]
    close = coin_df["Close"]

    col_stats, col_chart = st.columns([2, 7])

    last_year_mask = coin_df["Date"] >= dates.max() - pd.Timedelta(days=365)
    last_year = coin_df[last_year_mask]
    low_52w = last_year["Close"].min() if not last_year.empty else close.min()
    high_52w = last_year["Close"].max() if not last_year.empty else close.max()

    ath = close.max()
    ath_date = dates.iloc[np.argmax(close.values)]
    atl = close.min()
    atl_date = dates.iloc[np.argmin(close.values)]

    now_price = close.iloc[-1]
    pct_from_atl = ((now_price - atl) / atl) * 100 if atl != 0 else None

    with col_stats:
        st.markdown(
            f"""
            <div style="background-color:#F8F9F9;padding:18px;border-radius:12px;box-shadow:0 2px 10px rgba(44,62,80,0.08)">
            <h4 style="color:#2D3436;margin-bottom:14px;">Price performance</h4>
            <div style="display:flex;justify-content:space-between;">
                <span><b>Low (52w)</b></span>
                <span style="color:#c0392b">${low_52w:,.2f}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span><b>High (52w)</b></span>
                <span style="color:#27ae60">${high_52w:,.2f}</span>
            </div>
            <hr>
            <div>
                <span><b>All-time high</b></span><br>
                <span style="font-size:1.15em;color:#117A65">${ath:,.2f}</span>
                <span style="font-size:0.9em;color:#888;">&nbsp;{ath_date.strftime('%b %d, %Y')}</span>
            </div>
            <div>
                <span><b>All-time low</b></span><br>
                <span style="font-size:1.15em;color:#c0392b">${atl:,.5f}</span>
                <span style="font-size:0.9em;color:#888;">&nbsp;{atl_date.strftime('%b %d, %Y')}</span>
            </div>
            <div>
                <span><b>Growth from ATL:</b> <span style="color:#27ae60">{f"+{pct_from_atl:,.2f}%" if pct_from_atl is not None else ""}</span></span>
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_chart:
        if chart_type == "Closing Trend":
            fig = px.line(coin_df, x="Date", y="Close", title=f"{selected_coin} Closing Trend")
        elif chart_type == "Histogram":
            fig = px.histogram(coin_df, x="Close", nbins=50, title=f"{selected_coin} Closing Price Distribution")
        elif chart_type == "30-day SMA":
            sma = close.rolling(30).mean()
            fig = px.line(coin_df, x="Date", y=sma, title=f"{selected_coin} 30-day SMA")
        elif chart_type == "Candlestick":
            fig = go.Figure(data=[go.Candlestick(x=coin_df["Date"], open=coin_df["Open"], high=coin_df["High"], low=coin_df["Low"], close=coin_df["Close"])])
            fig.update_layout(title=f"{selected_coin} Candlestick Chart", xaxis_rangeslider_visible=False)
        elif chart_type == "Volume":
            fig = px.bar(coin_df, x="Date", y="Volume", title=f"{selected_coin} Volume Chart")
        st.plotly_chart(fig, use_container_width=True)

# --- NAVIGATION BUTTONS ---
st.header("Analytics & Tools")
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("📊 Data Exploration"): st.switch_page("pages/2.EDA.py")
with c2:
    if st.button("🔗 Correlation"): st.switch_page("pages/3.Group_&_Correlation.py")
with c3:
    if st.button("📈 Prediction"): st.switch_page("pages/4.Forecast.py")
with c4:
    if st.button("📰 News"): st.switch_page("pages/7.Top_Stories.py")