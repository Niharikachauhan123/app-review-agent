from google_play_scraper import reviews
import requests
import pandas as pd
import re


def scrape_play_store(app_name: str, count: int = 500) -> list:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        KNOWN_IDS = {
            "instagram": "com.instagram.android",
            "spotify": "com.spotify.music",
            "whatsapp": "com.whatsapp",
            "youtube": "com.google.android.youtube",
            "swiggy": "in.swiggy.android",
            "zomato": "com.application.zomato",
            "phonepe": "com.phonepe.app",
            "paytm": "net.one97.paytm",
            "netflix": "com.netflix.mediaclient",
            "amazon": "com.amazon.mShop.android.shopping",
            "facebook": "com.facebook.katana",
            "twitter": "com.twitter.android",
            "snapchat": "com.snapchat.android",
            "telegram": "org.telegram.messenger",
            "uber": "com.ubercabs",
            "ola": "com.olacabs.customer",
        }

        known_id = KNOWN_IDS.get(app_name.lower())
        if known_id:
            app_id = known_id
            print(f"Using known app ID: {app_id}")
        else:
            search_url = "https://play.google.com/store/search"
            params = {"q": app_name, "c": "apps", "hl": "en", "gl": "us"}
            resp = requests.get(search_url, params=params, headers=headers, timeout=10)
            matches = re.findall(r'/store/apps/details\?id=([a-zA-Z0-9_.]+)', resp.text)
            if not matches:
                print(f"Could not find Play Store ID for: {app_name}")
                return []
            app_id = matches[0]
            print(f"Play Store app ID found: {app_id}")

        # Fetch in batches of 200 to get 500+ reviews
        all_reviews = []
        continuation_token = None

        for batch in range(3):
            result, continuation_token = reviews(
                app_id,
                lang="en",
                country="us",
                count=200,
                continuation_token=continuation_token
            )
            all_reviews.extend(result)
            print(f"Play Store batch {batch + 1}: {len(result)} reviews")
            if not continuation_token:
                break

        print(f"Play Store reviews collected: {len(all_reviews)}")
        return [
            {
                "source": "play_store",
                "review": r["content"],
                "rating": r["score"],
                "date": str(r["at"])
            }
            for r in all_reviews if r["content"]
        ]

    except Exception as e:
        print(f"Play Store error: {e}")
        import traceback
        traceback.print_exc()
        return []


def scrape_app_store(app_name: str, count: int = 500) -> list:
    try:
        search_url = f"https://itunes.apple.com/search?term={app_name}&country=us&entity=software&limit=1"
        resp = requests.get(search_url, timeout=10)
        data = resp.json()
        if not data["results"]:
            return []

        app_id = data["results"][0]["trackId"]
        all_reviews = []

        # Fetch 10 pages x 50 reviews = 500 reviews
        for page in range(1, 11):
            reviews_url = f"https://itunes.apple.com/us/rss/customerreviews/page={page}/id={app_id}/sortBy=mostRecent/json"
            resp = requests.get(reviews_url, timeout=10)
            feed = resp.json().get("feed", {})
            entries = feed.get("entry", [])

            if not entries:
                print(f"App Store: no more reviews at page {page}")
                break

            for e in entries[1:]:
                review_text = e.get("content", {}).get("label", "")
                if review_text:
                    all_reviews.append({
                        "source": "app_store",
                        "review": review_text,
                        "rating": int(e["im:rating"]["label"]),
                        "date": e["updated"]["label"]
                    })

        print(f"App Store reviews collected: {len(all_reviews)}")
        return all_reviews

    except Exception as e:
        print(f"App Store error: {e}")
        return []

def get_all_reviews(app_name: str, count: int = 500) -> pd.DataFrame:
    print(f"Scraping reviews for: {app_name}")

    play_reviews = scrape_play_store(app_name, count)
    store_reviews = scrape_app_store(app_name, count)

    all_reviews = play_reviews + store_reviews

    if not all_reviews:
        return pd.DataFrame()

    df = pd.DataFrame(all_reviews)
    df = df.drop_duplicates(subset=["review"])
    df = df[df["review"].str.len() > 10]
    df = df.reset_index(drop=True)

    print(f"Total reviews collected: {len(df)}")
    return df