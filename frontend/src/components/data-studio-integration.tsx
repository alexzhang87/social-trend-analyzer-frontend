import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Progress } from '@/components/ui/progress';
import { 
  BarChart3, 
  FileText, 
  Download, 
  Share2, 
  Settings, 
  Plus, 
  Eye, 
  Calendar,
  TrendingUp,
  PieChart,
  Activity,
  Users,
  DollarSign,
  Target
} from 'lucide-react';

interface DataStudioReport {
  id: string;
  name: string;
  description: string;
  template: string;
  status: 'draft' | 'published' | 'scheduled';
  lastUpdated: string;
  shareUrl?: string;
  autoRefresh: boolean;
  refreshInterval: number; // hours
  dataSource: string;
  metrics: string[];
  dimensions: string[];
}

interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  category: 'pmf' | 'competitor' | 'market' | 'business' | 'custom';
  preview: string;
  metrics: string[];
  dimensions: string[];
  chartTypes: string[];
}

interface DataStudioIntegrationProps {
  onReportGenerated?: (report: DataStudioReport) => void;
}

const REPORT_TEMPLATES: ReportTemplate[] = [
  {
    id: 'pmf-dashboard',
    name: 'PMF Analysis Dashboard',
    description: 'Comprehensive product-market fit analysis report including customer satisfaction, market demand and other key metrics',
    category: 'pmf',
    preview: '/templates/pmf-dashboard.png',
    metrics: ['pmf_score', 'customer_satisfaction', 'market_demand', 'product_usability'],
    dimensions: ['date', 'user_segment', 'product_feature'],
    chartTypes: ['line_chart', 'radar_chart', 'gauge_chart']
  },
  {
    id: 'competitor-analysis',
    name: 'Competitor Analysis Report',
    description: 'Competitor dynamics monitoring and threat analysis including market share, product comparison and more',
    category: 'competitor',
    preview: '/templates/competitor-analysis.png',
    metrics: ['market_share', 'threat_score', 'funding_amount', 'employee_count'],
    dimensions: ['competitor_name', 'date', 'industry_category'],
    chartTypes: ['bar_chart', 'scatter_plot', 'heatmap']
  },
  {
    id: 'market-trends',
    name: 'Market Trends Analysis',
    description: 'Industry trends and market opportunity analysis based on social media and search data',
    category: 'market',
    preview: '/templates/market-trends.png',
    metrics: ['trend_volume', 'sentiment_score', 'growth_rate', 'opportunity_score'],
    dimensions: ['keyword', 'platform', 'geography', 'time_period'],
    chartTypes: ['line_chart', 'area_chart', 'treemap']
  },
  {
    id: 'business-metrics',
    name: 'Business Metrics Dashboard',
    description: 'Core business metrics monitoring including revenue, user growth, conversion rates and more',
    category: 'business',
    preview: '/templates/business-metrics.png',
    metrics: ['revenue', 'user_growth', 'conversion_rate', 'ltv', 'cac'],
    dimensions: ['date', 'channel', 'user_segment', 'product'],
    chartTypes: ['line_chart', 'bar_chart', 'funnel_chart']
  }
];

const CATEGORY_LABELS = {
  pmf: 'PMF Analysis',
  competitor: 'Competitor Analysis',
  market: 'Market Analysis',
  business: 'Business Metrics',
  custom: 'Custom'
};

const CATEGORY_COLORS = {
  pmf: 'bg-blue-500',
  competitor: 'bg-red-500',
  market: 'bg-green-500',
  business: 'bg-purple-500',
  custom: 'bg-gray-500'
};

export function DataStudioIntegration({ onReportGenerated }: DataStudioIntegrationProps) {
  const [reports, setReports] = useState<DataStudioReport[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<ReportTemplate | null>(null);
  const [isCreatingReport, setIsCreatingReport] = useState(false);
  const [newReport, setNewReport] = useState({
    name: '',
    description: '',
    autoRefresh: true,
    refreshInterval: 24,
    dataSource: 'default'
  });
  const [generationProgress, setGenerationProgress] = useState(0);
  const [isGenerating, setIsGenerating] = useState(false);

  // Mock existing reports
  useEffect(() => {
    const mockReports: DataStudioReport[] = [
      {
        id: '1',
        name: 'PMF Monthly Analysis Report',
        description: 'Monthly product-market fit tracking analysis',
        template: 'pmf-dashboard',
        status: 'published',
        lastUpdated: '2024-01-15',
        shareUrl: 'https://datastudio.google.com/reporting/pmf-monthly',
        autoRefresh: true,
        refreshInterval: 24,
        dataSource: 'pmf_analytics',
        metrics: ['pmf_score', 'customer_satisfaction'],
        dimensions: ['date', 'user_segment']
      },
      {
        id: '2',
        name: 'Competitor Threat Monitoring',
        description: 'Real-time competitor dynamics monitoring dashboard',
        template: 'competitor-analysis',
        status: 'published',
        lastUpdated: '2024-01-14',
        shareUrl: 'https://datastudio.google.com/reporting/competitor-monitor',
        autoRefresh: true,
        refreshInterval: 12,
        dataSource: 'competitor_data',
        metrics: ['threat_score', 'market_share'],
        dimensions: ['competitor_name', 'date']
      }
    ];
    setReports(mockReports);
  }, []);

  // Create report
  const createReport = async () => {
    if (!selectedTemplate || !newReport.name) return;
    
    setIsGenerating(true);
    setGenerationProgress(0);
    
    // Mock report generation process
    const steps = [
      { progress: 20, message: 'Connecting data source...' },
      { progress: 40, message: 'Configuring chart components...' },
      { progress: 60, message: 'Applying template styles...' },
      { progress: 80, message: 'Setting up auto-refresh...' },
      { progress: 100, message: 'Report generation completed!' }
    ];
    
    for (const step of steps) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setGenerationProgress(step.progress);
    }
    
    const report: DataStudioReport = {
      id: Date.now().toString(),
      name: newReport.name,
      description: newReport.description,
      template: selectedTemplate.id,
      status: 'published',
      lastUpdated: new Date().toISOString().split('T')[0],
      shareUrl: `https://datastudio.google.com/reporting/${Date.now()}`,
      autoRefresh: newReport.autoRefresh,
      refreshInterval: newReport.refreshInterval,
      dataSource: newReport.dataSource,
      metrics: selectedTemplate.metrics,
      dimensions: selectedTemplate.dimensions
    };
    
    setReports(prev => [...prev, report]);
    setIsCreatingReport(false);
    setIsGenerating(false);
    setGenerationProgress(0);
    setNewReport({ name: '', description: '', autoRefresh: true, refreshInterval: 24, dataSource: 'default' });
    setSelectedTemplate(null);
    
    if (onReportGenerated) {
      onReportGenerated(report);
    }
  };

  // Delete report
  const deleteReport = (id: string) => {
    setReports(prev => prev.filter(r => r.id !== id));
  };

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published': return 'bg-green-500';
      case 'draft': return 'bg-yellow-500';
      case 'scheduled': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  // Get status label
  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'published': return 'Published';
      case 'draft': return 'Draft';
      case 'scheduled': return 'Scheduled';
      default: return 'Unknown';
    }
  };

  return (
    <div className="space-y-6">
      {/* Overview Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Active Reports</p>
                <p className="text-2xl font-bold text-white">{reports.filter(r => r.status === 'published').length}</p>
              </div>
              <BarChart3 className="w-8 h-8 text-cyan-400" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Auto Refresh</p>
                <p className="text-2xl font-bold text-green-400">{reports.filter(r => r.autoRefresh).length}</p>
              </div>
              <Activity className="w-8 h-8 text-green-400" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Templates</p>
                <p className="text-2xl font-bold text-purple-400">{REPORT_TEMPLATES.length}</p>
              </div>
              <FileText className="w-8 h-8 text-purple-400" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Shared Links</p>
                <p className="text-2xl font-bold text-blue-400">{reports.filter(r => r.shareUrl).length}</p>
              </div>
              <Share2 className="w-8 h-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="reports" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="reports">My Reports</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="create">Create Report</TabsTrigger>
        </TabsList>
        
        {/* My Reports */}
        <TabsContent value="reports" className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">My Data Studio Reports</h3>
            <Button 
              onClick={() => setIsCreatingReport(true)}
              className="bg-cyan-600 hover:bg-cyan-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              New Report
            </Button>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {reports.map(report => {
              const template = REPORT_TEMPLATES.find(t => t.id === report.template);
              
              return (
                <Card key={report.id} className="border-border/20 bg-card/50 backdrop-blur-sm">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-lg">{report.name}</CardTitle>
                        <CardDescription>{report.description}</CardDescription>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={`${getStatusColor(report.status)} text-white`}>
                          {getStatusLabel(report.status)}
                        </Badge>
                        {template && (
                          <Badge className={`${CATEGORY_COLORS[template.category]} text-white`}>
                            {CATEGORY_LABELS[template.category]}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-muted-foreground">Last Updated</p>
                          <p className="font-medium">{report.lastUpdated}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Refresh Rate</p>
                          <p className="font-medium">{report.refreshInterval} hours</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Data Source</p>
                          <p className="font-medium">{report.dataSource}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Auto Refresh</p>
                          <p className="font-medium">{report.autoRefresh ? 'Enabled' : 'Disabled'}</p>
                        </div>
                      </div>
                      
                      <div className="flex gap-2">
                        {report.shareUrl && (
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => window.open(report.shareUrl, '_blank')}
                          >
                            <Eye className="w-4 h-4 mr-2" />
                            View Report
                          </Button>
                        )}
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => navigator.clipboard.writeText(report.shareUrl || '')}
                        >
                          <Share2 className="w-4 h-4 mr-2" />
                          Share
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => deleteReport(report.id)}
                        >
                          Delete
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>
        
        {/* Template Library */}
        <TabsContent value="templates" className="space-y-4">
          <h3 className="text-lg font-semibold">Report Template Library</h3>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {REPORT_TEMPLATES.map(template => (
              <Card 
                key={template.id} 
                className="border-border/20 bg-card/50 backdrop-blur-sm cursor-pointer hover:bg-card/70 transition-colors"
                onClick={() => {
                  setSelectedTemplate(template);
                  setIsCreatingReport(true);
                }}
              >
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">{template.name}</CardTitle>
                      <CardDescription>{template.description}</CardDescription>
                    </div>
                    <Badge className={`${CATEGORY_COLORS[template.category]} text-white`}>
                      {CATEGORY_LABELS[template.category]}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm text-muted-foreground mb-2">Metrics Included:</p>
                      <div className="flex flex-wrap gap-1">
                        {template.metrics.slice(0, 3).map(metric => (
                          <Badge key={metric} variant="outline" className="text-xs">
                            {metric}
                          </Badge>
                        ))}
                        {template.metrics.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{template.metrics.length - 3}
                          </Badge>
                        )}
                      </div>
                    </div>
                    
                    <div>
                      <p className="text-sm text-muted-foreground mb-2">Chart Types:</p>
                      <div className="flex flex-wrap gap-1">
                        {template.chartTypes.map(chart => (
                          <Badge key={chart} variant="secondary" className="text-xs">
                            {chart.replace('_', ' ')}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    
                    <Button className="w-full bg-cyan-600 hover:bg-cyan-700">
                      Use This Template
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
        
        {/* Create Report */}
        <TabsContent value="create" className="space-y-4">
          {!isCreatingReport ? (
            <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
              <CardContent className="p-8 text-center">
                <BarChart3 className="w-16 h-16 mx-auto mb-4 text-cyan-400 opacity-50" />
                <h3 className="text-lg font-semibold mb-2">Create New Data Studio Report</h3>
                <p className="text-muted-foreground mb-4">Choose a template or create a custom report from scratch</p>
                <Button 
                  onClick={() => setIsCreatingReport(true)}
                  className="bg-cyan-600 hover:bg-cyan-700"
                >
                  Start Creating
                </Button>
              </CardContent>
            </Card>
          ) : (
            <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Create New Report</CardTitle>
                <CardDescription>
                  {selectedTemplate ? `Based on template: ${selectedTemplate.name}` : 'Custom Report'}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {isGenerating ? (
                  <div className="space-y-4">
                    <div className="text-center">
                      <h3 className="text-lg font-semibold mb-2">Generating Report...</h3>
                      <Progress value={generationProgress} className="mb-4" />
                      <p className="text-sm text-muted-foreground">
                        {generationProgress < 20 ? 'Connecting to data source...' :
                         generationProgress < 40 ? 'Configuring chart components...' :
                         generationProgress < 60 ? 'Applying template styles...' :
                         generationProgress < 80 ? 'Setting up auto refresh...' : 'Report generation complete!'}
                      </p>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="report-name">Report Name</Label>
                        <Input
                          id="report-name"
                          value={newReport.name}
                          onChange={(e) => setNewReport(prev => ({ ...prev, name: e.target.value }))}
                          placeholder="Enter report name"
                        />
                      </div>
                      <div>
                        <Label htmlFor="data-source">Data Source</Label>
                        <Select 
                          value={newReport.dataSource} 
                          onValueChange={(value) => setNewReport(prev => ({ ...prev, dataSource: value }))}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select data source" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="default">Default Data Source</SelectItem>
                            <SelectItem value="pmf_analytics">PMF Analytics Data</SelectItem>
                            <SelectItem value="competitor_data">Competitor Data</SelectItem>
                            <SelectItem value="market_trends">Market Trends Data</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    
                    <div>
                      <Label htmlFor="description">Report Description</Label>
                      <Textarea
                        id="description"
                        value={newReport.description}
                        onChange={(e) => setNewReport(prev => ({ ...prev, description: e.target.value }))}
                        placeholder="Describe the purpose and content of the report"
                        rows={3}
                      />
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="flex items-center space-x-2">
                        <Switch
                          id="auto-refresh"
                          checked={newReport.autoRefresh}
                          onCheckedChange={(checked) => setNewReport(prev => ({ ...prev, autoRefresh: checked }))}
                        />
                        <Label htmlFor="auto-refresh">Enable Auto Refresh</Label>
                      </div>
                      
                      {newReport.autoRefresh && (
                        <div>
                          <Label htmlFor="refresh-interval">Refresh Interval (hours)</Label>
                          <Select 
                            value={newReport.refreshInterval.toString()} 
                            onValueChange={(value) => setNewReport(prev => ({ ...prev, refreshInterval: parseInt(value) }))}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="1">1 hour</SelectItem>
                              <SelectItem value="6">6 hours</SelectItem>
                              <SelectItem value="12">12 hours</SelectItem>
                              <SelectItem value="24">24 hours</SelectItem>
                              <SelectItem value="168">7 days</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      )}
                    </div>
                    
                    {selectedTemplate && (
                      <div className="p-4 rounded-lg bg-background/50">
                        <h4 className="font-semibold mb-2">Template Information</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                          <div>
                            <p className="text-muted-foreground">Metrics Included:</p>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {selectedTemplate.metrics.map(metric => (
                                <Badge key={metric} variant="outline" className="text-xs">
                                  {metric}
                                </Badge>
                              ))}
                            </div>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Chart Types:</p>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {selectedTemplate.chartTypes.map(chart => (
                                <Badge key={chart} variant="secondary" className="text-xs">
                                  {chart.replace('_', ' ')}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                    
                    <div className="flex gap-2">
                      <Button 
                        onClick={createReport}
                        className="bg-green-600 hover:bg-green-700"
                        disabled={!newReport.name}
                      >
                        <FileText className="w-4 h-4 mr-2" />
                        Generate Report
                      </Button>
                      <Button 
                        variant="outline" 
                        onClick={() => {
                          setIsCreatingReport(false);
                          setSelectedTemplate(null);
                          setNewReport({ name: '', description: '', autoRefresh: true, refreshInterval: 24, dataSource: 'default' });
                        }}
                      >
                        Cancel
                      </Button>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
