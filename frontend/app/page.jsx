"use client";

import { useState, useEffect } from "react";
import {
  Search,
  Zap,
  BarChart2,
  AlertCircle,
  Map,
  Play,
  CheckCircle,
  RefreshCw,
  Sliders,
  Database,
  TrendingUp,
  History,
  BookOpen,
  Cpu,
  Info,
  Brain,
  Clock,
  Sun,
  Moon,
  Rocket,
  Shield,
  Activity,
  Trophy,
} from "lucide-react";
import { useTheme } from "next-themes";

const apiUrl = process.env.NEXT_PUBLIC_API_URL || (typeof window !== "undefined" && window.location.port === "3000" ? "http://127.0.0.1:8000" : "");

export default function Home() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Navigation
  const [activeTab, setActiveTab] = useState("search");
  // Search state
  const [query, setQuery] = useState("");
  const [expandedQuery, setExpandedQuery] = useState(null);
  const [results, setResults] = useState([]);
  const [topResult, setTopResult] = useState(null);
  const [sources, setSources] = useState([]);
  const [matchedQuery, setMatchedQuery] = useState(null);
  const [similarity, setSimilarity] = useState(0);
  const [cluster, setCluster] = useState(0);
  const [cacheStatus, setCacheStatus] = useState("MISS");
  const [processingTime, setProcessingTime] = useState(0);
  // App UI states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [recentSearches, setRecentSearches] = useState([]);
  const [activeExplanation, setActiveExplanation] = useState(null);
  // Cluster visualization state
  const [clusterPoints, setClusterPoints] = useState([]);
  const [clusterLoading, setClusterLoading] = useState(false);
  const [hoveredPoint, setHoveredPoint] = useState(null);
  // Analytics data
  const [analyticsData, setAnalyticsData] = useState(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  // Evaluation data
  const [evaluationReport, setEvaluationReport] = useState(null);
  const [evaluationLoading, setEvaluationLoading] = useState(false);
  const [evalK, setEvalK] = useState(5);
  // Reindexing state
  const [reindexing, setReindexing] = useState(false);
  const [reindexSuccess, setReindexSuccess] = useState(false);

  const suggestionList = [
    "space missions and satellites",
    "apollo moon landing program",
    "graphics card gpu drivers",
    "cryptography key encryption algorithms",
    "nhl game hockey team playoffs",
    "medical cancer disease treatment",
    "christian faith bible studies",
    "politics gun laws congressional debate",
  ];

  const trendingTopics = [
    {
      icon: Rocket,
      label: "Space Exploration",
      query: "space exploration missions",
    },
    {
      icon: Shield,
      label: "Cryptography",
      query: "cryptography key encryption",
    },
    {
      icon: Activity,
      label: "Cancer Treatment",
      query: "medical cancer disease treatment",
    },
    { icon: Trophy, label: "Hockey Playoffs", query: "nhl game hockey team" },
  ];

  // Load recent searches from localStorage on mount
  useEffect(() => {
    setMounted(true);
    const saved = localStorage.getItem("vectormind_recent_searches");
    if (saved) {
      try {
        setRecentSearches(JSON.parse(saved));
      } catch (e) {
        console.error(e);
      }
    }
  }, []);

  // Auto-fetch visualization points when tab changes
  useEffect(() => {
    if (activeTab === "clusters" && clusterPoints.length === 0) {
      fetchClusterPoints();
    } else if (activeTab === "analytics") {
      fetchAnalytics();
    } else if (activeTab === "evaluation" && !evaluationReport) {
      runEvaluation();
    }
  }, [activeTab]);

  // Filter suggestions
  useEffect(() => {
    if (query.trim().length === 0) {
      setSuggestions([]);
      return;
    }
    const filtered = suggestionList.filter(
      (s) =>
        s.toLowerCase().includes(query.toLowerCase()) &&
        s.toLowerCase() !== query.toLowerCase(),
    );
    setSuggestions(filtered.slice(0, 4));
  }, [query]);

  const saveRecentSearch = (term) => {
    const cleanTerm = term.trim();
    if (!cleanTerm) return;
    const updated = [
      cleanTerm,
      ...recentSearches.filter((s) => s !== cleanTerm),
    ].slice(0, 5);
    setRecentSearches(updated);
    localStorage.setItem("vectormind_recent_searches", JSON.stringify(updated));
  };

  const handleSearch = async (searchQuery) => {
    const queryToSearch = searchQuery || query;
    if (!queryToSearch.trim()) return;

    setQuery(queryToSearch);
    setSuggestions([]);
    setLoading(true);
    setError(null);
    setHasSearched(true);
    setShowResults(false);
    setActiveExplanation(null);
    saveRecentSearch(queryToSearch);

    try {
      const response = await fetch(`${apiUrl}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: queryToSearch.trim() }),
      });

      if (!response.ok) {
        throw new Error(`API returned status ${response.status}`);
      }

      const data = await response.json();
      setResults(data.results || []);
      setTopResult(data.result || null);
      setMatchedQuery(data.matched_query || null);
      setSources(data.sources || []);
      setExpandedQuery(data.expanded_query || null);
      setSimilarity(Math.round((data.similarity_score || 0) * 100));
      setCluster(data.dominant_cluster || 0);
      setCacheStatus(data.cache_hit ? "HIT" : "MISS");
      setProcessingTime(data.processing_time || 0);
      setTimeout(() => setShowResults(true), 150);
    } catch (err) {
      console.error(err);
      setError(
        "Failed to fetch search results. Verify that your backend container is running.",
      );
    } finally {
      setLoading(false);
    }
  };

  // Fetch 2D cluster coordinates from t-SNE endpoint
  const fetchClusterPoints = async () => {
    setClusterLoading(true);
    try {
      const res = await fetch(`${apiUrl}/clusters/visualization`);
      const data = await res.json();
      setClusterPoints(data.points || []);
    } catch (e) {
      console.error(e);
    } finally {
      setClusterLoading(false);
    }
  };

  // Fetch telemetry logs
  const fetchAnalytics = async () => {
    setAnalyticsLoading(true);
    try {
      const res = await fetch(`${apiUrl}/analytics`);
      const data = await res.json();
      setAnalyticsData(data);
    } catch (e) {
      console.error(e);
    } finally {
      setAnalyticsLoading(false);
    }
  };

  // Run retrieval evaluation benchmarker
  const runEvaluation = async (kVal = evalK) => {
    setEvaluationLoading(true);
    try {
      const res = await fetch(`${apiUrl}/evaluate?k=${kVal}`);
      const data = await res.json();
      setEvaluationReport(data);
    } catch (e) {
      console.error(e);
    } finally {
      setEvaluationLoading(false);
    }
  };

  // Trigger backend document reindexing
  const triggerReindexing = async () => {
    setReindexing(true);
    setReindexSuccess(false);
    try {
      const res = await fetch(`${apiUrl}/reindex`, {
        method: "POST",
        headers: {
          "X-Admin-Token": "vectormind_admin_secret"
        }
      });
      if (res.ok) {
        setReindexSuccess(true);
        // Refresh visualization and stats
        setClusterPoints([]);
        setEvaluationReport(null);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setReindexing(false);
    }
  };

  // Helper colors for clusters
  const clusterColors = [
    {
      fill: "#6366F1",
      text: "text-indigo-600",
      bg: "bg-indigo-50 dark:bg-indigo-950/30",
      label: "Graphics & Computers",
    },
    {
      fill: "#10B981",
      text: "text-emerald-600",
      bg: "bg-emerald-50 dark:bg-emerald-950/30",
      label: "Medicine & Health",
    },
    {
      fill: "#8B5CF6",
      text: "text-violet-600",
      bg: "bg-violet-50 dark:bg-violet-950/30",
      label: "Space & Science",
    },
    {
      fill: "#F59E0B",
      text: "text-amber-600",
      bg: "bg-amber-50 dark:bg-amber-950/30",
      label: "Hockey & Sports",
    },
    {
      fill: "#EF4444",
      text: "text-rose-600",
      bg: "bg-rose-50 dark:bg-rose-950/30",
      label: "Politics & Law",
    },
  ];

  // Render highlighted search queries matching input
  const renderHighlighted = (text, kwQuery) => {
    if (!kwQuery) return text;
    const words = kwQuery.split(" ").filter((w) => w.length > 2);
    let result = text;
    words.forEach((word) => {
      const regex = new RegExp(
        `(${word.replace(/[-\/\\^$*+?.()|[\]{}]/g, "\\$&")})`,
        "gi",
      );
      result = result.replace(
        regex,
        `<mark class="bg-amber-100 dark:bg-amber-950/40 text-amber-800 dark:text-amber-300 font-semibold px-1 rounded-sm">$1</mark>`,
      );
    });
    return result;
  };

  // Draw 2D t-SNE scatter chart mapping coordinates to bounds
  const renderTSNEScatter = () => {
    if (clusterPoints.length === 0) return null;

    const width = 600;
    const height = 400;
    const padding = 35;

    const xCoords = clusterPoints.map((p) => p.x);
    const yCoords = clusterPoints.map((p) => p.y);

    const minX = Math.min(...xCoords);
    const maxX = Math.max(...xCoords);
    const minY = Math.min(...yCoords);
    const maxY = Math.max(...yCoords);

    const scaleX = (x) => {
      const range = maxX - minX || 1;
      return padding + ((x - minX) / range) * (width - 2 * padding);
    };

    const scaleY = (y) => {
      const range = maxY - minY || 1;
      return padding + ((y - minY) / range) * (height - 2 * padding);
    };

    return (
      <div className="relative border border-gray-200 dark:border-gray-800 rounded-2xl bg-white dark:bg-gray-900 p-6 flex flex-col items-center">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full max-w-xl h-auto overflow-visible cursor-crosshair"
        >
          {/* Grid lines */}
          <line
            x1={padding}
            y1={height / 2}
            x2={width - padding}
            y2={height / 2}
            stroke="#E5E7EB"
            strokeWidth="1"
            strokeDasharray="3"
            className="dark:stroke-gray-800"
          />
          <line
            x1={width / 2}
            y1={padding}
            x2={width / 2}
            y2={height - padding}
            stroke="#E5E7EB"
            strokeWidth="1"
            strokeDasharray="3"
            className="dark:stroke-gray-800"
          />

          {clusterPoints.map((point) => {
            const cx = scaleX(point.x);
            const cy = scaleY(point.y);
            const color =
              clusterColors[point.cluster % clusterColors.length].fill;
            const isHovered = hoveredPoint && hoveredPoint.id === point.id;
            const isSelected = results.some((r) => r.index === point.id);

            return (
              <circle
                key={point.id}
                cx={cx}
                cy={cy}
                r={isHovered ? 8 : isSelected ? 6 : 4}
                fill={color}
                opacity={isHovered ? 1.0 : isSelected ? 0.9 : 0.6}
                stroke={isHovered || isSelected ? "#000000" : "none"}
                strokeWidth="1.5"
                onMouseEnter={() => setHoveredPoint(point)}
                className="transition-all duration-150 ease-in-out cursor-pointer hover:scale-125"
              />
            );
          })}
        </svg>

        {/* Legend */}
        <div className="mt-6 flex flex-wrap justify-center gap-4 text-xs font-medium">
          {clusterColors.map((color, idx) => (
            <div key={idx} className="flex items-center gap-2">
              <span
                className="h-3.5 w-3.5 rounded-full inline-block"
                style={{ backgroundColor: color.fill }}
              ></span>
              <span className="text-gray-600 dark:text-gray-400">
                {color.label}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <main className="min-h-screen bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 font-sans transition-colors duration-200">
      {/* Upper Brand Header */}
      <nav className="border-b border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-50 dark:bg-indigo-950/30 rounded-xl text-indigo-600 dark:text-indigo-400">
              <Zap className="h-5 w-5 animate-pulse" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-600 bg-clip-text text-transparent">
              VectorMind{" "}
              <span className="text-xs font-semibold px-2 py-0.5 border border-indigo-400/30 rounded-full text-indigo-500 ml-1">
                v2.0 RAG
              </span>
            </span>
          </div>

          {/* Navigation Tabs & Theme Toggle */}
          <div className="flex items-center gap-3.5">
            <div className="flex items-center bg-gray-100 dark:bg-gray-800 p-1 rounded-xl">
              <button
                onClick={() => setActiveTab("search")}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                  activeTab === "search"
                    ? "bg-white dark:bg-gray-700 text-indigo-600 dark:text-indigo-400 shadow-sm"
                    : "text-gray-500 hover:text-gray-900 dark:hover:text-gray-200"
                }`}
              >
                <Search className="h-4 w-4" /> Search & RAG
              </button>
              <button
                onClick={() => setActiveTab("clusters")}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                  activeTab === "clusters"
                    ? "bg-white dark:bg-gray-700 text-indigo-600 dark:text-indigo-400 shadow-sm"
                    : "text-gray-500 hover:text-gray-900 dark:hover:text-gray-200"
                }`}
              >
                <Map className="h-4 w-4" /> Cluster Map
              </button>
              <button
                onClick={() => setActiveTab("analytics")}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                  activeTab === "analytics"
                    ? "bg-white dark:bg-gray-700 text-indigo-600 dark:text-indigo-400 shadow-sm"
                    : "text-gray-500 hover:text-gray-900 dark:hover:text-gray-200"
                }`}
              >
                <BarChart2 className="h-4 w-4" /> Analytics
              </button>
              <button
                onClick={() => setActiveTab("evaluation")}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                  activeTab === "evaluation"
                    ? "bg-white dark:bg-gray-700 text-indigo-600 dark:text-indigo-400 shadow-sm"
                    : "text-gray-500 hover:text-gray-900 dark:hover:text-gray-200"
                }`}
              >
                <Cpu className="h-4 w-4" /> Benchmarks
              </button>
            </div>

            <button
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="p-2.5 rounded-xl bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200 transition-all border border-transparent hover:border-gray-250 dark:hover:border-gray-700 h-9 w-9 flex items-center justify-center"
              aria-label="Toggle theme"
            >
              {mounted && theme === "dark" ? (
                <Sun className="h-4.5 w-4.5" />
              ) : (
                <Moon className="h-4.5 w-4.5" />
              )}
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content Area */}
      <div className="max-w-6xl mx-auto px-6 py-10">
        {/* ================= TAB 1: SEARCH & RAG ================= */}
        {activeTab === "search" && (
          <div className="space-y-8">
            {/* Search Input Card */}
            <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-6 shadow-md">
              <div className="flex gap-3 relative">
                <div className="flex-1 relative">
                  <Search className="absolute left-5 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                  <input
                    className="w-full bg-gray-50 dark:bg-gray-800 border-2 border-gray-150 dark:border-gray-700 rounded-full pl-13 pr-6 py-4 text-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all shadow-inner"
                    placeholder="Ask a question or enter keywords..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && handleSearch()}
                  />

                  {/* Query Auto-suggestions */}
                  {suggestions.length > 0 && (
                    <div className="absolute bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl shadow-2xl mt-2 w-full z-20 overflow-hidden divide-y divide-gray-100 dark:divide-gray-700">
                      {suggestions.map((s, idx) => (
                        <div
                          key={idx}
                          className="p-4 hover:bg-indigo-50 dark:hover:bg-indigo-950/20 cursor-pointer transition-colors"
                          onClick={() => handleSearch(s)}
                        >
                          <span className="text-gray-800 dark:text-gray-200 font-medium text-sm flex items-center gap-2">
                            <TrendingUp className="h-3.5 w-3.5 text-indigo-500" />{" "}
                            {s}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <button
                  disabled={loading}
                  onClick={() => handleSearch()}
                  className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white px-8 py-4 rounded-full font-bold shadow-md hover:shadow-lg hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center gap-2"
                >
                  {loading ? (
                    <RefreshCw className="h-4 w-4 animate-spin" />
                  ) : (
                    <Search className="h-4 w-4" />
                  )}
                  Search
                </button>
              </div>

              {/* Synonym Expansion Alert */}
              {hasSearched &&
                expandedQuery &&
                expandedQuery.toLowerCase() !== query.toLowerCase() && (
                  <div className="mt-4 px-4 py-2.5 bg-indigo-50/55 dark:bg-indigo-950/20 border border-indigo-100 dark:border-indigo-900/30 rounded-xl flex items-center gap-2.5 text-xs text-indigo-700 dark:text-indigo-300">
                    <Info className="h-4 w-4 text-indigo-500 flex-shrink-0" />
                    <span>
                      <strong>Query expanded for recall:</strong>{" "}
                      {expandedQuery}
                    </span>
                  </div>
                )}

              {/* Recent Searches & Trending */}
              {!hasSearched && (
                <div className="mt-6 pt-6 border-t border-gray-100 dark:border-gray-800 flex flex-col md:flex-row justify-between gap-6">
                  {recentSearches.length > 0 && (
                    <div className="space-y-2">
                      <p className="text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
                        <History className="h-3 w-3" /> Recent Queries
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {recentSearches.map((term, idx) => (
                          <button
                            key={idx}
                            onClick={() => handleSearch(term)}
                            className="text-xs bg-gray-150 dark:bg-gray-800 hover:bg-indigo-50 dark:hover:bg-indigo-950/30 hover:text-indigo-600 px-3.5 py-1.5 rounded-lg font-semibold border border-transparent hover:border-indigo-500/20 transition-all"
                          >
                            {term}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="space-y-2">
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
                      <TrendingUp className="h-3 w-3" /> Trending Topics
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {trendingTopics.map((t, idx) => {
                        const IconComponent = t.icon;
                        return (
                          <button
                            key={idx}
                            onClick={() => handleSearch(t.query)}
                            className="text-xs bg-gray-150 dark:bg-gray-800 hover:bg-indigo-50 dark:hover:bg-indigo-950/30 hover:text-indigo-600 px-3.5 py-1.5 rounded-lg font-semibold border border-transparent hover:border-indigo-500/20 transition-all flex items-center gap-1.5"
                          >
                            <IconComponent className="h-3.5 w-3.5 text-indigo-500" />{" "}
                            {t.label}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {error && (
              <div className="p-4 bg-red-50 dark:bg-red-950/25 border-2 border-red-200 dark:border-red-900/30 rounded-2xl flex items-center gap-3 text-red-600 dark:text-red-400 shadow-sm">
                <AlertCircle className="h-5 w-5 flex-shrink-0" />
                <span className="text-sm font-semibold">{error}</span>
              </div>
            )}

            {/* Loading Skeleton */}
            {loading && (
              <div className="space-y-8 animate-pulse">
                <div className="h-44 bg-gray-200 dark:bg-gray-800 rounded-3xl"></div>
                <div className="space-y-4">
                  <div className="h-6 w-44 bg-gray-200 dark:bg-gray-800 rounded-md"></div>
                  <div className="h-28 bg-gray-200 dark:bg-gray-800 rounded-2xl"></div>
                  <div className="h-28 bg-gray-200 dark:bg-gray-800 rounded-2xl"></div>
                </div>
              </div>
            )}

            {/* RAG Answer Display */}
            {!loading && hasSearched && topResult && (
              <div
                className={`space-y-8 transition-opacity duration-300 ${showResults ? "opacity-100" : "opacity-0"}`}
              >
                {/* Latency Meter Bar */}
                <div className="flex flex-wrap items-center justify-between gap-4 text-xs font-bold text-gray-400 px-2">
                  <span className="bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-400 px-3 py-1 rounded-full border border-emerald-500/10 flex items-center gap-1">
                    <CheckCircle className="h-3 w-3" /> System Ready
                  </span>
                  <div className="flex gap-4">
                    <span>
                      Latency:{" "}
                      <strong className="text-emerald-500">
                        {processingTime}s
                      </strong>
                    </span>
                    <span>
                      Cache:{" "}
                      <strong
                        className={
                          cacheStatus === "HIT"
                            ? "text-indigo-500"
                            : "text-amber-500"
                        }
                      >
                        {cacheStatus}
                      </strong>
                    </span>
                    <span>
                      Cluster:{" "}
                      <strong className="text-violet-500">#{cluster}</strong>
                    </span>
                  </div>
                </div>

                {/* Grounded LLM Response */}
                <div className="bg-gradient-to-tr from-indigo-500/5 to-purple-500/5 dark:from-indigo-950/20 dark:to-purple-950/20 border-2 border-indigo-500/20 rounded-3xl p-8 shadow-lg relative overflow-hidden">
                  <div className="absolute right-0 top-0 translate-x-4 -translate-y-4 opacity-5 text-indigo-600 dark:text-indigo-400 pointer-events-none select-none">
                    <Brain className="h-48 w-48" />
                  </div>

                  <h3 className="text-2xl font-bold mb-4 bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400 bg-clip-text text-transparent flex items-center gap-2">
                    <Cpu className="h-6 w-6 text-indigo-500" /> AI Grounded
                    Answer
                  </h3>

                  <p className="text-gray-800 dark:text-gray-200 leading-relaxed text-lg mb-6">
                    {topResult}
                  </p>

                  {/* Sources tag list */}
                  {sources.length > 0 && (
                    <div className="pt-4 border-t border-gray-200/50 dark:border-gray-850 flex flex-wrap items-center gap-3">
                      <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">
                        <BookOpen className="h-3.5 w-3.5 inline mr-1" />{" "}
                        Referenced Sources:
                      </span>
                      {sources.map((src, idx) => (
                        <span
                          key={idx}
                          className="text-xs font-semibold bg-gray-150 dark:bg-gray-800 text-gray-600 dark:text-gray-300 px-3 py-1.5 rounded-lg border border-gray-200/20 shadow-sm"
                        >
                          {src}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Document Results List */}
                <div className="space-y-4">
                  <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200 flex items-center gap-2">
                    <Database className="h-5.5 w-5.5 text-indigo-500" /> Ranked
                    Context Documents ({results.length})
                  </h2>

                  <div className="space-y-4">
                    {results.map((result, index) => {
                      const isExplaining = activeExplanation === index;
                      const colorSet =
                        clusterColors[result.cluster % clusterColors.length];
                      return (
                        <div
                          key={index}
                          className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm hover:shadow-lg transition-all hover:scale-[1.01] hover:border-indigo-500/25 relative overflow-hidden group"
                        >
                          {/* Upper Card Header */}
                          <div className="flex justify-between items-center mb-4">
                            <div className="flex items-center gap-2.5">
                              <span className="h-7 w-7 rounded-full bg-gray-100 dark:bg-gray-800 group-hover:bg-indigo-50 dark:group-hover:bg-indigo-950/30 text-xs font-bold flex items-center justify-center text-gray-500 group-hover:text-indigo-500 transition-colors">
                                {index + 1}
                              </span>
                              <span
                                className={`text-xs font-bold uppercase px-2.5 py-1 rounded-full border border-transparent ${colorSet.bg} ${colorSet.text}`}
                              >
                                {colorSet.label}
                              </span>
                            </div>

                            <div className="flex gap-4 text-xs font-bold">
                              {result.similarity_score !== undefined && (
                                <span className="text-indigo-600 dark:text-indigo-400">
                                  Score:{" "}
                                  {Math.round(result.similarity_score * 100)}%
                                </span>
                              )}
                              {result.rrf_score !== undefined && (
                                <span className="text-purple-600 dark:text-purple-400">
                                  RRF Rank Score:{" "}
                                  {roundVal(result.rrf_score, 3)}
                                </span>
                              )}
                            </div>
                          </div>

                          {/* Document text preview */}
                          <div
                            className="text-gray-800 dark:text-gray-200 leading-relaxed text-sm max-h-48 overflow-y-auto mb-4 border-l-2 border-gray-200 dark:border-gray-800 pl-4"
                            dangerouslySetInnerHTML={{
                              __html: renderHighlighted(result.document, query),
                            }}
                          />

                          {/* Explanation Toggle */}
                          <div className="pt-2 border-t border-gray-100 dark:border-gray-850">
                            <button
                              onClick={() =>
                                setActiveExplanation(
                                  isExplaining ? null : index,
                                )
                              }
                              className="text-xs font-semibold text-gray-500 hover:text-indigo-500 flex items-center gap-1 bg-gray-100 dark:bg-gray-800 px-3 py-1.5 rounded-lg border border-transparent hover:border-indigo-500/10 transition-colors"
                            >
                              <Info className="h-3.5 w-3.5" />{" "}
                              {isExplaining
                                ? "Hide explanation"
                                : "Why was this document retrieved?"}
                            </button>

                            {isExplaining && result.explanation && (
                              <div className="mt-3 p-4 bg-gray-50 dark:bg-gray-950 rounded-xl border border-gray-200/50 dark:border-gray-800 text-xs text-gray-600 dark:text-gray-400 leading-relaxed animate-fadeIn">
                                <strong>Retrieval Logic:</strong>{" "}
                                {result.explanation}
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            {/* Unsearched Placeholder State */}
            {!hasSearched && !loading && (
              <div className="rounded-3xl border-2 border-dashed border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-gray-900/35 p-16 text-center shadow-sm">
                <div className="h-16 w-16 bg-gray-100 dark:bg-gray-800 rounded-2xl inline-flex items-center justify-center mb-6 text-[#F97316]">
                  <Zap className="h-8 w-8" />
                </div>
                <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                  Intelligent Retrieval System
                </h3>
                <p className="text-gray-500 dark:text-gray-400 mt-2 max-w-md mx-auto">
                  Type a query above to query document embeddings, apply BM25
                  hybrid indexing, and run cross-encoder LLM reranking.
                </p>
              </div>
            )}
          </div>
        )}

        {/* ================= TAB 2: TOPIC CLUSTERS MAP ================= */}
        {activeTab === "clusters" && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Left side detail panel */}
            <div className="md:col-span-1 space-y-6">
              <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-6 shadow-md">
                <h3 className="text-xl font-bold mb-3 flex items-center gap-2">
                  <Map className="h-5 w-5 text-indigo-500" /> Topic Clusters Map
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
                  This 2D visualization projects the 384-dimensional document
                  embeddings down to a 2D space using **t-Distributed Stochastic
                  Neighbor Embedding (t-SNE)**.
                </p>

                <div className="mt-6 pt-6 border-t border-gray-100 dark:border-gray-800 space-y-4">
                  <button
                    disabled={reindexing}
                    onClick={triggerReindexing}
                    className="w-full bg-gray-150 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 py-3 rounded-xl font-bold transition-colors text-sm flex items-center justify-center gap-2 border border-gray-200/20"
                  >
                    <RefreshCw
                      className={`h-4 w-4 ${reindexing ? "animate-spin" : ""}`}
                    />
                    {reindexing
                      ? "Reindexing Corpus..."
                      : "Trigger Reindex Corpus"}
                  </button>

                  {reindexSuccess && (
                    <p className="text-xs font-bold text-emerald-500 text-center flex items-center justify-center gap-1.5">
                      <CheckCircle className="h-3.5 w-3.5" /> Reindexed
                      successfully!
                    </p>
                  )}
                </div>
              </div>

              {/* Point hover detail */}
              <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-6 shadow-md min-h-48 flex flex-col justify-between">
                {hoveredPoint ? (
                  <div className="space-y-3">
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">
                      Document Details
                    </p>
                    <span
                      className={`text-[10px] font-bold uppercase px-2.5 py-0.5 rounded-full inline-block ${clusterColors[hoveredPoint.cluster % clusterColors.length].bg} ${clusterColors[hoveredPoint.cluster % clusterColors.length].text}`}
                    >
                      {
                        clusterColors[
                          hoveredPoint.cluster % clusterColors.length
                        ].label
                      }
                    </span>
                    <p className="text-xs text-gray-800 dark:text-gray-200 leading-relaxed italic border-l border-gray-300 dark:border-gray-700 pl-3">
                      "{hoveredPoint.document}"
                    </p>
                    <div className="flex justify-between text-[10px] font-bold text-gray-400 pt-2">
                      <span>
                        Coordinates: ({hoveredPoint.x}, {hoveredPoint.y})
                      </span>
                      <span>
                        Membership probability:{" "}
                        {Math.round(hoveredPoint.probability * 100)}%
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="h-full flex items-center justify-center text-center py-12 text-gray-400">
                    <p className="text-xs font-semibold">
                      Hover over a cluster point coordinate to inspect document
                      details.
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Right side plot rendering */}
            <div className="md:col-span-2">
              {clusterLoading ? (
                <div className="w-full border border-gray-200 dark:border-gray-800 rounded-3xl bg-white dark:bg-gray-900 h-96 flex flex-col items-center justify-center gap-3 animate-pulse shadow-sm">
                  <RefreshCw className="h-8 w-8 animate-spin text-indigo-500" />
                  <p className="text-sm font-semibold text-gray-400">
                    Calculating t-SNE projections...
                  </p>
                </div>
              ) : (
                renderTSNEScatter()
              )}
            </div>
          </div>
        )}

        {/* ================= TAB 3: TELEMETRY ANALYTICS ================= */}
        {activeTab === "analytics" && (
          <div className="space-y-8 animate-fadeIn">
            {/* Loading placeholder */}
            {analyticsLoading && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-pulse">
                <div className="h-28 bg-gray-200 dark:bg-gray-800 rounded-2xl"></div>
                <div className="h-28 bg-gray-200 dark:bg-gray-800 rounded-2xl"></div>
                <div className="h-28 bg-gray-200 dark:bg-gray-800 rounded-2xl"></div>
              </div>
            )}

            {!analyticsLoading && analyticsData && (
              <>
                {/* Metric Summary Widgets */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm flex items-center gap-5">
                    <div className="h-12 w-12 bg-indigo-50 dark:bg-indigo-950/30 text-indigo-600 dark:text-indigo-400 rounded-xl flex items-center justify-center">
                      <Search className="h-6 w-6" />
                    </div>
                    <div>
                      <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">
                        Total Queries
                      </p>
                      <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">
                        {analyticsData.total_queries}
                      </p>
                    </div>
                  </div>

                  <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm flex items-center gap-5">
                    <div className="h-12 w-12 bg-purple-50 dark:bg-purple-950/30 text-purple-600 dark:text-purple-400 rounded-xl flex items-center justify-center">
                      <Database className="h-6 w-6" />
                    </div>
                    <div>
                      <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">
                        Cache Hit Rate
                      </p>
                      <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">
                        {Math.round(analyticsData.cache_hit_rate * 100)}%
                      </p>
                    </div>
                  </div>

                  <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-sm flex items-center gap-5">
                    <div className="h-12 w-12 bg-emerald-50 dark:bg-emerald-950/30 text-emerald-600 dark:text-emerald-400 rounded-xl flex items-center justify-center">
                      <Clock className="h-6 w-6" />
                    </div>
                    <div>
                      <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">
                        Average Latency
                      </p>
                      <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">
                        {analyticsData.average_latency_ms} ms
                      </p>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  {/* Top Searches */}
                  <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-6 shadow-md">
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                      <TrendingUp className="h-4 w-4 text-indigo-500" /> Top
                      Queries
                    </h3>
                    {analyticsData.top_queries.length > 0 ? (
                      <div className="space-y-3">
                        {analyticsData.top_queries.map((item, idx) => (
                          <div
                            key={idx}
                            className="flex justify-between items-center bg-gray-50 dark:bg-gray-950 px-4 py-3 rounded-xl"
                          >
                            <span className="text-xs font-bold text-gray-850 dark:text-gray-300">
                              {item.query}
                            </span>
                            <span className="text-xs font-semibold bg-indigo-50 dark:bg-indigo-950/30 text-indigo-600 px-3 py-1 rounded-md">
                              {item.count} searches
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs font-semibold text-gray-400 text-center py-12">
                        No search metrics logged yet.
                      </p>
                    )}
                  </div>

                  {/* Cluster distributions */}
                  <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-6 shadow-md">
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                      <Map className="h-4 w-4 text-indigo-500" /> Cluster
                      Distribution
                    </h3>
                    <div className="space-y-4">
                      {clusterColors.map((color, idx) => {
                        const count =
                          analyticsData.cluster_distribution[idx] || 0;
                        const total = Object.values(
                          analyticsData.cluster_distribution,
                        ).reduce((a, b) => a + b, 0);
                        const pct = total > 0 ? (count / total) * 100 : 0;
                        return (
                          <div key={idx} className="space-y-1">
                            <div className="flex justify-between text-xs font-bold">
                              <span className="text-gray-700 dark:text-gray-300">
                                {color.label}
                              </span>
                              <span className="text-gray-400">
                                {count} hits
                              </span>
                            </div>
                            <div className="h-3 w-full bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                              <div
                                className="h-full rounded-full transition-all duration-300"
                                style={{
                                  backgroundColor: color.fill,
                                  width: `${pct}%`,
                                }}
                              ></div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>

                {/* Latency graph */}
                {analyticsData.recent_latencies.length > 0 && (
                  <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-6 shadow-md">
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                      <Cpu className="h-4 w-4 text-indigo-500" /> Recent Latency
                      Distribution
                    </h3>
                    <div className="h-28 w-full flex items-end gap-1.5 pt-4">
                      {analyticsData.recent_latencies.map((lat, idx) => {
                        const maxLat = Math.max(
                          ...analyticsData.recent_latencies,
                          0.1,
                        );
                        const heightPct = (lat / maxLat) * 100;
                        return (
                          <div
                            key={idx}
                            title={`${roundVal(lat * 1000, 1)}ms`}
                            className="flex-1 bg-indigo-500/20 hover:bg-indigo-500 dark:bg-indigo-950/40 dark:hover:bg-indigo-400 rounded-sm transition-all cursor-help"
                            style={{ height: `${Math.max(8, heightPct)}%` }}
                          ></div>
                        );
                      })}
                    </div>
                    <div className="flex justify-between text-[10px] font-bold text-gray-400 pt-2 border-t border-gray-100 dark:border-gray-800 mt-2">
                      <span>Older queries</span>
                      <span>
                        Latest Query:{" "}
                        {roundVal(
                          analyticsData.recent_latencies[
                            analyticsData.recent_latencies.length - 1
                          ] * 1000,
                          1,
                        )}
                        ms
                      </span>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* ================= TAB 4: RETRIEVAL EVALUATION ================= */}
        {activeTab === "evaluation" && (
          <div className="space-y-8 animate-fadeIn">
            {/* Header / Parameter Config Panel */}
            <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-6 shadow-md flex flex-col sm:flex-row items-center justify-between gap-6">
              <div className="space-y-1">
                <h3 className="text-xl font-bold flex items-center gap-2">
                  <Sliders className="h-5 w-5 text-indigo-500" /> Retrieval
                  Evaluation Framework
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
                  Benchmarks retrieval metrics (NDCG, Precision, Recall, MRR)
                  over a ground truth evaluation set.
                </p>
              </div>

              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1.5 text-xs font-semibold">
                  <span>K parameter:</span>
                  <select
                    value={evalK}
                    onChange={(e) => setEvalK(Number(e.target.value))}
                    className="bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 px-3 py-1.5 rounded-lg focus:outline-none"
                  >
                    <option value={3}>K = 3</option>
                    <option value={5}>K = 5</option>
                    <option value={10}>K = 10</option>
                  </select>
                </div>

                <button
                  disabled={evaluationLoading}
                  onClick={() => runEvaluation(evalK)}
                  className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white px-5 py-2.5 rounded-xl font-bold shadow-sm transition-colors text-sm flex items-center gap-1.5"
                >
                  {evaluationLoading ? (
                    <RefreshCw className="h-4 w-4 animate-spin" />
                  ) : (
                    <Play className="h-4 w-4" />
                  )}
                  Run Benchmark
                </button>
              </div>
            </div>

            {/* Benchmark overall dashboard */}
            {evaluationLoading ? (
              <div className="w-full border border-gray-200 dark:border-gray-800 rounded-3xl bg-white dark:bg-gray-900 h-80 flex flex-col items-center justify-center gap-3 animate-pulse shadow-sm">
                <RefreshCw className="h-8 w-8 animate-spin text-indigo-500" />
                <p className="text-sm font-semibold text-gray-400">
                  Running evaluation test suite...
                </p>
              </div>
            ) : (
              evaluationReport && (
                <>
                  {/* Scores dashboard */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                    <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 text-center">
                      <p className="text-2xl font-black text-indigo-600 dark:text-indigo-400">
                        {Math.round(evaluationReport.ndcg_at_k * 100)}%
                      </p>
                      <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mt-1">
                        NDCG@{evaluationReport.k}
                      </p>
                    </div>

                    <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 text-center">
                      <p className="text-2xl font-black text-purple-600 dark:text-purple-400">
                        {Math.round(evaluationReport.precision_at_k * 100)}%
                      </p>
                      <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mt-1">
                        Precision@{evaluationReport.k}
                      </p>
                    </div>

                    <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 text-center">
                      <p className="text-2xl font-black text-emerald-600 dark:text-emerald-400">
                        {Math.round(evaluationReport.recall_at_k * 100)}%
                      </p>
                      <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mt-1">
                        Recall@{evaluationReport.k}
                      </p>
                    </div>

                    <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 text-center">
                      <p className="text-2xl font-black text-amber-600 dark:text-amber-400">
                        {Math.round(evaluationReport.mrr * 100)}%
                      </p>
                      <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mt-1">
                        Mean Reciprocal Rank
                      </p>
                    </div>
                  </div>

                  {/* Query results table */}
                  <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl p-6 shadow-md overflow-x-auto">
                    <h3 className="text-lg font-bold mb-4">
                      Detailed Query Report
                    </h3>
                    <table className="w-full text-left text-xs divide-y divide-gray-100 dark:divide-gray-800 font-medium">
                      <thead>
                        <tr className="text-gray-400 uppercase font-bold">
                          <th className="pb-3">Query</th>
                          <th className="pb-3 text-center">Relevance Set</th>
                          <th className="pb-3 text-center">Precision</th>
                          <th className="pb-3 text-center">Recall</th>
                          <th className="pb-3 text-center">MRR</th>
                          <th className="pb-3 text-center">NDCG</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                        {evaluationReport.query_reports.map((report, idx) => (
                          <tr key={idx}>
                            <td className="py-3.5 pr-4 text-gray-800 dark:text-gray-200 font-semibold">
                              {report.query}
                            </td>
                            <td className="py-3.5 text-center text-gray-400">
                              {report.relevant_count} docs
                            </td>
                            <td className="py-3.5 text-center text-indigo-600 font-bold">
                              {Math.round(report.precision_at_k * 100)}%
                            </td>
                            <td className="py-3.5 text-center text-emerald-600 font-bold">
                              {Math.round(report.recall_at_k * 100)}%
                            </td>
                            <td className="py-3.5 text-center text-amber-600 font-bold">
                              {Math.round(report.mrr * 100)}%
                            </td>
                            <td className="py-3.5 text-center text-purple-600 font-bold">
                              {Math.round(report.ndcg_at_k * 100)}%
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )
            )}
          </div>
        )}
      </div>
    </main>
  );
}

// Float formatting helper
function roundVal(num, decimals = 2) {
  if (num === undefined || num === null) return 0;
  return Number(num).toFixed(decimals);
}
