
import snscrape.modules.twitter as sntwitter
import pandas as pd
from datetime import datetime, timedelta

KEYWORDS = ['explosion', 'protest', 'shortage', 'flood', 'crisis', 'displacement', 'conflict', 'fire', 'violence']
COUNTRIES = {
    'Lebanon': ['Beirut', 'Tripoli', 'Sidon', 'Bekaa'],
    'Syria': ['Damascus', 'Aleppo', 'Homs', 'Idlib']
}
TWEETS_PER_COUNTRY = 100
DAYS_BACK = 1

def tag_sentiment(text):
    warning_keywords = ['explosion', 'fire', 'flood', 'violence', 'conflict']
    rumor_keywords = ['rumor', 'hearing', 'unconfirmed']

    if any(word in text.lower() for word in warning_keywords):
        return 'Warning'
    elif any(word in text.lower() for word in rumor_keywords):
        return 'Rumor'
    else:
        return 'Neutral'

def scrape_country(country, cities):
    since = (datetime.utcnow() - timedelta(days=DAYS_BACK)).strftime('%Y-%m-%d')
    until = datetime.utcnow().strftime('%Y-%m-%d')

    results = []
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
    return results

def run_scraper():
    all_data = []
    for country, cities in COUNTRIES.items():
        all_data.extend(scrape_country(country, cities))
    df = pd.DataFrame(all_data)
    df.to_csv("twitter_incidents.csv", index=False)
    return df
