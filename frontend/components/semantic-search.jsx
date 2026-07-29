"use client";

import { useState } from "react";
import { Search, AlertCircle, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";

export function SemanticSearch() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();

    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const response = await fetch(`${apiUrl}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: query.trim() }),
      });

      if (!response.ok) {
        throw new Error("API error");
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      setError("Unable to connect to the VectorMind search API.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !loading) {
      handleSearch(e);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-muted/20">
      {/* Header Section */}
      <div className="px-4 py-12 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <div className="mb-4 flex items-center justify-center gap-3">
            <Zap className="h-8 w-8 text-primary" />
            <h1 className="text-5xl font-bold tracking-tight text-foreground">
              VectorMind
            </h1>
          </div>
          <p className="text-xl text-muted-foreground">
            Search knowledge using vector intelligence
          </p>
        </div>
      </div>

      {/* Search Section */}
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl">
          <form onSubmit={handleSearch} className="mb-12">
            <div className="relative flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Ask VectorMind..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="rounded-full pl-12 py-6 text-base shadow-lg border-border/50 backdrop-blur-sm bg-card/80"
                  disabled={loading}
                  autoFocus
                />
              </div>
              <Button
                type="submit"
                disabled={loading}
                className="rounded-full px-8 py-6"
                size="lg"
              >
                {loading ? (
                  <>
                    <Spinner className="mr-2 h-4 w-4" />
                    Searching...
                  </>
                ) : (
                  <>
                    <Search className="mr-2 h-4 w-4" />
                    Search
                  </>
                )}
              </Button>
            </div>
          </form>

          {/* Error Alert */}
          {error && (
            <div className="mb-8 flex items-start gap-3 rounded-xl border border-red-200/50 bg-red-50/80 p-4 dark:border-red-900/30 dark:bg-red-950/20 backdrop-blur-sm">
              <AlertCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-red-600 dark:text-red-400" />
              <p className="text-sm text-red-900 dark:text-red-200">{error}</p>
            </div>
          )}
        </div>
      </div>

      {/* Results Section */}
      {data && (
        <div className="px-4 py-12 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-3xl space-y-8">
            {/* AI Insights Panel */}
            <div className="rounded-2xl border border-border/50 bg-card/80 backdrop-blur-sm p-6 shadow-lg">
              <h2 className="mb-6 text-lg font-semibold text-foreground">
                AI Insights
              </h2>
              <div className="grid gap-6 sm:grid-cols-3">
                {/* Cache Status */}
                <div className="rounded-xl border border-border/50 bg-muted/30 p-4">
                  <p className="text-sm font-medium text-muted-foreground">
                    Cache Status
                  </p>
                  <p className="mt-2 text-2xl font-bold text-foreground">
                    {data.cache_hit ? "HIT" : "MISS"}
                  </p>
                </div>

                {/* Similarity Score */}
                <div className="rounded-xl border border-border/50 bg-muted/30 p-4">
                  <p className="text-sm font-medium text-muted-foreground">
                    Similarity Score
                  </p>
                  <p className="mt-2 text-2xl font-bold text-foreground">
                    {(data.similarity_score * 100).toFixed(1)}%
                  </p>
                </div>

                {/* Dominant Cluster */}
                <div className="rounded-xl border border-border/50 bg-muted/30 p-4">
                  <p className="text-sm font-medium text-muted-foreground">
                    Dominant Cluster
                  </p>
                  <p className="mt-2 text-2xl font-bold text-foreground">
                    {data.dominant_cluster}
                  </p>
                </div>
              </div>
            </div>

            {/* Results Cards */}
            {data.result && data.result.length > 0 && (
              <div className="space-y-4">
                <h2 className="text-lg font-semibold text-foreground">
                  Results ({data.result.length})
                </h2>
                <div className="space-y-3">
                  {data.result.map((item, index) => (
                    <div
                      key={index}
                      className="group rounded-xl border border-border/50 bg-card/80 p-5 shadow-sm transition-all hover:border-primary/50 hover:shadow-md dark:hover:border-primary/30 backdrop-blur-sm"
                    >
                      <div className="flex gap-4">
                        {/* Result Number */}
                        <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-muted font-semibold text-sm text-muted-foreground group-hover:bg-primary/10 transition-colors">
                          {index + 1}
                        </div>

                        {/* Result Content */}
                        <div className="flex-1 min-w-0">
                          {(item.title || item.id) && (
                            <h3 className="font-semibold text-foreground truncate">
                              {item.title || item.id}
                            </h3>
                          )}

                          {item.content && (
                            <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
                              {item.content}
                            </p>
                          )}

                          {/* Additional Fields */}
                          {Object.entries(item).filter(
                            ([key]) =>
                              ![
                                "title",
                                "content",
                                "score",
                                "id",
                                "cluster",
                              ].includes(key),
                          ).length > 0 && (
                            <div className="mt-3 flex flex-wrap gap-3">
                              {Object.entries(item).map(([key, value]) => {
                                if (
                                  [
                                    "title",
                                    "content",
                                    "score",
                                    "id",
                                    "cluster",
                                  ].includes(key)
                                )
                                  return null;
                                return (
                                  <div key={key} className="text-xs">
                                    <span className="font-medium text-muted-foreground">
                                      {key}:
                                    </span>
                                    <span className="ml-1 text-foreground">
                                      {String(value)}
                                    </span>
                                  </div>
                                );
                              })}
                            </div>
                          )}
                        </div>

                        {/* Metrics */}
                        <div className="ml-4 flex flex-shrink-0 flex-col items-end justify-center gap-2">
                          {item.score !== undefined && (
                            <div className="rounded-lg bg-muted/50 px-3 py-1">
                              <span className="text-sm font-semibold text-foreground">
                                {(item.score * 100).toFixed(0)}%
                              </span>
                            </div>
                          )}
                          {item.cluster !== undefined && (
                            <div className="text-xs text-muted-foreground">
                              Cluster {item.cluster}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* No Results */}
            {(!data.result || data.result.length === 0) && (
              <div className="rounded-xl border border-dashed border-border/50 bg-muted/30 p-12 text-center">
                <AlertCircle className="mx-auto mb-3 h-8 w-8 text-muted-foreground" />
                <p className="text-muted-foreground">
                  No results found for "{data.query}"
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Initial State */}
      {!data && !error && !loading && (
        <div className="flex items-center justify-center min-h-[50vh] px-4">
          <div className="mx-auto max-w-2xl text-center">
            <div className="mb-6 inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-muted/50">
              <Search className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="text-xl font-semibold text-foreground">
              Ready to explore
            </h3>
            <p className="mt-2 text-muted-foreground">
              Ask VectorMind anything to search through your knowledge base
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
