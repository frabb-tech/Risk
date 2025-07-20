
import streamlit as st
import pandas as pd
import snscrape.modules.twitter as sntwitter
from datetime import datetime, timedelta

# -----------------------
# Configuration
# -----------------------
KEYWORDS = ['explosion', 'protest', 'shortage', 'flood', 'crisis', 'displacement', 'conflict', 'fire', 'violence']
COUNTRIES = {
    'Lebanon': ['Beirut', 'Tripoli', 'Sidon', 'Bekaa'],
    'Syria': ['Damascus', 'Aleppo', 'Homs', 'Idlib']
}
TWEETS_PER_COUNTRY = 100
DAYS_BACK = 1

# -----------------------
# Helper Functions
# -----------------------
def tag_sentiment(text):
    warning_keywords = ['explosion', 'fire', 'flood', 'violence', 'conflict']
    rumor_keywords = ['rumor', 'hearing', 'unconfirmed']
    if any(word in text.lower() for word in warning_keywords):
        return 'Warning'
    elif any(word in text.lower() for word in rumor_keywords):
        return 'Rumor'
    else:
        return 'Neutral'

def run_scraper():
    since = (datetime.utcnow() - timedelta(days=DAYS_BACK)).strftime('%Y-%m-%d')
    until = datetime.utcnow().strftime('%Y-%m-%d')
    results = []
    for country, cities in COUNTRIES.items():
        for city in cities:
            for keyword in KEYWORDS:
                query = f"{keyword} {city} since:{since} until:{until} lang:en"
                for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
                    if i >= TWEETS_PER_COUNTRY:
                        break
                    results.append({
                        'timestamp': tweet.date,
                        'country': country,
                        'admin1': city,
                        'keyword': keyword,
                        'user': tweet.user.username,
                        'text': tweet.content,
                        'sentiment': tag_sentiment(tweet.content),
                        'url': tweet.url
                    })
    df = pd.DataFrame(results)
    df.to_csv("twitter_incidents.csv", index=False)
    return df

# -----------------------
# Streamlit App
# -----------------------
st.set_page_config(page_title="AI Risk Monitor", layout="wide")
st.title("🧠 AI-Powered Incident & Rumor Monitor")
st.markdown("Live Twitter scraping for early warnings in Lebanon & Syria")

if st.button("🔁 Refresh Data Now"):
    with st.spinner("Fetching new tweets..."):
        df = run_scraper()
        st.success(f"{len(df)} tweets loaded.")
else:
    try:
        df = pd.read_csv("twitter_incidents.csv")
    except:
        df = pd.DataFrame()

if not df.empty:
    st.markdown(f"### Results ({len(df)} tweets)")
    col1, col2 = st.columns(2)
    with col1:
        country_filter = st.selectbox("Filter by Country", ["All"] + sorted(df['country'].unique().tolist()))
    with col2:
        sentiment_filter = st.selectbox("Filter by Sentiment", ["All", "Warning", "Rumor", "Neutral"])

    if country_filter != "All":
        df = df[df["country"] == country_filter]
    if sentiment_filter != "All":
        df = df[df["sentiment"] == sentiment_filter]

    st.dataframe(df[['timestamp', 'country', 'admin1', 'keyword', 'sentiment', 'text', 'url']], use_container_width=True)
else:
    st.warning("No data available. Click the refresh button above to load.")
