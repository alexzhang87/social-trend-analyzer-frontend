import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  TrendingUp, 
  TrendingDown, 
  Target, 
  Users, 
  DollarSign, 
  BarChart3, 
  Lightbulb, 
  AlertCircle,
  RefreshCw,
  Brain,
  Zap
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';

interface KeywordAnalysisData {
  keyword: string;
  searchVolume: number;
  competition: number;
  trend: 'up' | 'down' | 'stable';
  difficulty: number;
  cpc: number;
  relatedKeywords: string[];
  marketSize: number;
  growthRate: number;
  userIntent: 'informational' | 'commercial' | 'transactional' | 'navigational';
  seasonality: number;
}

interface AutomatedPMFMetrics {
  marketDemand: number;
  competitiveAdvantage: number;
  searchTrend: number;
  commercialViability: number;
  marketMaturity: number;
  opportunityScore: number;
}

interface PMFInsight {
  type: 'strength' | 'weakness' | 'opportunity' | 'threat';
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  actionable: boolean;
}

interface AutomatedPMFEvaluationProps {
  keywordData?: KeywordAnalysisData;
  onEvaluationComplete?: (score: number, metrics: AutomatedPMFMetrics) => void;
}

export function AutomatedPMFEvaluation({ keywordData, onEvaluationComplete }: AutomatedPMFEvaluationProps) {
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [pmfMetrics, setPmfMetrics] = useState<AutomatedPMFMetrics | null>(null);
  const [insights, setInsights] = useState<PMFInsight[]>([]);
  const [overallScore, setOverallScore] = useState<number>(0);
  const [evaluationHistory, setEvaluationHistory] = useState<Array<{
    date: string;
    keyword: string;
    score: number;
    metrics: AutomatedPMFMetrics;
  }>>([]);

  // Automated PMF calculation based on keyword analysis
  const calculateAutomatedPMF = (data: KeywordAnalysisData): AutomatedPMFMetrics => {
    // Market Demand Score (based on search volume and growth)
    const marketDemand = Math.min(10, (
      (Math.log10(data.searchVolume + 1) / 6) * 5 + // Search volume component (0-5)
      (data.growthRate / 20) * 3 + // Growth rate component (0-3)
      (data.marketSize / 1000000) * 2 // Market size component (0-2)
    ));

    // Competitive Advantage Score (inverse of competition and difficulty)
    const competitiveAdvantage = Math.max(1, 10 - (
      (data.competition / 10) * 4 + // Competition level (0-4)
      (data.difficulty / 100) * 6 // SEO difficulty (0-6)
    ));

    // Search Trend Score
    const searchTrend = data.trend === 'up' ? 8.5 : 
                       data.trend === 'stable' ? 6.0 : 3.5;

    // Commercial Viability Score (based on CPC and user intent)
    const intentMultiplier = {
      'transactional': 1.0,
      'commercial': 0.8,
      'navigational': 0.6,
      'informational': 0.4
    };
    const commercialViability = Math.min(10, (
      (data.cpc / 5) * 6 + // CPC component (0-6)
      4 * intentMultiplier[data.userIntent] // Intent component (0-4)
    ));

    // Market Maturity Score (inverse of seasonality, higher is better for stability)
    const marketMaturity = Math.max(1, 10 - (data.seasonality / 10));

    // Opportunity Score (Comprehensive Opportunity Rating)
    const opportunityScore = (
      marketDemand * 0.3 +
      competitiveAdvantage * 0.25 +
      searchTrend * 0.2 +
      commercialViability * 0.15 +
      marketMaturity * 0.1
    );

    return {
      marketDemand: Math.round(marketDemand * 10) / 10,
      competitiveAdvantage: Math.round(competitiveAdvantage * 10) / 10,
      searchTrend: Math.round(searchTrend * 10) / 10,
      commercialViability: Math.round(commercialViability * 10) / 10,
      marketMaturity: Math.round(marketMaturity * 10) / 10,
      opportunityScore: Math.round(opportunityScore * 10) / 10
    };
  };

  // Generate insights based on metrics
  const generateInsights = (metrics: AutomatedPMFMetrics, data: KeywordAnalysisData): PMFInsight[] => {
    const insights: PMFInsight[] = [];

    // Market Demand Insights
    if (metrics.marketDemand >= 8) {
      insights.push({
        type: 'strength',
        title: 'High Market Demand',
        description: `Strong search volume (${data.searchVolume.toLocaleString()}) indicates significant market interest`,
        impact: 'high',
        actionable: true
      });
    } else if (metrics.marketDemand <= 4) {
      insights.push({
        type: 'weakness',
        title: 'Low Market Demand',
        description: 'Limited search volume suggests niche market or low awareness',
        impact: 'high',
        actionable: true
      });
    }

    // Competitive Advantage Insights
    if (metrics.competitiveAdvantage >= 7) {
      insights.push({
        type: 'opportunity',
        title: 'Low Competition Window',
        description: 'Relatively low competition provides entry opportunity',
        impact: 'medium',
        actionable: true
      });
    } else if (metrics.competitiveAdvantage <= 4) {
      insights.push({
        type: 'threat',
        title: 'High Competition',
        description: 'Saturated market with established competitors',
        impact: 'high',
        actionable: true
      });
    }

    // Search Trend Insights
    if (data.trend === 'up') {
      insights.push({
        type: 'strength',
        title: 'Growing Interest',
        description: 'Upward search trend indicates increasing market interest',
        impact: 'medium',
        actionable: false
      });
    } else if (data.trend === 'down') {
      insights.push({
        type: 'threat',
        title: 'Declining Interest',
        description: 'Downward trend may indicate market saturation or declining relevance',
        impact: 'medium',
        actionable: true
      });
    }

    // Commercial Viability Insights
    if (metrics.commercialViability >= 7) {
      insights.push({
        type: 'strength',
        title: 'Strong Commercial Potential',
        description: 'High CPC and commercial intent suggest profitable market',
        impact: 'high',
        actionable: false
      });
    }

    return insights;
  };

  // Perform automated evaluation
  const performEvaluation = async () => {
    if (!keywordData) {
      return;
    }

    setIsEvaluating(true);
    
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const metrics = calculateAutomatedPMF(keywordData);
    const generatedInsights = generateInsights(metrics, keywordData);
    const score = metrics.opportunityScore;
    
    setPmfMetrics(metrics);
    setInsights(generatedInsights);
    setOverallScore(score);
    
    // Add to history
    const newEntry = {
      date: new Date().toISOString().split('T')[0],
      keyword: keywordData.keyword,
      score,
      metrics
    };
    setEvaluationHistory(prev => [newEntry, ...prev.slice(0, 9)]); // Keep last 10 entries
    
    setIsEvaluating(false);
    
    if (onEvaluationComplete) {
      onEvaluationComplete(score, metrics);
    }
  };

  // Get PMF level and color
  const getPMFLevel = (score: number) => {
    if (score >= 8.5) return { level: 'Excellent', color: 'bg-green-500', textColor: 'text-green-700' };
    if (score >= 7.0) return { level: 'Good', color: 'bg-blue-500', textColor: 'text-blue-700' };
    if (score >= 5.5) return { level: 'Average', color: 'bg-yellow-500', textColor: 'text-yellow-700' };
    if (score >= 4.0) return { level: 'Poor', color: 'bg-orange-500', textColor: 'text-orange-700' };
    return { level: 'Very Poor', color: 'bg-red-500', textColor: 'text-red-700' };
  };

  const pmfLevel = getPMFLevel(overallScore);

  // Radar chart data
  const radarData = pmfMetrics ? [
    { metric: 'Market Demand', value: pmfMetrics.marketDemand },
    { metric: 'Competitive Advantage', value: pmfMetrics.competitiveAdvantage },
    { metric: 'Search Trend', value: pmfMetrics.searchTrend },
    { metric: 'Commercial Viability', value: pmfMetrics.commercialViability },
    { metric: 'Market Maturity', value: pmfMetrics.marketMaturity },
  ] : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5" />
            Automated PMF Evaluation
          </CardTitle>
          <CardDescription>
            AI-powered Product-Market Fit analysis based on keyword research data
          </CardDescription>
        </CardHeader>
        <CardContent>
          {keywordData ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Analyzing: {keywordData.keyword}</p>
                  <p className="text-sm text-muted-foreground">
                    Search Volume: {keywordData.searchVolume.toLocaleString()} | 
                    Competition: {keywordData.competition}/10 | 
                    Trend: {keywordData.trend}
                  </p>
                </div>
                <Button 
                  onClick={performEvaluation} 
                  disabled={isEvaluating}
                  className="min-w-[140px]"
                >
                  {isEvaluating ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Evaluating...
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4 mr-2" />
                      Start Evaluation
                    </>
                  )}
                </Button>
              </div>
            </div>
          ) : (
            <Alert>
              <AlertCircle className="w-4 h-4" />
              <AlertDescription>
                No keyword data available. Please perform a keyword analysis first.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Results */}
      {pmfMetrics && (
        <>
          {/* Overall Score */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5" />
                PMF Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-4xl font-bold">{overallScore.toFixed(1)}/10</p>
                  <p className="text-sm text-muted-foreground">Overall PMF Score</p>
                </div>
                <Badge className={`${pmfLevel.color} text-white`}>
                  {pmfLevel.level}
                </Badge>
              </div>
              <Progress value={overallScore * 10} className="mb-2" />
            </CardContent>
          </Card>

          {/* Metrics Breakdown */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Metrics Cards */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Metrics Breakdown</h3>
              
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Market Demand</span>
                    <span className="text-sm font-bold">{pmfMetrics.marketDemand}/10</span>
                  </div>
                  <Progress value={pmfMetrics.marketDemand * 10} />
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Competitive Advantage</span>
                    <span className="text-sm font-bold">{pmfMetrics.competitiveAdvantage}/10</span>
                  </div>
                  <Progress value={pmfMetrics.competitiveAdvantage * 10} />
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Search Trend</span>
                    <span className="text-sm font-bold">{pmfMetrics.searchTrend}/10</span>
                  </div>
                  <Progress value={pmfMetrics.searchTrend * 10} />
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Commercial Viability</span>
                    <span className="text-sm font-bold">{pmfMetrics.commercialViability}/10</span>
                  </div>
                  <Progress value={pmfMetrics.commercialViability * 10} />
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Market Maturity</span>
                    <span className="text-sm font-bold">{pmfMetrics.marketMaturity}/10</span>
                  </div>
                  <Progress value={pmfMetrics.marketMaturity * 10} />
                </CardContent>
              </Card>
            </div>

            {/* Radar Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">PMF Radar</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={radarData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="metric" className="text-xs" />
                    <PolarRadiusAxis angle={90} domain={[0, 10]} className="text-xs" />
                    <Radar
                      name="PMF Score"
                      dataKey="value"
                      stroke="#3b82f6"
                      fill="#3b82f6"
                      fillOpacity={0.3}
                      strokeWidth={2}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Insights */}
          {insights.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="w-5 h-5" />
                  AI Insights
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {insights.map((insight, index) => (
                    <Alert key={index} className={`border-l-4 ${
                      insight.type === 'strength' ? 'border-l-green-500' :
                      insight.type === 'opportunity' ? 'border-l-blue-500' :
                      insight.type === 'weakness' ? 'border-l-yellow-500' :
                      'border-l-red-500'
                    }`}>
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="font-medium">{insight.title}</h4>
                          <p className="text-sm text-muted-foreground mt-1">{insight.description}</p>
                        </div>
                        <div className="flex gap-2">
                          <Badge variant="outline" className="text-xs">
                            {insight.impact} impact
                          </Badge>
                          <Badge variant={insight.type === 'strength' || insight.type === 'opportunity' ? 'default' : 'secondary'} className="text-xs capitalize">
                            {insight.type}
                          </Badge>
                        </div>
                      </div>
                    </Alert>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}