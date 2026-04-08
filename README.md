# App Review Intelligence Agent 🤖

An AI-powered product analytics tool that scrapes real user reviews from Google Play Store and App Store, runs ML models to classify and prioritize issues, and generates actionable business insights using a Groq LLM agent.

## 🔴 Live Demo
[Frontend](https://app-review-agent.vercel.app) | [Backend API](https://app-review-agent.onrender.com)

## 🎯 What it does
Type any app name → Agent scrapes 500+ real reviews → NLP + ML models analyze them → Groq AI generates a business intelligence report with charts

## 🧠 How it works

1. **Data Collection** — Scrapes 500+ most recent reviews from both Play Store and App Store using free APIs
2. **NLP Analysis** — TextBlob sentiment analysis classifies each review as positive, negative, or neutral
3. **ML Classification** — XGBoost model categorizes reviews into Bug Report, Feature Request, Ads Complaint, Pricing, Performance, Praise
4. **Priority Scoring** — Random Forest model scores each issue 0-100 based on urgency
5. **Trend Detection** — Logistic Regression predicts if app rating is improving or declining
6. **AI Insight** — Groq LLM agent synthesizes everything into an executive summary with recommendations

## 🛠️ Tech Stack

### Backend
- **FastAPI** — REST API framework
- **Groq** — Free LLM API (llama-3.3-70b-versatile)
- **HuggingFace Transformers** — NLP models
- **XGBoost + Scikit-learn** — ML classification and regression
- **Pandas + NumPy** — Data processing
- **Pydantic** — JSON schema validation
- **Tenacity** — Retry logic with exponential backoff
- **google-play-scraper** — Play Store reviews
- **TextBlob** — Sentiment analysis

### Frontend
- **React + Vite** — Frontend framework
- **TailwindCSS** — Styling
- **Recharts** — Interactive charts
- **Axios** — API calls
- **Lucide React** — Icons

## 📁 Project Structure
app-review-agent/
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   │   └── agent.py        # Groq LLM agent
│   │   ├── models/
│   │   │   └── classifier.py   # ML models
│   │   ├── tools/
│   │   │   ├── scraper.py      # Review scraper
│   │   │   └── sentiment.py    # NLP sentiment
│   │   └── main.py             # FastAPI endpoints
│   └── tests/
└── frontend/
└── src/
└── App.jsx             # React dashboard


## 🚀 Run Locally

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables
Create `backend/.env`:



## 📊 API Endpoints

| Endpoint | Description |
|---|---|
| `GET /analyze/{app_name}` | Full analysis pipeline |
| `GET /test-scraper/{app_name}` | Test review scraping |
| `GET /test-sentiment/{app_name}` | Test sentiment analysis |
| `GET /test-ml/{app_name}` | Test ML models |
| `GET /health` | Health check |

## 🎯 JD Coverage

This project covers requirements from all 3 internship applications:
- ✅ NLP + Deep Learning (sentiment analysis, transformers)
- ✅ ML Models (XGBoost, Random Forest, Logistic Regression)
- ✅ Tool-calling Agent (Groq LLM orchestrating multiple tools)
- ✅ JSON Schema + Pydantic validation
- ✅ Retry logic with Tenacity
- ✅ REST API with FastAPI
- ✅ Data preprocessing pipeline
- ✅ Interactive dashboard with charts
- ✅ Structured outputs with guardrails

## 👩‍💻 Author
Niharika Chauhan — [GitHub](https://github.com/Niharikachauhan123)