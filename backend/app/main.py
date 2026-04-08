from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="App Review Agent API",
    description="AI agent that analyzes app reviews and generates insights",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "running",
        "message": "App Review Agent is live!"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "groq_key_loaded": bool(os.getenv("GROQ_API_KEY"))
    }

from app.tools.scraper import get_all_reviews

@app.get("/test-scraper/{app_name}")
def test_scraper(app_name: str):
    df = get_all_reviews(app_name, count=20)
    if df.empty:
        return {"status": "no reviews found"}
    return {
        "status": "success",
        "total_reviews": len(df),
        "sample": df.head(3).to_dict(orient="records")
    }

from app.tools.sentiment import analyze_sentiment, get_sentiment_summary

@app.get("/test-sentiment/{app_name}")
def test_sentiment(app_name: str):
    df = get_all_reviews(app_name, count=30)
    if df.empty:
        return {"status": "no reviews found"}
    df = analyze_sentiment(df)
    summary = get_sentiment_summary(df)
    return {
        "status": "success",
        "app": app_name,
        "sentiment_summary": summary
    }

from app.models.classifier import classify_reviews, get_category_summary, train_priority_scorer, predict_rating_trend
from app.tools.sentiment import analyze_sentiment, get_sentiment_summary

@app.get("/test-ml/{app_name}")
def test_ml(app_name: str):
    df = get_all_reviews(app_name, count=100)
    if df.empty:
        return {"status": "no reviews found"}

    df = analyze_sentiment(df)
    df = classify_reviews(df)
    df = train_priority_scorer(df)
    sentiment = get_sentiment_summary(df)
    categories = get_category_summary(df)
    trend = predict_rating_trend(df)

    return {
        "status": "success",
        "app": app_name,
        "sentiment": sentiment,
        "categories": categories,
        "trend": trend,
        "top_issues": df[df["predicted_label"] != "praise"]
            .nlargest(5, "priority_score")[["review", "predicted_label", "priority_score"]]
            .to_dict(orient="records")
    }

from app.agent.agent import generate_insight

@app.get("/analyze/{app_name}")
def analyze_app(app_name: str):
    # Step 1: Scrape
    df = get_all_reviews(app_name, count=500)
    if df.empty:
        return {"status": "no reviews found"}

    # Step 2: NLP
    df = analyze_sentiment(df)

    # Step 3: ML models
    df = classify_reviews(df)
    df = train_priority_scorer(df)

    # Step 4: Build ML summary
    ml_data = {
        "sentiment": get_sentiment_summary(df),
        "categories": get_category_summary(df),
        "trend": predict_rating_trend(df),
        "top_issues": df[df["predicted_label"] != "praise"]
            .nlargest(5, "priority_score")[["review", "predicted_label", "priority_score"]]
            .to_dict(orient="records")
    }

    # Step 5: Groq agent generates insight
    insight = generate_insight(app_name, ml_data)

    return {
        "status": "success",
        "app": app_name,
        "ml_analysis": ml_data,
        "ai_insight": insight.dict()
    }