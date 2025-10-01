import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  Target, 
  Users, 
  DollarSign, 
  BarChart3, 
  Lightbulb,
  RefreshCw,
  Eye,
  Zap,
  Brain,
  Shield,
  Rocket
} from 'lucide-react';
import { useAuth } from '@/components/auth-provider';
import { useToast } from '@/components/ui/use-toast';
import { PMFScoreCard } from './pmf-scorecard';
import { CompetitorAlert } from './competitor-alert';
import { DataStudioIntegration } from './data-studio-integration';
// AI Model Training moved to admin interface

// Data interface definitions
interface PMFScore {
  overall_score: number;
  market_demand: number;
  product_fit: number;
  user_satisfaction: number;
  growth_potential: number;
  last_updated: string;
  trend: 'up' | 'down' | 'stable';
}

interface CompetitorAlert {
  id: string;
  competitor_name: string;
  alert_type: 'threat' | 'opportunity' | 'update';
  severity: 'low' | 'medium' | 'high';
  title: string;
  description: string;
  created_at: string;
  action_required: boolean;
}

interface BusinessInsight {
  id: string;
  type: 'market_trend' | 'user_behavior' | 'competitive_gap' | 'growth_opportunity';
  title: string;
  description: string;
  impact_score: number;
  confidence: number;
  created_at: string;
  tags: string[];
}

interface DashboardData {
  pmf_score: PMFScore;
  competitor_alerts: CompetitorAlert[];
  business_insights: BusinessInsight[];
  quick_stats: {
    total_analyses: number;
    active_monitors: number;
    insights_generated: number;
    success_rate: number;
  };
}

export function EntrepreneurDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const { user } = useAuth();
  const { toast } = useToast();

  // Simulate data loading
  const loadDashboardData = async () => {
    try {
      setLoading(true);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockData: DashboardData = {
        pmf_score: {
          overall_score: 78,
          market_demand: 85,
          product_fit: 72,
          user_satisfaction: 80,
          growth_potential: 75,
          last_updated: new Date().toISOString(),
          trend: 'up'
        },
        competitor_alerts: [
          {
            id: '1',
            competitor_name: 'CompetitorX',
            alert_type: 'threat',
            severity: 'high',
            title: 'New Feature Release',
            description: 'CompetitorX released similar AI analysis features, potentially impacting market share',
            created_at: new Date().toISOString(),
            action_required: true
          },
          {
            id: '2',
            competitor_name: 'StartupY',
            alert_type: 'opportunity',
            severity: 'medium',
            title: 'Funding Difficulties',
            description: 'StartupY is facing funding challenges, creating expansion opportunities during market gaps',
            created_at: new Date().toISOString(),
            action_required: false
          }
        ],
        business_insights: [
          {
            id: '1',
            type: 'market_trend',
            title: 'Surge in AI-Driven Analysis Demand',
            description: 'Search volume for AI analysis tools increased by 45% in the past 30 days, indicating strong market demand',
            impact_score: 85,
            confidence: 92,
            created_at: new Date().toISOString(),
            tags: ['AI', 'Market Demand', 'Growth']
          },
          {
            id: '2',
            type: 'competitive_gap',
            title: 'SME Market Gap',
            description: 'Existing competitors mainly serve large enterprises, leaving a clear gap in the SME market',
            impact_score: 78,
            confidence: 88,
            created_at: new Date().toISOString(),
            tags: ['SME', 'Market Gap', 'Opportunity']
          }
        ],
        quick_stats: {
          total_analyses: 156,
          active_monitors: 8,
          insights_generated: 23,
          success_rate: 94.2
        }
      };
      
      setData(mockData);
    } catch (error) {
      toast({
        title: "Loading Failed",
        description: "Unable to load workspace data, please try again later",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const refreshData = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
    toast({
      title: "Data Updated",
      description: "Workspace data has been refreshed"
    });
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-white mb-4">Loading Failed</h2>
            <Button onClick={loadDashboardData} className="bg-cyan-500 hover:bg-cyan-600">
              Reload
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'low': return 'bg-green-500/20 text-green-400 border-green-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'threat': return <AlertTriangle className="h-4 w-4" />;
      case 'opportunity': return <Lightbulb className="h-4 w-4" />;
      case 'update': return <Eye className="h-4 w-4" />;
      default: return <AlertTriangle className="h-4 w-4" />;
    }
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'market_trend': return <TrendingUp className="h-5 w-5" />;
      case 'user_behavior': return <Users className="h-5 w-5" />;
      case 'competitive_gap': return <Shield className="h-5 w-5" />;
      case 'growth_opportunity': return <Rocket className="h-5 w-5" />;
      default: return <Brain className="h-5 w-5" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Page title and refresh button */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
              Entrepreneur Workspace
            </h1>
            <p className="text-gray-400 mt-2">Monitor your product market performance and competitive landscape in real-time</p>
          </div>
          <Button 
            onClick={refreshData} 
            disabled={refreshing}
            className="bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/30 text-cyan-400"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh Data
          </Button>
        </div>

        {/* Quick stats cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-white/5 backdrop-blur-md border-white/10 hover:bg-white/10 transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Total Analyses</p>
                  <p className="text-2xl font-bold text-white">{data.quick_stats.total_analyses}</p>
                </div>
                <BarChart3 className="h-8 w-8 text-cyan-400" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white/5 backdrop-blur-md border-white/10 hover:bg-white/10 transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Active Monitors</p>
                  <p className="text-2xl font-bold text-white">{data.quick_stats.active_monitors}</p>
                </div>
                <Eye className="h-8 w-8 text-purple-400" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white/5 backdrop-blur-md border-white/10 hover:bg-white/10 transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Generated Insights</p>
                  <p className="text-2xl font-bold text-white">{data.quick_stats.insights_generated}</p>
                </div>
                <Brain className="h-8 w-8 text-green-400" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white/5 backdrop-blur-md border-white/10 hover:bg-white/10 transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Success Rate</p>
                  <p className="text-2xl font-bold text-white">{data.quick_stats.success_rate}%</p>
                </div>
                <Target className="h-8 w-8 text-yellow-400" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main content area */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="bg-white/10 backdrop-blur-md border border-white/20">
            <TabsTrigger value="overview" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
              Overview
            </TabsTrigger>
            <TabsTrigger value="pmf" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
              PMF Score
            </TabsTrigger>
            <TabsTrigger value="competitors" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
              Competitor Monitoring
            </TabsTrigger>
            <TabsTrigger value="insights" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
              Business Insights
            </TabsTrigger>
          </TabsList>

          {/* Overview tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* PMF score card */}
              <Card className="bg-white/5 backdrop-blur-md border-white/10">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-white">
                    <Target className="h-5 w-5 text-cyan-400" />
                    PMF Score Overview
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-3xl font-bold text-white">{data.pmf_score.overall_score}</span>
                      <Badge className={`${data.pmf_score.trend === 'up' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                        {data.pmf_score.trend === 'up' ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                        {data.pmf_score.trend === 'up' ? 'Rising' : 'Falling'}
                      </Badge>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Market Demand</span>
                        <span className="text-white">{data.pmf_score.market_demand}%</span>
                      </div>
                      <Progress value={data.pmf_score.market_demand} className="h-2" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Latest competitor alerts */}
              <Card className="bg-white/5 backdrop-blur-md border-white/10">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-white">
                    <AlertTriangle className="h-5 w-5 text-yellow-400" />
                    Latest Alerts
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {data.competitor_alerts.slice(0, 2).map((alert) => (
                      <Alert key={alert.id} className={`${getSeverityColor(alert.severity)} border`}>
                        <div className="flex items-start gap-2">
                          {getAlertIcon(alert.alert_type)}
                          <div className="flex-1">
                            <AlertTitle className="text-sm font-medium">{alert.title}</AlertTitle>
                            <AlertDescription className="text-xs mt-1">
                              {alert.description}
                            </AlertDescription>
                          </div>
                        </div>
                      </Alert>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* PMF score tab */}
          <TabsContent value="pmf" className="space-y-6">
            <PMFScoreCard onScoreUpdate={(score, metrics) => {
              console.log('PMF Score Updated:', score, metrics);
            }} />
          </TabsContent>

          {/* Competitor monitoring tab */}
          <TabsContent value="competitors" className="space-y-6">
            <CompetitorAlert onThreatDetected={(competitor, alert) => {
              console.log('Threat Detected:', competitor, alert);
            }} />
          </TabsContent>

          {/* Business insights tab */}
          <TabsContent value="insights" className="space-y-6">
            <DataStudioIntegration />
          </TabsContent>


        </Tabs>
      </div>
    </div>
  );
}