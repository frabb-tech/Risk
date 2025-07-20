
import streamlit as st
import pandas as pd
from twitter_scraper import run_scraper

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
