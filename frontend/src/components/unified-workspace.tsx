import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
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
  Send,
  MessageCircle
} from 'lucide-react';
import { useAuth } from '@/components/auth-provider';
import { CanvaSidebar } from './canva-sidebar';
import { DualTrackAnalysis } from './dual-track-analysis';
import { QuickValidation } from './quick-validation';
import { ProfessionalAnalysis } from './professional-analysis';
import { PMFScoreCard } from './pmf-scorecard';
import { CompetitorAlert } from './competitor-alert';

type WorkspaceView = 'home' | 'analysis-selection' | 'quick-results' | 'professional-results';
type SidebarSection = 'dashboard' | 'analysis' | 'pmf' | 'insights' | 'competitors' | 'reports' | 'templates' | 'settings' | 'help' | 'account';

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
    totalAnalyses: 0,
    creditsUsed: 0,
    creditsRemaining: 10,
    averageScore: 0
  });
  const [analysisHistory, setAnalysisHistory] = useState<AnalysisHistory[]>([]);
  const [showAllHistory, setShowAllHistory] = useState(false);
  const [chartData, setChartData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const { user } = useAuth();

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
        }
      ];

      // Mock chart data for performance analytics
      const chartData = [
        { name: 'Jan', score: 65, analyses: 8, marketValue: 45, engagement: 72 },
        { name: 'Feb', score: 72, analyses: 12, marketValue: 58, engagement: 78 },
        { name: 'Mar', score: 78, analyses: 15, marketValue: 62, engagement: 85 },
        { name: 'Apr', score: 85, analyses: 18, marketValue: 75, engagement: 88 },
        { name: 'May', score: 82, analyses: 22, marketValue: 71, engagement: 82 },
        { name: 'Jun', score: 88, analyses: 25, marketValue: 85, engagement: 92 }
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

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Render input box component (migrated from homepage dialog)
  const renderInputBox = (isCenter: boolean = false) => (
    <div className={`relative ${isCenter ? 'w-full max-w-2xl mx-auto' : 'w-full'}`}>
      <textarea
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Message IdeaEden..."
        className={`w-full px-6 py-4 pr-14 border border-gray-300 rounded-3xl resize-none focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all duration-200 text-gray-900 placeholder-gray-500 shadow-sm ${
          isCenter ? 'text-lg' : 'text-base'
        }`}
        rows={1}
        style={{ 
          minHeight: isCenter ? '56px' : '48px', 
          maxHeight: '120px',
          fontSize: isCenter ? '18px' : '16px',
          lineHeight: '1.5'
        }}
      />
      <button
        onClick={handleSendMessage}
        disabled={!inputValue.trim() || isLoading}
        className={`absolute right-2 top-1/2 transform -translate-y-1/2 bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-400 text-white rounded-full flex items-center justify-center hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed ${
          isCenter ? 'w-10 h-10' : 'w-8 h-8'
        }`}
      >
        <Send className={isCenter ? 'w-4 h-4' : 'w-3 h-3'} />
      </button>
    </div>
  );

  // Render feature buttons (migrated from homepage dialog)
  const renderFeatureButtons = () => (
    <div className="flex gap-2 justify-center flex-wrap w-full max-w-2xl mx-auto mt-4">
      <button 
        onClick={() => setActiveSection('analysis')}
        className="flex items-center gap-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors"
      >
        <span>🔍</span>
        <span>Keyword Analysis</span>
      </button>
      <button 
        onClick={() => setActiveSection('pmf')}
        className="flex items-center gap-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors"
      >
        <span>🎯</span>
        <span>PMF Evaluation</span>
      </button>
      <button 
        onClick={() => setActiveSection('insights')}
        className="flex items-center gap-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors"
      >
        <span>📊</span>
        <span>Market Dashboard</span>
      </button>
      <button 
        onClick={() => setActiveSection('reports')}
        className="flex items-center gap-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors"
      >
        <span>📈</span>
        <span>Analysis Reports</span>
      </button>
    </div>
  );

  const renderHomeView = () => (
    <div className="min-h-screen bg-gray-50 flex flex-col">


      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-12">
        <div className="max-w-2xl mx-auto w-full space-y-8">
          
          {/* Chat Input Box - Main Dialog */}
          <Card className="bg-white rounded-2xl border border-gray-200 shadow-lg">
            <CardContent className="p-8 text-center space-y-6">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-400 flex items-center justify-center mx-auto">
                <MessageCircle className="w-6 h-6 text-white" />
              </div>
              <div className="space-y-3">
                <h1 className="text-2xl font-bold text-gray-900">
                  <span>AI Expert</span>
                </h1>
                <p className="text-lg text-gray-600">
                  Enter your idea or product for professional market validation analysis
                </p>
              </div>
              
              {/* Integrated dialog input component */}
              <div className="mt-6">
                {renderInputBox(true)}
              </div>
              
              {/* Feature buttons */}
              {renderFeatureButtons()}
            </CardContent>
          </Card>




        </div>
      </div>
    </div>
  );

  const renderAnalysisView = () => (
    <DualTrackAnalysis
      onModeSelect={handleModeSelect}
      onBackToHome={handleBackToHome}
      userCredits={userStats.creditsRemaining}
    />
  );

  const renderQuickResults = () => (
    <QuickValidation
      keyword={currentKeyword}
      onUpgrade={handleUpgradeToProf}
      onNewAnalysis={handleNewAnalysis}
      onBackToHome={handleBackToHome}
    />
  );

  const renderProfessionalResults = () => (
    <ProfessionalAnalysis
      keyword={currentKeyword}
      onNewAnalysis={handleNewAnalysis}
      onBackToHome={handleBackToHome}
    />
  );

  const renderPMFView = () => (
    <PMFScoreCard />
  );

  const renderInsightsView = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5" />
            AI Insights Dashboard
          </CardTitle>
          <CardDescription>Intelligent market analysis and recommendations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <Brain className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">AI Insights Coming Soon</h3>
            <p className="text-gray-600 mb-4">
              Advanced AI-powered insights and recommendations are in development
            </p>
            <Button variant="outline">
              Learn More
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderHistoryView = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="w-5 h-5" />
            Analysis History
          </CardTitle>
          <CardDescription>Your complete analysis history and results</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {analysisHistory.map((analysis) => (
              <div key={analysis.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <h4 className="font-medium">{analysis.keyword}</h4>
                  <p className="text-sm text-gray-500">{analysis.date} • {analysis.type}</p>
                </div>
                <div className="flex items-center gap-3">
                  <Badge variant={analysis.type === 'professional' ? 'default' : 'secondary'}>
                    Score: {analysis.score}
                  </Badge>
                  <Button variant="ghost" size="sm">
                    <Eye className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderCompetitorsView = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            Competitor Monitor
          </CardTitle>
          <CardDescription>Track and analyze your competition</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Competitor Monitoring Coming Soon</h3>
            <p className="text-gray-600 mb-4">
              Advanced competitor tracking and analysis tools are in development
            </p>
            <Button variant="outline">
              Get Notified
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderReportsView = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Data Studio
          </CardTitle>
          <CardDescription>Create and manage your analysis reports</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Data Studio Coming Soon</h3>
            <p className="text-gray-600 mb-4">
              Comprehensive reporting and data visualization tools are in development
            </p>
            <Button variant="outline">
              Preview Features
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderTemplatesView = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="w-5 h-5" />
            Analysis Templates
          </CardTitle>
          <CardDescription>Pre-built templates for common analysis scenarios</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Templates Coming Soon</h3>
            <p className="text-gray-600 mb-4">
              Ready-to-use analysis templates are in development
            </p>
            <Button variant="outline">
              Request Template
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderSettingsView = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Settings
          </CardTitle>
          <CardDescription>Manage your preferences and account settings</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <Settings className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Settings Panel Coming Soon</h3>
            <p className="text-gray-600 mb-4">
              Comprehensive settings and preferences are in development
            </p>
            <Button variant="outline">
              Contact Support
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderHelpView = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <HelpCircle className="w-5 h-5" />
            Help & Support
          </CardTitle>
          <CardDescription>Get help and learn how to use the platform</CardDescription>
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
    </div>
  );

  const renderAccountView = () => (
    <div className="space-y-6">
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
    </div>
  );

  const renderMainContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return renderHomeView();
      case 'analysis':
        return currentView === 'home' || currentView === 'analysis-selection' ? renderAnalysisView() :
               currentView === 'quick-results' ? renderQuickResults() :
               currentView === 'professional-results' ? renderProfessionalResults() :
               renderAnalysisView();
      case 'pmf':
        return renderPMFView();
      case 'insights':
        return renderInsightsView();
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
        return renderHomeView();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Canva-style Sidebar */}
      <CanvaSidebar
        activeSection={activeSection}
        onSectionChange={setActiveSection}
        userStats={{
          creditsRemaining: 150,
          totalProjects: 12,
          completedAnalyses: 45
        }}
      />

      {/* Main Content Area */}
      <div className="ml-64 flex flex-col overflow-hidden min-h-screen bg-transparent">
        {/* Top Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white/80 backdrop-blur-sm border-b border-white/20 px-6 py-4 sticky top-0 z-10 shadow-sm"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 capitalize">
                    {activeSection === 'dashboard' ? 'Dashboard' : 
                     activeSection === 'analysis' ? 'Keyword Analysis' :
                     activeSection === 'pmf' ? 'PMF Scorecard' :
                     activeSection === 'insights' ? 'AI Insights' :
                     activeSection === 'history' ? 'Chat History' :
                     activeSection === 'competitors' ? 'Competitor Monitor' :
                     activeSection === 'reports' ? 'Data Studio' :
                     activeSection === 'templates' ? 'Templates' :
                     activeSection === 'settings' ? 'Settings' :
                     activeSection === 'help' ? 'Help & Support' :
                     activeSection === 'account' ? 'Account' : 'Dashboard'}
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
                <Button variant="outline" size="sm" className="gap-2 hover:bg-gray-100">
                  <Plus className="w-4 h-4" />
                  New Analysis
                </Button>
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
        <div className="flex-1 overflow-y-auto p-6 max-w-7xl mx-auto w-full">
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
