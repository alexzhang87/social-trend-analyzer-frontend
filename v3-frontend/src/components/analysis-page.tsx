import { useState, useRef, useEffect } from "react";
import { Header } from "./header";
import { HeroSection } from "./hero-section";
import { AnalysisResults } from "./analysis-results";
import PerformanceMonitor from "./performance-monitor";
import type { TrendAnalysis } from "../declarations";
import { useAuth } from "@/components/auth-provider";
import { useToast } from "@/components/ui/use-toast";
import { useNavigate, useSearchParams } from "react-router-dom";

// Define the shape of the filters
export interface FilterState {
  platform: string;
  timeRange: string;
  category: string;
}

export function AnalysisPage() {
  const { user } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  // Get keywords from URL params if available
  const initialKeywords = searchParams.get('keywords') || '';
  
  const [keywords, setKeywords] = useState(initialKeywords);
  const [filters, setFilters] = useState<FilterState>({
    platform: 'twitter',
    timeRange: '7d',
    category: 'all'
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<TrendAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Check authentication on component mount
  useEffect(() => {
    if (!user) {
      toast({
        title: "Login Required",
        description: "Please login to use analysis features",
        variant: "destructive",
      });
      navigate('/pricing');
    }
  }, [user, navigate, toast]);

  const handleAnalyze = async () => {
    if (!keywords.trim()) {
      toast({
        title: "Please Enter Keywords",
        description: "Keywords are required to start analysis",
        variant: "destructive",
      });
      return;
    }

    if (!user) {
      navigate('/pricing');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setAnalysisResults(null);

    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      
      const response = await fetch(`${apiBaseUrl}/api/v1/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`,
        },
        body: JSON.stringify({
          keywords: keywords.split(',').map(k => k.trim()),
          filters: filters
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setAnalysisResults(data);
      
      toast({
        title: "Analysis Complete",
        description: "Trend analysis has been completed successfully",
      });

    } catch (error) {
      console.error('Analysis error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred during analysis';
      setError(errorMessage);
      
      toast({
        title: "Analysis Failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Auto-analyze if keywords are provided in URL
  useEffect(() => {
    if (initialKeywords && user && !analysisResults && !isAnalyzing) {
      handleAnalyze();
    }
  }, [initialKeywords, user]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="space-y-8">
          {/* Analysis Input Section */}
          <HeroSection 
            keywords={keywords}
            setKeywords={setKeywords}
            onAnalyze={handleAnalyze}
            isAnalyzing={isAnalyzing}
            filters={filters}
            setFilters={setFilters}
          />

          {/* Performance Monitor */}
          <PerformanceMonitor />

          {/* Error Display */}
          {error && (
            <div className="max-w-4xl mx-auto">
              <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-6">
                <h3 className="text-red-400 font-semibold mb-2">Analysis Error</h3>
                <p className="text-red-300">{error}</p>
                <button
                  onClick={handleAnalyze}
                  className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
                >
                  Retry Analysis
                </button>
              </div>
            </div>
          )}

          {/* Analysis Results */}
          {analysisResults && (
            <AnalysisResults 
              results={analysisResults}
              keywords={keywords}
            />
          )}

          {/* Loading State */}
          {isAnalyzing && (
            <div className="max-w-4xl mx-auto text-center py-12">
              <div className="inline-flex items-center gap-3 glass-card rounded-xl p-6 border border-white/10">
                <div className="w-6 h-6 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-white font-medium">Analyzing trend data...</span>
              </div>
            </div>
          )}

          {/* Empty State */}
          {!analysisResults && !isAnalyzing && !error && (
            <div className="max-w-4xl mx-auto text-center py-12">
              <div className="glass-card rounded-xl p-8 border border-white/10">
                <h3 className="text-2xl font-semibold text-white mb-4">Start Your Trend Analysis</h3>
                <p className="text-gray-300 mb-6">
                  Enter keywords and click the analyze button to get detailed market trend insights
                </p>
                <div className="flex justify-center gap-4">
                  <button
                    onClick={() => navigate('/workspace')}
                    className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold rounded-lg hover:from-cyan-600 hover:to-blue-700 transition-all duration-300"
                  >
                    Go to Dashboard
                  </button>
                  <button
                    onClick={() => navigate('/')}
                    className="px-6 py-3 border border-white/20 text-white font-semibold rounded-lg hover:bg-white/10 transition-all duration-300"
                  >
                    Back to Home
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}