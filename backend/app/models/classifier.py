import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
import re


def clean_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def label_review(row) -> str:
    text = str(row["review"]).lower()
    rating = row["rating"]

    if any(w in text for w in ["crash", "bug", "error", "fix", "broken", "freeze", "problem", "issue", "glitch"]):
        return "bug_report"
    elif any(w in text for w in ["add", "feature", "wish", "would be", "should", "please add", "need"]):
        return "feature_request"
    elif any(w in text for w in ["ads", "advertisement", "ad", "popup", "annoying ad"]):
        return "ads_complaint"
    elif any(w in text for w in ["slow", "lag", "loading", "speed", "performance"]):
        return "performance"
    elif any(w in text for w in ["price", "cost", "expensive", "cheap", "subscription", "pay", "money"]):
        return "pricing"
    elif rating >= 4:
        return "praise"
    else:
        return "general_complaint"


def train_review_classifier(df: pd.DataFrame):
    df = df.copy()
    df["clean_review"] = df["review"].apply(clean_text)
    df["label"] = df.apply(label_review, axis=1)

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
        ("clf", XGBClassifier(n_estimators=100, random_state=42, eval_metric="mlogloss"))
    ])

    le = LabelEncoder()
    y = le.fit_transform(df["label"])
    pipeline.fit(df["clean_review"], y)

    return pipeline, le, df


def classify_reviews(df: pd.DataFrame):
    pipeline, le, df_labeled = train_review_classifier(df)
    df_labeled["predicted_label"] = le.inverse_transform(
        pipeline.predict(df_labeled["clean_review"])
    )
    return df_labeled


def get_category_summary(df: pd.DataFrame) -> dict:
    if "predicted_label" not in df.columns:
        return {}

    counts = df["predicted_label"].value_counts()
    total = len(df)

    return {
        category: {
            "count": int(count),
            "percentage": round(count / total * 100, 1)
        }
        for category, count in counts.items()
    }


def train_priority_scorer(df: pd.DataFrame):
    df = df.copy()
    df["clean_review"] = df["review"].apply(clean_text)

    sentiment_map = {"negative": 0, "neutral": 0.5, "positive": 1}
    df["sentiment_num"] = df.get("sentiment", pd.Series(["neutral"] * len(df))).map(sentiment_map).fillna(0.5)

    df["priority_score"] = (
        (5 - df["rating"]) * 20 +
        (1 - df["sentiment_num"]) * 40 +
        df["clean_review"].str.len().clip(0, 500) / 500 * 20
    ).clip(0, 100).round(1)

    return df


def predict_rating_trend(df: pd.DataFrame) -> dict:
    if df.empty or len(df) < 10:
        return {"trend": "insufficient_data"}

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df = df.sort_values("date")

    mid = len(df) // 2
    early_avg = df.iloc[:mid]["rating"].mean()
    recent_avg = df.iloc[mid:]["rating"].mean()
    diff = recent_avg - early_avg

    if diff > 0.2:
        trend = "improving"
    elif diff < -0.2:
        trend = "declining"
    else:
        trend = "stable"

    return {
        "trend": trend,
        "early_avg_rating": round(early_avg, 2),
        "recent_avg_rating": round(recent_avg, 2),
        "change": round(diff, 2)
    }