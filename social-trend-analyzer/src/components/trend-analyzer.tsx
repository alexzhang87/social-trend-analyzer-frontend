import { useState, useRef, useEffect } from "react";
import { Header } from "./header";
import { HeroSection } from "./hero-section";
import { AnalysisResults } from "./analysis-results";
import { TrendModal } from "./trend-modal";
import { HowItWorks } from "./how-it-works";
import { FeaturedAnalysis } from "./featured-analysis";

export interface FilterState {
  timeRange: string;
  category: string;
  searchTrend: string;
  keyword: string;
  platform: string;
}

export interface TrendCluster {
  cluster_id: string;
  title: string;
  category: string;
  hot_score: number;
  platforms: string[];
  keywords: string[];
  date: string;
  trend_history: Array<{ date: string; score: number }>;
  pain_points: Array<{
    text: string;
    evidence: Array<{
      text: string;
      author: string;
      platform: string;
      url: string;
    }>;
    intent: string;
    severity: number;
    confidence: number;
  }>;
  opportunities: Array<{
    text: string;
    impact: number;
    effort: number;
  }>;
  mvp_1week: {
    goal: string;
    days: string[];
    resources: string;
    budget_usd: number;
    kpi: string;
  };
  emotion_analysis?: {
    joy: number;
    sadness: number;
    anger: number;
    sarcasm: number;
    neutral: number;
  };
}

// Data Mapper: Translates the rich analysis object from the LLM-powered backend
// into the `TrendCluster` format required by the frontend components.
const mapApiDataToTrendClusters = (apiResults: any[]): TrendCluster[] => {
  if (!apiResults || !Array.isArray(apiResults) || apiResults.length === 0) {
    return []; // Return empty array if data is invalid or empty
  }

  // The API now returns an array with a single, rich analysis object.
  const result = apiResults[0];

  const cluster: TrendCluster = {
    cluster_id: `llm-${new Date().getTime()}`,
    title: result.title || "Untitled Trend",
    category: result.category || "Uncategorized",
    hot_score: result.hot_score || 0,
    // Extract platforms from the top mentions provided by the backend
    platforms: [...new Set(result.top_mentions?.map((m: any) => m.platform).filter(Boolean) || [])] as string[],
    // Extract keywords from pain points and opportunities
    keywords: [
      ...(result.insights?.pain_points?.map((p: any) => p.text.split(' ')[0]) || []),
      ...(result.insights?.opportunities?.map((o: any) => o.text.split(' ')[0]) || [])
    ].slice(0, 5), // Limit to 5 keywords
    date: new Date().toISOString().split('T')[0], // Use today's date
    // Generate a plausible trend history based on the hot score
    trend_history: Array.from({ length: 7 }, (_, i) => ({
      date: new Date(Date.now() - (6 - i) * 86400000).toISOString().split('T')[0],
      score: Math.max(0, Math.round((result.hot_score || 50) * (1 + (i - 5) * 0.1 + (Math.random() - 0.5) * 0.1)))
    })),
    // Map pain points, providing evidence from top mentions
    pain_points: result.insights?.pain_points?.map((p: any) => ({
      text: p.text,
      // Use top_mentions as evidence for the first pain point
      evidence: result.top_mentions?.map((mention: any) => ({
        text: mention.text,
        author: mention.author,
        platform: mention.platform,
        url: mention.url,
      })) || [],
      intent: "User Complaint", // Placeholder
      severity: 75, // Placeholder
      confidence: 0.9, // Placeholder
    })) || [],
    // Map opportunities with placeholder impact/effort
    opportunities: result.insights?.opportunities?.map((o: any) => ({
      text: o.text,
      impact: Math.floor(Math.random() * 3) + 7, // Placeholder 7-9
      effort: Math.floor(Math.random() * 3) + 4, // Placeholder 4-6
    })) || [],
    // Map the MVP plan from the insights
    mvp_1week: {
      goal: result.insights?.mvp_plan?.goal || "Define MVP goal.",
      days: ["Day 1-3: Ideation & Design", "Day 4-7: Develop & Test"], // Placeholder
      resources: "1 PM, 1 Designer, 1 Dev", // Placeholder
      budget_usd: 1500, // Placeholder
      kpi: "Validate problem-solution fit.", // Placeholder
    },
    emotion_analysis: result.emotion_analysis || { joy: 20, sadness: 20, anger: 20, sarcasm: 20, neutral: 20 },
  };

  return [cluster]; // Return an array containing the single, detailed cluster
};

export function TrendAnalyzer() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analyzedData, setAnalyzedData] = useState<TrendCluster[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [selectedCluster, setSelectedCluster] = useState<TrendCluster | null>(null);
  const resultsRef = useRef<HTMLDivElement>(null);
  const [filters, setFilters] = useState<FilterState>({
    timeRange: "1 Week",
    category: "All Categories",
    searchTrend: "All",
    keyword: "",
    platform: "Both",
  });

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    setAnalyzedData([]);
    setError(null);

    // Use the keyword from filters, or a default value if empty.
    const query = filters.keyword.trim() || "AI in marketing";
    
    try {
      // Use environment variable for API base URL, fallback to localhost for development
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
      const response = await fetch(`${apiBaseUrl}/api/analyze-trends/?query=${encodeURIComponent(query)}`, {
        method: 'GET',
      });

      if (!response.ok) {
        // Attempt to read error details from the backend response
        const errorData = await response.json().catch(() => null); // Gracefully handle non-JSON responses
        const detail = errorData?.detail || `HTTP error! status: ${response.status}`;
        throw new Error(detail);
      }

      const data = await response.json();
      // The new endpoint returns the array directly, not nested under `results`.
      const mappedData = mapApiDataToTrendClusters(data);
      setAnalyzedData(mappedData);
    } catch (error: any) {
      console.error("Failed to fetch and map analysis data:", error);
      setError(error.message || "An unknown error occurred.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const filteredData = analyzedData.filter(cluster => {
    if (filters.timeRange !== 'All Time') {
      const today = new Date();
      const clusterDate = new Date(cluster.date);
      let daysToCompare = 0;
      switch (filters.timeRange) {
        case '1 Week': daysToCompare = 7; break;
        case '1 Month': daysToCompare = 30; break;
        case '3 Months': daysToCompare = 90; break;
        case '6 Months': daysToCompare = 180; break;
      }
      if (daysToCompare > 0) {
        const diffTime = Math.abs(today.getTime() - clusterDate.getTime());
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        if (diffDays > daysToCompare) return false;
      }
    }
    if (filters.platform !== 'Both') {
      const platformMatch = filters.platform === 'X' ? cluster.platforms.includes('x') : cluster.platforms.includes('reddit');
      if (!platformMatch) return false;
    }
    if (filters.category !== 'All Categories' && cluster.category !== filters.category) {
      return false;
    }
    if (filters.keyword.trim()) {
      const keyword = filters.keyword.trim().toLowerCase();
      const titleMatch = cluster.title.toLowerCase().includes(keyword);
      const keywordMatch = cluster.keywords.some(k => k.toLowerCase().includes(keyword));
      if (!titleMatch && !keywordMatch) return false;
    }
    return true;
  });

  const showResultsArea = !isAnalyzing && analyzedData.length > 0;

  useEffect(() => {
    if (showResultsArea && resultsRef.current) {
      resultsRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [showResultsArea]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <HeroSection 
          filters={filters}
          setFilters={setFilters}
          onAnalyze={handleAnalyze}
          isAnalyzing={isAnalyzing}
        />

        {isAnalyzing && (
          <div className="text-center p-12">
            <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="mt-4 text-lg font-semibold">Analyzing trends...</p>
            <p className="text-sm text-gray-500">Please wait while we gather and process the data.</p>
          </div>
        )}

        {error && (
          <div className="mt-8 text-center p-12 bg-red-50 border border-red-200 rounded-lg shadow-sm">
            <h3 className="text-xl font-semibold text-red-800">Analysis Failed</h3>
            <p className="mt-2 text-red-600">Could not retrieve or process trend data.</p>
            <pre className="mt-4 text-left bg-red-100 text-red-900 p-4 rounded text-xs overflow-x-auto">
              <code>Error: {error}</code>
            </pre>
          </div>
        )}

        {showResultsArea && !error && (
          <div className="mt-8" ref={resultsRef}>
            {filteredData.length > 0 ? (
              <AnalysisResults
                data={filteredData}
                onClusterClick={setSelectedCluster}
              />
            ) : (
              <div className="text-center p-12 bg-white rounded-lg shadow-sm">
                <h3 className="text-xl font-semibold">No Results Found</h3>
                <p className="mt-2 text-gray-600">Try adjusting your filters to find what you're looking for.</p>
              </div>
            )}
          </div>
        )}
      </main>

      {selectedCluster && (
        <TrendModal
          cluster={selectedCluster}
          onClose={() => setSelectedCluster(null)}
        />
      )}

      <HowItWorks />
      <FeaturedAnalysis />
    </div>
  );
}
