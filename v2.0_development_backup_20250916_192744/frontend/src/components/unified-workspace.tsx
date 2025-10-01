import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
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
  Rocket,
  User,
  CreditCard,
  History,
  Settings,
  Calendar,
  Download,
  Search,
  Home,
  PieChart,
  FileText,
  Menu,
  X,
  Loader2,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { useAuth } from '@/components/auth-provider';
import { AnalysisResults } from './analysis-results';
import { useToast } from '@/components/ui/use-toast';
import { useAnalysisLimit } from './subscription-gate';
import { PMFScoreCard } from './pmf-scorecard';
import { AutomatedPMFEvaluation } from './automated-pmf-evaluation';
import { PMFExplanation } from './pmf-explanation';
import { CompetitorAlert } from './competitor-alert';
import { DataStudioIntegration } from './data-studio-integration';
import CreditsPurchase from './credits-purchase';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { trendsApiClient, type TrendAnalysis, type ComprehensiveAnalysisRequest } from '@/lib/trends-api';

// Interface definitions
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

const sidebarItems = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: Home,
    description: 'Overview and key metrics'
  },
  {
    id: 'analysis',
    label: 'Keyword Analysis',
    icon: Search,
    description: 'Analyze market trends'
  },
  {
    id: 'pmf',
    label: 'PMF Scorecard',
    icon: Target,
    description: 'Product-market fit evaluation'
  },
  {
    id: 'competitors',
    label: 'Competitor Alerts',
    icon: AlertTriangle,
    description: 'Monitor competition'
  },
  {
    id: 'insights',
    label: 'Business Insights',
    icon: Lightbulb,
    description: 'AI-powered recommendations'
  },
  {
    id: 'reports',
    label: 'Data Studio',
    icon: FileText,
    description: 'Generate reports'
  },
  {
    id: 'account',
    label: 'Account',
    icon: User,
    description: 'Profile and settings'
  }
];

export function UnifiedWorkspace() {
  const [activeSection, setActiveSection] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [keywords, setKeywords] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [keywordAnalysisData, setKeywordAnalysisData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const { user, isAuthenticated } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const { canAnalyze, remainingAnalyses } = useAnalysisLimit();

  // Load dashboard data
  const loadDashboardData = async () => {
    try {
      setLoading(true);
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockData: DashboardData = {
        pmf_score: {
          overall_score: 7.8,
          market_demand: 8.5,
          product_fit: 7.2,
          user_satisfaction: 8.0,
          growth_potential: 7.5,
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
            description: 'CompetitorX released similar AI analysis features',
            created_at: new Date().toISOString(),
            action_required: true
          }
        ],
        business_insights: [
          {
            id: '1',
            type: 'market_trend',
            title: 'Growing Demand for AI Tools',
            description: 'Market shows 40% increase in AI tool adoption',
            impact_score: 8.5,
            confidence: 0.92,
            created_at: new Date().toISOString(),
            tags: ['AI', 'Market Growth']
          }
        ],
        quick_stats: {
          total_analyses: 156,
          active_monitors: 8,
          insights_generated: 23,
          success_rate: 94.2
        }
      };
      
      setDashboardData(mockData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const refreshData = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
    toast({
      title: "Data refreshed",
      description: "Dashboard data has been updated",
    });
  };

  useEffect(() => {
    loadDashboardData();
    
    // Check URL parameters for section and keywords
    const urlParams = new URLSearchParams(location.search);
    const section = urlParams.get('section');
    const urlKeywords = urlParams.get('keywords');
    
    if (section) {
      setActiveSection(section);
    }
    
    if (urlKeywords) {
      setKeywords(decodeURIComponent(urlKeywords));
    }
  }, [location.search]);

  const handleAnalyze = async () => {
    if (!keywords.trim()) {
      toast({
        title: "Please enter keywords",
        description: "Keywords are required to start analysis",
        variant: "destructive",
      });
      return;
    }

    // Check analysis limit for free users
    if (!canAnalyze) {
      toast({
        title: "Analysis limit reached",
        description: "Free users can perform up to 3 analyses. Please upgrade to continue.",
        variant: "destructive",
      });
      return;
    }

    setIsAnalyzing(true);
    try {
      // Prepare request data
      const keywordList = keywords.split(',').map(k => k.trim()).filter(k => k.length > 0);
      const request: ComprehensiveAnalysisRequest = {
        keywords: keywordList,
        platforms: ['reddit', 'twitter', 'product_hunt'],
        time_filter: '7d',
        limit_per_platform: 10
      };

      // Call real API
      const response = await trendsApiClient.comprehensiveAnalysis(request);
      
      // Validate API response
      if (!response || !response.data) {
        throw new Error('Invalid API response: missing data');
      }
      
      const apiData = response.data;
      const hypeIndex = apiData.hypeIndex || 0;
      
      // Transform API response to match component expectations
      const analysisData = {
        keyword: keywords,
        trend_score: hypeIndex,
        market_size: Math.floor(Math.random() * 1000000), // TODO: Add real market size calculation
        competition_level: hypeIndex > 7 ? 'High' : hypeIndex > 4 ? 'Medium' : 'Low',
        sentiment_analysis: apiData.sentimentSpectrum || { positive: 0, negative: 0, neutral: 0 },
        key_themes: (apiData.keyThemes || []).map(theme => ({
          theme: theme.theme || 'Unknown',
          frequency: Math.floor(Math.random() * 100) + 50 // TODO: Add real frequency data
        })),
        top_mentions: apiData.top_mentions || [],
        user_personas: apiData.userPersonaSnapshot || [],
        opportunities: (apiData.actionableOpportunities || []).map(opp => ({
          title: opp.opportunity || 'Unknown Opportunity',
          description: opp.description || 'No description available',
          impact: 'Medium', // TODO: Add impact scoring
          effort: 'Medium' // TODO: Add effort estimation
        })),
        trend_data: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
          datasets: [{
            label: 'Interest Over Time',
            data: [65, 72, 68, 85, 92, 88], // TODO: Add real trend data
            borderColor: 'rgb(34, 197, 94)',
            backgroundColor: 'rgba(34, 197, 94, 0.1)'
          }]
        },
        // Store the full API response for AnalysisResults component
        apiResponse: response.data
      };
      
      setKeywordAnalysisData(analysisData);
      
      // Auto-navigate to analysis section after completion
      const newUrl = `/workspace?section=analysis&keywords=${encodeURIComponent(keywords)}`;
      navigate(newUrl, { replace: false });
      setActiveSection('analysis');
      
      toast({
        title: "Analysis completed",
        description: `Analysis for "${keywords}" has been completed`,
      });
    } catch (error: any) {
      console.error('Analysis failed:', error);
      let errorMessage = "Please try again later";
      
      if (error.response?.status === 401) {
        errorMessage = "Please log in to perform analysis";
      } else if (error.response?.status === 403) {
        errorMessage = "Insufficient credits or subscription required";
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      }
      
      toast({
        title: "Analysis failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return (
          <div className="space-y-6">
            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card className="glass-card border-white/10">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-400">Total Analyses</p>
                      <p className="text-2xl font-bold text-white">
                        {dashboardData?.quick_stats.total_analyses || 0}
                      </p>
                    </div>
                    <BarChart3 className="w-8 h-8 text-cyan-400" />
                  </div>
                </CardContent>
              </Card>
              
              <Card className="glass-card border-white/10">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-400">Active Monitors</p>
                      <p className="text-2xl font-bold text-white">
                        {dashboardData?.quick_stats.active_monitors || 0}
                      </p>
                    </div>
                    <Eye className="w-8 h-8 text-green-400" />
                  </div>
                </CardContent>
              </Card>
              
              <Card className="glass-card border-white/10">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-400">Insights Generated</p>
                      <p className="text-2xl font-bold text-white">
                        {dashboardData?.quick_stats.insights_generated || 0}
                      </p>
                    </div>
                    <Lightbulb className="w-8 h-8 text-yellow-400" />
                  </div>
                </CardContent>
              </Card>
              
              <Card className="glass-card border-white/10">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-400">Success Rate</p>
                      <p className="text-2xl font-bold text-white">
                        {dashboardData?.quick_stats.success_rate || 0}%
                      </p>
                    </div>
                    <Target className="w-8 h-8 text-purple-400" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Keyword Analysis */}
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="text-white">Keyword Analysis</CardTitle>
                <CardDescription className="text-gray-300">
                  Enter keywords to analyze market trends
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex gap-2">
                    <Input
                      placeholder="Enter keywords..."
                      value={keywords}
                      onChange={(e) => setKeywords(e.target.value)}
                      className="flex-1 bg-white/10 border-white/20 text-white"
                    />
                    <Button 
                       onClick={handleAnalyze}
                       disabled={isAnalyzing || !canAnalyze}
                       className="bg-cyan-600 hover:bg-cyan-700"
                     >
                      {isAnalyzing ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        'Analyze'
                      )}
                    </Button>
                  </div>
                  
                  {user?.subscription_tier === 'free' && (
                    <div className="text-sm text-gray-400">
                      Remaining analyses: {remainingAnalyses}/3
                      {remainingAnalyses === 0 && (
                        <span className="text-red-400 ml-2">
                          Limit reached. Please upgrade to continue.
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* PMF Score */}
            {dashboardData && (
              <PMFScoreCard pmfScore={dashboardData.pmf_score} />
            )}
            
            {/* Analysis Results */}
            {keywordAnalysisData && (
              <AnalysisResults data={keywordAnalysisData} />
            )}
          </div>
        );
      
      case 'analysis':
        return (
          <div className="space-y-6">
            {keywordAnalysisData ? (
              <AnalysisResults data={keywordAnalysisData} />
            ) : (
              <Card className="glass-card border-white/10">
                <CardContent className="p-8 text-center">
                  <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-white mb-2">No Analysis Data</h3>
                  <p className="text-gray-400 mb-4">
                    Start a keyword analysis from the Dashboard to see results here.
                  </p>
                  <Button 
                    onClick={() => setActiveSection('dashboard')}
                    className="bg-cyan-600 hover:bg-cyan-700"
                  >
                    Go to Dashboard
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        );
      
      case 'pmf':
        return (
          <div className="space-y-6">
            <AutomatedPMFEvaluation />
            <PMFExplanation />
          </div>
        );
      
      case 'competitors':
        return (
          <div className="space-y-6">
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="text-white">Competitor Alerts</CardTitle>
                <CardDescription className="text-gray-300">
                  Monitor your competition
                </CardDescription>
              </CardHeader>
              <CardContent>
                {dashboardData?.competitor_alerts.map((alert) => (
                  <CompetitorAlert key={alert.id} alert={alert} />
                )) || <p className="text-gray-400">No alerts available</p>}
              </CardContent>
            </Card>
          </div>
        );
      
      case 'insights':
        return (
          <div className="space-y-6">
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="text-white">Business Insights</CardTitle>
                <CardDescription className="text-gray-300">
                  AI-powered recommendations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {dashboardData?.business_insights.map((insight) => (
                    <div key={insight.id} className="p-4 bg-white/5 rounded-lg">
                      <h3 className="font-semibold text-white">{insight.title}</h3>
                      <p className="text-gray-300 text-sm">{insight.description}</p>
                      <div className="flex gap-2 mt-2">
                        {insight.tags.map((tag) => (
                          <Badge key={tag} variant="secondary">{tag}</Badge>
                        ))}
                      </div>
                    </div>
                  )) || <p className="text-gray-400">No insights available</p>}
                </div>
              </CardContent>
            </Card>
          </div>
        );
      
      case 'reports':
        return <DataStudioIntegration />;
      
      case 'account':
        return (
          <div className="space-y-6">
            {/* User Center Content */}
            <div className="mb-8 flex items-start justify-between">
              <div>
                <h1 className="text-3xl font-bold mb-2 text-white">User Center</h1>
                <p className="text-gray-300">Manage your account, credits and subscriptions</p>
              </div>
              <Button variant="outline" onClick={() => window.location.reload()}>
                Refresh
              </Button>
            </div>

            <Tabs defaultValue="overview" className="space-y-6">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="overview" className="flex items-center gap-2">
                  <User className="w-4 h-4" />
                  Overview
                </TabsTrigger>
                <TabsTrigger value="credits" className="flex items-center gap-2">
                  <CreditCard className="w-4 h-4" />
                  Credit Management
                </TabsTrigger>
                <TabsTrigger value="history" className="flex items-center gap-2">
                  <History className="w-4 h-4" />
                  Transaction History
                </TabsTrigger>
                <TabsTrigger value="settings" className="flex items-center gap-2">
                  <Settings className="w-4 h-4" />
                  Account Settings
                </TabsTrigger>
              </TabsList>

              {/* Overview Tab */}
              <TabsContent value="overview" className="space-y-6">
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {/* Account Information */}
                  <Card className="glass-card border-white/10">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-white">
                        <User className="w-5 h-5" />
                        Account Information
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div>
                        <p className="text-sm text-gray-400">Username</p>
                        <p className="font-medium text-white">{user?.username || '—'}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-400">Email</p>
                        <p className="font-medium text-white">{user?.email || '—'}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-400">Current Plan</p>
                        <Badge variant="outline" className="mt-1">
                          {(user?.subscription_tier || 'free').toUpperCase()}
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Credit Balance */}
                  <Card className="glass-card border-white/10">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-white">
                        <CreditCard className="w-5 h-5 text-yellow-500" />
                        Credit Balance
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-center">
                        <p className="text-3xl font-bold text-primary mb-2">
                          {user?.credits_balance ?? 0}
                        </p>
                        <p className="text-sm text-gray-400">Available Credits</p>
                        <Button size="sm" className="mt-3">
                          Purchase Credits
                        </Button>
                        {(user?.credits_balance ?? 0) <= 0 && (
                          <div className="mt-4 bg-blue-50/10 border border-blue-200/20 text-blue-300 p-4 rounded">
                            Your credit balance is 0. Please purchase credits or subscribe to continue using advanced analysis features.
                            <div className="mt-3 flex gap-3 justify-center">
                              <Link to="/pricing" className="px-3 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700 text-sm">View Plans</Link>
                              <Link to="/credits" className="px-3 py-1.5 rounded bg-indigo-600 text-white hover:bg-indigo-700 text-sm">Buy Credits</Link>
                            </div>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Subscription Status */}
                  <Card className="glass-card border-white/10">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-white">
                        <Calendar className="w-5 h-5 text-blue-500" />
                        Subscription Status
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div>
                        <p className="text-sm text-gray-400">Plan Type</p>
                        <p className="font-medium text-white">{(user?.subscription_tier || 'free').toUpperCase()}</p>
                      </div>
                      {user?.subscription_expires_at && (
                        <div>
                          <p className="text-sm text-gray-400">Expiry Date</p>
                          <p className="font-medium text-white">
                            {new Date(user.subscription_expires_at).toLocaleDateString('en-US', {
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric'
                            })}
                          </p>
                        </div>
                      )}
                      <Button size="sm" variant="outline" className="w-full">
                        Manage Subscription
                      </Button>
                    </CardContent>
                  </Card>
                </div>

                {/* Usage Statistics */}
                <Card className="glass-card border-white/10">
                  <CardHeader>
                    <CardTitle className="text-white">Monthly Usage Statistics</CardTitle>
                    <CardDescription className="text-gray-400">Your analysis usage overview</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center">
                        <p className="text-2xl font-bold text-primary">12</p>
                        <p className="text-sm text-gray-400">Total Analyses</p>
                      </div>
                      <div className="text-center">
                        <p className="text-2xl font-bold text-green-500">8</p>
                        <p className="text-sm text-gray-400">Successful Analyses</p>
                      </div>
                      <div className="text-center">
                        <p className="text-2xl font-bold text-blue-500">3</p>
                        <p className="text-sm text-gray-400">PDF Reports</p>
                      </div>
                      <div className="text-center">
                        <p className="text-2xl font-bold text-orange-500">25</p>
                        <p className="text-sm text-gray-400">Credits Consumed</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Credits Tab */}
              <TabsContent value="credits">
                <CreditsPurchase 
                  currentBalance={user?.credits_balance ?? 0}
                  userTier={user?.subscription_tier || 'free'}
                />
              </TabsContent>

              {/* Transaction History Tab */}
              <TabsContent value="history" className="space-y-6">
                <Card className="glass-card border-white/10">
                  <CardHeader>
                    <CardTitle className="text-white">Credit Transaction History</CardTitle>
                    <CardDescription className="text-gray-400">View all your credit transaction records</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {[
                        {
                          id: '1',
                          type: 'consumption',
                          amount: -2,
                          description: 'Analysis: advanced_analysis',
                          date: '2025-08-24T10:30:00Z',
                          status: 'completed'
                        },
                        {
                          id: '2',
                          type: 'purchase',
                          amount: 30,
                          description: 'Credit package purchase: medium',
                          date: '2025-08-23T15:45:00Z',
                          status: 'completed'
                        },
                        {
                          id: '3',
                          type: 'subscription',
                          amount: 15,
                          description: 'Monthly credits reset: starter',
                          date: '2025-08-01T00:00:00Z',
                          status: 'completed'
                        }
                      ].map((transaction) => (
                        <div key={transaction.id} className="flex items-center justify-between p-4 border border-white/10 rounded-lg">
                          <div className="flex items-center gap-3">
                            {transaction.type === 'consumption' ? (
                              <TrendingUp className="w-4 h-4 text-red-500" />
                            ) : transaction.type === 'purchase' ? (
                              <CreditCard className="w-4 h-4 text-green-500" />
                            ) : (
                              <Calendar className="w-4 h-4 text-blue-500" />
                            )}
                            <div>
                              <p className="font-medium text-white">{transaction.description}</p>
                              <p className="text-sm text-gray-400">
                                {new Date(transaction.date).toLocaleDateString('en-US', {
                                  year: 'numeric',
                                  month: 'long',
                                  day: 'numeric'
                                })}
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className={`font-bold ${
                              transaction.amount > 0 ? 'text-green-500' : 'text-red-500'
                            }`}>
                              {transaction.amount > 0 ? '+' : ''}{transaction.amount} Credits
                            </p>
                            <Badge variant={transaction.status === 'completed' ? 'default' : 'secondary'}>
                              {transaction.status === 'completed' ? 'Completed' : 'Processing'}
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                    
                    <div className="mt-6 text-center">
                      <Button variant="outline" className="gap-2">
                        <Download className="w-4 h-4" />
                        Export Transaction Records
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Account Settings Tab */}
              <TabsContent value="settings" className="space-y-6">
                <Card className="glass-card border-white/10">
                  <CardHeader>
                    <CardTitle className="text-white">Account Settings</CardTitle>
                    <CardDescription className="text-gray-400">Manage your personal information and preferences</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div>
                      <h3 className="text-lg font-semibold mb-3 text-white">Personal Information</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="text-sm font-medium text-gray-400">Username</label>
                          <p className="mt-1 p-2 border border-white/10 rounded bg-white/5 text-white">{user?.username || '—'}</p>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-gray-400">Email Address</label>
                          <p className="mt-1 p-2 border border-white/10 rounded bg-white/5 text-white">{user?.email || '—'}</p>
                        </div>
                      </div>
                      <Button className="mt-4" variant="outline">
                        Edit Personal Information
                      </Button>
                    </div>

                    <div>
                      <h3 className="text-lg font-semibold mb-3 text-white">Notification Settings</h3>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-white">Analysis Completion Notifications</span>
                          <Button variant="outline" size="sm">Enabled</Button>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-white">Monthly Reports</span>
                          <Button variant="outline" size="sm">Enabled</Button>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-white">Promotional Notifications</span>
                          <Button variant="outline" size="sm">Enabled</Button>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-lg font-semibold mb-3 text-white">Security Settings</h3>
                      <div className="space-y-3">
                        <Button variant="outline">
                          Change Password
                        </Button>
                        <Button variant="outline">
                          Two-Factor Authentication
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        );
      
      default:
        return <div className="text-white">Content not found</div>;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="flex">
        {/* Sidebar */}
        <div className={cn(
          "fixed left-0 top-0 h-full bg-black/20 backdrop-blur-sm border-r border-white/10 transition-all duration-300 z-50",
          sidebarOpen ? "w-64" : "w-16"
        )}>
          <div className="p-4">
            <div className="flex items-center justify-between mb-8">
              <h1 className={cn(
                "font-bold text-white transition-opacity duration-300",
                sidebarOpen ? "opacity-100" : "opacity-0"
              )}>
                IdeaEden
              </h1>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="text-white hover:bg-white/10"
              >
                {sidebarOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
              </Button>
            </div>
            
            <nav className="space-y-2">
              {sidebarItems.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.id}
                    onClick={() => {
                      const newUrl = `/workspace?section=${item.id}`;
                      navigate(newUrl, { replace: false });
                      setActiveSection(item.id);
                    }}
                    className={cn(
                      "w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors",
                      activeSection === item.id
                        ? "bg-cyan-600/20 text-cyan-400 border border-cyan-500/30"
                        : "text-gray-300 hover:bg-white/10 hover:text-white"
                    )}
                  >
                    <Icon className="w-5 h-5 flex-shrink-0" />
                    {sidebarOpen && (
                      <div className="text-left">
                        <div className="font-medium">{item.label}</div>
                        <div className="text-xs opacity-70">{item.description}</div>
                      </div>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <div className={cn(
          "flex-1 transition-all duration-300",
          sidebarOpen ? "ml-64" : "ml-16"
        )}>
          <div className="p-6">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-3xl font-bold text-white mb-2">
                  {sidebarItems.find(item => item.id === activeSection)?.label || 'Dashboard'}
                </h1>
                <p className="text-gray-300">
                  {sidebarItems.find(item => item.id === activeSection)?.description || 'Overview and key metrics'}
                </p>
              </div>
              
              <Button
                onClick={refreshData}
                disabled={refreshing}
                variant="outline"
                className="border-white/20 text-white hover:bg-white/10"
              >
                <RefreshCw className={cn("w-4 h-4 mr-2", refreshing && "animate-spin")} />
                Refresh
              </Button>
            </div>
            
            {loading ? (
              <div className="space-y-6">
                <Skeleton className="h-32 bg-white/10" />
                <Skeleton className="h-48 bg-white/10" />
                <Skeleton className="h-64 bg-white/10" />
              </div>
            ) : (
              renderContent()
            )}
          </div>
        </div>
      </div>
    </div>
  );
}