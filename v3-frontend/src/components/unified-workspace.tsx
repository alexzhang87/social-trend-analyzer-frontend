import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Input } from '@/components/ui/input';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { 
  BarChart3, 
  Target, 
  Users, 
  TrendingUp, 
  Zap,
  Brain,
  Rocket,
  Star,
  Clock,
  CheckCircle,
  ArrowRight,
  Plus,
  History,
  BookOpen,
  Settings,
  HelpCircle,
  Search,
  Home,
  FileText,
  Lightbulb,
  AlertTriangle,
  Sparkles,
  Menu,
  User,
  Download,
  Share2,
  Filter,
  Calendar,
  ChevronDown,
  ChevronRight,
  Eye,
  Edit,
  Trash2,
  MoreHorizontal,
  AlertCircle,
  RefreshCw,
  ExternalLink,
  Leaf,
  Send
} from 'lucide-react';
import { useAuth } from '@/components/auth-provider';
import { CanvaSidebar } from './canva-sidebar';
import { DualTrackAnalysis } from './dual-track-analysis';
import { QuickValidation } from './quick-validation';
import { ProfessionalAnalysis } from './professional-analysis';
import { PMFScoreCard } from './pmf-scorecard';
import { AnalysisSelection } from './analysis-selection';
import { CompetitorAlert } from './competitor-alert';
import { useAIInsights, type DashboardData, type MarketIntelligence, type StrategicRecommendations } from '@/services/aiInsightsApi';

type WorkspaceView = 'home' | 'analysis-selection' | 'quick-results' | 'professional-results';
type SidebarSection = 'dashboard' | 'history' | 'competitors' | 'reports' | 'templates' | 'settings' | 'help' | 'account';

interface AnalysisHistory {
  id: string;
  keyword: string;
  type: 'quick' | 'professional';
  score: number;
  date: string;
  status: 'completed' | 'in-progress';
}

interface UserStats {
  totalAnalyses: number;
  creditsUsed: number;
  creditsRemaining: number;
  averageScore: number;
}

export function UnifiedWorkspace() {
  const [activeSection, setActiveSection] = useState<SidebarSection>('dashboard');

  const [currentView, setCurrentView] = useState<WorkspaceView>('home');
  const [currentKeyword, setCurrentKeyword] = useState('');
  const [currentMode, setCurrentMode] = useState<'quick' | 'professional' | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [userStats, setUserStats] = useState<UserStats>({
    totalAnalyses: 45,
    creditsUsed: 38,
    creditsRemaining: 62,
    averageScore: 86
  });
  const [analysisHistory, setAnalysisHistory] = useState<AnalysisHistory[]>([]);
  const [showAllHistory, setShowAllHistory] = useState(false);
  const [chartData, setChartData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // AI Insights related state
  const [aiInsightsData, setAiInsightsData] = useState<DashboardData | null>(null);
  const [aiInsightsLoading, setAiInsightsLoading] = useState(false);
  const [aiInsightsError, setAiInsightsError] = useState<string | null>(null);
  
  const { user } = useAuth();
  
  // AI Insights API hooks
  const aiInsights = useAIInsights();

  // Get time greeting
  const getTimeGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  // Chat related state
  const [inputValue, setInputValue] = useState('');

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;
    
    // Add message sending logic here
    console.log('Sending message:', inputValue.trim());
    setInputValue('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  useEffect(() => {
    if (user) {
      fetchUserData();
    }
  }, [user]);

  const fetchUserData = async () => {
    try {
      // Fetch user stats and history
      // This would be replaced with actual API calls
      const mockStats: UserStats = {
        totalAnalyses: 45,
        creditsUsed: 38,
        creditsRemaining: 62,
        averageScore: 86
      };

      const mockHistory: AnalysisHistory[] = [
        {
          id: '1',
          keyword: 'AI Writing Assistant',
          type: 'professional',
          score: 95,
          date: '2024-12-15',
          status: 'completed'
        },
        {
          id: '2',
          keyword: 'Sustainable Fashion Brand',
          type: 'quick',
          score: 88,
          date: '2024-12-14',
          status: 'completed'
        },
        {
          id: '3',
          keyword: 'Smart Fitness App',
          type: 'professional',
          score: 92,
          date: '2024-12-13',
          status: 'completed'
        },
        {
          id: '4',
          keyword: 'Online Education Platform',
          type: 'quick',
          score: 78,
          date: '2024-12-12',
          status: 'completed'
        },
        {
          id: '5',
          keyword: 'Bike Sharing Service',
          type: 'professional',
          score: 82,
          date: '2024-12-11',
          status: 'completed'
        },
        {
          id: '6',
          keyword: 'Smart Home System',
          type: 'quick',
          score: 89,
          date: '2024-12-10',
          status: 'completed'
        },
        {
          id: '7',
          keyword: 'Blockchain Wallet',
          type: 'professional',
          score: 76,
          date: '2024-12-09',
          status: 'completed'
        },
        {
          id: '8',
          keyword: 'Short Video Creation Tool',
          type: 'quick',
          score: 91,
          date: '2024-12-08',
          status: 'completed'
        }
      ];

      // Mock chart data for performance analytics
      const chartData = [
    { name: 'Jan', score: 65, analyses: 8, marketValue: 45, engagement: 72 },
    { name: 'Feb', score: 72, analyses: 12, marketValue: 58, engagement: 78 },
    { name: 'Mar', score: 78, analyses: 15, marketValue: 62, engagement: 85 },
    { name: 'Apr', score: 85, analyses: 18, marketValue: 75, engagement: 88 },
    { name: 'May', score: 82, analyses: 22, marketValue: 71, engagement: 82 },
    { name: 'Jun', score: 88, analyses: 25, marketValue: 85, engagement: 92 },
    { name: 'Jul', score: 91, analyses: 28, marketValue: 89, engagement: 95 },
    { name: 'Aug', score: 87, analyses: 32, marketValue: 82, engagement: 89 },
    { name: 'Sep', score: 93, analyses: 35, marketValue: 91, engagement: 97 },
    { name: 'Oct', score: 89, analyses: 38, marketValue: 87, engagement: 91 },
    { name: 'Nov', score: 95, analyses: 42, marketValue: 94, engagement: 98 },
    { name: 'Dec', score: 92, analyses: 45, marketValue: 90, engagement: 94 }
  ];

      setUserStats(mockStats);
      setAnalysisHistory(mockHistory);
      setChartData(chartData);
    } catch (error) {
      console.error('Failed to fetch user data:', error);
    }
  };

  const handleModeSelect = (mode: 'quick' | 'professional', keyword: string) => {
    setCurrentMode(mode);
    setCurrentKeyword(keyword);
    setIsAnalyzing(true);
    
    if (mode === 'quick') {
      setCurrentView('quick-results');
    } else {
      setCurrentView('professional-results');
    }
  };

  const handleNewAnalysis = () => {
    setCurrentView('analysis-selection');
    setCurrentMode(null);
    setCurrentKeyword('');
    setIsAnalyzing(false);
  };

  const handleUpgradeToProf = () => {
    setCurrentMode('professional');
    setCurrentView('professional-results');
  };

  const handleBackToHome = () => {
    setCurrentView('home');
    setCurrentMode(null);
    setCurrentKeyword('');
    setIsAnalyzing(false);
  };

  const handleSectionChange = (section: SidebarSection) => {
    setActiveSection(section);
    // Reset analysis view when changing sections
    if (section === 'analysis') {
      setCurrentView('analysis-selection');
    } else {
      setCurrentView('home');
    }
  };

  // 渲染功能按钮
  const renderFeatureButtons = () => (
    <motion.div 
      initial={{ opacity: 0, y: 20 }} 
      animate={{ opacity: 1, y: 0 }} 
      transition={{ delay: 0.4 }}
      className="w-full max-w-2xl mx-auto mt-6"
    >
      <div className="flex gap-2 justify-center flex-wrap">
        <button 
          onClick={() => handleFeatureClick('keyword-analysis')}
          className="flex items-center gap-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors"
        >
          <span>🔍</span>
          <span>Keyword Analysis</span>
        </button>
        <button 
          onClick={() => handleFeatureClick('pmf-evaluation')}
          className="flex items-center gap-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors"
        >
          <span>🎯</span>
          <span>PMF Evaluation</span>
        </button>
        <button 
          onClick={() => handleFeatureClick('market-dashboard')}
          className="flex items-center gap-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors"
        >
          <span>📊</span>
          <span>Market Dashboard</span>
        </button>
        <button 
          onClick={() => handleFeatureClick('analysis-reports')}
          className="flex items-center gap-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors"
        >
          <span>📈</span>
          <span>Analysis Reports</span>
        </button>
      </div>
    </motion.div>
  );

  // 处理功能按钮点击事件
  const handleFeatureClick = (feature: string) => {
    switch (feature) {
      case 'keyword-analysis':
        setActiveSection('analysis');
        setCurrentView('analysis-selection');
        break;
      case 'pmf-evaluation':
        setActiveSection('insights');
        break;
      case 'market-dashboard':
        setActiveSection('dashboard');
        break;
      case 'analysis-reports':
        setActiveSection('history');
        break;
      default:
        break;
    }
  };

  // Load AI Insights data
  const loadAIInsightsData = async () => {
    setAiInsightsLoading(true);
    setAiInsightsError(null);
    try {
      const data = await aiInsights.getDashboardData();
      setAiInsightsData(data);
    } catch (error) {
      console.error('Failed to load AI insights data:', error);
      setAiInsightsError('Failed to load AI insights data, please try again later');
    } finally {
      setAiInsightsLoading(false);
    }
  };

  // Refresh AI Insights data
  const refreshAIInsights = async (keyword?: string) => {
    setIsLoading(true);
    try {
      await aiInsights.refreshInsights(keyword);
      await loadAIInsightsData(); // Reload data
    } catch (error) {
      console.error('Failed to refresh AI insights data:', error);
      setAiInsightsError('Failed to refresh data, please try again later');
    } finally {
      setIsLoading(false);
    }
  };

  // Load data when switching to insights view
  useEffect(() => {
    if (activeSection === 'insights' && !aiInsightsData && !aiInsightsLoading) {
      loadAIInsightsData();
    }
  }, [activeSection]);



  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const renderHomeView = () => (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      {/* Welcome Header */}
      <div className="text-center space-y-4">
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Your unified platform for market validation and business insights. 
          Discover opportunities, validate ideas, and make data-driven decisions.
        </p>
        
        {/* Platform Overview */}
        <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          <Card className="bg-gradient-to-br from-blue-50 to-indigo-100 border-blue-200 hover:shadow-lg transition-all duration-300">
            <CardContent className="p-6 text-center">
              <div className="p-3 bg-blue-500 rounded-xl w-fit mx-auto mb-3">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-blue-900 mb-1">Market Analysis</h3>
              <p className="text-sm text-blue-700">Real-time market insights</p>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-green-50 to-emerald-100 border-green-200 hover:shadow-lg transition-all duration-300">
            <CardContent className="p-6 text-center">
              <div className="p-3 bg-green-500 rounded-xl w-fit mx-auto mb-3">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-green-900 mb-1">AI Insights</h3>
              <p className="text-sm text-green-700">Intelligent recommendations</p>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-purple-50 to-violet-100 border-purple-200 hover:shadow-lg transition-all duration-300">
            <CardContent className="p-6 text-center">
              <div className="p-3 bg-purple-500 rounded-xl w-fit mx-auto mb-3">
                <Rocket className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-purple-900 mb-1">Validation Engine</h3>
              <p className="text-sm text-purple-700">Idea validation tools</p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6 text-center">
            <BarChart3 className="w-8 h-8 text-blue-500 mx-auto mb-2" />
            <div className="text-2xl font-bold">{userStats.totalAnalyses}</div>
            <p className="text-gray-600 text-sm">Total Analyses</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6 text-center">
            <Zap className="w-8 h-8 text-yellow-500 mx-auto mb-2" />
            <div className="text-2xl font-bold">{userStats.creditsRemaining}</div>
            <p className="text-gray-600 text-sm">Credits Remaining</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6 text-center">
            <Target className="w-8 h-8 text-green-500 mx-auto mb-2" />
            <div className={`text-2xl font-bold ${getScoreColor(userStats.averageScore)}`}>
              {userStats.averageScore}
            </div>
            <p className="text-gray-600 text-sm">Average Score</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6 text-center">
            <TrendingUp className="w-8 h-8 text-purple-500 mx-auto mb-2" />
            <div className="text-2xl font-bold">{userStats.creditsUsed}</div>
            <p className="text-gray-600 text-sm">Credits Used</p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Analyses */}
      <div className="grid md:grid-cols-1 gap-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <History className="w-6 h-6 text-green-500" />
              Recent Analyses
            </CardTitle>
            <CardDescription>
              Your latest market validation results
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {analysisHistory.slice(0, 3).map((analysis) => (
                <div key={analysis.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-sm">{analysis.keyword}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="outline" className="text-xs">
                        {analysis.type}
                      </Badge>
                      <span className="text-xs text-gray-500">{analysis.date}</span>
                    </div>
                  </div>
                  <div className={`text-lg font-bold ${getScoreColor(analysis.score)}`}>
                    {analysis.score}
                  </div>
                </div>
              ))}
            </div>
            <Button variant="outline" className="w-full mt-4">
              View All History
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Feature Highlights */}
      <div className="grid md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6 text-center">
            <Zap className="w-12 h-12 text-blue-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Quick Validation</h3>
            <p className="text-gray-600 text-sm">
              Get instant market feedback in just 2 minutes with basic insights and trend analysis.
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6 text-center">
            <Brain className="w-12 h-12 text-purple-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Professional Analysis</h3>
            <p className="text-gray-600 text-sm">
              Deep market research with competitor analysis, user personas, and business opportunities.
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6 text-center">
            <Target className="w-12 h-12 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Actionable Insights</h3>
            <p className="text-gray-600 text-sm">
              Get specific recommendations and next steps to turn your ideas into successful products.
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Getting Started Guide */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-blue-600" />
            Getting Started
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                1
              </div>
              <div>
                <h4 className="font-semibold">Choose Your Path</h4>
                <p className="text-sm text-gray-600">
                  Select Quick Validation for fast insights or Professional Analysis for deep research.
                </p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                2
              </div>
              <div>
                <h4 className="font-semibold">Enter Your Idea</h4>
                <p className="text-sm text-gray-600">
                  Input your product keyword or business idea for comprehensive market analysis.
                </p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                3
              </div>
              <div>
                <h4 className="font-semibold">Get Insights</h4>
                <p className="text-sm text-gray-600">
                  Receive detailed reports with actionable recommendations for your business.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderAnalysisSelection = () => (
    <DualTrackAnalysis 
      onModeSelect={handleModeSelect}
      isLoading={isAnalyzing}
    />
  );

  const renderQuickResults = () => (
    <QuickValidation 
      keyword={currentKeyword}
      onUpgrade={handleUpgradeToProf}
      onNewAnalysis={handleNewAnalysis}
    />
  );

  const renderProfessionalResults = () => (
    <ProfessionalAnalysis 
      keyword={currentKeyword}
      onNewAnalysis={handleNewAnalysis}
    />
  );

  const renderDashboardView = () => {
    switch (currentView) {
      case 'analysis-selection':
        return (
          <AnalysisSelection
            onModeSelect={handleModeSelect}
            isLoading={isAnalyzing}
            defaultKeyword={currentKeyword}
          />
        );
      case 'quick-results':
        return (
          <QuickValidation
            keyword={currentKeyword}
            onUpgrade={() => handleModeSelect('professional', currentKeyword)}
          />
        );
      case 'professional-results':
        return (
          <ProfessionalAnalysis
            keyword={currentKeyword}
          />
        );
      default:
        return (
          <div className="min-h-[calc(100vh-200px)] flex flex-col items-center justify-center space-y-8">
            {/* Welcome Message */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center space-y-4"
            >
              <div>
                <h1 className="text-5xl font-bold text-gray-900 mb-4">AI Expert</h1>
              </div>
              <p className="text-gray-600 text-lg">Enter your idea or product for professional market validation analysis</p>
            </motion.div>

            {/* Central Chat Box */}
            <motion.div 
              initial={{ opacity: 0, y: 30 }} 
              animate={{ opacity: 1, y: 0 }} 
              transition={{ delay: 0.2 }} 
              className="w-full max-w-2xl mx-auto" 
            > 
              <div className="relative">
                <textarea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Message AI Expert..."
                  className="w-full px-6 py-4 pr-14 border border-gray-300 rounded-3xl resize-none focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all duration-200 text-gray-900 placeholder-gray-500 shadow-sm text-lg"
                  rows={1}
                  style={{ 
                    minHeight: '56px', 
                    maxHeight: '120px',
                    fontSize: '18px',
                    lineHeight: '1.5'
                  }}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isLoading}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-400 text-white rounded-full flex items-center justify-center hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed w-10 h-10"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </motion.div>

            {/* Feature Buttons */}
            {renderFeatureButtons()}
          </div>
        );
    }
  };

  const renderHistoryView = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analysis History</h1>
          <p className="text-gray-600 mt-2">View your previous market analyses and results</p>
        </div>
        <Button variant="outline" className="flex items-center gap-2">
          <Search className="w-4 h-4" />
          Search History
        </Button>
      </div>

      {/* Analysis History List */}
      <div className="space-y-4">
        {analysisHistory.map((analysis) => (
          <Card key={analysis.id} className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      analysis.type === 'professional' 
                        ? 'bg-purple-100 text-purple-600' 
                        : 'bg-blue-100 text-blue-600'
                    }`}>
                      {analysis.type === 'professional' ? <Brain className="w-5 h-5" /> : <Search className="w-5 h-5" />}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{analysis.keyword}</h3>
                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        <span>{analysis.date}</span>
                        <span>•</span>
                        <Badge variant={analysis.type === 'professional' ? 'default' : 'secondary'}>
                          {analysis.type === 'professional' ? 'Professional Analysis' : 'Quick Validation'}
                        </Badge>
                        <span>•</span>
                        <Badge variant={analysis.status === 'completed' ? 'outline' : 'secondary'}>
                          {analysis.status}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className={`text-lg font-bold ${
                    analysis.score >= 90 ? 'text-green-600' :
                    analysis.score >= 80 ? 'text-blue-600' :
                    analysis.score >= 70 ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {analysis.score}
                  </div>
                  <Button variant="ghost" size="sm">
                    <Eye className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Load More */}
      <div className="text-center">
        <Button variant="outline" className="w-full max-w-md">
          Load More Analyses
        </Button>
      </div>
    </motion.div>
  );

  const renderAnalysisView = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8"
    >
      {/* Simple Keyword Input */}
      <Card className="border-2 border-gray-200 hover:border-gray-300 transition-colors">
        <CardContent className="p-6">
          <div className="max-w-2xl mx-auto">
            <div className="relative">
              <Input
                type="text"
                placeholder="Enter your startup idea or keyword"
                value={currentKeyword}
                onChange={(e) => setCurrentKeyword(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && currentKeyword.trim()) {
                    setCurrentView('analysis-selection');
                  }
                }}
                className="w-full h-12 pl-4 pr-24 text-base border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              />
              <Button
                onClick={() => {
                  if (currentKeyword.trim()) {
                    setCurrentView('analysis-selection');
                  }
                }}
                disabled={!currentKeyword.trim()}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-blue-600 hover:bg-blue-700 text-white font-medium h-8 px-4 rounded-md transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Search className="w-4 h-4 mr-1" />
                Analyze
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Dual Track Analysis Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Quick Validation Card */}
        <Card className="relative group cursor-pointer transform transition-all duration-300 hover:scale-105 hover:shadow-xl border-2 border-blue-200 hover:border-blue-400">
          <CardContent className="p-8">
            <div className="absolute top-4 right-4">
              <Badge className="bg-blue-100 text-blue-800 hover:bg-blue-200">
                <Zap className="w-3 h-3 mr-1" />
                Quick
              </Badge>
            </div>
            
            <div className="flex items-center mb-6">
              <div className="p-3 rounded-xl bg-blue-100 mr-4">
                <Zap className="w-8 h-8 text-blue-600" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-gray-900">Quick Validation</h3>
                <p className="text-gray-600">Instant Market Check</p>
              </div>
            </div>
            
            <p className="text-gray-700 mb-6">
              Validate your idea in 30 seconds with AI-powered insights
            </p>
            
            <div className="space-y-3 mb-6">
              {[
                'One-click analysis',
                'Market demand score',
                'Trend momentum',
                'Competition level',
                'Instant recommendations'
              ].map((feature, idx) => (
                <div key={idx} className="flex items-center text-gray-600">
                  <CheckCircle className="w-4 h-4 text-green-500 mr-3" />
                  <span className="text-sm">{feature}</span>
                </div>
              ))}
            </div>
            
            <div className="bg-blue-50 rounded-lg p-4 mb-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Clock className="w-4 h-4 mr-2 text-blue-600" />
                  <span className="text-blue-800 font-medium">30 seconds</span>
                </div>
                <div className="text-blue-800 font-semibold">1 Credit</div>
              </div>
            </div>

            <Button
              onClick={() => handleModeSelect('quick', currentKeyword || 'market analysis')}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
              disabled={isAnalyzing}
            >
              {isAnalyzing && currentMode === 'quick' ? (
                <>
                  <Brain className="w-4 h-4 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  Start Quick Analysis
                  <ArrowRight className="w-4 h-4 ml-2" />
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Professional Analysis Card */}
        <Card className="relative group cursor-pointer transform transition-all duration-300 hover:scale-105 hover:shadow-xl border-2 border-purple-200 hover:border-purple-400">
          <CardContent className="p-8">
            
            <div className="flex items-center mb-6">
              <div className="p-3 rounded-xl bg-purple-100 mr-4">
                <Target className="w-8 h-8 text-purple-600" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-gray-900">Professional Analysis</h3>
                <p className="text-gray-600">Complete Market Intelligence</p>
              </div>
            </div>
            
            <p className="text-gray-700 mb-6">
              In-depth analysis providing actionable business insights
            </p>
            
            <div className="space-y-3 mb-6">
              {[
                'Multi-source Data Integration',
                'PMF Assessment Scoring',
                'Competitive Landscape Mapping',
                'User Persona Analysis',
                'Revenue Opportunity Assessment',
                'Strategic Recommendations'
              ].map((feature, idx) => (
                <div key={idx} className="flex items-center text-gray-600">
                  <CheckCircle className="w-4 h-4 text-green-500 mr-3" />
                  <span className="text-sm">{feature}</span>
                </div>
              ))}
            </div>
            
            <div className="bg-purple-50 rounded-lg p-4 mb-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Clock className="w-4 h-4 mr-2 text-purple-600" />
                  <span className="text-purple-800 font-medium">2-5 minutes</span>
                </div>
                <div className="text-purple-800 font-semibold">3 Credits</div>
              </div>
            </div>

            <Button
              onClick={() => handleModeSelect('professional', currentKeyword || 'market analysis')}
              className="w-full bg-purple-600 hover:bg-purple-700 text-white"
              disabled={isAnalyzing}
            >
              {isAnalyzing && currentMode === 'professional' ? (
                <>
                  <Brain className="w-4 h-4 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  Start Professional Analysis
                  <ArrowRight className="w-4 h-4 ml-2" />
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6 text-center">
            <div className="text-2xl font-bold text-blue-600 mb-2">{userStats.creditsRemaining}</div>
            <div className="text-sm text-gray-600">Credits Remaining</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 text-center">
            <div className="text-2xl font-bold text-green-600 mb-2">{userStats.totalAnalyses}</div>
            <div className="text-sm text-gray-600">Total Analyses</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 text-center">
            <div className="text-2xl font-bold text-purple-600 mb-2">{userStats.averageScore.toFixed(1)}</div>
            <div className="text-sm text-gray-600">Average PMF Score</div>
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );

  const renderPMFView = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Product-Market Fit Scorecard</h2>
        <p className="text-gray-600">
          Evaluate your product-market fit with comprehensive metrics and get actionable insights
        </p>
      </div>
      <PMFScoreCard />
    </motion.div>
  );

  const renderInsightsView = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">AI-Powered Insights</h2>
        <p className="text-gray-600 mb-4">
          Based on keyword analysis data, AI provides intelligent business advice and strategic insights
        </p>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Lightbulb className="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <h4 className="font-semibold text-blue-900 mb-1">Difference from Keyword Analysis</h4>
              <p className="text-sm text-blue-700">
                <strong>Keyword Analysis</strong>: Provides search data, competition level and basic information → 
                <strong>AI Insights</strong>: Generates strategic recommendations, market opportunities and business decision support based on this data
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Error State */}
      {aiInsightsError && (
        <Alert className="border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-700">
            {aiInsightsError}
          </AlertDescription>
        </Alert>
      )}
      
      {/* AI Insights Dashboard */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-purple-600" />
              Market Intelligence
            </CardTitle>
            <div className="flex gap-2">
              <Button 
                variant="ghost" 
                size="sm"
                onClick={refreshAIInsights}
                disabled={aiInsightsLoading}
              >
                <RefreshCw className={`w-4 h-4 ${aiInsightsLoading ? 'animate-spin' : ''}`} />
              </Button>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => setSelectedMode('professional')}
              >
                <ExternalLink className="w-4 h-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {aiInsightsLoading ? (
              <div className="space-y-4">
                <div className="animate-pulse">
                  <div className="h-20 bg-gray-200 rounded-lg mb-4"></div>
                  <div className="h-20 bg-gray-200 rounded-lg mb-4"></div>
                  <div className="h-8 bg-gray-200 rounded-lg"></div>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {aiInsightsData?.marketIntelligence?.trends?.map((trend, index) => (
                  <div key={index} className="p-4 bg-purple-50 rounded-lg cursor-pointer hover:bg-purple-100 transition-colors"
                       onClick={() => {
                         setCurrentView('analysis');
                         setCurrentKeyword(trend.keyword);
                         setCurrentMode('professional');
                       }}>
                    <div className="flex items-start gap-3">
                      <Sparkles className="w-5 h-5 text-purple-600 mt-1" />
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <h4 className="font-semibold text-purple-900">{trend.title}</h4>
                          <span className="text-xs text-purple-600 bg-purple-200 px-2 py-1 rounded">
                            {trend.growth > 0 ? '+' : ''}{trend.growth}%
                          </span>
                        </div>
                        <p className="text-sm text-purple-700 mt-1">
                          {trend.description}
                        </p>
                        <div className="flex items-center gap-4 mt-2 text-xs text-purple-600">
                          <span>📊 Search Volume: {trend.searchVolume}</span>
                          <span>💰 Market Size: {trend.marketSize}</span>
                          <span className="text-purple-800 font-medium cursor-pointer hover:underline">→ Click for detailed analysis</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}

                <div className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Market Intelligence Score</span>
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-purple-500 to-blue-500"
                          style={{ width: `${(aiInsightsData?.marketIntelligence?.score || 0) * 10}%` }}
                        ></div>
                      </div>
                      <span className="font-semibold text-gray-900">
                        {aiInsightsData?.marketIntelligence?.score || 0}/10
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Target className="w-5 h-5 text-green-600" />
              Strategic Recommendations
            </CardTitle>
            <div className="flex gap-2">
              <Button 
                variant="ghost" 
                size="sm"
                onClick={refreshAIInsights}
                disabled={aiInsightsLoading}
              >
                <Sparkles className={`w-4 h-4 ${aiInsightsLoading ? 'animate-pulse' : ''}`} />
              </Button>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => setSelectedMode('pmf')}
              >
                <ExternalLink className="w-4 h-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {aiInsightsLoading ? (
              <div className="space-y-4">
                <div className="animate-pulse">
                  <div className="h-20 bg-gray-200 rounded-lg mb-4"></div>
                  <div className="h-20 bg-gray-200 rounded-lg mb-4"></div>
                  <div className="h-8 bg-gray-200 rounded-lg"></div>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {aiInsightsData?.strategicRecommendations?.recommendations?.map((rec, index) => {
                  const priorityColors = {
                    high: 'green',
                    medium: 'orange',
                    low: 'blue'
                  };
                  const color = priorityColors[rec.priority] || 'blue';
                  
                  return (
                    <div key={index} className={`p-4 bg-${color}-50 rounded-lg cursor-pointer hover:bg-${color}-100 transition-colors`}
                         onClick={() => {
                           if (rec.type === 'product') {
                             setCurrentView('pmf');
                             setActiveSection('pmf');
                           } else {
                             setCurrentView('analysis');
                             setCurrentKeyword(rec.title);
                             setCurrentMode('professional');
                           }
                         }}>
                      <div className="flex items-start gap-3">
                        {rec.type === 'product' && <CheckCircle className={`w-5 h-5 text-${color}-600 mt-1`} />}
                        {rec.type === 'risk' && <AlertTriangle className={`w-5 h-5 text-${color}-600 mt-1`} />}
                        {rec.type === 'opportunity' && <Lightbulb className={`w-5 h-5 text-${color}-600 mt-1`} />}
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <h4 className={`font-semibold text-${color}-900`}>{rec.title}</h4>
                            <span className={`text-xs text-${color}-600 bg-${color}-200 px-2 py-1 rounded`}>
                              {rec.priority === 'high' ? 'High Priority' : 
                               rec.priority === 'medium' ? 'Monitor' : 'New'}
                            </span>
                          </div>
                          <p className={`text-sm text-${color}-700 mt-1`}>
                            {rec.description}
                          </p>
                          <div className={`flex items-center gap-4 mt-2 text-xs text-${color}-600`}>
                            <span>⚡ Impact: {rec.impact}</span>
                            <span>⏰ Timeline: {rec.timeline}</span>
                            <span className={`text-${color}-800 font-medium cursor-pointer hover:underline`}>
                              → View {rec.type} analysis
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}

                <div className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Recommendations Relevance</span>
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-green-500 to-blue-500"
                          style={{ width: `${(aiInsightsData?.strategicRecommendations?.relevanceScore || 0) * 10}%` }}
                        ></div>
                      </div>
                      <span className="font-semibold text-gray-900">
                        {aiInsightsData?.strategicRecommendations?.relevanceScore || 0}/10
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* AI Analysis Tools */}
      <Card>
        <CardHeader>
          <CardTitle>AI Analysis Tools</CardTitle>
          <CardDescription>Leverage AI to analyze your business data and market trends</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button 
              variant="outline" 
              className="h-auto p-4 flex flex-col items-center gap-2 hover:bg-blue-50 hover:border-blue-300 transition-all"
              onClick={() => setSelectedMode('keyword')}
            >
              <Brain className="w-8 h-8 text-blue-600" />
              <div className="text-center">
                <div className="font-semibold">Sentiment Analysis</div>
                <div className="text-xs text-gray-600">Analyze customer feedback</div>
                <div className="text-xs text-blue-600 mt-1 font-medium cursor-pointer hover:underline">Click to analyze →</div>
              </div>
            </Button>
            
            <Button 
              variant="outline" 
              className="h-auto p-4 flex flex-col items-center gap-2 hover:bg-green-50 hover:border-green-300 transition-all"
              onClick={() => setSelectedMode('automated')}
            >
              <TrendingUp className="w-8 h-8 text-green-600" />
              <div className="text-center">
                <div className="font-semibold">Trend Prediction</div>
                <div className="text-xs text-gray-600">Forecast market trends</div>
                <div className="text-xs text-green-600 mt-1 font-medium cursor-pointer hover:underline">Click to predict →</div>
              </div>
            </Button>
            
            <Button 
              variant="outline" 
              className="h-auto p-4 flex flex-col items-center gap-2 hover:bg-purple-50 hover:border-purple-300 transition-all"
              onClick={() => setSelectedMode('professional')}
            >
              <Target className="w-8 h-8 text-purple-600" />
              <div className="text-center">
                <div className="font-semibold">Opportunity Finder</div>
                <div className="text-xs text-gray-600">Discover new opportunities</div>
                <div className="text-xs text-purple-600 mt-1 font-medium cursor-pointer hover:underline">Click to discover →</div>
              </div>
            </Button>
          </div>

          {/* Quick Actions */}
          <div className="mt-6 pt-4 border-t border-gray-200">
            <h4 className="font-semibold text-gray-900 mb-3">Quick Actions</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <Button 
                variant="ghost" 
                size="sm" 
                className="justify-start"
                onClick={() => setSelectedMode('keyword')}
              >
                <Search className="w-4 h-4 mr-2" />
                Keyword Research
              </Button>
              <Button 
                variant="ghost" 
                size="sm" 
                className="justify-start"
                onClick={() => setSelectedMode('pmf')}
              >
                <BarChart3 className="w-4 h-4 mr-2" />
                PMF Analysis
              </Button>
              <Button 
                variant="ghost" 
                size="sm" 
                className="justify-start"
                onClick={() => setSelectedMode('competitors')}
              >
                <Users className="w-4 h-4 mr-2" />
                Competitor Intel
              </Button>
              <Button 
                variant="ghost" 
                size="sm" 
                className="justify-start"
                onClick={() => setSelectedMode('professional')}
              >
                <FileText className="w-4 h-4 mr-2" />
                Market Report
              </Button>
            </div>
          </div>

          {/* Usage Statistics */}
          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">AI Tools Usage Today</span>
              <div className="flex items-center gap-4">
                <span className="text-gray-900">🔍 12 analyses</span>
                <span className="text-gray-900">⚡ 3 insights generated</span>
                <span className="text-gray-900">📊 85% accuracy</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  const renderCompetitorsView = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Competitor Monitoring</h2>
        <p className="text-gray-600">
          Track and analyze your competitors' activities, pricing, and market positioning
        </p>
      </div>
      <CompetitorAlert />
    </motion.div>
  );

  const renderReportsView = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Data Studio</h2>
        <p className="text-gray-600">
          Generate comprehensive reports and create custom visualizations for your business data
        </p>
      </div>
      
      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <Card className="cursor-pointer hover:shadow-lg transition-shadow">
          <CardContent className="p-6 text-center">
            <BarChart3 className="w-12 h-12 text-blue-600 mx-auto mb-4" />
            <h3 className="font-semibold mb-2">Create Report</h3>
            <p className="text-sm text-gray-600">Build custom reports with your data</p>
          </CardContent>
        </Card>
        
        <Card className="cursor-pointer hover:shadow-lg transition-shadow">
          <CardContent className="p-6 text-center">
            <TrendingUp className="w-12 h-12 text-green-600 mx-auto mb-4" />
            <h3 className="font-semibold mb-2">Analytics Dashboard</h3>
            <p className="text-sm text-gray-600">View key performance metrics</p>
          </CardContent>
        </Card>
        
        <Card className="cursor-pointer hover:shadow-lg transition-shadow">
          <CardContent className="p-6 text-center">
            <Download className="w-12 h-12 text-purple-600 mx-auto mb-4" />
            <h3 className="font-semibold mb-2">Export Data</h3>
            <p className="text-sm text-gray-600">Download reports in various formats</p>
          </CardContent>
        </Card>
      </div>

      {/* Sample Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Performance Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Growth Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="growth" stackId="1" stroke="#10b981" fill="#10b981" fillOpacity={0.3} />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );

  const renderTemplatesView = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Analysis Templates</h2>
        <p className="text-gray-600">
          Pre-built templates for common analysis scenarios to accelerate your research
        </p>
      </div>

      {/* Template Categories */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card className="cursor-pointer hover:shadow-lg transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <Target className="w-8 h-8 text-blue-600" />
              <div>
                <h3 className="font-semibold">Market Research</h3>
                <Badge variant="secondary" className="text-xs">5 templates</Badge>
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Comprehensive market analysis templates including competitor research, market sizing, and trend analysis.
            </p>
            <Button variant="outline" size="sm" className="w-full">
              View Templates
            </Button>
          </CardContent>
        </Card>

        <Card className="cursor-pointer hover:shadow-lg transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <Users className="w-8 h-8 text-green-600" />
              <div>
                <h3 className="font-semibold">Customer Analysis</h3>
                <Badge variant="secondary" className="text-xs">4 templates</Badge>
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Customer segmentation, persona development, and user journey mapping templates.
            </p>
            <Button variant="outline" size="sm" className="w-full">
              View Templates
            </Button>
          </CardContent>
        </Card>

        <Card className="cursor-pointer hover:shadow-lg transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <TrendingUp className="w-8 h-8 text-purple-600" />
              <div>
                <h3 className="font-semibold">Financial Analysis</h3>
                <Badge variant="secondary" className="text-xs">6 templates</Badge>
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Revenue forecasting, cost analysis, and financial modeling templates.
            </p>
            <Button variant="outline" size="sm" className="w-full">
              View Templates
            </Button>
          </CardContent>
        </Card>

        <Card className="cursor-pointer hover:shadow-lg transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <Rocket className="w-8 h-8 text-orange-600" />
              <div>
                <h3 className="font-semibold">Product Strategy</h3>
                <Badge variant="secondary" className="text-xs">3 templates</Badge>
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Product roadmap planning, feature prioritization, and go-to-market strategy templates.
            </p>
            <Button variant="outline" size="sm" className="w-full">
              View Templates
            </Button>
          </CardContent>
        </Card>

        <Card className="cursor-pointer hover:shadow-lg transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <Brain className="w-8 h-8 text-pink-600" />
              <div>
                <h3 className="font-semibold">SWOT Analysis</h3>
                <Badge variant="secondary" className="text-xs">2 templates</Badge>
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Strengths, weaknesses, opportunities, and threats analysis frameworks.
            </p>
            <Button variant="outline" size="sm" className="w-full">
              View Templates
            </Button>
          </CardContent>
        </Card>

        <Card className="cursor-pointer hover:shadow-lg transition-shadow border-dashed border-2">
          <CardContent className="p-6 text-center">
            <Plus className="w-8 h-8 text-gray-400 mx-auto mb-4" />
            <h3 className="font-semibold mb-2">Custom Template</h3>
            <p className="text-sm text-gray-600 mb-4">
              Create your own analysis template
            </p>
            <Button variant="outline" size="sm">
              Create Template
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Recent Templates */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Recently Used Templates</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-blue-600" />
                <div>
                  <p className="font-medium">Competitor Analysis Framework</p>
                  <p className="text-sm text-gray-600">Last used 2 days ago</p>
                </div>
              </div>
              <Button variant="ghost" size="sm">
                Use Template
              </Button>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-green-600" />
                <div>
                  <p className="font-medium">Customer Persona Template</p>
                  <p className="text-sm text-gray-600">Last used 1 week ago</p>
                </div>
              </div>
              <Button variant="ghost" size="sm">
                Use Template
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  const renderSettingsView = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Settings
          </CardTitle>
          <CardDescription>Manage your account preferences and app settings</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <Settings className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Settings Panel Coming Soon</h3>
            <p className="text-gray-600 mb-4">
              Comprehensive settings management is in development
            </p>
            <Button variant="outline">
              Contact Support
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  const renderHelpView = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <HelpCircle className="w-5 h-5" />
            Help & Support
          </CardTitle>
          <CardDescription>Get help, tutorials, and support resources</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <HelpCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Help Center Coming Soon</h3>
            <p className="text-gray-600 mb-4">
              Comprehensive help resources and tutorials are in development
            </p>
            <Button variant="outline">
              Contact Us
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  const renderAccountView = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="w-5 h-5" />
            Account Management
          </CardTitle>
          <CardDescription>Manage your profile, subscription, and billing</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <User className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Account Panel Coming Soon</h3>
            <p className="text-gray-600 mb-4">
              Complete account management features are in development
            </p>
            <Button variant="outline">
              Manage Subscription
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  const renderMainContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return renderDashboardView();
      case 'analysis':
        return renderDashboardView(); // This will show analysis-selection view
      case 'insights':
        return <PMFScoreCard />;
      case 'history':
        return renderHistoryView();
      case 'competitors':
        return renderCompetitorsView();
      case 'reports':
        return renderReportsView();
      case 'templates':
        return renderTemplatesView();
      case 'settings':
        return renderSettingsView();
      case 'help':
        return renderHelpView();
      case 'account':
        return renderAccountView();
      default:
        return renderDashboardView();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Canva-style Sidebar */}
      <CanvaSidebar
        activeSection={activeSection}
        onSectionChange={setActiveSection}
        userStats={{
          creditsRemaining: userStats.creditsRemaining,
          totalProjects: 12,
          completedAnalyses: userStats.totalAnalyses
        }}
      />

      {/* Main Content Area */}
      <div className="ml-64 flex flex-col min-h-screen bg-gray-50">
        {/* Top Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-10"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 capitalize">
                    {activeSection === 'dashboard' ? 'AI Expert' : 
                     activeSection === 'history' ? 'Analysis History' :
                     activeSection === 'competitors' ? 'Competitor Monitor' :
                     activeSection === 'reports' ? 'Data Studio' :
                     activeSection === 'templates' ? 'Templates' :
                     activeSection === 'settings' ? 'Settings' :
                     activeSection === 'help' ? 'Help & Support' :
                     activeSection === 'account' ? 'Account' : 'AI Expert'}
                  </h1>
                  {currentKeyword && (
                    <div className="flex items-center gap-2 text-sm text-gray-600 mt-1">
                      <span>Analyzing:</span>
                      <Badge variant="outline" className="text-purple-700 border-purple-200">
                        "{currentKeyword}"
                      </Badge>
                    </div>
                  )}
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {isAnalyzing && (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex items-center gap-2 text-blue-600 bg-blue-50 px-3 py-1 rounded-full"
                >
                  <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                  <span className="text-sm font-medium">Analyzing...</span>
                </motion.div>
              )}
              
              <div className="flex items-center gap-2 text-sm text-gray-600 bg-yellow-50 px-3 py-1 rounded-full border border-yellow-200">
                <Zap className="w-4 h-4 text-yellow-500" />
                <span className="font-medium">{userStats.creditsRemaining} credits</span>
              </div>
              
              <div className="hidden md:flex items-center gap-2">
                <Button variant="ghost" size="sm" className="hover:bg-gray-100">
                  <Settings className="w-4 h-4" />
                </Button>
                <Button variant="ghost" size="sm" className="hover:bg-gray-100">
                  <HelpCircle className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Main Content */}
        <div className="flex-1 p-6 max-w-7xl mx-auto w-full pb-12">
          <motion.div
            key={activeSection}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {renderMainContent()}
          </motion.div>
        </div>
      </div>
    </div>
  );
}