import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { AlertTriangle, Shield, TrendingUp, Eye, Plus, X, Bell, Activity, Users, DollarSign } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

interface Competitor {
  id: string;
  name: string;
  website: string;
  category: string;
  threatLevel: 'low' | 'medium' | 'high' | 'critical';
  lastUpdated: string;
  metrics: {
    marketShare: number;
    funding: number;
    employees: number;
    socialMentions: number;
    productUpdates: number;
  };
  alerts: CompetitorAlert[];
}

interface CompetitorAlert {
  id: string;
  type: 'funding' | 'product_launch' | 'market_expansion' | 'partnership' | 'acquisition';
  title: string;
  description: string;
  severity: 'info' | 'warning' | 'danger';
  date: string;
  source: string;
}

interface CompetitorAlertProps {
  onThreatDetected?: (competitor: Competitor, alert: CompetitorAlert) => void;
}

const THREAT_LEVELS = {
  low: { label: 'Low Threat', color: 'bg-green-500', textColor: 'text-green-700' },
  medium: { label: 'Medium Threat', color: 'bg-yellow-500', textColor: 'text-yellow-700' },
  high: { label: 'High Threat', color: 'bg-orange-500', textColor: 'text-orange-700' },
  critical: { label: 'Critical Threat', color: 'bg-red-500', textColor: 'text-red-700' }
};

const ALERT_TYPES = {
  funding: { label: 'Funding Updates', icon: DollarSign, color: 'text-green-400' },
  product_launch: { label: 'Product Launch', icon: TrendingUp, color: 'text-blue-400' },
  market_expansion: { label: 'Market Expansion', icon: Users, color: 'text-purple-400' },
  partnership: { label: 'Partnerships', icon: Shield, color: 'text-cyan-400' },
  acquisition: { label: 'Acquisitions', icon: AlertTriangle, color: 'text-red-400' }
};

const MOCK_COMPETITORS: Competitor[] = [
  {
    id: '1',
    name: 'IdeaEden AI',
        website: 'https://ideaeden.ai',
    category: 'Social Media Analytics',
    threatLevel: 'high',
    lastUpdated: '2024-01-15',
    metrics: {
      marketShare: 15.2,
      funding: 50000000,
      employees: 120,
      socialMentions: 2500,
      productUpdates: 8
    },
    alerts: [
      {
        id: 'a1',
        type: 'funding',
        title: 'Completed $50M Series B Funding',
        description: 'IdeaEden AI announced completion of $50M Series B funding for AI technology R&D and market expansion',
        severity: 'danger',
        date: '2024-01-15',
        source: 'TechCrunch'
      },
      {
        id: 'a2',
        type: 'product_launch',
        title: 'Launched Real-time Sentiment Analysis',
        description: 'Added real-time social media sentiment analysis with multi-language and multi-platform support',
        severity: 'warning',
        date: '2024-01-10',
        source: 'Product Hunt'
      }
    ]
  },
  {
    id: '2',
    name: 'SocialInsight Pro',
    website: 'https://socialinsight.pro',
    category: 'Social Media Analytics',
    threatLevel: 'medium',
    lastUpdated: '2024-01-12',
    metrics: {
      marketShare: 8.7,
      funding: 15000000,
      employees: 45,
      socialMentions: 1200,
      productUpdates: 3
    },
    alerts: [
      {
        id: 'a3',
        type: 'partnership',
        title: 'Strategic Partnership with Meta',
        description: 'Obtained Meta official API partner status with access to deeper data insights',
        severity: 'warning',
        date: '2024-01-12',
        source: 'Meta Official Blog'
      }
    ]
  }
];

export function CompetitorAlert({ onThreatDetected }: CompetitorAlertProps) {
  const [competitors, setCompetitors] = useState<Competitor[]>(MOCK_COMPETITORS);
  const [newCompetitor, setNewCompetitor] = useState({ name: '', website: '', category: '' });
  const [isAddingCompetitor, setIsAddingCompetitor] = useState(false);
  const [selectedCompetitor, setSelectedCompetitor] = useState<Competitor | null>(null);
  const [alertFilter, setAlertFilter] = useState<string>('all');

  // Calculate threat score
  const calculateThreatScore = (competitor: Competitor): number => {
    const { metrics } = competitor;
    const weights = {
      marketShare: 0.3,
      funding: 0.25,
      employees: 0.15,
      socialMentions: 0.15,
      productUpdates: 0.15
    };
    
    // Normalize metrics (assuming maximum values)
    const normalized = {
      marketShare: Math.min(metrics.marketShare / 50, 1),
      funding: Math.min(metrics.funding / 100000000, 1),
      employees: Math.min(metrics.employees / 500, 1),
      socialMentions: Math.min(metrics.socialMentions / 10000, 1),
      productUpdates: Math.min(metrics.productUpdates / 20, 1)
    };
    
    return Object.entries(weights).reduce((score, [key, weight]) => {
      return score + (normalized[key as keyof typeof normalized] * weight * 100);
    }, 0);
  };

  // Add competitor
  const addCompetitor = () => {
    if (!newCompetitor.name || !newCompetitor.website) return;
    
    const competitor: Competitor = {
      id: Date.now().toString(),
      name: newCompetitor.name,
      website: newCompetitor.website,
      category: newCompetitor.category || 'Uncategorized',
      threatLevel: 'low',
      lastUpdated: new Date().toISOString().split('T')[0],
      metrics: {
        marketShare: 0,
        funding: 0,
        employees: 0,
        socialMentions: 0,
        productUpdates: 0
      },
      alerts: []
    };
    
    setCompetitors(prev => [...prev, competitor]);
    setNewCompetitor({ name: '', website: '', category: '' });
    setIsAddingCompetitor(false);
  };

  // Remove competitor
  const removeCompetitor = (id: string) => {
    setCompetitors(prev => prev.filter(c => c.id !== id));
    if (selectedCompetitor?.id === id) {
      setSelectedCompetitor(null);
    }
  };

  // Get all alerts
  const allAlerts = competitors.flatMap(competitor => 
    competitor.alerts.map(alert => ({ ...alert, competitorName: competitor.name }))
  ).sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

  // Filter alerts
  const filteredAlerts = alertFilter === 'all' 
    ? allAlerts 
    : allAlerts.filter(alert => alert.type === alertFilter);

  // Threat trend data
  const threatTrendData = competitors.map(competitor => ({
    name: competitor.name,
    threatScore: calculateThreatScore(competitor),
    marketShare: competitor.metrics.marketShare
  }));

  return (
    <div className="space-y-6">
      {/* Threat Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Monitored Competitors</p>
                <p className="text-2xl font-bold text-white">{competitors.length}</p>
              </div>
              <Eye className="w-8 h-8 text-cyan-400" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">High Threat Competitors</p>
                <p className="text-2xl font-bold text-red-400">
                  {competitors.filter(c => c.threatLevel === 'high' || c.threatLevel === 'critical').length}
                </p>
              </div>
              <AlertTriangle className="w-8 h-8 text-red-400" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">New Alerts</p>
                <p className="text-2xl font-bold text-yellow-400">
                  {allAlerts.filter(a => new Date(a.date) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)).length}
                </p>
              </div>
              <Bell className="w-8 h-8 text-yellow-400" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Activity Level</p>
                <p className="text-2xl font-bold text-green-400">85%</p>
              </div>
              <Activity className="w-8 h-8 text-green-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="competitors" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="competitors">Competitor Monitoring</TabsTrigger>
          <TabsTrigger value="alerts">Threat Alerts</TabsTrigger>
          <TabsTrigger value="analysis">Competitive Analysis</TabsTrigger>
        </TabsList>
        
        {/* Competitor Monitoring */}
        <TabsContent value="competitors" className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Competitor List</h3>
            <Button 
              onClick={() => setIsAddingCompetitor(true)}
              className="bg-cyan-600 hover:bg-cyan-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Competitor
            </Button>
          </div>
          
          {/* Add Competitor Form */}
          {isAddingCompetitor && (
            <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Add New Competitor</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <Label htmlFor="name">Company Name</Label>
                    <Input
                      id="name"
                      value={newCompetitor.name}
                      onChange={(e) => setNewCompetitor(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="Enter company name"
                    />
                  </div>
                  <div>
                    <Label htmlFor="website">Website URL</Label>
                    <Input
                      id="website"
                      value={newCompetitor.website}
                      onChange={(e) => setNewCompetitor(prev => ({ ...prev, website: e.target.value }))}
                      placeholder="https://example.com"
                    />
                  </div>
                  <div>
                    <Label htmlFor="category">Business Category</Label>
                    <Input
                      id="category"
                      value={newCompetitor.category}
                      onChange={(e) => setNewCompetitor(prev => ({ ...prev, category: e.target.value }))}
                      placeholder="e.g., Social Media Analytics"
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button onClick={addCompetitor} className="bg-green-600 hover:bg-green-700">
                    Add
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => setIsAddingCompetitor(false)}
                  >
                    Cancel
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
          
          {/* Competitor List */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {competitors.map(competitor => {
              const threatScore = calculateThreatScore(competitor);
              const threatConfig = THREAT_LEVELS[competitor.threatLevel];
              
              return (
                <Card 
                  key={competitor.id} 
                  className="border-border/20 bg-card/50 backdrop-blur-sm cursor-pointer hover:bg-card/70 transition-colors"
                  onClick={() => setSelectedCompetitor(competitor)}
                >
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-lg">{competitor.name}</CardTitle>
                        <CardDescription>{competitor.category}</CardDescription>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={`${threatConfig.color} text-white`}>
                          {threatConfig.label}
                        </Badge>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            removeCompetitor(competitor.id);
                          }}
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Threat Score</p>
                        <p className="font-semibold">{threatScore.toFixed(1)}/100</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Market Share</p>
                        <p className="font-semibold">{competitor.metrics.marketShare}%</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Funding</p>
                        <p className="font-semibold">${(competitor.metrics.funding / 1000000).toFixed(1)}M</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Team Size</p>
                        <p className="font-semibold">{competitor.metrics.employees} people</p>
                      </div>
                    </div>
                    {competitor.alerts.length > 0 && (
                      <div className="mt-4">
                        <p className="text-sm text-muted-foreground mb-2">Latest Alerts:</p>
                        <div className="space-y-1">
                          {competitor.alerts.slice(0, 2).map(alert => (
                            <div key={alert.id} className="text-xs p-2 rounded bg-background/50">
                              <span className={`font-medium ${
                                alert.severity === 'danger' ? 'text-red-400' :
                                alert.severity === 'warning' ? 'text-yellow-400' : 'text-blue-400'
                              }`}>
                                {alert.title}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>
        
        {/* Threat Alerts */}
        <TabsContent value="alerts" className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Threat Alerts</h3>
            <Select value={alertFilter} onValueChange={setAlertFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter alert types" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Alerts</SelectItem>
                {Object.entries(ALERT_TYPES).map(([key, config]) => (
                  <SelectItem key={key} value={key}>{config.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div className="space-y-3">
            {filteredAlerts.map(alert => {
              const alertConfig = ALERT_TYPES[alert.type];
              const IconComponent = alertConfig.icon;
              
              return (
                <Card key={alert.id} className="border-border/20 bg-card/50 backdrop-blur-sm">
                  <CardContent className="p-4">
                    <div className="flex items-start gap-4">
                      <div className={`p-2 rounded-lg bg-background/50`}>
                        <IconComponent className={`w-5 h-5 ${alertConfig.color}`} />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-semibold">{alert.title}</h4>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline">{alertConfig.label}</Badge>
                            <Badge className={`${
                              alert.severity === 'danger' ? 'bg-red-500' :
                              alert.severity === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
                            } text-white`}>
                              {alert.severity === 'danger' ? 'High Risk' :
                               alert.severity === 'warning' ? 'Warning' : 'Info'}
                            </Badge>
                          </div>
                        </div>
                        <p className="text-sm text-muted-foreground mb-2">{alert.description}</p>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span>Competitor: {(alert as any).competitorName}</span>
                          <span>Source: {alert.source}</span>
                          <span>Time: {alert.date}</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>
        
        {/* Competitive Analysis */}
        <TabsContent value="analysis" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Threat Score Comparison */}
            <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Threat Score Comparison</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={threatTrendData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" className="text-xs" />
                    <YAxis className="text-xs" />
                    <Tooltip />
                    <Bar dataKey="threatScore" fill="#06b6d4" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
            
            {/* Market Share Distribution */}
            <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Market Share Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={threatTrendData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" className="text-xs" />
                    <YAxis className="text-xs" />
                    <Tooltip />
                    <Bar dataKey="marketShare" fill="#10b981" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
      
      {/* Competitor Details Modal */}
      {selectedCompetitor && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto border-border/20 bg-card/95 backdrop-blur-sm">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-xl">{selectedCompetitor.name}</CardTitle>
                  <CardDescription>{selectedCompetitor.website}</CardDescription>
                </div>
                <Button 
                  variant="ghost" 
                  onClick={() => setSelectedCompetitor(null)}
                >
                  <X className="w-5 h-5" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Detailed Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="text-center">
                  <p className="text-sm text-muted-foreground">Market Share</p>
                  <p className="text-2xl font-bold text-cyan-400">{selectedCompetitor.metrics.marketShare}%</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-muted-foreground">Funding</p>
                  <p className="text-2xl font-bold text-green-400">${(selectedCompetitor.metrics.funding / 1000000).toFixed(1)}M</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-muted-foreground">Team Size</p>
                  <p className="text-2xl font-bold text-blue-400">{selectedCompetitor.metrics.employees}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-muted-foreground">Social Mentions</p>
                  <p className="text-2xl font-bold text-purple-400">{selectedCompetitor.metrics.socialMentions}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-muted-foreground">Product Updates</p>
                  <p className="text-2xl font-bold text-yellow-400">{selectedCompetitor.metrics.productUpdates}</p>
                </div>
              </div>
              
              {/* Alert History */}
              <div>
                <h4 className="font-semibold mb-4">Alert History</h4>
                <div className="space-y-3">
                  {selectedCompetitor.alerts.map(alert => {
                    const alertConfig = ALERT_TYPES[alert.type];
                    const IconComponent = alertConfig.icon;
                    
                    return (
                      <div key={alert.id} className="p-4 rounded-lg bg-background/50">
                        <div className="flex items-start gap-3">
                          <IconComponent className={`w-5 h-5 ${alertConfig.color} mt-0.5`} />
                          <div className="flex-1">
                            <h5 className="font-medium">{alert.title}</h5>
                            <p className="text-sm text-muted-foreground mt-1">{alert.description}</p>
                            <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                              <span>Source: {alert.source}</span>
                              <span>Time: {alert.date}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}