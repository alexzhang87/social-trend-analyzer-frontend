import { useState, useEffect } from "react";
import { Header } from "./header";
import { useAuth } from "@/components/auth-provider";
import { useToast } from "@/components/ui/use-toast";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  FileText, 
  Download, 
  Settings, 
  BarChart3, 
  PieChart, 
  TrendingUp,
  Users,
  Globe,
  Calendar,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2
} from "lucide-react";
import { useNavigate } from "react-router-dom";

interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  sections: string[];
  format: 'pdf' | 'docx' | 'html';
  premium: boolean;
}

interface ReportConfig {
  title: string;
  description: string;
  template: string;
  format: 'pdf' | 'docx' | 'html';
  sections: string[];
  includeCharts: boolean;
  includeRawData: boolean;
  brandingEnabled: boolean;
  analysisIds: string[];
}

interface GeneratedReport {
  id: string;
  title: string;
  status: 'generating' | 'completed' | 'failed';
  format: string;
  createdAt: string;
  downloadUrl?: string;
  error?: string;
}

const REPORT_TEMPLATES: ReportTemplate[] = [
  {
    id: 'comprehensive',
    name: 'Comprehensive Analysis Report',
    description: 'Complete report including trend analysis, user personas, market insights and all modules',
    sections: ['executive_summary', 'trend_analysis', 'sentiment_analysis', 'demographics', 'insights', 'recommendations'],
    format: 'pdf',
    premium: false
  },
  {
    id: 'executive',
    name: 'Executive Summary Report',
    description: 'Concise report designed for executives, highlighting key metrics and recommendations',
    sections: ['executive_summary', 'key_metrics', 'recommendations'],
    format: 'pdf',
    premium: true
  },
  {
    id: 'technical',
    name: 'Technical Analysis Report',
    description: 'Detailed technical analysis including raw data and in-depth statistics',
    sections: ['methodology', 'raw_data', 'statistical_analysis', 'technical_insights'],
    format: 'pdf',
    premium: true
  },
  {
    id: 'marketing',
    name: 'Marketing Strategy Report',
    description: 'Marketing-focused report with audience analysis and strategic recommendations',
    sections: ['audience_analysis', 'content_strategy', 'channel_recommendations', 'campaign_ideas'],
    format: 'pdf',
    premium: false
  }
];

export function ReportGenerator() {
  const { user } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();

  const [config, setConfig] = useState<ReportConfig>({
    title: '',
    description: '',
    template: 'comprehensive',
    format: 'pdf',
    sections: [],
    includeCharts: true,
    includeRawData: false,
    brandingEnabled: true,
    analysisIds: []
  });

  const [availableAnalyses, setAvailableAnalyses] = useState<any[]>([]);
  const [generatedReports, setGeneratedReports] = useState<GeneratedReport[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      toast({
        title: "Login Required",
        description: "Please login to use the report generation feature",
        variant: "destructive",
      });
      navigate('/pricing');
      return;
    }

    fetchAvailableAnalyses();
    fetchGeneratedReports();
  }, [user]);

  const fetchAvailableAnalyses = async () => {
    if (!user) return;

    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      
      const response = await fetch(`${apiBaseUrl}/api/v1/analysis/list`, {
        headers: {
          'Authorization': `Bearer ${user.token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAvailableAnalyses(data.analyses || []);
      }
    } catch (error) {
      console.error('Error fetching analyses:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchGeneratedReports = async () => {
    if (!user) return;

    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      
      const response = await fetch(`${apiBaseUrl}/api/v1/reports/list`, {
        headers: {
          'Authorization': `Bearer ${user.token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setGeneratedReports(data.reports || []);
      }
    } catch (error) {
      console.error('Error fetching reports:', error);
    }
  };

  const handleTemplateChange = (templateId: string) => {
    const template = REPORT_TEMPLATES.find(t => t.id === templateId);
    if (template) {
      setConfig(prev => ({
        ...prev,
        template: templateId,
        format: template.format,
        sections: template.sections
      }));
    }
  };

  const handleSectionToggle = (section: string, checked: boolean) => {
    setConfig(prev => ({
      ...prev,
      sections: checked 
        ? [...prev.sections, section]
        : prev.sections.filter(s => s !== section)
    }));
  };

  const handleAnalysisToggle = (analysisId: string, checked: boolean) => {
    setConfig(prev => ({
      ...prev,
      analysisIds: checked 
        ? [...prev.analysisIds, analysisId]
        : prev.analysisIds.filter(id => id !== analysisId)
    }));
  };

  const handleGenerateReport = async () => {
    if (!user) return;

    if (!config.title.trim()) {
      toast({
        title: "Please Enter Report Title",
        description: "Report title is required",
        variant: "destructive",
      });
      return;
    }

    if (config.analysisIds.length === 0) {
      toast({
        title: "Please Select Analysis Data",
        description: "At least one analysis result must be selected",
        variant: "destructive",
      });
      return;
    }

    setIsGenerating(true);

    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      
      const response = await fetch(`${apiBaseUrl}/api/v1/reports/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`,
        },
        body: JSON.stringify(config),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate report');
      }

      const result = await response.json();
      
      toast({
        title: "Report Generation Started",
        description: "Report is being generated in the background and will appear in the reports list when completed",
      });

      // Reset form
      setConfig(prev => ({
        ...prev,
        title: '',
        description: '',
        analysisIds: []
      }));

    } catch (error) {
      console.error('Error generating report:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred while generating report';
      
      toast({
        title: "Generation Failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownloadReport = async (report: GeneratedReport) => {
    if (!report.downloadUrl) return;

    try {
      const response = await fetch(report.downloadUrl, {
        headers: {
          'Authorization': `Bearer ${user?.token}`,
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
      a.download = `${report.title}.${report.format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast({
        title: "Download Successful",
        description: "Report has been downloaded to local",
      });
    } catch (error) {
      toast({
        title: "Download Failed",
        description: "Error occurred while downloading report",
        variant: "destructive",
      });
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
                <span className="text-white font-medium">Loading...</span>
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
            <h1 className="text-3xl font-bold text-white mb-2">Professional Report Generator</h1>
            <p className="text-gray-300">
              Generate professional PDF reports based on your analysis data
            </p>
          </div>

          <Tabs defaultValue="generator" className="space-y-6">
            <TabsList className="grid w-full grid-cols-2 glass-card border-white/10">
              <TabsTrigger value="generator">Generate Report</TabsTrigger>
              <TabsTrigger value="history">Report History</TabsTrigger>
            </TabsList>

            <TabsContent value="generator" className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Configuration Panel */}
                <div className="lg:col-span-2 space-y-6">
                  {/* Basic Info */}
                  <Card className="glass-card border-white/10">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center gap-2">
                         <FileText className="w-5 h-5" />
                         Basic Information
                       </CardTitle>
                     </CardHeader>
                     <CardContent className="space-y-4">
                       <div>
                         <Label htmlFor="title" className="text-gray-300">Report Title</Label>
                         <Input
                           id="title"
                           value={config.title}
                           onChange={(e) => setConfig(prev => ({ ...prev, title: e.target.value }))}
                           placeholder="Enter report title"
                           className="bg-white/5 border-white/10 text-white"
                         />
                       </div>
                       <div>
                         <Label htmlFor="description" className="text-gray-300">Report Description</Label>
                         <Textarea
                           id="description"
                           value={config.description}
                           onChange={(e) => setConfig(prev => ({ ...prev, description: e.target.value }))}
                           placeholder="Enter report description (optional)"
                           className="bg-white/5 border-white/10 text-white"
                           rows={3}
                         />
                       </div>
                    </CardContent>
                  </Card>

                  {/* Template Selection */}
                  <Card className="glass-card border-white/10">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center gap-2">
                         <Settings className="w-5 h-5" />
                         Report Template
                       </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {REPORT_TEMPLATES.map((template) => (
                          <div
                            key={template.id}
                            className={`p-4 rounded-lg border cursor-pointer transition-all ${
                              config.template === template.id
                                ? 'border-cyan-500 bg-cyan-500/10'
                                : 'border-white/10 bg-white/5 hover:border-white/20'
                            }`}
                            onClick={() => handleTemplateChange(template.id)}
                          >
                            <div className="flex items-start justify-between mb-2">
                              <h4 className="font-medium text-white">{template.name}</h4>
                              {template.premium && (
                                 <Badge variant="secondary" className="text-xs">
                                   Advanced
                                 </Badge>
                               )}
                            </div>
                            <p className="text-sm text-gray-300 mb-3">{template.description}</p>
                            <div className="flex flex-wrap gap-1">
                              {template.sections.slice(0, 3).map((section) => (
                                <Badge key={section} variant="outline" className="text-xs">
                                  {section}
                                </Badge>
                              ))}
                              {template.sections.length > 3 && (
                                <Badge variant="outline" className="text-xs">
                                  +{template.sections.length - 3}
                                </Badge>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Data Selection */}
                  <Card className="glass-card border-white/10">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center gap-2">
                         <BarChart3 className="w-5 h-5" />
                         Select Analysis Data
                       </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {availableAnalyses.length === 0 ? (
                        <div className="text-center py-8">
                          <p className="text-gray-400 mb-4">No analysis data available</p>
                          <Button 
                            onClick={() => navigate('/analysis')}
                            className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700"
                          >
                            Start Analysis
                          </Button>
                        </div>
                      ) : (
                        <div className="space-y-3">
                          {availableAnalyses.map((analysis) => (
                            <div
                              key={analysis.id}
                              className="flex items-center space-x-3 p-3 bg-white/5 rounded-lg"
                            >
                              <Checkbox
                                id={analysis.id}
                                checked={config.analysisIds.includes(analysis.id)}
                                onCheckedChange={(checked) => 
                                  handleAnalysisToggle(analysis.id, checked as boolean)
                                }
                              />
                              <div className="flex-1">
                                <Label htmlFor={analysis.id} className="text-white font-medium cursor-pointer">
                                  {analysis.keywords?.join(', ') || 'Unnamed Analysis'}
                                </Label>
                                <p className="text-sm text-gray-400">
                                  {analysis.created_at ? new Date(analysis.created_at).toLocaleDateString('zh-CN') : ''}
                                </p>
                              </div>
                              <Badge variant="outline">
                                Score: {analysis.trend_score || 0}
                              </Badge>
                            </div>
                          ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>

                {/* Options Panel */}
                <div className="space-y-6">
                  <Card className="glass-card border-white/10">
                    <CardHeader>
                      <CardTitle className="text-white">Report Options</CardTitle>
                     </CardHeader>
                     <CardContent className="space-y-4">
                       <div>
                         <Label className="text-gray-300">Output Format</Label>
                        <Select
                          value={config.format}
                          onValueChange={(value: 'pdf' | 'docx' | 'html') => 
                            setConfig(prev => ({ ...prev, format: value }))
                          }
                        >
                          <SelectTrigger className="bg-white/5 border-white/10 text-white">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="pdf">PDF</SelectItem>
                            <SelectItem value="docx">Word Document</SelectItem>
                            <SelectItem value="html">HTML</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-3">
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id="includeCharts"
                            checked={config.includeCharts}
                            onCheckedChange={(checked) => 
                              setConfig(prev => ({ ...prev, includeCharts: checked as boolean }))
                            }
                          />
                          <Label htmlFor="includeCharts" className="text-gray-300">
                            Include Charts
                          </Label>
                        </div>

                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id="includeRawData"
                            checked={config.includeRawData}
                            onCheckedChange={(checked) => 
                              setConfig(prev => ({ ...prev, includeRawData: checked as boolean }))
                            }
                          />
                          <Label htmlFor="includeRawData" className="text-gray-300">
                            Include Raw Data
                          </Label>
                        </div>

                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id="brandingEnabled"
                            checked={config.brandingEnabled}
                            onCheckedChange={(checked) => 
                              setConfig(prev => ({ ...prev, brandingEnabled: checked as boolean }))
                            }
                          />
                          <Label htmlFor="brandingEnabled" className="text-gray-300">
                            Include Branding
                          </Label>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Button
                    onClick={handleGenerateReport}
                    disabled={isGenerating || !config.title.trim() || config.analysisIds.length === 0}
                    className="w-full"
                    size="lg"
                  >
                    {isGenerating ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <FileText className="w-4 h-4 mr-2" />
                        Generate Report
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="history" className="space-y-6">
              <Card className="glass-card border-white/10">
                <CardHeader>
                  <CardTitle className="text-white">Report History</CardTitle>
                </CardHeader>
                <CardContent>
                  {generatedReports.length === 0 ? (
                    <div className="text-center py-8">
                      <p className="text-gray-400">No reports generated yet</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {generatedReports.map((report) => (
                        <div
                          key={report.id}
                          className="flex items-center justify-between p-4 bg-white/5 rounded-lg"
                        >
                          <div className="flex-1">
                            <h4 className="font-medium text-white">{report.title}</h4>
                            <div className="flex items-center gap-4 mt-1">
                              <span className="text-sm text-gray-400 flex items-center gap-1">
                                <Calendar className="w-3 h-3" />
                                {new Date(report.createdAt).toLocaleDateString('zh-CN')}
                              </span>
                              <Badge variant="outline" className="text-xs">
                                {report.format.toUpperCase()}
                              </Badge>
                            </div>
                          </div>
                          <div className="flex items-center gap-3">
                            {report.status === 'generating' && (
                              <div className="flex items-center gap-2 text-yellow-400">
                                <Loader2 className="w-4 h-4 animate-spin" />
                                <span className="text-sm">Generating</span>
                              </div>
                            )}
                            {report.status === 'completed' && (
                              <div className="flex items-center gap-2">
                                <CheckCircle className="w-4 h-4 text-green-400" />
                                <Button
                                  onClick={() => handleDownloadReport(report)}
                                  size="sm"
                                  variant="outline"
                                >
                                  <Download className="w-4 h-4 mr-1" />
                                  Download
                                </Button>
                              </div>
                            )}
                            {report.status === 'failed' && (
                              <div className="flex items-center gap-2 text-red-400">
                                <AlertCircle className="w-4 h-4" />
                                <span className="text-sm">Generation Failed</span>
                              </div>
                            )}
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