import feedparser
import hashlib
import json
from newspaper import Article
from datetime import datetime
from pathlib import Path
import requests
import re
import pandas as pd
from datetime import datetime

# this is where the human review staging directory is
REVIEW_QUEUE_DIR = "/opt/airflow/review_queue"


# the RSS feeds we are currently listening to
RSS_FEEDS = [
    "https://www.lgbtqnation.com/feed/",
    "https://www.advocate.com/rss.xml",
    "https://www.pinknews.co.uk/feed",
    "https://www.hrc.org/news/rss",
    "https://feeds.npr.org/512446800/podcast.xml",
    "https://www.metroweekly.com/feed/",
    "https://www.washingtonblade.com/feed/",
    "https://76crimes.com/feed/",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://www.politico.com/rss/politicopicks.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://www.washingtontimes.com/rss/headlines/news",
    "https://www.vox.com/rss/index.xml",
    "https://observer.com/feed/",
    "https://www.mercurynews.com/feed/",
    "https://nypost.com/feed/",
    "https://www.bostonherald.com/feed/",
    "https://www.phillyvoice.com/feed/",
    "https://wsvn.com/feed/",
    "https://citylimits.org/feed/",
    "https://www.texasobserver.org/feed/",
    "https://www.miamitodaynews.com/feed/",
    "https://www.denverpost.com/feed/",
    "https://foxtonnews.com/feed/",
    "https://www.westword.com/denver/Rss.xml",
    "http://www.usnews.com/rss/news",
    "http://www.redstate.com/feed/",
    "https://www.nationalreview.com/rss.xml",
    "http://www.popsci.com/rss.xml"

]

# this tracks the RSS articles we have already pulled
RSS_SEEN_FILE = "seen_articles.json"

# these are the keywords we are looking for in the RSS content
# we check both title and content for keywords
KEYWORDS = [
    "transgender", "trans", "non-binary", "genderqueer", 
    "gender nonconforming", "gender fluid", "gender identity", 
    "LGBTQ", "LGBTQIA", "LGBTQ+", "queer", "two-spirit", 
    "gender expression", "transition", "hormone therapy", 
    "gender-affirming care", "top surgery", "bottom surgery", 
    "gender dysphoria", "transphobia", "anti-trans", 
    "pro-trans", "trans rights", "trans issues", "pride", 
    "trans-inclusive", "deadname", "chosen name", 
    "they/them", "he/him", "she/her", "misgender", 
    "TERF", "trans women", "trans men", "trans youth", 
    "trans healthcare", "conversion therapy", 
    "gender marker", "birth certificate", 
    "drag queen", "drag performer", "drag ban", 
    "trans military", "bathroom bill", 
    "drag show", "queer community", 
    "transitioning", "name change", "pronouns", 
    "HRT", "gender confirmation surgery", 
    "anti-LGBTQ", "equality", "discrimination", 
    "hate crime", "civil rights", "intersectionality",
    "Stonewall", "Pride Month", "rainbow flag", 
    "trans visibility", "trans liberation", 
    "gender justice", "trans panic defense", 
    "trans athlete", "trans student", 
    "trans teacher", "trans worker", 
    "drag queen story hour", "pride parade", 
    "trans march", "allyship", "safe space", 
    "inclusive education", "inclusive healthcare"
]

# Load already seen articles
if Path(RSS_SEEN_FILE).exists():
    with open(RSS_SEEN_FILE, "r") as f:
        seen = set(json.load(f))
else:
    seen = set()

articles = []

for feed_url in RSS_FEEDS:
    try:
        feed = feedparser.parse(requests.get(feed_url, timeout=10).text)
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch RSS feed {feed_url}: {e}")
        continue  # Skip to the next feed

    for entry in feed.entries:
        url = entry.link
        uid = hashlib.sha256(url.encode()).hexdigest()
        if uid in seen:
            continue

        try:
            article = Article(url)
            article.download()
            article.parse()

            # Split title and content into words
            title_words = re.findall(r'\b\w+\b', entry.title.lower())
            content_words = re.findall(r'\b\w+\b', article.text.lower())

            # Check for keyword matches
            title_match = [kw for kw in KEYWORDS if kw.lower() in title_words]
            content_match = [kw for kw in KEYWORDS if kw.lower() in content_words]

            if not (title_match or content_match):
                continue  # Skip if no keyword match

            published_date = datetime(*entry.published_parsed[:6]).date().isoformat()

            article_data = {
                "uid": uid,
                "date": published_date,
                "title": article.title,
                "url": url,
                "publication": entry.get("published", ""),
                "author": None,  # we don't have author support with RSS
                "stance": None,  # we need to label the new articles
                "full_text": article.text,
                "stance_encoded": None,
                "embedding": None
            }

            # Save each article as a separate JSON file in the review queue
            current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            article_filename = f"{REVIEW_QUEUE_DIR}/article_{uid}_{current_datetime}.json"
            with open(article_filename, "w") as f:
                json.dump(article_data, f, indent=2)
            
            seen.add(uid)

            # Print save reason
            save_reason = []
            if title_match:
                save_reason.append(f"title (keywords: {', '.join(title_match)})")
            if content_match:
                save_reason.append(f"content (keywords: {', '.join(content_match)})")

            print(f"✅ Saved: {article.title} - Reason: {', '.join(save_reason)}")

        except Exception as e:
            print(f"❌ Failed to fetch article {url}: {e}")

# Update seen log
with open(RSS_SEEN_FILE, "w") as f:
    json.dump(list(seen), f)

print(f"Fetch Articles has concluded.")