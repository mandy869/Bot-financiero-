import feedparser
import requests
import json
import os
import time

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

FEEDS = {
    "Investing.com": "https://www.investing.com/rss/news.rss",
    "Investing.com Mercados": "https://www.investing.com/rss/market_overview.rss",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "CNBC Finanzas": "https://www.cnbc.com/id/15839069/device/rss/rss.html",
    "CNBC Mercados": "https://www.cnbc.com/id/20910258/device/rss/rss.html",
    "BCE": "https://www.ecb.europa.eu/rss/press.html",
    "Fed": "https://www.federalreserve.gov/feeds/press_all.xml",
    "Investing.com España": "https://es.investing.com/rss/news.rss",
    "El Economista": "https://www.eleconomista.es/rss/rss-mercados.php",
}

POSTED_FILE = "posted.json"

def load_posted():
    if os.path.exists(POSTED_FILE):
        with open(POSTED_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_posted(posted):
    with open(POSTED_FILE, "w") as f:
        json.dump(list(posted)[-500:], f)

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    r = requests.post(url, data=payload)
    return r.ok

def main():
    posted = load_posted()
    new_posted = set(posted)

    for source_name, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
        except Exception as e:
            print(f"Error leyendo {source_name}: {e}")
            continue

        for entry in feed.entries[:5]:
            entry_id = entry.get("id", entry.get("link"))
            if entry_id in posted:
                continue

            title = entry.get("title", "Sin título")
            link = entry.get("link", "")

            message = f"📰 <b>{title}</b>\n\n🔗 Fuente: {source_name}\n{link}"

            if send_message(message):
                new_posted.add(entry_id)
                time.sleep(2)

    save_posted(new_posted)

if __name__ == "__main__":
    main()
