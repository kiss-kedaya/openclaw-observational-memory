import { useState } from "react";
import { observationApi } from "../lib/api";
import type { Observation } from "../types";

interface SearchResult {
  observation: Observation;
  similarity: number;
  highlights: string[];
}

export default function Search() {
  const [query, setQuery] = useState("");
  const [minSimilarity, setMinSimilarity] = useState(0.3);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setSearched(true);

    try {
      // For now, we'll do a simple client-side search
      // TODO: Implement vector search API in backend
      const { data: sessions } = await observationApi.list("all");
      
      // Simple text matching (placeholder for vector search)
      const matches: SearchResult[] = [];
      const queryLower = query.toLowerCase();

      // This is a placeholder - real implementation will use Tantivy
      sessions.forEach((obs: Observation) => {
        const contentLower = obs.content.toLowerCase();
        if (contentLower.includes(queryLower)) {
          const similarity = calculateSimilarity(queryLower, contentLower);
          if (similarity >= minSimilarity) {
            matches.push({
              observation: obs,
              similarity,
              highlights: extractHighlights(obs.content, query),
            });
          }
        }
      });

      // Sort by similarity
      matches.sort((a, b) => b.similarity - a.similarity);
      setResults(matches);
    } catch (error) {
      console.error("Search failed:", error);
    } finally {
      setLoading(false);
    }
  };

  const calculateSimilarity = (query: string, content: string): number => {
    // Simple similarity calculation (placeholder)
    const matches = content.split(query).length - 1;
    return Math.min(matches * 0.2 + 0.3, 1.0);
  };

  const extractHighlights = (content: string, query: string): string[] => {
    const highlights: string[] = [];
    const queryLower = query.toLowerCase();
    const contentLower = content.toLowerCase();
    
    let index = contentLower.indexOf(queryLower);
    while (index !== -1 && highlights.length < 3) {
      const start = Math.max(0, index - 30);
      const end = Math.min(content.length, index + query.length + 30);
      highlights.push(content.substring(start, end));
      index = contentLower.indexOf(queryLower, index + 1);
    }
    
    return highlights;
  };

  const highlightText = (text: string, query: string) => {
    const parts = text.split(new RegExp(`(${query})`, "gi"));
    return (
      <span>
        {parts.map((part, i) =>
          part.toLowerCase() === query.toLowerCase() ? (
            <mark key={i} className="bg-yellow-200 dark:bg-yellow-800">
              {part}
            </mark>
          ) : (
            part
          )
        )}
      </span>
    );
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Semantic Search</h1>

      {/* Search Form */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">
            Search Query
          </label>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSearch()}
            placeholder="Enter search query..."
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Minimum Similarity: {minSimilarity.toFixed(2)}
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={minSimilarity}
            onChange={(e) => setMinSimilarity(parseFloat(e.target.value))}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
            <span>0.0 (Less strict)</span>
            <span>1.0 (More strict)</span>
          </div>
        </div>

        <button
          onClick={handleSearch}
          disabled={loading || !query.trim()}
          className="w-full px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      {/* Results */}
      {searched && (
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold mb-4">
            Search Results ({results.length})
          </h2>

          {results.length === 0 ? (
            <div className="text-center text-gray-500 dark:text-gray-400 py-12">
              No results found. Try adjusting your query or similarity threshold.
            </div>
          ) : (
            <div className="space-y-4">
              {results.map((result, index) => (
                <div
                  key={result.observation.id}
                  className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500 transition"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                        #{index + 1}
                      </span>
                      <span
                        className={`px-2 py-1 text-xs rounded ${
                          result.observation.priority === "HIGH"
                            ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                            : result.observation.priority === "MEDIUM"
                            ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
                            : "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                        }`}
                      >
                        {result.observation.priority}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        Similarity:
                      </span>
                      <span className="font-bold text-blue-500">
                        {(result.similarity * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  <p className="text-sm mb-2">
                    {highlightText(result.observation.content, query)}
                  </p>

                  {result.highlights.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                      <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                        Highlights:
                      </div>
                      {result.highlights.map((highlight, i) => (
                        <div
                          key={i}
                          className="text-xs text-gray-600 dark:text-gray-300 mb-1"
                        >
                          ...{highlightText(highlight, query)}...
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                    Session: {result.observation.session_id} •{" "}
                    {new Date(result.observation.created_at).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
