import os
import json
from groq import Groq
from pydantic import BaseModel, Field
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class ReviewInsight(BaseModel):
    app_name: str
    overall_health: str = Field(description="poor/fair/good/excellent")
    summary: str = Field(description="2-3 sentence executive summary")
    top_problem: str = Field(description="Single biggest issue users face")
    top_praise: str = Field(description="Single biggest thing users love")
    recommendation: str = Field(description="One clear action to take")
    urgency: str = Field(description="low/medium/high/critical")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_insight(app_name: str, ml_data: dict) -> ReviewInsight:
    prompt = f"""
You are a product analytics expert. Analyze this app review data and provide insights.

App: {app_name}
Total Reviews: {ml_data.get('sentiment', {}).get('total_reviews', 0)}
Positive: {ml_data.get('sentiment', {}).get('positive_pct', 0)}%
Negative: {ml_data.get('sentiment', {}).get('negative_pct', 0)}%
Average Rating: {ml_data.get('sentiment', {}).get('average_rating', 0)}
Rating Trend: {ml_data.get('trend', {}).get('trend', 'unknown')}
Categories: {json.dumps(ml_data.get('categories', {}), indent=2)}
Top Issues: {json.dumps(ml_data.get('top_issues', [])[:3], indent=2)}

Respond ONLY with a valid JSON object with these exact fields:
{{
    "app_name": "{app_name}",
    "overall_health": "poor/fair/good/excellent",
    "summary": "2-3 sentence executive summary",
    "top_problem": "single biggest issue",
    "top_praise": "single biggest thing users love",
    "recommendation": "one clear action to take",
    "urgency": "low/medium/high/critical"
}}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500
    )

    raw = response.choices[0].message.content.strip()

    # Clean markdown if present
    raw = raw.replace("```json", "").replace("```", "").strip()

    data = json.loads(raw)
    return ReviewInsight(**data)