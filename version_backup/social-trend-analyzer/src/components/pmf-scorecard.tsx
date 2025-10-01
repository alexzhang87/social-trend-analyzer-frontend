import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AlertCircle, TrendingUp, Users, DollarSign, Target, Lightbulb, BarChart3 } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';

interface PMFMetrics {
  customerSatisfaction: number;
  marketDemand: number;
  productUsability: number;
  competitiveAdvantage: number;
  businessModel: number;
  teamCapability: number;
}

interface PMFHistory {
  date: string;
  score: number;
  metrics: PMFMetrics;
}

interface PMFScoreCardProps {
  onScoreUpdate?: (score: number, metrics: PMFMetrics) => void;
}

const PMF_QUESTIONS = {
  customerSatisfaction: [
    "How satisfied are customers with the product? (1-10 scale)",
    "How likely are customers to recommend the product to others? (1-10 scale)",
    "What is the customer renewal or repeat purchase rate? (1-10 scale)"
  ],
  marketDemand: [
    "What is the size and growth potential of the target market? (1-10 scale)",
    "How urgent is the customer need for this solution? (1-10 scale)",
    "How open is the market to accepting new products? (1-10 scale)"
  ],
  productUsability: [
    "How is the product's usability and user experience? (1-10 scale)",
    "How complete and stable are the product features? (1-10 scale)",
    "How effective is the product at solving core problems? (1-10 scale)"
  ],
  competitiveAdvantage: [
    "What is the unique value proposition compared to competitors? (1-10 scale)",
    "How high are the technical or business model barriers? (1-10 scale)",
    "What is the brand recognition and market position? (1-10 scale)"
  ],
  businessModel: [
    "How sustainable is the revenue model? (1-10 scale)",
    "What is the customer acquisition cost to lifetime value ratio? (1-10 scale)",
    "How is the profitability and cash flow situation? (1-10 scale)"
  ],
  teamCapability: [
    "What is the team's execution capability and professional level? (1-10 scale)",
    "How deep is the team's understanding of market and technology? (1-10 scale)",
    "What is the team's ability to adapt to change and learn? (1-10 scale)"
  ]
};

const METRIC_LABELS = {
  customerSatisfaction: 'Customer Satisfaction',
  marketDemand: 'Market Demand',
  productUsability: 'Product Usability',
  competitiveAdvantage: 'Competitive Advantage',
  businessModel: 'Business Model',
  teamCapability: 'Team Capability'
};

export function PMFScoreCard({ onScoreUpdate }: PMFScoreCardProps) {
  const [currentMetrics, setCurrentMetrics] = useState<PMFMetrics>({
    customerSatisfaction: 0,
    marketDemand: 0,
    productUsability: 0,
    competitiveAdvantage: 0,
    businessModel: 0,
    teamCapability: 0
  });
  
  const [history, setHistory] = useState<PMFHistory[]>([]);
  const [isAssessing, setIsAssessing] = useState(false);
  const [assessmentAnswers, setAssessmentAnswers] = useState<{[key: string]: number[]}>({});
  const [insights, setInsights] = useState<string>('');

  // Calculate overall PMF score
  const calculatePMFScore = (metrics: PMFMetrics): number => {
    const weights = {
      customerSatisfaction: 0.25,
      marketDemand: 0.20,
      productUsability: 0.20,
      competitiveAdvantage: 0.15,
      businessModel: 0.15,
      teamCapability: 0.05
    };
    
    return Object.entries(metrics).reduce((total, [key, value]) => {
      return total + (value * weights[key as keyof PMFMetrics]);
    }, 0);
  };

  const currentScore = calculatePMFScore(currentMetrics);

  // Get PMF level and recommendations
  const getPMFLevel = (score: number) => {
    if (score >= 8.5) return { level: 'Excellent', color: 'bg-green-500', advice: 'Product-market fit is extremely high, ready for large-scale expansion' };
    if (score >= 7.0) return { level: 'Good', color: 'bg-blue-500', advice: 'Product-market fit is good, continue optimizing and expanding' };
    if (score >= 5.5) return { level: 'Average', color: 'bg-yellow-500', advice: 'Need to focus on improving weak areas to enhance fit' };
    if (score >= 4.0) return { level: 'Poor', color: 'bg-orange-500', advice: 'Major issues exist, need to re-examine product positioning' };
    return { level: 'Very Poor', color: 'bg-red-500', advice: 'Product-market fit is very low, recommend redesigning' };
  };

  const pmfLevel = getPMFLevel(currentScore);

  // Start assessment
  const startAssessment = () => {
    setIsAssessing(true);
    setAssessmentAnswers({});
  };

  // Update assessment answer
  const updateAnswer = (category: string, questionIndex: number, score: number) => {
    setAssessmentAnswers(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [questionIndex]: score
      }
    }));
  };

  // Complete assessment
  const completeAssessment = () => {
    const newMetrics: PMFMetrics = {} as PMFMetrics;
    
    Object.keys(PMF_QUESTIONS).forEach(category => {
      const answers = assessmentAnswers[category] || {};
      const scores = Object.values(answers) as number[];
      const average = scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;
      newMetrics[category as keyof PMFMetrics] = average;
    });
    
    setCurrentMetrics(newMetrics);
    
    // Add to history
    const newHistory: PMFHistory = {
      date: new Date().toISOString().split('T')[0],
      score: calculatePMFScore(newMetrics),
      metrics: newMetrics
    };
    
    setHistory(prev => [...prev, newHistory]);
    setIsAssessing(false);
    
    // Generate insights
    generateInsights(newMetrics);
    
    // Callback
    if (onScoreUpdate) {
      onScoreUpdate(calculatePMFScore(newMetrics), newMetrics);
    }
  };

  // Generate AI insights
  const generateInsights = (metrics: PMFMetrics) => {
    const weakestMetric = Object.entries(metrics).reduce((min, [key, value]) => 
      value < min.value ? { key, value } : min, 
      { key: '', value: 10 }
    );
    
    const strongestMetric = Object.entries(metrics).reduce((max, [key, value]) => 
      value > max.value ? { key, value } : max, 
      { key: '', value: 0 }
    );
    
    const insights = `
Based on current assessment results:

🎯 **Greatest Strength**: ${METRIC_LABELS[strongestMetric.key as keyof typeof METRIC_LABELS]} (${strongestMetric.value.toFixed(1)} points)
⚠️ **Biggest Weakness**: ${METRIC_LABELS[weakestMetric.key as keyof typeof METRIC_LABELS]} (${weakestMetric.value.toFixed(1)} points)

📈 **Improvement Recommendations**:
${weakestMetric.key === 'customerSatisfaction' ? '• Deeply understand customer needs and optimize user experience\n• Establish customer feedback loop mechanisms\n• Improve customer service quality' : ''}
${weakestMetric.key === 'marketDemand' ? '• Re-validate target market positioning\n• Strengthen market research and user interviews\n• Adjust product positioning strategy' : ''}
${weakestMetric.key === 'productUsability' ? '• Optimize product features and interface design\n• Improve product stability and performance\n• Simplify user operation workflows' : ''}
${weakestMetric.key === 'competitiveAdvantage' ? '• Strengthen unique value proposition\n• Build technical or business barriers\n• Enhance brand building and marketing' : ''}
${weakestMetric.key === 'businessModel' ? '• Optimize revenue model and pricing strategy\n• Reduce customer acquisition cost, improve LTV\n• Improve cash flow management' : ''}
${weakestMetric.key === 'teamCapability' ? '• Strengthen team training and capability building\n• Introduce experts in relevant fields\n• Build a learning organization culture' : ''}
    `;
    
    setInsights(insights);
  };

  // Radar chart data
  const radarData = Object.entries(currentMetrics).map(([key, value]) => ({
    metric: METRIC_LABELS[key as keyof typeof METRIC_LABELS],
    value: value,
    fullMark: 10
  }));

  return (
    <div className="space-y-6">
      {/* PMF Score Overview */}
      <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5 text-cyan-400" />
                Product-Market Fit (PMF)
              </CardTitle>
              <CardDescription>
                Assess the degree of fit between product and market demand
              </CardDescription>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-white">{currentScore.toFixed(1)}</div>
              <Badge className={`${pmfLevel.color} text-white`}>
                {pmfLevel.level}
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Progress value={currentScore * 10} className="mb-4" />
          <p className="text-sm text-muted-foreground">{pmfLevel.advice}</p>
          
          {!isAssessing && (
            <Button 
              onClick={startAssessment} 
              className="mt-4 bg-cyan-600 hover:bg-cyan-700"
            >
              <BarChart3 className="w-4 h-4 mr-2" />
              Start PMF Assessment
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Assessment Questionnaire */}
      {isAssessing && (
        <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle>PMF Assessment Questionnaire</CardTitle>
            <CardDescription>
              Please rate each question based on actual situation (1-10 scale, 10 being highest)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="customerSatisfaction" className="w-full">
              <TabsList className="grid w-full grid-cols-3 lg:grid-cols-6">
                {Object.keys(PMF_QUESTIONS).map(category => (
                  <TabsTrigger key={category} value={category} className="text-xs">
                    {METRIC_LABELS[category as keyof typeof METRIC_LABELS]}
                  </TabsTrigger>
                ))}
              </TabsList>
              
              {Object.entries(PMF_QUESTIONS).map(([category, questions]) => (
                <TabsContent key={category} value={category} className="space-y-4">
                  <h3 className="font-semibold text-lg">
                    {METRIC_LABELS[category as keyof typeof METRIC_LABELS]}
                  </h3>
                  {questions.map((question, index) => (
                    <div key={index} className="space-y-2">
                      <Label>{question}</Label>
                      <div className="flex gap-2">
                        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(score => (
                          <Button
                            key={score}
                            variant={assessmentAnswers[category]?.[index] === score ? "default" : "outline"}
                            size="sm"
                            onClick={() => updateAnswer(category, index, score)}
                            className="w-10 h-10"
                          >
                            {score}
                          </Button>
                        ))}
                      </div>
                    </div>
                  ))}
                </TabsContent>
              ))}
            </Tabs>
            
            <div className="flex justify-end mt-6">
              <Button 
                onClick={completeAssessment}
                className="bg-green-600 hover:bg-green-700"
                disabled={Object.keys(assessmentAnswers).length < 6}
              >
                Complete Assessment
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Visualization charts */}
      {currentScore > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Radar Chart */}
          <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle>PMF Dimension Analysis</CardTitle>
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
                    stroke="#06b6d4"
                    fill="#06b6d4"
                    fillOpacity={0.3}
                    strokeWidth={2}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Historical Trend */}
          <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle>PMF Score Trend</CardTitle>
            </CardHeader>
            <CardContent>
              {history.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={history}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" className="text-xs" />
                    <YAxis domain={[0, 10]} className="text-xs" />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="score"
                      stroke="#06b6d4"
                      strokeWidth={3}
                      dot={{ fill: '#06b6d4', strokeWidth: 2, r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                  <div className="text-center">
                    <TrendingUp className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No historical data available</p>
                    <p className="text-sm">Trend chart will be displayed after completing first assessment</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* AI Insights & Recommendations */}
      {insights && (
        <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-yellow-400" />
              AI Insights & Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="whitespace-pre-line text-sm text-muted-foreground">
              {insights}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}