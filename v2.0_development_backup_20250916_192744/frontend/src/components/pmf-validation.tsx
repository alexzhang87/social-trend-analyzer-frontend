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
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Slider } from "@/components/ui/slider";
import { 
  Target, 
  TrendingUp, 
  Users, 
  Heart,
  BarChart3,
  PieChart,
  FileText,
  Download,
  CheckCircle,
  AlertTriangle,
  Star,
  Zap,
  Clock,
  DollarSign,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  ArrowRight,
  Lightbulb,
  Award
} from "lucide-react";
import { useNavigate } from "react-router-dom";

interface PMFValidationData {
  productInfo: {
    name: string;
    description: string;
    category: string;
    stage: 'idea' | 'prototype' | 'mvp' | 'launched';
    targetMarket: string;
  };
  customerMetrics: {
    totalUsers: number;
    activeUsers: number;
    retentionRate: number;
    churnRate: number;
    nps: number;
    customerSatisfaction: number;
  };
  businessMetrics: {
    revenue: number;
    growthRate: number;
    customerAcquisitionCost: number;
    lifetimeValue: number;
    burnRate: number;
  };
  qualitativeData: {
    customerFeedback: string;
    painPoints: string[];
    valueProposition: string;
    competitiveAdvantage: string;
  };
}

interface PMFReport {
  id: string;
  score: number;
  level: 'poor' | 'developing' | 'good' | 'excellent';
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  nextSteps: string[];
  createdAt: string;
  productName: string;
}

const PMF_QUESTIONS = [
  {
    id: 'disappointment',
    question: 'What percentage of users would be very disappointed if your product disappeared tomorrow?',
    type: 'percentage',
    weight: 0.3
  },
  {
    id: 'recommendation',
    question: 'How likely are users to recommend your product to friends?',
    type: 'scale',
    weight: 0.25
  },
  {
    id: 'frequency',
    question: 'How frequently do users use your product?',
    type: 'frequency',
    weight: 0.2
  },
  {
    id: 'value',
    question: 'How do users perceive the value of your product?',
    type: 'scale',
    weight: 0.15
  },
  {
    id: 'alternatives',
    question: 'What alternatives would users use if your product didn\'t exist?',
    type: 'text',
    weight: 0.1
  }
];

export function PMFValidation() {
  const { user } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();

  const [validationData, setValidationData] = useState<PMFValidationData>({
    productInfo: {
      name: '',
      description: '',
      category: 'saas',
      stage: 'mvp',
      targetMarket: ''
    },
    customerMetrics: {
      totalUsers: 0,
      activeUsers: 0,
      retentionRate: 0,
      churnRate: 0,
      nps: 0,
      customerSatisfaction: 0
    },
    businessMetrics: {
      revenue: 0,
      growthRate: 0,
      customerAcquisitionCost: 0,
      lifetimeValue: 0,
      burnRate: 0
    },
    qualitativeData: {
      customerFeedback: '',
      painPoints: [],
      valueProposition: '',
      competitiveAdvantage: ''
    }
  });

  const [pmfAnswers, setPmfAnswers] = useState<Record<string, any>>({});
  const [currentReport, setCurrentReport] = useState<PMFReport | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [reports, setReports] = useState<PMFReport[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      toast({
        title: "Login Required",
        description: "Please login to use the PMF validation feature",
        variant: "destructive",
      });
      navigate('/pricing');
      return;
    }

    fetchPMFReports();
  }, [user]);

  const fetchPMFReports = async () => {
    if (!user) return;

    try {
      setLoading(true);
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      
      const response = await fetch(`${apiBaseUrl}/api/v1/pmf/reports`, {
        headers: {
          'Authorization': `Bearer ${user.token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setReports(data.reports || []);
        if (data.reports && data.reports.length > 0) {
          setCurrentReport(data.reports[0]);
        }
      }
    } catch (error) {
      console.error('Error fetching PMF reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!user) return;

    if (!validationData.productInfo.name.trim()) {
      toast({
        title: "Please Enter Product Name",
        description: "Product name is required",
        variant: "destructive",
      });
      return;
    }

    setIsGenerating(true);

    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      
      const response = await fetch(`${apiBaseUrl}/api/v1/pmf/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`,
        },
        body: JSON.stringify({
          ...validationData,
          pmfAnswers
        }),
      });

      if (!response.ok) {
        throw new Error('PMF validation failed');
      }

      const result = await response.json();
      setCurrentReport(result);
      setReports(prev => [result, ...prev]);

      toast({
        title: "Validation Completed",
        description: "PMF validation report has been generated",
      });

    } catch (error) {
      console.error('Error generating PMF report:', error);
      toast({
        title: "Validation Failed",
        description: "Error occurred while generating PMF validation report",
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownloadReport = async (reportId: string) => {
    if (!user) return;

    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      
      const response = await fetch(`${apiBaseUrl}/api/v1/pmf/reports/${reportId}/download`, {
        headers: {
          'Authorization': `Bearer ${user.token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Download failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `pmf-report-${reportId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast({
        title: "Download Successful",
        description: "PMF validation report has been downloaded",
      });
    } catch (error) {
      toast({
        title: "Download Failed",
        description: "Error occurred while downloading report",
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

  const getPMFLevelLabel = (level: string) => {
    switch (level) {
      case 'excellent': return 'Excellent';
      case 'good': return 'Good';
      case 'developing': return 'Developing';
      case 'poor': return 'Poor';
      default: return 'Unknown';
    }
  };

  const getPMFLevelBadge = (level: string) => {
    switch (level) {
      case 'excellent': return 'default';
      case 'good': return 'secondary';
      case 'developing': return 'outline';
      case 'poor': return 'destructive';
      default: return 'outline';
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
                <span className="text-white font-medium">Loading PMF Validation...</span>
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
              <Target className="w-8 h-8 text-cyan-400" />
PMF Validation Report
            </h1>
            <p className="text-gray-300">
Comprehensive assessment of your product-market fit with professional improvement recommendations
            </p>
          </div>

          {/* Current PMF Score */}
          {currentReport && (
            <Card className="glass-card border-white/10">
              <CardContent className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div className="text-center">
                    <div className={`text-4xl font-bold mb-2 ${getPMFScoreColor(currentReport.score)}`}>
                      {currentReport.score}/100
                    </div>
                    <Badge variant={getPMFLevelBadge(currentReport.level)}>
                      {getPMFLevelLabel(currentReport.level)}
                    </Badge>
                    <p className="text-sm text-gray-400 mt-2">{currentReport.productName}</p>
                  </div>
                  
                  <div className="space-y-2">
                    <h4 className="font-medium text-green-400 flex items-center gap-2">
                      <CheckCircle className="w-4 h-4" />
                      Strengths
                    </h4>
                    <ul className="space-y-1">
                      {currentReport.strengths.slice(0, 2).map((strength, index) => (
                        <li key={index} className="text-sm text-gray-300">• {strength}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="space-y-2">
                    <h4 className="font-medium text-red-400 flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4" />
                      Areas for Improvement
                    </h4>
                    <ul className="space-y-1">
                      {currentReport.weaknesses.slice(0, 2).map((weakness, index) => (
                        <li key={index} className="text-sm text-gray-300">• {weakness}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="flex flex-col gap-3">
                    <Button
                      onClick={() => handleDownloadReport(currentReport.id)}
                      variant="outline"
                      size="sm"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Download Report
                    </Button>
                    <p className="text-xs text-gray-400">
                      {new Date(currentReport.createdAt).toLocaleDateString('zh-CN')}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          <Tabs defaultValue="validation" className="space-y-6">
            <TabsList className="grid w-full grid-cols-3 glass-card border-white/10">
              <TabsTrigger value="validation">New Validation</TabsTrigger>
              <TabsTrigger value="results">Validation Results</TabsTrigger>
              <TabsTrigger value="history">History Reports</TabsTrigger>
            </TabsList>

            {/* New Validation */}
            <TabsContent value="validation" className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Product Information */}
                <Card className="glass-card border-white/10">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                      <Lightbulb className="w-5 h-5" />
Product Information
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label className="text-gray-300">Product Name</Label>
                      <Input
                        value={validationData.productInfo.name}
                        onChange={(e) => setValidationData(prev => ({
                          ...prev,
                          productInfo: { ...prev.productInfo, name: e.target.value }
                        }))}
                        placeholder="Enter product name"
                        className="bg-white/5 border-white/10 text-white"
                      />
                    </div>

                    <div>
                      <Label className="text-gray-300">Product Description</Label>
                      <Textarea
                        value={validationData.productInfo.description}
                        onChange={(e) => setValidationData(prev => ({
                          ...prev,
                          productInfo: { ...prev.productInfo, description: e.target.value }
                        }))}
                        placeholder="Briefly describe your product"
                        className="bg-white/5 border-white/10 text-white"
                        rows={3}
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-gray-300">Product Category</Label>
                        <select
                          value={validationData.productInfo.category}
                          onChange={(e) => setValidationData(prev => ({
                            ...prev,
                            productInfo: { ...prev.productInfo, category: e.target.value }
                          }))}
                          className="w-full p-2 bg-white/5 border border-white/10 rounded-md text-white"
                        >
                          <option value="saas">SaaS</option>
                          <option value="mobile">Mobile App</option>
                          <option value="ecommerce">E-commerce</option>
                          <option value="fintech">FinTech</option>
                          <option value="healthtech">HealthTech</option>
                          <option value="edtech">EdTech</option>
                          <option value="other">Other</option>
                        </select>
                      </div>

                      <div>
                        <Label className="text-gray-300">Product Stage</Label>
                        <select
                          value={validationData.productInfo.stage}
                          onChange={(e) => setValidationData(prev => ({
                            ...prev,
                            productInfo: { ...prev.productInfo, stage: e.target.value as any }
                          }))}
                          className="w-full p-2 bg-white/5 border border-white/10 rounded-md text-white"
                        >
                          <option value="idea">Idea Stage</option>
                          <option value="prototype">Prototype Stage</option>
                          <option value="mvp">MVP Stage</option>
                          <option value="launched">Launched</option>
                        </select>
                      </div>
                    </div>

                    <div>
                      <Label className="text-gray-300">Target Market</Label>
                      <Input
                        value={validationData.productInfo.targetMarket}
                        onChange={(e) => setValidationData(prev => ({
                          ...prev,
                          productInfo: { ...prev.productInfo, targetMarket: e.target.value }
                        }))}
                        placeholder="Describe your target customer group"
                        className="bg-white/5 border-white/10 text-white"
                      />
                    </div>
                  </CardContent>
                </Card>

                {/* Customer Metrics */}
                <Card className="glass-card border-white/10">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                      <Users className="w-5 h-5" />
User Metrics
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-gray-300">Total Users</Label>
                        <Input
                          type="number"
                          value={validationData.customerMetrics.totalUsers}
                          onChange={(e) => setValidationData(prev => ({
                            ...prev,
                            customerMetrics: { ...prev.customerMetrics, totalUsers: parseInt(e.target.value) || 0 }
                          }))}
                          className="bg-white/5 border-white/10 text-white"
                        />
                      </div>

                      <div>
                        <Label className="text-gray-300">Active Users</Label>
                        <Input
                          type="number"
                          value={validationData.customerMetrics.activeUsers}
                          onChange={(e) => setValidationData(prev => ({
                            ...prev,
                            customerMetrics: { ...prev.customerMetrics, activeUsers: parseInt(e.target.value) || 0 }
                          }))}
                          className="bg-white/5 border-white/10 text-white"
                        />
                      </div>
                    </div>

                    <div>
                      <Label className="text-gray-300">Retention Rate (%): {validationData.customerMetrics.retentionRate}%</Label>
                      <Slider
                        value={[validationData.customerMetrics.retentionRate]}
                        onValueChange={(value) => setValidationData(prev => ({
                          ...prev,
                          customerMetrics: { ...prev.customerMetrics, retentionRate: value[0] }
                        }))}
                        max={100}
                        step={1}
                        className="mt-2"
                      />
                    </div>

                    <div>
                      <Label className="text-gray-300">Churn Rate (%): {validationData.customerMetrics.churnRate}%</Label>
                      <Slider
                        value={[validationData.customerMetrics.churnRate]}
                        onValueChange={(value) => setValidationData(prev => ({
                          ...prev,
                          customerMetrics: { ...prev.customerMetrics, churnRate: value[0] }
                        }))}
                        max={100}
                        step={1}
                        className="mt-2"
                      />
                    </div>

                    <div>
                      <Label className="text-gray-300">NPS Score: {validationData.customerMetrics.nps}</Label>
                      <Slider
                        value={[validationData.customerMetrics.nps + 100]}
                        onValueChange={(value) => setValidationData(prev => ({
                          ...prev,
                          customerMetrics: { ...prev.customerMetrics, nps: value[0] - 100 }
                        }))}
                        max={200}
                        step={1}
                        className="mt-2"
                      />
                      <div className="flex justify-between text-xs text-gray-400 mt-1">
                        <span>-100</span>
                        <span>0</span>
                        <span>100</span>
                      </div>
                    </div>

                    <div>
                      <Label className="text-gray-300">Customer Satisfaction (%): {validationData.customerMetrics.customerSatisfaction}%</Label>
                      <Slider
                        value={[validationData.customerMetrics.customerSatisfaction]}
                        onValueChange={(value) => setValidationData(prev => ({
                          ...prev,
                          customerMetrics: { ...prev.customerMetrics, customerSatisfaction: value[0] }
                        }))}
                        max={100}
                        step={1}
                        className="mt-2"
                      />
                    </div>
                  </CardContent>
                </Card>

                {/* Business Metrics */}
                <Card className="glass-card border-white/10">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                      <DollarSign className="w-5 h-5" />
Business Metrics
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-gray-300">Monthly Revenue (¥)</Label>
                        <Input
                          type="number"
                          value={validationData.businessMetrics.revenue}
                          onChange={(e) => setValidationData(prev => ({
                            ...prev,
                            businessMetrics: { ...prev.businessMetrics, revenue: parseInt(e.target.value) || 0 }
                          }))}
                          className="bg-white/5 border-white/10 text-white"
                        />
                      </div>

                      <div>
                        <Label className="text-gray-300">Growth Rate (%)</Label>
                        <Input
                          type="number"
                          value={validationData.businessMetrics.growthRate}
                          onChange={(e) => setValidationData(prev => ({
                            ...prev,
                            businessMetrics: { ...prev.businessMetrics, growthRate: parseInt(e.target.value) || 0 }
                          }))}
                          className="bg-white/5 border-white/10 text-white"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-gray-300">Customer Acquisition Cost (¥)</Label>
                        <Input
                          type="number"
                          value={validationData.businessMetrics.customerAcquisitionCost}
                          onChange={(e) => setValidationData(prev => ({
                            ...prev,
                            businessMetrics: { ...prev.businessMetrics, customerAcquisitionCost: parseInt(e.target.value) || 0 }
                          }))}
                          className="bg-white/5 border-white/10 text-white"
                        />
                      </div>

                      <div>
                        <Label className="text-gray-300">Customer Lifetime Value (¥)</Label>
                        <Input
                          type="number"
                          value={validationData.businessMetrics.lifetimeValue}
                          onChange={(e) => setValidationData(prev => ({
                            ...prev,
                            businessMetrics: { ...prev.businessMetrics, lifetimeValue: parseInt(e.target.value) || 0 }
                          }))}
                          className="bg-white/5 border-white/10 text-white"
                        />
                      </div>
                    </div>

                    <div>
                      <Label className="text-gray-300">Monthly Burn Rate (¥)</Label>
                      <Input
                        type="number"
                        value={validationData.businessMetrics.burnRate}
                        onChange={(e) => setValidationData(prev => ({
                          ...prev,
                          businessMetrics: { ...prev.businessMetrics, burnRate: parseInt(e.target.value) || 0 }
                        }))}
                        className="bg-white/5 border-white/10 text-white"
                      />
                    </div>
                  </CardContent>
                </Card>

                {/* PMF Questions */}
                <Card className="glass-card border-white/10">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                      <MessageSquare className="w-5 h-5" />
Key PMF Questions
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {PMF_QUESTIONS.map((question) => (
                      <div key={question.id} className="space-y-3">
                        <Label className="text-gray-300 text-sm">{question.question}</Label>
                        
                        {question.type === 'percentage' && (
                          <div>
                            <Slider
                              value={[pmfAnswers[question.id] || 0]}
                              onValueChange={(value) => setPmfAnswers(prev => ({ ...prev, [question.id]: value[0] }))}
                              max={100}
                              step={5}
                              className="mt-2"
                            />
                            <div className="flex justify-between text-xs text-gray-400 mt-1">
                              <span>0%</span>
                              <span className="text-white">{pmfAnswers[question.id] || 0}%</span>
                              <span>100%</span>
                            </div>
                          </div>
                        )}

                        {question.type === 'scale' && (
                          <div>
                            <Slider
                              value={[pmfAnswers[question.id] || 5]}
                              onValueChange={(value) => setPmfAnswers(prev => ({ ...prev, [question.id]: value[0] }))}
                              min={1}
                              max={10}
                              step={1}
                              className="mt-2"
                            />
                            <div className="flex justify-between text-xs text-gray-400 mt-1">
                              <span>1</span>
                              <span className="text-white">{pmfAnswers[question.id] || 5}</span>
                              <span>10</span>
                            </div>
                          </div>
                        )}

                        {question.type === 'frequency' && (
                          <select
                            value={pmfAnswers[question.id] || 'weekly'}
                            onChange={(e) => setPmfAnswers(prev => ({ ...prev, [question.id]: e.target.value }))}
                            className="w-full p-2 bg-white/5 border border-white/10 rounded-md text-white"
                          >
                            <option value="daily">Daily</option>
                            <option value="weekly">Weekly</option>
                            <option value="monthly">Monthly</option>
                            <option value="rarely">Rarely</option>
                          </select>
                        )}

                        {question.type === 'text' && (
                          <Textarea
                            value={pmfAnswers[question.id] || ''}
                            onChange={(e) => setPmfAnswers(prev => ({ ...prev, [question.id]: e.target.value }))}
                            placeholder="Please describe in detail..."
                            className="bg-white/5 border-white/10 text-white"
                            rows={2}
                          />
                        )}
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>

              {/* Generate Button */}
              <div className="text-center">
                <Button
                  onClick={handleGenerateReport}
                  disabled={isGenerating || !validationData.productInfo.name.trim()}
                  size="lg"
                  className="px-8"
                >
                  {isGenerating ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
Generating...
                    </>
                  ) : (
                    <>
                      <Target className="w-5 h-5 mr-2" />
Generate PMF Validation Report
                    </>
                  )}
                </Button>
              </div>
            </TabsContent>

            {/* Validation Results */}
            <TabsContent value="results" className="space-y-6">
              {currentReport ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Score Overview */}
                  <Card className="glass-card border-white/10">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center gap-2">
                        <Award className="w-5 h-5" />
PMF Score Details
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-center mb-6">
                        <div className={`text-6xl font-bold mb-4 ${getPMFScoreColor(currentReport.score)}`}>
                          {currentReport.score}
                        </div>
                        <Badge variant={getPMFLevelBadge(currentReport.level)} className="text-lg px-4 py-2">
                          {getPMFLevelLabel(currentReport.level)}
                        </Badge>
                      </div>

                      <div className="space-y-4">
                        <div>
                          <h4 className="font-medium text-green-400 mb-3 flex items-center gap-2">
                            <CheckCircle className="w-4 h-4" />
Product Strengths
                          </h4>
                          <ul className="space-y-2">
                            {currentReport.strengths.map((strength, index) => (
                              <li key={index} className="text-sm text-gray-300 flex items-start gap-2">
                                <Star className="w-3 h-3 text-yellow-400 mt-1 flex-shrink-0" />
                                {strength}
                              </li>
                            ))}
                          </ul>
                        </div>

                        <div>
                          <h4 className="font-medium text-red-400 mb-3 flex items-center gap-2">
                            <AlertTriangle className="w-4 h-4" />
Areas for Improvement
                          </h4>
                          <ul className="space-y-2">
                            {currentReport.weaknesses.map((weakness, index) => (
                              <li key={index} className="text-sm text-gray-300 flex items-start gap-2">
                                <Zap className="w-3 h-3 text-orange-400 mt-1 flex-shrink-0" />
                                {weakness}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Recommendations */}
                  <Card className="glass-card border-white/10">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center gap-2">
                        <Lightbulb className="w-5 h-5" />
Improvement Recommendations
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-6">
                        <div>
                          <h4 className="font-medium text-cyan-400 mb-3">Immediate Actions</h4>
                          <ul className="space-y-3">
                            {currentReport.recommendations.map((rec, index) => (
                              <li key={index} className="text-sm text-gray-300 flex items-start gap-3">
                                <div className="w-6 h-6 bg-cyan-500/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                                  <span className="text-cyan-400 text-xs font-bold">{index + 1}</span>
                                </div>
                                {rec}
                              </li>
                            ))}
                          </ul>
                        </div>

                        <div>
                          <h4 className="font-medium text-purple-400 mb-3">Next Steps</h4>
                          <ul className="space-y-3">
                            {currentReport.nextSteps.map((step, index) => (
                              <li key={index} className="text-sm text-gray-300 flex items-start gap-3">
                                <ArrowRight className="w-4 h-4 text-purple-400 mt-0.5 flex-shrink-0" />
                                {step}
                              </li>
                            ))}
                          </ul>
                        </div>

                        <div className="pt-4 border-t border-white/10">
                          <Button
                            onClick={() => handleDownloadReport(currentReport.id)}
                            className="w-full"
                            variant="outline"
                          >
                            <Download className="w-4 h-4 mr-2" />
Download Full Report
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ) : (
                <div className="text-center py-12">
                  <Target className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-2">No Validation Results Yet</h3>
                  <p className="text-gray-400 mb-6">
                    Complete product information and PMF questions to generate your first validation report
                  </p>
                  <Button onClick={() => navigate('#validation')}>
                    Start Validation
                  </Button>
                </div>
              )}
            </TabsContent>

            {/* History Reports */}
            <TabsContent value="history" className="space-y-6">
              <Card className="glass-card border-white/10">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Clock className="w-5 h-5" />
History Reports
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {reports.length === 0 ? (
                    <div className="text-center py-8">
                      <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-400">No history reports</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {reports.map((report) => (
                        <div
                          key={report.id}
                          className="flex items-center justify-between p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors"
                        >
                          <div className="flex-1">
                            <h4 className="font-medium text-white">{report.productName}</h4>
                            <div className="flex items-center gap-4 mt-1">
                              <span className="text-sm text-gray-400">
                                {new Date(report.createdAt).toLocaleDateString('zh-CN')}
                              </span>
                              <Badge variant={getPMFLevelBadge(report.level)} className="text-xs">
                                {getPMFLevelLabel(report.level)}
                              </Badge>
                            </div>
                          </div>
                          <div className="flex items-center gap-4">
                            <div className={`text-2xl font-bold ${getPMFScoreColor(report.score)}`}>
                              {report.score}
                            </div>
                            <Button
                              onClick={() => handleDownloadReport(report.id)}
                              size="sm"
                              variant="outline"
                            >
                              <Download className="w-4 h-4 mr-1" />
Download
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  );
}