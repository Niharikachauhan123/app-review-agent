from transformers import pipeline
import pandas as pd

print("Loading sentiment model...")
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    truncation=True,
    max_length=512
)
print("Sentiment model loaded!")
from textblob import TextBlob

def analyze_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    def quick_sentiment(text):
        analysis = TextBlob(str(text))
        score = analysis.sentiment.polarity
        if score > 0.1:
            return "positive", round(score, 3)
        elif score < -0.1:
            return "negative", round(abs(score), 3)
        else:
            return "neutral", round(abs(score), 3)

    results = df["review"].apply(quick_sentiment)
    df["sentiment"] = results.apply(lambda x: x[0])
    df["sentiment_score"] = results.apply(lambda x: x[1])

    return df


def get_sentiment_summary(df: pd.DataFrame) -> dict:
    if df.empty:
        return {}

    counts = df["sentiment"].value_counts()
    total = len(df)

    return {
        "total_reviews": total,
        "positive": int(counts.get("positive", 0)),
        "negative": int(counts.get("negative", 0)),
        "neutral": int(counts.get("neutral", 0)),
        "positive_pct": round(counts.get("positive", 0) / total * 100, 1),
        "negative_pct": round(counts.get("negative", 0) / total * 100, 1),
        "neutral_pct": round(counts.get("neutral", 0) / total * 100, 1),
        "average_rating": round(df["rating"].mean(), 2)
    }