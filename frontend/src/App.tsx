import { useState } from "react"
import axios from "axios"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts"
import { Search, TrendingUp, TrendingDown, Minus, AlertCircle, Star, Zap } from "lucide-react"

const API = "http://localhost:8000"

const COLORS = ["#6366f1", "#f43f5e", "#10b981", "#f59e0b", "#3b82f6", "#8b5cf6"]

const healthColor = {
  excellent: "text-emerald-400",
  good: "text-blue-400",
  fair: "text-amber-400",
  poor: "text-red-400"
}

const urgencyColor = {
  low: "bg-emerald-500/20 text-emerald-400",
  medium: "bg-amber-500/20 text-amber-400",
  high: "bg-orange-500/20 text-orange-400",
  critical: "bg-red-500/20 text-red-400"
}

export default function App() {
  const [query, setQuery] = useState("")
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  const analyze = async () => {
    if (!query.trim()) return
    setLoading(true)
    setError(null)
    setData(null)
    try {
      const res = await axios.get(`${API}/analyze/${query.trim()}`)
      setData(res.data)
    } catch (e) {
      setError("Failed to analyze. Make sure the backend is running.")
    }
    setLoading(false)
  }

  const categoryData = data
    ? Object.entries(data.ml_analysis.categories).map(([name, val]) => ({
        name: name.replace("_", " "),
        count: val.count,
        pct: val.percentage
      }))
    : []

  const sentimentData = data
    ? [
        { name: "Positive", value: data.ml_analysis.sentiment.positive },
        { name: "Negative", value: data.ml_analysis.sentiment.negative },
        { name: "Neutral", value: data.ml_analysis.sentiment.neutral }
      ]
    : []

  const TrendIcon = data
    ? data.ml_analysis.trend.trend === "improving"
      ? TrendingUp
      : data.ml_analysis.trend.trend === "declining"
      ? TrendingDown
      : Minus
    : Minus

  const trendColor = data
    ? data.ml_analysis.trend.trend === "improving"
      ? "text-emerald-400"
      : data.ml_analysis.trend.trend === "declining"
      ? "text-red-400"
      : "text-amber-400"
    : ""

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <div className="max-w-6xl mx-auto">

        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-white mb-2">
            App Review <span className="text-indigo-400">Intelligence</span>
          </h1>
          <p className="text-gray-400 text-lg">AI-powered product analytics from real user reviews</p>
        </div>

        {/* Search */}
        <div className="flex gap-3 mb-10 max-w-xl mx-auto">
          <input
            className="flex-1 bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 transition"
            placeholder="Enter app name (e.g. Spotify, Swiggy...)"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === "Enter" && analyze()}
          />
          <button
            onClick={analyze}
            disabled={loading}
            className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-900 px-6 py-3 rounded-xl font-medium transition flex items-center gap-2"
          >
            {loading ? (
              <span className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
            ) : (
              <Search size={18} />
            )}
            {loading ? "Analyzing..." : "Analyze"}
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-400 text-center mb-6">
            {error}
          </div>
        )}

        {/* Loading state */}
        {loading && (
          <div className="text-center py-20">
            <div className="animate-spin h-12 w-12 border-4 border-indigo-500 border-t-transparent rounded-full mx-auto mb-4" />
            <p className="text-gray-400 text-lg">Scraping reviews and running AI analysis...</p>
            <p className="text-gray-600 text-sm mt-2">This takes about 60 seconds</p>
          </div>
        )}

        {/* Results */}
        {data && !loading && (
          <div className="space-y-6">

            {/* AI Insight Card */}
            <div className="bg-gray-900 border border-indigo-500/30 rounded-2xl p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-2xl font-bold capitalize">{data.app}</h2>
                  <p className={`text-lg font-medium capitalize mt-1 ${healthColor[data.ai_insight.overall_health]}`}>
                    {data.ai_insight.overall_health} health
                  </p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium capitalize ${urgencyColor[data.ai_insight.urgency]}`}>
                  {data.ai_insight.urgency} urgency
                </span>
              </div>
              <p className="text-gray-300 mb-4">{data.ai_insight.summary}</p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-800 rounded-xl p-4">
                  <p className="text-gray-500 text-sm mb-1">Top problem</p>
                  <p className="text-red-400 font-medium capitalize">{data.ai_insight.top_problem}</p>
                </div>
                <div className="bg-gray-800 rounded-xl p-4">
                  <p className="text-gray-500 text-sm mb-1">Top praise</p>
                  <p className="text-emerald-400 font-medium capitalize">{data.ai_insight.top_praise}</p>
                </div>
                <div className="bg-gray-800 rounded-xl p-4">
                  <p className="text-gray-500 text-sm mb-1">Recommendation</p>
                  <p className="text-indigo-400 font-medium capitalize">{data.ai_insight.recommendation}</p>
                </div>
              </div>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-900 rounded-2xl p-5 border border-gray-800">
                <p className="text-gray-500 text-sm">Total reviews</p>
                <p className="text-3xl font-bold text-white mt-1">{data.ml_analysis.sentiment.total_reviews}</p>
              </div>
              <div className="bg-gray-900 rounded-2xl p-5 border border-gray-800">
                <p className="text-gray-500 text-sm">Avg rating</p>
                <p className="text-3xl font-bold text-amber-400 mt-1 flex items-center gap-1">
                  {data.ml_analysis.sentiment.average_rating}
                  <Star size={20} />
                </p>
              </div>
              <div className="bg-gray-900 rounded-2xl p-5 border border-gray-800">
                <p className="text-gray-500 text-sm">Positive</p>
                <p className="text-3xl font-bold text-emerald-400 mt-1">{data.ml_analysis.sentiment.positive_pct}%</p>
              </div>
              <div className="bg-gray-900 rounded-2xl p-5 border border-gray-800">
                <p className="text-gray-500 text-sm">Trend</p>
                <p className={`text-3xl font-bold mt-1 flex items-center gap-1 capitalize ${trendColor}`}>
                  <TrendIcon size={24} />
                  {data.ml_analysis.trend.trend}
                </p>
              </div>
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

              {/* Category Bar Chart */}
              <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
                <h3 className="text-lg font-semibold mb-4">Review categories</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={categoryData}>
                    <XAxis dataKey="name" tick={{ fill: "#9ca3af", fontSize: 11 }} />
                    <YAxis tick={{ fill: "#9ca3af", fontSize: 11 }} />
                    <Tooltip
                      contentStyle={{ background: "#111827", border: "1px solid #374151", borderRadius: 8 }}
                      labelStyle={{ color: "#fff" }}
                    />
                    <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                      {categoryData.map((_, i) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Sentiment Pie Chart */}
              <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
                <h3 className="text-lg font-semibold mb-4">Sentiment breakdown</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={sentimentData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={4}
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}`}
                      labelLine={{ stroke: "#4b5563" }}
                    >
                      {sentimentData.map((_, i) => (
                        <Cell key={i} fill={["#10b981", "#f43f5e", "#f59e0b"][i]} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ background: "#111827", border: "1px solid #374151", borderRadius: 8 }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Top Issues */}
            <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <AlertCircle size={20} className="text-red-400" />
                Top priority issues
              </h3>
              <div className="space-y-3">
                {data.ml_analysis.top_issues.map((issue, i) => (
                  <div key={i} className="bg-gray-800 rounded-xl p-4 flex items-start gap-4">
                    <div className="bg-red-500/20 text-red-400 rounded-lg px-2 py-1 text-xs font-medium whitespace-nowrap capitalize">
                      {issue.predicted_label.replace("_", " ")}
                    </div>
                    <p className="text-gray-300 text-sm">{issue.review}</p>
                    <div className="ml-auto">
                      <div className="flex items-center gap-1 text-amber-400 text-sm font-medium whitespace-nowrap">
                        <Zap size={14} />
                        {issue.priority_score}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        )}
      </div>
    </div>
  )
}