import streamlit as st
import pandas as pd
import feedparser
import re
from utils import load_all_data  # Using the centralized engine

# --- PAGE SETUP ---
st.set_page_config(page_title="Crypto Top Stories", layout="wide", page_icon="📰")

st.markdown(
    "<h1 style='text-align:center;color:#2E86C1'>📰 Crypto Top Stories</h1>",
    unsafe_allow_html=True,
)

# --- LOAD DATA VIA UTILS ---
try:
    data_dict = load_all_data()
    representatives = data_dict["rep_coins"]
    all_coins = data_dict["all_coins"]
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Process coin names for filtering
all_coins_upper = sorted(set([c.split("-")[0].upper() for c in all_coins]))
rep_coins_simple = [c.split("-")[0].upper() for c in representatives]

# RSS feeds to parse
rss_urls = [
    "https://cryptonews.com/news/feed",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://news.bitcoin.com/feed/",
]

# UI: filter selection
st.write("Filter news by cryptocurrency scope:")
selected_filter = st.radio(
    "",
    ["All 30 Cryptocurrencies", "4 Representatives"],
    horizontal=True,
    index=0,
    help="Select which coins to filter news by",
)

filter_coins = (
    rep_coins_simple if selected_filter == "4 Representatives" else all_coins_upper
)

# UI: slider for number of news articles
max_display = st.slider(
    "Number of news articles to display:", min_value=1, max_value=20, value=8, step=1
)

# Cache news fetch for 10 minutes
@st.cache_data(ttl=600)
def fetch_news(filter_coins):
    entries = []
    for url in rss_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            combined_text = (entry.title + " " + entry.get("summary", "")).upper()
            if any(coin in combined_text for coin in filter_coins):
                image_url = None
                # extract image using multiple strategies
                if "media_content" in entry:
                    mc = entry.media_content
                    if isinstance(mc, list) and len(mc) > 0 and "url" in mc[0]:
                        image_url = mc[0]["url"]
                    elif isinstance(mc, dict) and "url" in mc:
                        image_url = mc["url"]
                elif "media_thumbnail" in entry:
                    mt = entry.media_thumbnail
                    if isinstance(mt, list) and len(mt) > 0 and "url" in mt[0]:
                        image_url = mt[0]["url"]
                elif "links" in entry:
                    for link in entry.links:
                        if link.get("type", "").startswith("image"):
                            image_url = link["href"]
                            break
                if not image_url:
                    matches = re.findall(r'<img[^>]+src="([^">]+)"', entry.get("summary", ""))
                    if matches:
                        image_url = matches[0]
                if not image_url:
                    image_url = "https://cryptologos.cc/logos/all-crypto-logos.png"
                
                summary = entry.get("summary", "")
                summary = re.sub(r"The post .+? appeared first on .+?(\.|\.\.\.|!| )*", "", summary).strip()
                if len(summary) > 220:
                    summary = summary[:220] + "..."
                
                entries.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.get("published", "No date"),
                    "summary": summary,
                    "image": image_url,
                })
    return entries

news = fetch_news(filter_coins)

# UI styling for cards
card_style = """
    background-color: #f9fafb;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(44,62,80,0.07);
    padding: 15px 20px;
    margin-bottom: 20px;
    display: flex;
    align-items: flex-start;
"""
scrollable_div = "<div style='max-height:480px; overflow-y:auto; padding:5px'>"

st.markdown(scrollable_div, unsafe_allow_html=True)

if news:
    for article in news[:max_display]:
        st.markdown(
            f"""
            <div style="{card_style}">
                <img src="{article['image']}" style="width:110px; height:75px; object-fit:cover; border-radius:8px; margin-right:16px;">
                <div style="flex:1;">
                    <div style="font-size:1.05em; font-weight:bold; margin-bottom:6px;">{article['title']}</div>
                    <div style="color:#444; font-size:0.95em; margin-bottom:8px;">{article['summary']}</div>
                    <a href="{article['link']}" target="_blank" style="color:#2E86C1; font-weight:600; text-decoration:none;">
                        Read More &rarr;
                    </a>
                    <div style="font-size:0.85em; color:#888; margin-top:5px;">{article['published']}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.info("No recent news articles found for the selected filter.")

st.markdown("</div>", unsafe_allow_html=True)