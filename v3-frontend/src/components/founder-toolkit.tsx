import { useState, useEffect } from "react";
import { Header } from "./header";
import { useAuth } from "@/components/auth-provider";
import { useToast } from "@/components/ui/use-toast";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { 
  Rocket, 
  Target, 
  Users, 
  TrendingUp,
  BarChart3,
  FileText,
  Lightbulb,
  CheckCircle,
  AlertTriangle,
  Star,
  Calendar,
  DollarSign,
  Globe,
  MessageSquare,
  Settings,
  Download,
  Plus,
  ArrowRight
} from "lucide-react";
import { useNavigate } from "react-router-dom";

interface PMFMetrics {
  score: number;
  productMarketFit: 'poor' | 'developing' | 'good' | 'excellent';
  keyMetrics: {
    customerSatisfaction: number;
    retentionRate: number;
    growthRate: number;
    netPromoterScore: number;
  };
  recommendations: string[];
}

interface BusinessIdea {
  id: string;
  title: string;
  description: string;
  category: string;
  viabilityScore: number;
  marketSize: string;
  competition: 'low' | 'medium' | 'high';
  createdAt: string;
}

interface CompetitorAnalysis {
  id: string;
  name: string;
  strengths: string[];
  weaknesses: string[];
  marketShare: number;
  pricing: string;
  features: string[];
}

export function FounderToolkit() {
  const { user } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();

  const [pmfMetrics, setPmfMetrics] = useState<PMFMetrics | null>(null);
  const [businessIdeas, setBusinessIdeas] = useState<BusinessIdea[]>([]);
  const [competitors, setCompetitors] = useState<CompetitorAnalysis[]>([]);
  const [loading, setLoading] = useState(true);

  // PMF Assessment Form
  const [pmfForm, setPmfForm] = useState({
    productDescription: '',
    targetMarket: '',
    customerFeedback: '',
    keyMetrics: {
      monthlyActiveUsers: '',
      retentionRate: '',
      customerSatisfaction: '',
      revenueGrowth: ''
    }
  });

  // Business Idea Form
  const [ideaForm, setIdeaForm] = useState({
    title: '',
    description: '',
    category: 'saas',
    targetMarket: '',
    problemSolving: ''
  });

  useEffect(() => {
    if (!user) {
      toast({
        title: "Login Required",
        description: "Please login to use the Founder Toolkit",
        variant: "destructive",
      });
      navigate('/pricing');
      return;
    }

    fetchFounderData();
  }, [user]);

  const fetchFounderData = async () => {
    if (!user) return;

    try {
      setLoading(true);
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      
      // Fetch PMF metrics
      const pmfResponse = await fetch(`${apiBaseUrl}/api/v1/founder/pmf-metrics`, {
        headers: {
          'Authorization': `Bearer ${user.token}`,
        },
      });

      if (pmfResponse.ok) {
        const pmfData = await pmfResponse.json();
        setPmfMetrics(pmfData);
      }

      // Fetch business ideas
      const ideasResponse = await fetch(`${apiBaseUrl}/api/v1/founder/business-ideas`, {
        headers: {
          'Authorization': `Bearer ${user.token}`,
        },
      });

      if (ideasResponse.ok) {
        const ideasData = await ideasResponse.json();
        setBusinessIdeas(ideasData.ideas || []);
      }

      // Fetch competitor analysis
      const competitorsResponse = await fetch(`${apiBaseUrl}/api/v1/founder/competitors`, {
        headers: {
          'Authorization': `Bearer ${user.token}`,
        },
      });

      if (competitorsResponse.ok) {
        const competitorsData = await competitorsResponse.json();
        setCompetitors(competitorsData.competitors || []);
      }

    } catch (error) {
      console.error('Error fetching founder data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePMFAssessment = async () => {
    if (!user) return;

    if (!pmfForm.productDescription.trim() || !pmfForm.targetMarket.trim()) {
      toast({
        title: "Please Fill Required Information",
        description: "Product description and target market are required fields",
        variant: "destructive",
      });
      return;
    }

    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      
      const response = await fetch(`${apiBaseUrl}/api/v1/founder/pmf-assessment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`,
        },
        body: JSON.stringify(pmfForm),
      });

      if (!response.ok) {
        throw new Error('PMF assessment failed');
      }

      const result = await response.json();
      setPmfMetrics(result);

      toast({
        title: "Assessment Completed",
        description: "PMF assessment has been completed, please review the results",
      });

      // Reset form
      setPmfForm({
        productDescription: '',
        targetMarket: '',
        customerFeedback: '',
        keyMetrics: {
          monthlyActiveUsers: '',
          retentionRate: '',
          customerSatisfaction: '',
          revenueGrowth: ''
        }
      });

    } catch (error) {
      console.error('Error in PMF assessment:', error);
      toast({
        title: "Assessment Failed",
        description: "Error occurred during PMF assessment",
        variant: "destructive",
      });
    }
  };

  const handleBusinessIdeaSubmit = async () => {
    if (!user) return;

    if (!ideaForm.title.trim() || !ideaForm.description.trim()) {
      toast({
        title: "Please Fill Required Information",
        description: "Title and description are required fields",
        variant: "destructive",
      });
      return;
    }

    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      
      const response = await fetch(`${apiBaseUrl}/api/v1/founder/business-ideas`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`,
        },
        body: JSON.stringify(ideaForm),
      });

      if (!response.ok) {
        throw new Error('Failed to submit business idea');
      }

      const result = await response.json();
      setBusinessIdeas(prev => [result, ...prev]);

      toast({
        title: "Submission Successful",
        description: "Business idea has been submitted and analyzed",
      });

      // Reset form
      setIdeaForm({
        title: '',
        description: '',
        category: 'saas',
        targetMarket: '',
        problemSolving: ''
      });

    } catch (error) {
      console.error('Error submitting business idea:', error);
      toast({
        title: "Submission Failed",
        description: "Error occurred while submitting business idea",
        variant: "destructive",
      });
    }
  };

  const getPMFScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    if (score >= 40) return 'text-orange-400';
    return 'text-red-400';
  };

  const getPMFScoreLabel = (fit: string) => {
    switch (fit) {
      case 'excellent': return 'Excellent';
      case 'good': return 'Good';
      case 'developing': return 'Developing';
      case 'poor': return 'Poor';
      default: return 'Unknown';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="glass-card rounded-xl p-8 border border-white/10">
              <div className="flex items-center gap-3">
                <div className="w-6 h-6 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-white font-medium">Loading Founder Toolkit...</span>
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="space-y-6">
          {/* Header */}
          <div className="text-center">
            <h1 className="text-3xl font-bold text-white mb-2 flex items-center justify-center gap-3">
              <Rocket className="w-8 h-8 text-cyan-400" />
              Founder Toolkit
            </h1>
            <p className="text-gray-300">
              Comprehensive toolkit designed for entrepreneurs to accelerate your startup journey
            </p>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card className="glass-card border-white/10">
              <CardContent className="p-6">
                <div className="flex items-center gap-3">
                  <Target className="w-8 h-8 text-cyan-400" />
                  <div>
                    <p className="text-sm text-gray-400">PMF Score</p>
                    <p className={`text-2xl font-bold ${getPMFScoreColor(pmfMetrics?.score || 0)}`}>
                      {pmfMetrics?.score || 0}/100
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="glass-card border-white/10">
              <CardContent className="p-6">
                <div className="flex items-center gap-3">
                  <Lightbulb className="w-8 h-8 text-yellow-400" />
                  <div>
                    <p className="text-sm text-gray-400">Business Ideas</p>
                    <p className="text-2xl font-bold text-white">{businessIdeas.length}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="glass-card border-white/10">
              <CardContent className="p-6">
                <div className="flex items-center gap-3">
                  <Users className="w-8 h-8 text-green-400" />
                  <div>
                    <p className="text-sm text-gray-400">Competitors</p>
                    <p className="text-2xl font-bold text-white">{competitors.length}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="glass-card border-white/10">
              <CardContent className="p-6">
                <div className="flex items-center gap-3">
                  <TrendingUp className="w-8 h-8 text-purple-400" />
                  <div>
                    <p className="text-sm text-gray-400">Growth Stage</p>
                    <p className="text-lg font-bold text-white">
                      {pmfMetrics ? getPMFScoreLabel(pmfMetrics.productMarketFit) : 'Not Assessed'}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Tabs defaultValue="pmf" className="space-y-6">
            <TabsList className="grid w-full grid-cols-4 glass-card border-white/10">
              <TabsTrigger value="pmf">PMF Validation</TabsTrigger>
              <TabsTrigger value="ideas">Business Ideas</TabsTrigger>
              <TabsTrigger value="competitors">Competitor Analysis</TabsTrigger>
              <TabsTrigger value="resources">Resources</TabsTrigger>
            </TabsList>

            {/* PMF Validation */}
            <TabsContent value="pmf" className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* PMF Assessment Form */}
                <Card className="glass-card border-white/10">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                      <Target className="w-5 h-5" />
                      PMF Assessment
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label className="text-gray-300">Product Description</Label>
                      <Textarea
                        value={pmfForm.productDescription}
                        onChange={(e) => setPmfForm(prev => ({ ...prev, productDescription: e.target.value }))}
                        placeholder="Briefly describe your product or service"
                        className="bg-white/5 border-white/10 text-white"
                        rows={3}
                      />
                    </div>

                    <div>
                      <Label className="text-gray-300">Target Market</Label>
                      <Input
                        value={pmfForm.targetMarket}
                        onChange={(e) => setPmfForm(prev => ({ ...prev, targetMarket: e.target.value }))}
                        placeholder="Describe your target customer group"
                        className="bg-white/5 border-white/10 text-white"
                      />
                    </div>

                    <div>
                      <Label className="text-gray-300">Customer Feedback</Label>
                      <Textarea
                        value={pmfForm.customerFeedback}
                        onChange={(e) => setPmfForm(prev => ({ ...prev, customerFeedback: e.target.value }))}
                        placeholder="Summarize key customer feedback"
                        className="bg-white/5 border-white/10 text-white"
                        rows={2}
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-gray-300">Monthly Active Users</Label>
                        <Input
                          value={pmfForm.keyMetrics.monthlyActiveUsers}
                          onChange={(e) => setPmfForm(prev => ({ 
                            ...prev, 
                            keyMetrics: { ...prev.keyMetrics, monthlyActiveUsers: e.target.value }
                          }))}
                          placeholder="Number"
                          className="bg-white/5 border-white/10 text-white"
                        />
                      </div>
                      <div>
                        <Label className="text-gray-300">Retention Rate (%)</Label>
                        <Input
                          value={pmfForm.keyMetrics.retentionRate}
                          onChange={(e) => setPmfForm(prev => ({ 
                            ...prev, 
                            keyMetrics: { ...prev.keyMetrics, retentionRate: e.target.value }
                          }))}
                          placeholder="Percentage"
                          className="bg-white/5 border-white/10 text-white"
                        />
                      </div>
                    </div>

                    <Button onClick={handlePMFAssessment} className="w-full">
                      <Target className="w-4 h-4 mr-2" />
                      Start PMF Assessment
                    </Button>
                  </CardContent>
                </Card>

                {/* PMF Results */}
                <Card className="glass-card border-white/10">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                      <BarChart3 className="w-5 h-5" />
                      PMF Assessment Results
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {pmfMetrics ? (
                      <div className="space-y-6">
                        {/* Overall Score */}
                        <div className="text-center">
                          <div className={`text-4xl font-bold mb-2 ${getPMFScoreColor(pmfMetrics.score)}`}>
                            {pmfMetrics.score}/100
                          </div>
                          <Badge variant={pmfMetrics.score >= 70 ? "default" : pmfMetrics.score >= 40 ? "secondary" : "destructive"}>
                            {getPMFScoreLabel(pmfMetrics.productMarketFit)}
                          </Badge>
                        </div>

                        {/* Key Metrics */}
                        <div className="space-y-3">
                          <div>
                            <div className="flex justify-between text-sm mb-1">
                              <span className="text-gray-300">Customer Satisfaction</span>
                              <span className="text-white">{pmfMetrics.keyMetrics.customerSatisfaction}%</span>
                            </div>
                            <Progress value={pmfMetrics.keyMetrics.customerSatisfaction} className="h-2" />
                          </div>

                          <div>
                            <div className="flex justify-between text-sm mb-1">
                              <span className="text-gray-300">Retention Rate</span>
                              <span className="text-white">{pmfMetrics.keyMetrics.retentionRate}%</span>
                            </div>
                            <Progress value={pmfMetrics.keyMetrics.retentionRate} className="h-2" />
                          </div>

                          <div>
                            <div className="flex justify-between text-sm mb-1">
                              <span className="text-gray-300">Growth Rate</span>
                              <span className="text-white">{pmfMetrics.keyMetrics.growthRate}%</span>
                            </div>
                            <Progress value={pmfMetrics.keyMetrics.growthRate} className="h-2" />
                          </div>

                          <div>
                            <div className="flex justify-between text-sm mb-1">
                              <span className="text-gray-300">NPS Score</span>
                              <span className="text-white">{pmfMetrics.keyMetrics.netPromoterScore}</span>
                            </div>
                            <Progress value={Math.max(0, pmfMetrics.keyMetrics.netPromoterScore + 100) / 2} className="h-2" />
                          </div>
                        </div>

                        {/* Recommendations */}
                        <div>
                          <h4 className="font-medium text-white mb-3">Recommendations</h4>
                          <div className="space-y-2">
                            {pmfMetrics.recommendations.map((rec, index) => (
                              <div key={index} className="flex items-start gap-2 text-sm">
                                <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                                <span className="text-gray-300">{rec}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-400 mb-4">No PMF assessment yet</p>
                        <p className="text-sm text-gray-500">
                          Fill out the form on the left to start your product-market fit assessment
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Business Ideas */}
            <TabsContent value="ideas" className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Add New Idea */}
                <Card className="glass-card border-white/10">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                      <Plus className="w-5 h-5" />
                      Add New Idea
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label className="text-gray-300">Title</Label>
                      <Input
                        value={ideaForm.title}
                        onChange={(e) => setIdeaForm(prev => ({ ...prev, title: e.target.value }))}
                        placeholder="Business idea title"
                        className="bg-white/5 border-white/10 text-white"
                      />
                    </div>

                    <div>
                      <Label className="text-gray-300">Description</Label>
                      <Textarea
                        value={ideaForm.description}
                        onChange={(e) => setIdeaForm(prev => ({ ...prev, description: e.target.value }))}
                        placeholder="Describe your business idea in detail"
                        className="bg-white/5 border-white/10 text-white"
                        rows={4}
                      />
                    </div>

                    <div>
                      <Label className="text-gray-300">Category</Label>
                      <select
                        value={ideaForm.category}
                        onChange={(e) => setIdeaForm(prev => ({ ...prev, category: e.target.value }))}
                        className="w-full p-2 bg-white/5 border border-white/10 rounded-md text-white"
                      >
                        <option value="saas">SaaS</option>
                        <option value="ecommerce">E-commerce</option>
                        <option value="fintech">FinTech</option>
                        <option value="healthtech">HealthTech</option>
                        <option value="edtech">EdTech</option>
                        <option value="other">Other</option>
                      </select>
                    </div>

                    <Button onClick={handleBusinessIdeaSubmit} className="w-full">
                      <Lightbulb className="w-4 h-4 mr-2" />
                      Submit for Analysis
                    </Button>
                  </CardContent>
                </Card>

                {/* Ideas List */}
                <div className="lg:col-span-2">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {businessIdeas.length === 0 ? (
                      <div className="col-span-2 text-center py-12">
                        <Lightbulb className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-400">No business ideas yet</p>
                        <p className="text-sm text-gray-500 mt-2">
                          Add your first business idea on the left
                        </p>
                      </div>
                    ) : (
                      businessIdeas.map((idea) => (
                        <Card key={idea.id} className="glass-card border-white/10">
                          <CardHeader className="pb-3">
                            <div className="flex items-start justify-between">
                              <CardTitle className="text-white text-lg">{idea.title}</CardTitle>
                              <Badge variant="outline" className="text-xs">
                                {idea.category}
                              </Badge>
                            </div>
                          </CardHeader>
                          <CardContent>
                            <p className="text-gray-300 text-sm mb-4 line-clamp-3">
                              {idea.description}
                            </p>
                            
                            <div className="space-y-3">
                              <div>
                                <div className="flex justify-between text-sm mb-1">
                                  <span className="text-gray-400">Viability Score</span>
                                  <span className="text-white">{idea.viabilityScore}/100</span>
                                </div>
                                <Progress value={idea.viabilityScore} className="h-2" />
                              </div>

                              <div className="flex items-center justify-between text-sm">
                                <span className="text-gray-400">Market Size</span>
                                <span className="text-white">{idea.marketSize}</span>
                              </div>

                              <div className="flex items-center justify-between text-sm">
                                <span className="text-gray-400">Competition Level</span>
                                <Badge 
                                  variant={idea.competition === 'low' ? 'default' : idea.competition === 'medium' ? 'secondary' : 'destructive'}
                                  className="text-xs"
                                >
                                  {idea.competition === 'low' ? 'Low' : idea.competition === 'medium' ? 'Medium' : 'High'}
                                </Badge>
                              </div>

                              <div className="flex items-center justify-between text-xs text-gray-500">
                                <span>Created</span>
                                <span>{new Date(idea.createdAt).toLocaleDateString('zh-CN')}</span>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </TabsContent>

            {/* Competitor Analysis */}
            <TabsContent value="competitors" className="space-y-6">
              <Card className="glass-card border-white/10">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Users className="w-5 h-5" />
                    Competitor Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {competitors.length === 0 ? (
                    <div className="text-center py-12">
                      <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-400 mb-4">No competitor analysis yet</p>
                      <Button onClick={() => navigate('/analysis')} variant="outline">
                        Start Analysis
                      </Button>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {competitors.map((competitor) => (
                        <Card key={competitor.id} className="bg-white/5 border-white/10">
                          <CardHeader className="pb-3">
                            <CardTitle className="text-white text-lg">{competitor.name}</CardTitle>
                            <div className="flex items-center gap-2">
                              <span className="text-sm text-gray-400">Market Share</span>
                              <Badge variant="outline">{competitor.marketShare}%</Badge>
                            </div>
                          </CardHeader>
                          <CardContent className="space-y-4">
                            <div>
                              <h5 className="text-sm font-medium text-green-400 mb-2">Strengths</h5>
                              <ul className="space-y-1">
                                {competitor.strengths.slice(0, 3).map((strength, index) => (
                                  <li key={index} className="text-xs text-gray-300 flex items-start gap-1">
                                    <CheckCircle className="w-3 h-3 text-green-400 mt-0.5 flex-shrink-0" />
                                    {strength}
                                  </li>
                                ))}
                              </ul>
                            </div>

                            <div>
                              <h5 className="text-sm font-medium text-red-400 mb-2">Weaknesses</h5>
                              <ul className="space-y-1">
                                {competitor.weaknesses.slice(0, 3).map((weakness, index) => (
                                  <li key={index} className="text-xs text-gray-300 flex items-start gap-1">
                                    <AlertTriangle className="w-3 h-3 text-red-400 mt-0.5 flex-shrink-0" />
                                    {weakness}
                                  </li>
                                ))}
                              </ul>
                            </div>

                            <div className="pt-2 border-t border-white/10">
                              <div className="flex items-center justify-between text-sm">
                                <span className="text-gray-400">Pricing</span>
                                <span className="text-white">{competitor.pricing}</span>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Resources */}
            <TabsContent value="resources" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <Card className="glass-card border-white/10 hover:border-cyan-500/30 transition-colors cursor-pointer">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <FileText className="w-8 h-8 text-cyan-400" />
                      <div>
                        <h3 className="font-semibold text-white">Business Plan Template</h3>
                        <p className="text-sm text-gray-400">Professional business plan templates</p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm" className="w-full">
                      <Download className="w-4 h-4 mr-2" />
                      Download Template
                    </Button>
                  </CardContent>
                </Card>

                <Card className="glass-card border-white/10 hover:border-cyan-500/30 transition-colors cursor-pointer">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <DollarSign className="w-8 h-8 text-green-400" />
                      <div>
                        <h3 className="font-semibold text-white">Financial Forecasting Tool</h3>
                        <p className="text-sm text-gray-400">Create detailed financial projections</p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm" className="w-full">
                      <ArrowRight className="w-4 h-4 mr-2" />
                      Use Tool
                    </Button>
                  </CardContent>
                </Card>

                <Card className="glass-card border-white/10 hover:border-cyan-500/30 transition-colors cursor-pointer">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <Globe className="w-8 h-8 text-purple-400" />
                      <div>
                        <h3 className="font-semibold text-white">Market Research Guide</h3>
                        <p className="text-sm text-gray-400">Deep dive into your target market</p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm" className="w-full">
                      <ArrowRight className="w-4 h-4 mr-2" />
                      View Guide
                    </Button>
                  </CardContent>
                </Card>

                <Card className="glass-card border-white/10 hover:border-cyan-500/30 transition-colors cursor-pointer">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <MessageSquare className="w-8 h-8 text-yellow-400" />
                      <div>
                        <h3 className="font-semibold text-white">Entrepreneur Community</h3>
                        <p className="text-sm text-gray-400">Connect with other entrepreneurs</p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm" className="w-full">
                      <ArrowRight className="w-4 h-4 mr-2" />
                      Join Community
                    </Button>
                  </CardContent>
                </Card>

                <Card className="glass-card border-white/10 hover:border-cyan-500/30 transition-colors cursor-pointer">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <Star className="w-8 h-8 text-orange-400" />
                      <div>
                        <h3 className="font-semibold text-white">Investor Directory</h3>
                        <p className="text-sm text-gray-400">Find suitable investors</p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm" className="w-full">
                      <ArrowRight className="w-4 h-4 mr-2" />
                      View Directory
                    </Button>
                  </CardContent>
                </Card>

                <Card className="glass-card border-white/10 hover:border-cyan-500/30 transition-colors cursor-pointer">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <Calendar className="w-8 h-8 text-blue-400" />
                      <div>
                        <h3 className="font-semibold text-white">Startup Schedule</h3>
                        <p className="text-sm text-gray-400">Manage startup milestones</p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm" className="w-full">
                      <ArrowRight className="w-4 h-4 mr-2" />
                      Set Schedule
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  );
}