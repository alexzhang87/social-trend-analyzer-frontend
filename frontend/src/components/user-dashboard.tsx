import React, { useState, useEffect } from 'react';
import { useAuth } from '@/components/auth-provider';
import { useNavigate } from 'react-router-dom';
import { Header } from './header';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  TrendingUp, 
  Search, 
  Clock, 
  Star, 
  ArrowRight, 
  Zap,
  BarChart3,
  Users,
  Target,
  Crown,
  Sparkles,
  History,
  ExternalLink,
  Check
} from 'lucide-react';

// Sample data - showcasing product value
const sampleAnalyses = [
  {
    id: 1,
    keyword: 'AI Startup',
    trend_score: 85,
    sentiment: 'positive',
    opportunities: 12,
    created_at: '2024-01-15'
  },
  {
    id: 2,
    keyword: 'Blockchain Application',
    trend_score: 72,
    sentiment: 'positive',
    opportunities: 8,
    created_at: '2024-01-14'
  },
  {
    id: 3,
    keyword: 'E-commerce Live Streaming',
    trend_score: 68,
    sentiment: 'neutral',
    opportunities: 6,
    created_at: '2024-01-13'
  }
];

const trendingKeywords = [
  { keyword: 'ChatGPT Application', growth: '+156%', category: 'AI Technology' },
  { keyword: 'New Energy Vehicle', growth: '+89%', category: 'Automotive' },
  { keyword: 'Live Commerce', growth: '+67%', category: 'E-commerce' },
  { keyword: 'Metaverse Gaming', growth: '+45%', category: 'Gaming' }
];

export function UserDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [analysisCount, setAnalysisCount] = useState(0);
  const [maxAnalyses, setMaxAnalyses] = useState(3);

  // Simulate getting user usage
  useEffect(() => {
    // Set limits based on user level
    if (user?.subscription_type === 'free') {
      setMaxAnalyses(3);
      setAnalysisCount(1); // Assume 1 analysis used
    } else {
      setMaxAnalyses(-1); // Unlimited
    }
  }, [user]);

  const handleQuickAnalysis = (keyword: string) => {
    navigate(`/workspace?section=analysis&keywords=${encodeURIComponent(keyword)}`);
  };

  const handleViewAnalysis = (id: string) => {
    navigate(`/workspace?section=analysis&demo=${id}`);
  };

  const remainingAnalyses = maxAnalyses === -1 ? 'Unlimited' : Math.max(0, maxAnalyses - analysisCount);
  const usageProgress = maxAnalyses === -1 ? 0 : (analysisCount / maxAnalyses) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">
            Welcome back, {user?.username || 'User'}!
          </h1>
          <p className="text-gray-300">
            Discover your next business opportunity with data-driven entrepreneurial decisions
          </p>
        </div>

        {/* Usage Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-gray-800/50 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-300">
                    Remaining Analyses
                  </p>
                  <p className="text-2xl font-bold text-white">
                    {remainingAnalyses}
                  </p>
                </div>
                <div className="h-12 w-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                  <BarChart3 className="h-6 w-6 text-blue-400" />
                </div>
              </div>
              <p className="text-xs text-gray-400 mt-2">
                Used {analysisCount}/{maxAnalyses} times
              </p>
            </CardContent>
          </Card>

          {/* Trend Insights Card */}
          <Card className="bg-gray-800/50 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-300">
                    Opportunities Found
                  </p>
                  <p className="text-2xl font-bold text-white">
                    {sampleAnalyses.reduce((sum, analysis) => sum + analysis.opportunities, 0)}
                  </p>
                </div>
                <div className="h-12 w-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                  <TrendingUp className="h-6 w-6 text-green-400" />
                </div>
              </div>
              <p className="text-xs text-gray-400 mt-2">
                Based on your analysis history
              </p>
            </CardContent>
          </Card>

          {/* Membership Status Card */}
          <Card className="bg-gray-800/50 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-300">
                    Membership Level
                  </p>
                  <p className="text-2xl font-bold text-white">
                    {user?.subscription_type === 'free' ? 'Free' : 'Pro'}
                  </p>
                </div>
                <div className="h-12 w-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
                  <Crown className="h-6 w-6 text-purple-400" />
                </div>
              </div>
              {user?.subscription_type === 'free' && (
                <Button 
                  size="sm" 
                  className="mt-2 w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                  onClick={() => navigate('/pricing')}
                >
                  Upgrade Pro
                </Button>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Quick Analysis Section */}
        <Card className="mb-8 bg-gray-800/50 border-gray-700">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <Sparkles className="h-5 w-5 text-yellow-500" />
              Trending Analysis
            </CardTitle>
            <CardDescription className="text-gray-400">
              One-click analysis of the hottest startup keywords
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {trendingKeywords.map((item, index) => (
                <div 
                  key={index}
                  className="p-4 bg-gray-700/30 border border-gray-600 rounded-lg hover:bg-gray-700/50 transition-colors cursor-pointer"
                  onClick={() => handleQuickAnalysis(item.keyword)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-white">{item.keyword}</span>
                    <span className="text-xs text-green-400 font-semibold">{item.growth}</span>
                  </div>
                  <p className="text-xs text-gray-400">{item.category}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Analysis History */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <Clock className="h-5 w-5 text-blue-500" />
                Recent Analyses
              </CardTitle>
              <CardDescription className="text-gray-400">
                View your analysis history and discovered opportunities
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {sampleAnalyses.map((analysis) => (
                  <div 
                    key={analysis.id} 
                    className="flex items-center justify-between p-4 bg-gray-700/30 border border-gray-600 rounded-lg hover:bg-gray-700/50 transition-colors cursor-pointer"
                    onClick={() => handleViewAnalysis(analysis.id.toString())}
                  >
                    <div className="flex-1">
                      <h4 className="font-medium text-white">{analysis.keyword}</h4>
                      <div className="flex items-center gap-4 mt-1 text-sm text-gray-400">
                        <span>
                          {analysis.sentiment === 'positive' ? 'Positive' : 'Neutral'}
                        </span>
                        <span>•</span>
                        <span>
                          Trend: {analysis.trend_score}%
                        </span>
                        <span>•</span>
                        <span>
                          {analysis.opportunities} opportunities
                        </span>
                      </div>
                    </div>
                    <ArrowRight className="h-4 w-4 text-gray-400" />
                  </div>
                ))}
              </div>
              <Button 
                variant="outline" 
                className="w-full mt-4 border-gray-600 text-gray-300 hover:bg-gray-700"
                onClick={() => navigate('/workspace')}
              >
                Start New Analysis
              </Button>
            </CardContent>
          </Card>

          {/* Upgrade Prompt - Only show for free users */}
          {user?.subscription_type === 'free' && (
            <Card className="bg-gradient-to-r from-purple-900/50 to-blue-900/50 border-purple-500/30">
              <CardHeader>
                <CardTitle className="text-white">
                  Unlock More Business Insights
                </CardTitle>
                <CardDescription className="text-gray-300">
                  Upgrade to Pro version for unlimited analyses, detailed user profiles, competitor monitoring, and advanced features
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 mb-4">
                  <div className="flex items-center gap-2 text-sm text-gray-300">
                    <Users className="h-4 w-4" />
                    Detailed User Profiles
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-300">
                    <BarChart3 className="h-4 w-4" />
                    Competitor Analysis
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-300">
                    <Star className="h-4 w-4" />
                    PDF Report Export
                  </div>
                </div>
                <Button 
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                  onClick={() => navigate('/pricing')}
                >
                  Upgrade Now
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          )}
        </div>


      </main>
    </div>
  );
}
