import { useState, useRef, useEffect } from "react";
import { Header } from "./header";
import { HeroSection } from "./hero-section";
import { AnalysisResults } from "./analysis-results";
import { DemoAnalysisShowcase } from "./demo-analysis-showcase";

import PerformanceMonitor from "./performance-monitor";
import type { TrendAnalysis } from "../declarations";
import { HelpCircle, Cpu, FileText, CreditCard, ArrowRight, AlertCircle } from "lucide-react";
import { useAuth } from "@/components/auth-provider";
import { useToast } from "@/components/ui/use-toast";
import { useNavigate } from "react-router-dom";

// Define the shape of the filters
export interface FilterState {
  platform: string;
  timeRange: string;
  category: string;
}

// Simple animation for the cards
const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: i * 0.2,
      duration: 0.5,
    },
  }),
};

// A simple motion component stub to avoid dependency issues
const motion = {
  div: ({ variants, initial, whileInView, viewport, custom, ...props }: any) => {
    // This is a placeholder. In a real app, you'd use Framer Motion.
    // For this fix, we'll just render a div. The animation logic is conceptual here.
    return <div {...props} />;
  }
};


// Removed unused interfaces and constants - simplified for redirect functionality

export function TrendAnalyzer() {
  const { user } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const [keywords, setKeywords] = useState('');
  const [filters, setFilters] = useState<FilterState>({
    platform: 'twitter',
    timeRange: '7d',
    category: 'all'
  });

  const handleAnalyze = async () => {
    if (!keywords.trim()) {
      toast({
        title: "Please enter keywords",
        description: "Keywords are required to start analysis",
        variant: "destructive",
      });
      return;
    }

    // Check if user is authenticated
    if (!user) {
      // New user - redirect to registration with free trial
      navigate('/pricing?trial=true');
      return;
    }

    try {
      // Import the trends API service
      const { trendsApi } = await import('@/services/trendsApi');
      
      // Check user credits first
      const creditsInfo = await trendsApi.checkCredits();
      if (creditsInfo.remaining <= 0) {
        toast({
          title: "Insufficient Credits",
          description: "You don't have enough credits to perform analysis. Please upgrade your plan.",
          variant: "destructive",
        });
        navigate('/pricing');
        return;
      }

      // Prepare analysis request
      const keywordList = keywords.split(',').map(k => k.trim()).filter(k => k.length > 0);
      const analysisRequest = {
        keywords: keywordList,
        platforms: [filters.platform],
        timeframe: filters.timeRange,
        filters: filters
      };

      // Show loading state
      toast({
        title: "Analysis Started",
        description: "Your trend analysis is being processed...",
      });

      // Start comprehensive analysis
      const result = await trendsApi.comprehensiveAnalysis(analysisRequest);
      
      // Navigate to workspace with analysis results
      navigate(`/workspace?section=analysis&analysisId=${result.id}`);
      
    } catch (error: any) {
      console.error('Analysis failed:', error);
      
      // Handle specific error cases
      if (error.response?.status === 401) {
        toast({
          title: "Authentication Required",
          description: "Please log in to perform analysis",
          variant: "destructive",
        });
        navigate('/login');
      } else if (error.response?.status === 402) {
        toast({
          title: "Insufficient Credits",
          description: "You don't have enough credits. Please upgrade your plan.",
          variant: "destructive",
        });
        navigate('/pricing');
      } else if (error.response?.status === 429) {
        toast({
          title: "Rate Limit Exceeded",
          description: "Too many requests. Please try again later.",
          variant: "destructive",
        });
      } else {
        toast({
          title: "Analysis Failed",
          description: error.response?.data?.detail || "An error occurred during analysis. Please try again.",
          variant: "destructive",
        });
      }
    }
  };

  // Add missing handleAnalyzeRequest function, which is the callback function needed by HeroSection component
  const handleAnalyzeRequest = handleAnalyze;

  // Removed analysis functions - now redirects to pricing page

  return (
    <div className="container mx-auto px-4 py-8">
      <Header />
      <main className="container mx-auto px-4 py-8">
        {/* Trend analysis content */}
        <div className="space-y-8">
            <HeroSection 
              keywords={keywords}
              setKeywords={setKeywords}
              onAnalyze={handleAnalyzeRequest}
              isAnalyzing={false}
              filters={filters}
              setFilters={setFilters}
            />

            {/* Display demo analysis results - show product value to users */}
            <DemoAnalysisShowcase />

        {/* AI-Powered PMF Intelligence Section */}
        <div className="max-w-6xl mx-auto my-20 px-4">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-6xl font-black mb-6 tracking-tight leading-tight md:leading-tight">
              <span className="bg-gradient-to-r from-cyan-300 to-purple-300 bg-clip-text text-transparent font-extrabold">
                AI-Powered PMF
              </span>
              <br />
              <span className="bg-gradient-to-r from-purple-300 to-green-300 bg-clip-text text-transparent font-extrabold">
                Intelligence
              </span>
            </h2>
            <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed mt-6 mb-12 font-medium">
                🚀 AI-powered market research for smart business decisions. Validate ideas with real-time PMF analysis and competitor intelligence.
              </p>
          </div>
          
          <div className="glass-card rounded-3xl p-8 md:p-12 border border-white/10 backdrop-blur-sm relative overflow-hidden">
            {/* Background decoration */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-cyan-400/20 to-purple-400/20 rounded-full blur-3xl"></div>
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-gradient-to-tr from-green-400/20 to-blue-400/20 rounded-full blur-3xl"></div>
            
            <div className="relative z-10">

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
                <motion.div
                   className="glass-card rounded-2xl p-6 border border-white/10 backdrop-blur-sm hover:border-cyan-400/30 transition-all duration-300 group"
                   variants={cardVariants}
                   initial="hidden"
                   whileInView="visible"
                   viewport={{ once: true }}
                   custom={0}
                 >
                   <div className="w-16 h-16 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-2xl flex items-center justify-center mb-6 mx-auto group-hover:scale-110 transition-transform duration-300">
                     <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                       <path fillRule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                     </svg>
                   </div>
                   <h3 className="text-xl font-semibold text-cyan-300 mb-4 h-14 flex items-center justify-center">Market Demand Analysis</h3>
                   <p className="text-gray-300 leading-relaxed min-h-[4.5rem] flex items-center justify-center">Analyze search volume, growth trends, and market size to validate real customer demand for your product idea.</p>
                 </motion.div>

                <motion.div
                   className="glass-card rounded-2xl p-6 border border-white/10 backdrop-blur-sm hover:border-purple-400/30 transition-all duration-300 group"
                   variants={cardVariants}
                   initial="hidden"
                   whileInView="visible"
                   viewport={{ once: true }}
                   custom={1}
                 >
                   <div className="w-16 h-16 bg-gradient-to-br from-purple-400 to-pink-500 rounded-2xl flex items-center justify-center mb-6 mx-auto group-hover:scale-110 transition-transform duration-300">
                     <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                       <path fillRule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" clipRule="evenodd" />
                     </svg>
                   </div>
                   <h3 className="text-xl font-semibold text-purple-300 mb-4 h-14 flex items-center justify-center">Competitive Intelligence</h3>
                   <p className="text-gray-300 leading-relaxed min-h-[4.5rem] flex items-center justify-center">Real-time competitor analysis, market gap identification, and strategic advantage assessment with comprehensive reports.</p>
                 </motion.div>

                <motion.div
                   className="glass-card rounded-2xl p-6 border border-white/10 backdrop-blur-sm hover:border-green-400/30 transition-all duration-300 group"
                   variants={cardVariants}
                   initial="hidden"
                   whileInView="visible"
                   viewport={{ once: true }}
                   custom={2}
                 >
                   <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-emerald-500 rounded-2xl flex items-center justify-center mb-6 mx-auto group-hover:scale-110 transition-transform duration-300">
                     <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                       <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
                       <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clipRule="evenodd" />
                     </svg>
                   </div>
                   <h3 className="text-xl font-semibold text-green-300 mb-4 h-14 flex items-center justify-center">Commercial Viability</h3>
                   <p className="text-gray-300 leading-relaxed min-h-[4.5rem] flex items-center justify-center">Evaluate revenue potential, customer acquisition costs, and business model sustainability with actionable insights.</p>
                 </motion.div>
              </div>

              {/* Enhanced PMF Analysis Demo */}
              <div className="space-y-8">
                {/* Main PMF Score Display */}
                <div className="text-center">
                  <div className="inline-flex items-center gap-4 glass-card rounded-2xl p-6 border border-white/20 mb-6">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                      <span className="text-white font-semibold">PMF Score: 8.5/10</span>
                    </div>
                    <div className="w-px h-6 bg-white/20"></div>
                    <div className="flex items-center gap-2">
                      <span className="text-gray-300">Market Validation:</span>
                      <span className="text-green-400 font-semibold">Strong Fit</span>
                    </div>
                    <div className="w-px h-6 bg-white/20"></div>
                    <div className="flex items-center gap-2">
                      <span className="text-gray-300">Success Probability:</span>
                      <span className="text-cyan-400 font-semibold">85%</span>
                    </div>
                  </div>
                </div>

                {/* Detailed Metrics Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Market Demand Metrics */}
                  <div className="glass-card rounded-xl p-6 border border-white/10">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="text-lg font-semibold text-white">Market Demand</h4>
                      <span className="text-2xl font-bold text-cyan-400">9.2/10</span>
                    </div>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-300">Search Volume</span>
                        <span className="text-sm font-medium text-white">↗ +127%</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div className="bg-gradient-to-r from-cyan-400 to-blue-500 h-2 rounded-full" style={{width: '92%'}}></div>
                      </div>
                      <div className="flex justify-between text-xs text-gray-400">
                        <span>Monthly searches: 45K+</span>
                        <span>Trend: Rising</span>
                      </div>
                    </div>
                  </div>

                  {/* Competition Analysis */}
                  <div className="glass-card rounded-xl p-6 border border-white/10">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="text-lg font-semibold text-white">Competition</h4>
                      <span className="text-2xl font-bold text-purple-400">7.8/10</span>
                    </div>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-300">Market Gap</span>
                        <span className="text-sm font-medium text-green-400">Identified</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div className="bg-gradient-to-r from-purple-400 to-pink-500 h-2 rounded-full" style={{width: '78%'}}></div>
                      </div>
                      <div className="flex justify-between text-xs text-gray-400">
                        <span>Direct competitors: 3</span>
                        <span>Advantage: Clear</span>
                      </div>
                    </div>
                  </div>

                  {/* Revenue Potential */}
                  <div className="glass-card rounded-xl p-6 border border-white/10">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="text-lg font-semibold text-white">Revenue Potential</h4>
                      <span className="text-2xl font-bold text-green-400">8.9/10</span>
                    </div>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-300">Market Size</span>
                        <span className="text-sm font-medium text-white">$2.4B</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div className="bg-gradient-to-r from-green-400 to-emerald-500 h-2 rounded-full" style={{width: '89%'}}></div>
                      </div>
                      <div className="flex justify-between text-xs text-gray-400">
                        <span>CAGR: 23.5%</span>
                        <span>TAM: Growing</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Success Case Study */}
                <div className="glass-card rounded-xl p-6 border border-white/10">
                  <div className="flex items-start gap-4">
                    <div className="flex-1">
                      <h4 className="text-lg font-semibold text-white mb-2">Real Success Story: AI Writing Assistant</h4>
                      <p className="text-gray-300 mb-4">Similar PMF score (8.7/10) led to successful product launch with 10K+ users in first 3 months</p>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                        <div>
                          <div className="text-xl font-bold text-cyan-400">10K+</div>
                          <div className="text-xs text-gray-400">Active Users</div>
                        </div>
                        <div>
                          <div className="text-xl font-bold text-green-400">$50K</div>
                          <div className="text-xs text-gray-400">Monthly Revenue</div>
                        </div>
                        <div>
                          <div className="text-xl font-bold text-purple-400">4.8★</div>
                          <div className="text-xs text-gray-400">User Rating</div>
                        </div>
                        <div>
                          <div className="text-xl font-bold text-yellow-400">78%</div>
                          <div className="text-xs text-gray-400">Retention Rate</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <p className="text-sm text-gray-400 text-center">*Example PMF analysis results for demonstration purposes</p>
              </div>
            </div>
          </div>
        </div>



        {/* Analysis progress and results removed - now shows feature showcase */}
        </div>
      </main>
    </div>
  );
}
