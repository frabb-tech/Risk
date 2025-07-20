
import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
import re

# --- RSS Sources ---
RSS_FEEDS = {
    "Al Jazeera English": "https://www.aljazeera.com/xml/rss/all.xml",
    "Reuters Middle East": "http://feeds.reuters.com/Reuters/middleeastNews",
    "L’Orient-Le Jour (FR)": "https://www.lorientlejour.com/rss/accueil.xml"
}

KEYWORDS = ['explosion', 'protest', 'shortage', 'flood', 'crisis', 'displacement', 'conflict', 'fire', 'violence']
ADMIN1_LOCATIONS = {
    'Lebanon': ['Beirut', 'Tripoli', 'Sidon', 'Bekaa'],
    'Syria': ['Damascus', 'Aleppo', 'Homs', 'Idlib']
}

# --- Functions ---
def fetch_rss_entries():
    entries = []
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.title
            summary = entry.get("summary", "")
            published = entry.get("published", "")
            link = entry.link
            for keyword in KEYWORDS:
                if keyword.lower() in title.lower() or keyword.lower() in summary.lower():
                    entries.append({
                        'source': source,
                        'title': title,
                        'summary': summary,
                        'published': published,
                        'keyword': keyword,
                        'url': link,
                        'sentiment': tag_sentiment(title + " " + summary),
                        'admin1': detect_admin1(title + " " + summary)
                    })
    return pd.DataFrame(entries)

def tag_sentiment(text):
    warning_keywords = ['explosion', 'fire', 'flood', 'violence', 'conflict']
    rumor_keywords = ['rumor', 'hearing', 'unconfirmed']
    if any(word in text.lower() for word in warning_keywords):
        return 'Warning'
    elif any(word in text.lower() for word in rumor_keywords):
        return 'Rumor'
    else:
        return 'Neutral'

def detect_admin1(text):
    for country, cities in ADMIN1_LOCATIONS.items():
        for city in cities:
            if re.search(rf"\b{city}\b", text, re.IGNORECASE):
                return city
    return "Unknown"

# --- Streamlit App ---
st.set_page_config(page_title="📰 RSS Risk Monitor", layout="wide")
st.title("🧠 AI-Powered RSS Monitor")
st.markdown("Monitoring key humanitarian keywords across selected news feeds")

if st.button("🔁 Fetch Latest Feeds"):
    with st.spinner("Loading articles..."):
        df = fetch_rss_entries()
        st.success(f"{len(df)} entries loaded.")
        df.to_csv("rss_results.csv", index=False)
else:
    try:
        df = pd.read_csv("rss_results.csv")
    except:
        df = pd.DataFrame()

if not df.empty:
    st.markdown(f"### Results ({len(df)} entries)")
    col1, col2 = st.columns(2)
    with col1:
        filter_source = st.selectbox("Filter by Source", ["All"] + sorted(df['source'].unique()))
    with col2:
        filter_sentiment = st.selectbox("Filter by Sentiment", ["All", "Warning", "Rumor", "Neutral"])

    if filter_source != "All":
        df = df[df["source"] == filter_source]
    if filter_sentiment != "All":
        df = df[df["sentiment"] == filter_sentiment]

    st.dataframe(df[['published', 'source', 'admin1', 'keyword', 'sentiment', 'title', 'url']], use_container_width=True)
else:
    st.info("No data to display. Click above to fetch the latest feeds.")
