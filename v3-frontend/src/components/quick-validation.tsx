import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  Search, 
  Heart,
  MessageCircle,
  Share2,
  BarChart3,
  Clock,
  Target,
  Zap,
  ArrowRight,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  Info
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

interface QuickValidationData {
  keyword: string;
  overallScore: number;
  trendDirection: 'up' | 'down' | 'stable';
  searchVolume: number;
  competitionLevel: 'low' | 'medium' | 'high';
  sentiment: {
    positive: number;
    neutral: number;
    negative: number;
  };
  quickInsights: string[];
  trendData: Array<{
    date: string;
    interest: number;
  }>;
  relatedKeywords: Array<{
    keyword: string;
    relevance: number;
  }>;
  marketOpportunity: 'high' | 'medium' | 'low';
  recommendation: string;
}

interface QuickValidationProps {
  keyword: string;
  onUpgrade: () => void;
  onNewAnalysis: () => void;
}

export function QuickValidation({ keyword, onUpgrade, onNewAnalysis }: QuickValidationProps) {
  const [data, setData] = useState<QuickValidationData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchQuickValidation();
  }, [keyword]);

  const fetchQuickValidation = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Simulate API call - replace with actual API
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock data - replace with actual API response
      const mockData: QuickValidationData = {
        keyword,
        overallScore: Math.floor(Math.random() * 40) + 60, // 60-100
        trendDirection: ['up', 'down', 'stable'][Math.floor(Math.random() * 3)] as any,
        searchVolume: Math.floor(Math.random() * 50000) + 10000,
        competitionLevel: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)] as any,
        sentiment: {
          positive: Math.floor(Math.random() * 30) + 50,
          neutral: Math.floor(Math.random() * 20) + 20,
          negative: Math.floor(Math.random() * 20) + 10
        },
        quickInsights: [
          'Growing interest in this market segment',
          'Moderate competition with room for innovation',
          'Strong positive sentiment from early adopters',
          'Seasonal trends show consistent growth'
        ],
        trendData: Array.from({ length: 12 }, (_, i) => ({
          date: new Date(2024, i, 1).toLocaleDateString('en-US', { month: 'short' }),
          interest: Math.floor(Math.random() * 40) + 30
        })),
        relatedKeywords: [
          { keyword: 'AI automation', relevance: 85 },
          { keyword: 'productivity tools', relevance: 78 },
          { keyword: 'workflow optimization', relevance: 72 },
          { keyword: 'business efficiency', relevance: 65 }
        ],
        marketOpportunity: ['high', 'medium', 'low'][Math.floor(Math.random() * 3)] as any,
        recommendation: 'This keyword shows promising potential with growing market interest and manageable competition.'
      };
      
      setData(mockData);
    } catch (err) {
      setError('Failed to fetch validation data. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    return 'Needs Improvement';
  };

  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case 'up': return <TrendingUp className="w-5 h-5 text-green-500" />;
      case 'down': return <TrendingDown className="w-5 h-5 text-red-500" />;
      default: return <BarChart3 className="w-5 h-5 text-gray-500" />;
    }
  };

  const getCompetitionBadge = (level: string) => {
    const colors = {
      low: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-red-100 text-red-800'
    };
    return <Badge className={colors[level as keyof typeof colors]}>{level.toUpperCase()}</Badge>;
  };

  const getOpportunityBadge = (level: string) => {
    const colors = {
      high: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-red-100 text-red-800'
    };
    return <Badge className={colors[level as keyof typeof colors]}>{level.toUpperCase()}</Badge>;
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-500 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Analyzing "{keyword}"</h3>
            <p className="text-gray-600 text-center">
              Gathering market insights and trend data...
            </p>
            <Progress value={75} className="w-64 mt-4" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Alert variant="destructive">
          <AlertTriangle className="w-4 h-4" />
          <AlertDescription>
            {error || 'Failed to load validation data'}
            <Button 
              variant="outline" 
              size="sm" 
              onClick={fetchQuickValidation}
              className="ml-4"
            >
              Try Again
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-gray-900">
          Quick Validation Results
        </h1>
        <p className="text-gray-600">
          Analysis for: <span className="font-semibold">"{keyword}"</span>
        </p>
      </div>

      {/* Overall Score */}
      <Card>
        <CardHeader className="text-center">
          <CardTitle className="flex items-center justify-center gap-2">
            <Zap className="w-6 h-6 text-blue-500" />
            Market Validation Score
          </CardTitle>
        </CardHeader>
        <CardContent className="text-center">
          <div className={`text-6xl font-bold ${getScoreColor(data.overallScore)} mb-2`}>
            {data.overallScore}
          </div>
          <div className="text-xl text-gray-600 mb-4">
            {getScoreLabel(data.overallScore)}
          </div>
          <Progress value={data.overallScore} className="w-64 mx-auto" />
        </CardContent>
      </Card>

      {/* Key Metrics */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Trend Direction</p>
                <div className="flex items-center gap-2 mt-1">
                  {getTrendIcon(data.trendDirection)}
                  <span className="font-semibold capitalize">{data.trendDirection}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Search Volume</p>
                <p className="text-lg font-semibold">{data.searchVolume.toLocaleString()}</p>
              </div>
              <Search className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Competition</p>
                <div className="mt-1">
                  {getCompetitionBadge(data.competitionLevel)}
                </div>
              </div>
              <Target className="w-8 h-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Market Opportunity</p>
                <div className="mt-1">
                  {getOpportunityBadge(data.marketOpportunity)}
                </div>
              </div>
              <BarChart3 className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Trend Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Interest Trend (Last 12 Months)</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="interest" 
                stroke="#3B82F6" 
                strokeWidth={2}
                dot={{ fill: '#3B82F6' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Sentiment Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>Sentiment Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Positive</span>
              <span className="text-sm text-gray-600">{data.sentiment.positive}%</span>
            </div>
            <Progress value={data.sentiment.positive} className="h-2" />
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Neutral</span>
              <span className="text-sm text-gray-600">{data.sentiment.neutral}%</span>
            </div>
            <Progress value={data.sentiment.neutral} className="h-2" />
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Negative</span>
              <span className="text-sm text-gray-600">{data.sentiment.negative}%</span>
            </div>
            <Progress value={data.sentiment.negative} className="h-2" />
          </div>
        </CardContent>
      </Card>

      {/* Quick Insights */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Insights</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {data.quickInsights.map((insight, index) => (
              <div key={index} className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700">{insight}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Related Keywords */}
      <Card>
        <CardHeader>
          <CardTitle>Related Keywords</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            {data.relatedKeywords.map((item, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="font-medium">{item.keyword}</span>
                <Badge variant="outline">{item.relevance}% match</Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recommendation */}
      <Alert>
        <Info className="w-4 h-4" />
        <AlertDescription>
          <strong>Recommendation:</strong> {data.recommendation}
        </AlertDescription>
      </Alert>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <Button onClick={onUpgrade} size="lg" className="bg-purple-600 hover:bg-purple-700">
          <Target className="w-4 h-4 mr-2" />
          Upgrade to Professional Analysis
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
        
        <Button onClick={onNewAnalysis} variant="outline" size="lg">
          <RefreshCw className="w-4 h-4 mr-2" />
          Analyze Another Keyword
        </Button>
      </div>

      {/* Upgrade Prompt */}
      <Card className="border-purple-200 bg-purple-50">
        <CardContent className="p-6">
          <div className="text-center space-y-4">
            <h3 className="text-lg font-semibold text-purple-900">
              Want Deeper Insights?
            </h3>
            <p className="text-purple-700">
              Upgrade to Professional Analysis for competitor analysis, user personas, 
              business opportunities, and actionable recommendations.
            </p>
            <div className="flex items-center justify-center gap-6 text-sm text-purple-600">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4" />
                Competitor Analysis
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4" />
                User Personas
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4" />
                Business Opportunities
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}