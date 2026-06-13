"use client"

import { useState, useEffect } from "react"

export default function Home() {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<any[]>([])
  const [topResult, setTopResult] = useState<string | null>(null)
  const [matchedQuery, setMatchedQuery] = useState<string | null>(null)
  const [similarity, setSimilarity] = useState(0)
  const [cluster, setCluster] = useState(2)
  const [cacheStatus, setCacheStatus] = useState("MISS")
  const [processingTime, setProcessingTime] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [hasSearched, setHasSearched] = useState(false)
  const [showResults, setShowResults] = useState(false)

  const suggestionList = [
    "space missions",
    "apollo moon landing",
    "nasa astronauts",
    "space shuttle",
    "mars rover mission",
    "space exploration"
  ]

  const exampleQueries = [
    "space exploration missions",
    "artificial intelligence ethics",
    "climate change debate",
    "satellite technology"
  ]

  const trendingTopics = [
    { emoji: "🚀", label: "Space Exploration", query: "space exploration missions" },
    { emoji: "🤖", label: "Artificial Intelligence", query: "artificial intelligence" },
    { emoji: "🌍", label: "Climate Change", query: "climate change" },
    { emoji: "📡", label: "Satellite Technology", query: "satellite technology" },
    { emoji: "🧠", label: "Neuroscience", query: "neuroscience research" }
  ]

  useEffect(() => {
    if (query.length === 0) {
      setSuggestions([])
      return
    }

    const filtered = suggestionList.filter(s =>
      s.toLowerCase().includes(query.toLowerCase())
    )

    setSuggestions(filtered.slice(0, 5))
  }, [query])

  const highlightText = (text: string, query: string) => {
    if (!query) return text

    const words = query.split(" ")
    let result = text

    words.forEach(word => {
      const regex = new RegExp(`(${word})`, "gi")
      result = result.replace(regex, "<mark>$1</mark>")
    })

    return result
  }

  const generateAISummary = () => {
    if (results.length === 0) return ""
    
    const topResults = results.slice(0, 3)
    const sentences = topResults.map(r => {
      const text = r.document.replace(/<[^>]*>/g, '')
      const firstSentence = text.split('.')[0]
      return firstSentence
    })
    
    return sentences.join('. ') + '.'
  }

  const handleSearch = async (searchQuery?: string) => {
    const queryToSearch = searchQuery || query
    if (!queryToSearch) return

    if (searchQuery) {
      setQuery(searchQuery)
    }

    setLoading(true)
    setError(null)
    setHasSearched(true)
    setShowResults(false)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"
      const response = await fetch(`${apiUrl}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          query: queryToSearch
        })
      })

      const data = await response.json()

      const resultsData = data.results || []

      setResults(resultsData)
      setTopResult(data.result || null)
      setMatchedQuery(data.matched_query || null)

      if (data.similarity_score) {
        setSimilarity(Math.round(data.similarity_score * 100))
      } else if (resultsData.length > 0) {
        setSimilarity(Math.round(resultsData[0].similarity_score * 100))
      } else {
        setSimilarity(0)
      }

      setCluster(data.dominant_cluster || 2)
      setCacheStatus(data.cache_hit ? "HIT" : "MISS")
      setProcessingTime(data.processing_time || 0)
      
      // Trigger fade-in animation
      setTimeout(() => setShowResults(true), 100)
    } catch (err) {
      console.error(err)
      setError("Unable to connect to the VectorMind search API.")
    }

    setLoading(false)
  }

  return (
    <main className="min-h-screen bg-[#F9FAFB]">
      <div className="max-w-6xl mx-auto px-6 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="flex items-center justify-center gap-3 mb-4">
            <span className="text-6xl text-[#F97316]">⚡</span>
            <h1 className="text-6xl font-bold bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] bg-clip-text text-transparent">
              VectorMind
            </h1>
          </div>
          <p className="text-[#6B7280] text-xl">
            Search knowledge using vector intelligence
          </p>
        </div>

        {/* Search Bar */}
        <div className="mb-12">
          <div className="flex gap-4 relative">
            <div className="flex-1 relative">
              <input
                className="w-full bg-white border-2 border-gray-200 rounded-full px-6 py-4 text-lg focus:outline-none focus:ring-2 focus:ring-[#6366F1] focus:border-[#6366F1] transition-all duration-200 ease-in-out shadow-lg"
                placeholder="Ask VectorMind anything..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />

              {suggestions.length > 0 && (
                <div className="absolute bg-white border-2 border-gray-200 rounded-xl shadow-xl mt-2 w-full z-10">
                  {suggestions.map((s, index) => (
                    <div
                      key={index}
                      className="p-4 hover:bg-[#6366F1]/5 cursor-pointer first:rounded-t-xl last:rounded-b-xl transition-all duration-200 ease-in-out"
                      onClick={() => {
                        setQuery(s)
                        setSuggestions([])
                      }}
                    >
                      <span className="text-[#111827]">{s}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <button
              className="bg-[#6366F1] hover:bg-[#4F46E5] text-white px-10 py-4 rounded-xl font-semibold shadow-md hover:shadow-lg transition-all duration-200 ease-in-out hover:scale-105 active:scale-95"
              onClick={() => handleSearch()}
            >
              Search
            </button>
          </div>
        </div>

        {/* Try Searching - Empty State */}
        {!hasSearched && (
          <div className="mb-10">
            <h3 className="text-xl font-bold mb-5 text-[#111827]">Try Searching</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {exampleQueries.map((q, index) => (
                <div
                  key={index}
                  className="p-5 bg-white border-2 border-gray-200 rounded-xl hover:border-[#6366F1] hover:bg-[#6366F1]/5 cursor-pointer transition-all duration-200 ease-in-out hover:scale-105 active:scale-95 shadow-sm"
                  onClick={() => handleSearch(q)}
                >
                  <p className="text-[#111827] font-medium">{q}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Trending Topics */}
        {!hasSearched && (
          <div className="mb-16">
            <h3 className="text-xl font-bold mb-5 text-[#111827]">Trending Topics</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {trendingTopics.map((topic, index) => (
                <div
                  key={index}
                  className="p-6 bg-white border-2 border-gray-200 rounded-xl hover:border-[#6366F1] hover:bg-[#6366F1]/5 cursor-pointer transition-all duration-200 ease-in-out hover:scale-105 active:scale-95 text-center shadow-sm"
                  onClick={() => handleSearch(topic.query)}
                >
                  <div className="text-4xl mb-3">{topic.emoji}</div>
                  <p className="text-sm font-semibold text-[#111827]">{topic.label}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {error && (
          <div className="mb-8 p-5 bg-red-50 border-2 border-red-200 rounded-xl text-red-600 shadow-sm">
            {error}
          </div>
        )}

        {/* AI Insights */}
        {hasSearched && (
          <div className={`mb-10 transition-opacity duration-300 ${showResults ? 'opacity-100' : 'opacity-0'}`}>
            <h2 className="text-3xl font-bold mb-6 text-[#111827]">AI Insights</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
              <div className="p-6 bg-white rounded-xl shadow-sm hover:shadow-lg transition-all duration-200 ease-in-out text-center border border-gray-100">
                <p className="text-[#6B7280] text-sm font-medium mb-2">Cache Status</p>
                <p className="text-3xl font-bold text-[#111827]">{cacheStatus}</p>
                {cacheStatus === "HIT" && matchedQuery && (
                  <p className="text-xs text-[#6B7280] mt-2">Matched: {matchedQuery.slice(0, 30)}...</p>
                )}
              </div>

              <div className="p-6 bg-white rounded-xl shadow-sm hover:shadow-lg transition-all duration-200 ease-in-out text-center border border-gray-100">
                <p className="text-[#6B7280] text-sm font-medium mb-2">Similarity Score</p>
                <p className="text-3xl font-bold text-[#6366F1]">{similarity}%</p>
              </div>

              <div className="p-6 bg-white rounded-xl shadow-sm hover:shadow-lg transition-all duration-200 ease-in-out text-center border border-gray-100">
                <p className="text-[#6B7280] text-sm font-medium mb-2">Dominant Cluster</p>
                <p className="text-3xl font-bold text-[#8B5CF6]">{cluster}</p>
              </div>

              <div className="p-6 bg-white rounded-xl shadow-sm hover:shadow-lg transition-all duration-200 ease-in-out text-center border border-gray-100">
                <p className="text-[#6B7280] text-sm font-medium mb-2">Search Time</p>
                <p className="text-3xl font-bold text-[#10B981]">{processingTime}s</p>
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="text-center py-16">
            <div className="inline-flex items-center gap-2 mb-6">
              <div className="w-3 h-3 bg-[#6366F1] rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-3 h-3 bg-[#6366F1] rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-3 h-3 bg-[#6366F1] rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
            <p className="text-[#6B7280] text-xl font-medium">Searching knowledge base...</p>
          </div>
        )}

        {/* Top Result */}
        {!loading && topResult && (
          <div className={`mb-10 transition-opacity duration-300 ${showResults ? 'opacity-100' : 'opacity-0'}`}>
            <div className="bg-[#6366F1]/10 border-2 border-[#6366F1]/30 rounded-xl p-6 shadow-md">
              <h3 className="text-2xl font-bold mb-4 text-[#111827]">Top Result</h3>
              <p className="text-[#111827] leading-relaxed text-base mb-3">{topResult.slice(0, 300)}...</p>
              <p className="text-sm text-[#6B7280]">
                Similarity: {similarity}%
              </p>
            </div>
          </div>
        )}

        {/* AI Summary */}
        {!loading && results.length > 0 && (
          <div className={`mb-10 transition-opacity duration-300 ${showResults ? 'opacity-100' : 'opacity-0'}`}>
            <div className="bg-gradient-to-r from-[#6366F1]/10 to-[#8B5CF6]/10 border-2 border-[#6366F1]/30 rounded-xl p-8 shadow-sm">
              <h3 className="text-2xl font-bold mb-4 text-[#111827] flex items-center gap-3">
                <span className="text-3xl">🤖</span> AI Summary
              </h3>
              <p className="text-[#111827] leading-relaxed text-lg">
                {generateAISummary().slice(0, 300)}...
              </p>
            </div>
          </div>
        )}

        {/* Results */}
        {!loading && results.length > 0 && (
          <div className={`transition-opacity duration-300 ${showResults ? 'opacity-100' : 'opacity-0'}`}>
            <h2 className="text-3xl font-bold mb-6 text-[#111827]">Search Results</h2>
            {results.map((result, index) => (
              <div
                key={index}
                className="bg-white border border-gray-200 rounded-xl p-7 mb-5 shadow-sm hover:shadow-lg transition-all duration-200 ease-in-out hover:scale-[1.02]"
              >
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-bold text-[#111827]">Result {index + 1}</h3>
                  <div className="flex gap-5 text-sm">
                    <span className="text-[#6366F1] font-semibold">
                      Similarity: {Math.round(result.similarity_score * 100)}%
                    </span>
                    <span className="text-[#8B5CF6] font-semibold">
                      Cluster: {cluster}
                    </span>
                  </div>
                </div>

                <div className="text-[#6B7280] mb-3 text-sm font-semibold uppercase tracking-wide">Preview:</div>
                <div
                  className="text-[#111827] leading-relaxed text-base"
                  dangerouslySetInnerHTML={{
                    __html: highlightText(result.document.slice(0, 200) + "...", query)
                  }}
                />

                <style jsx>{`
                  mark {
                    background-color: #FEF3C7;
                    color: #92400E;
                    padding: 3px 6px;
                    border-radius: 6px;
                    font-weight: 600;
                  }
                `}</style>
              </div>
            ))}
          </div>
        )}

        {/* No Results */}
        {!loading && hasSearched && results.length === 0 && (
          <div className="text-center py-16">
            <div className="text-7xl mb-6">🔍</div>
            <p className="text-[#111827] text-2xl font-bold mb-2">No results found for "{query}"</p>
            <p className="text-[#6B7280] text-lg">Try a different search query</p>
          </div>
        )}
      </div>
    </main>
  )
}
