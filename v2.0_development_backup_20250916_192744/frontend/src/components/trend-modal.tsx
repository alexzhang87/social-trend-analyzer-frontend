import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { TrendCluster } from "@/components/trend-analyzer"
import { FileText, Share2, CheckSquare, ExternalLink, Lock, Zap, Smile, Frown, Angry, Meh, Drama, UserCircle, ThumbsUp, MessageCircle } from "lucide-react"
import { XLogo } from "@/components/ui/x-logo"
import { RedditLogo } from "@/components/ui/reddit-logo"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';

interface TrendModalProps {
  cluster: TrendCluster
  onClose: () => void
}

export function TrendModal({ cluster, onClose }: TrendModalProps) {
  // In a real app, this would come from user auth state.
  const [isSubscribed, setIsSubscribed] = useState(false);

  const emotionData = cluster.emotion_analysis ? Object.entries(cluster.emotion_analysis).map(([name, value]) => ({ name: name.charAt(0).toUpperCase() + name.slice(1), value })).sort((a, b) => b.value - a.value) : [];

  const emotionVisuals: { [key: string]: { color: string; icon: React.ElementType } } = {
    Joy: { color: "#22c55e", icon: Smile },
    Sarcasm: { color: "#a855f7", icon: Drama },
    Sadness: { color: "#3b82f6", icon: Frown },
    Anger: { color: "#ef4444", icon: Angry },
    Neutral: { color: "#6b7280", icon: Meh },
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary to-green-400 flex items-center justify-center text-primary-foreground font-bold text-lg">
                {cluster.hot_score}
              </div>
              <DialogTitle className="text-xl">{cluster.title}</DialogTitle>
            </div>
            <div className="flex items-center space-x-2">
              {cluster.platforms.map(platform => (
                <Badge key={platform} variant="outline" className="flex items-center">
                  {platform === "x" && <XLogo className="w-4 h-4 mr-1" />}
                  {platform === "reddit" && <RedditLogo className="w-4 h-4 mr-1 text-orange-600" />}
                  <span className="capitalize">{platform}</span>
                </Badge>
              ))}
            </div>
          </div>
        </DialogHeader>
        
        <Tabs defaultValue="overview" className="mt-4">
          <TabsList className="grid w-full grid-cols-6 mb-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="trend-analysis">Trend Analysis</TabsTrigger>
            <TabsTrigger value="pain-points">Pain Points</TabsTrigger>
            <TabsTrigger value="opportunities">Opportunities</TabsTrigger>
            <TabsTrigger value="mvp-plan">MVP Plan</TabsTrigger>
            <TabsTrigger value="data">Data</TabsTrigger>
          </TabsList>
          
          <TabsContent value="overview" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Core Need</CardTitle>
                <CardDescription>A one-sentence summary based on data analysis.</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-lg font-medium">{cluster.pain_points[0].text}</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Keywords</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {cluster.keywords.map(keyword => (
                    <Badge key={keyword} className="px-3 py-1">
                      {keyword}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Trend Overview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground">Hot Score</h4>
                    <p className="text-2xl font-bold">{cluster.hot_score}/100</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground">Confidence</h4>
                    <p className="text-2xl font-bold">{Math.round(cluster.pain_points[0].confidence * 100)}%</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="trend-analysis" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>7-Day Hot Score Trend</CardTitle>
                <CardDescription>Visualizing the trend's momentum over the past week.</CardDescription>
              </CardHeader>
              <CardContent className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={cluster.trend_history} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tickFormatter={(str) => new Date(str).toLocaleDateString('en-us', { month: 'short', day: 'numeric' })} />
                    <YAxis />
                    <Tooltip 
                      contentStyle={{
                        backgroundColor: 'hsl(var(--background))',
                        borderColor: 'hsl(var(--border))'
                      }}
                    />
                    <Legend />
                    <Line type="monotone" dataKey="score" stroke="hsl(var(--primary))" strokeWidth={2} name="Hot Score" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
            
            {cluster.emotion_analysis && (
              <Card>
                <CardHeader>
                  <CardTitle>Emotion Analysis</CardTitle>
                  <CardDescription>Breakdown of emotions detected in mentions.</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {emotionData.map((emotion) => {
                      const EmotionIcon = emotionVisuals[emotion.name]?.icon || Meh;
                      return (
                        <div key={emotion.name} className="flex items-center">
                          <EmotionIcon className="w-5 h-5 mr-3" style={{ color: emotionVisuals[emotion.name]?.color }} />
                          <span className="w-24 font-medium">{emotion.name}</span>
                          <div className="flex-1 bg-muted rounded-full h-4">
                            <div 
                              className="h-4 rounded-full" 
                              style={{ 
                                width: `${(emotion.value / Math.max(...emotionData.map(e => e.value))) * 100}%`,
                                backgroundColor: emotionVisuals[emotion.name]?.color 
                              }}
                            />
                          </div>
                          <span className="w-12 text-right font-mono text-sm">{emotion.value}</span>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>
          
          <TabsContent value="pain-points" className="space-y-4">
            {cluster.pain_points.map((pain, index) => (
              <Card key={index}>
                <CardHeader>
                  <CardTitle className="text-lg">Pain Point #{index + 1}</CardTitle>
                  <CardDescription>
                    <Badge variant="outline">{pain.intent}</Badge>
                    <span className="ml-2 text-sm">Severity: {pain.severity}/100</span>
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-lg font-medium">{pain.text}</p>
                  
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground mb-2">Evidence from Social Mentions:</h4>
                    <div className="space-y-4">
                      {pain.evidence.map((evidence, i) => {
                        const sentiment = i % 3 === 0 ? "Positive" : i % 3 === 1 ? "Sarcasm" : "Negative";
                        const sentimentColor = sentiment === "Positive" ? "bg-green-100 text-green-800" : sentiment === "Sarcasm" ? "bg-purple-100 text-purple-800" : "bg-red-100 text-red-800";
                        
                        return (
                          <div key={i} className="border rounded-lg p-4 space-y-3 bg-white shadow-sm">
                            <div className="flex justify-between items-start">
                              <div className="flex items-center space-x-3">
                                <UserCircle className="w-9 h-9 text-muted-foreground" />
                                <div>
                                  <p className="font-semibold text-sm">{evidence.author}</p>
                                  <div className="flex items-center text-xs text-muted-foreground">
                                    {evidence.platform === "x" && <XLogo className="w-3 h-3 mr-1" />}
                                    {evidence.platform === "reddit" && <RedditLogo className="w-3 h-3 mr-1 text-orange-600" />}
                                    <span className="capitalize">{evidence.platform}</span>
                                  </div>
                                </div>
                              </div>
                              <Badge className={`text-xs ${sentimentColor}`}>{sentiment}</Badge>
                            </div>
                            
                            <p className="text-sm text-foreground/90 italic">"{evidence.text}"</p>
                            
                            <div className="flex justify-between items-center text-xs text-muted-foreground pt-2 border-t">
                              <div className="flex items-center space-x-4">
                                <div className="flex items-center">
                                  <ThumbsUp className="w-3.5 h-3.5 mr-1" />
                                  <span>{(i + 1) * 23 + 10}</span>
                                </div>
                                <div className="flex items-center">
                                  <MessageCircle className="w-3.5 h-3.5 mr-1" />
                                  <span>{(i + 1) * 5 - 2}</span>
                                </div>
                              </div>
                              <Button variant="ghost" size="sm" className="h-6 text-xs">
                                <ExternalLink className="w-3 h-3 mr-1" />
                                View Original
                              </Button>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>
          
          <TabsContent value="opportunities" className="space-y-4">
            {cluster.opportunities.map((opportunity, index) => (
              <Card key={index}>
                <CardHeader>
                  <CardTitle className="text-lg">Opportunity #{index + 1}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-lg font-medium mb-4">{opportunity.text}</p>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h4 className="text-sm font-medium text-muted-foreground">Potential Impact</h4>
                      <div className="flex items-center mt-1">
                        {Array(10).fill(0).map((_, i) => (
                          <div 
                            key={i} 
                            className={`w-6 h-2 mr-0.5 rounded-sm ${
                              i < opportunity.impact ? 'bg-primary' : 'bg-muted'
                            }`}
                          />
                        ))}
                        <span className="ml-2 text-sm">{opportunity.impact}/10</span>
                      </div>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-muted-foreground">Effort Required</h4>
                      <div className="flex items-center mt-1">
                        {Array(10).fill(0).map((_, i) => (
                          <div 
                            key={i} 
                            className={`w-6 h-2 mr-0.5 rounded-sm ${
                              i < opportunity.effort ? 'bg-secondary' : 'bg-muted'
                            }`}
                          />
                        ))}
                        <span className="ml-2 text-sm">{opportunity.effort}/10</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>
          
          <TabsContent value="mvp-plan" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>7-Day MVP Plan</CardTitle>
                <CardDescription>{cluster.mvp_1week.goal}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 relative">
                {!isSubscribed && (
                  <div className="absolute inset-0 bg-background/80 backdrop-blur-sm flex flex-col items-center justify-center z-10 rounded-lg">
                    <Lock className="w-12 h-12 text-primary mb-4" />
                    <h3 className="text-xl font-bold">Unlock the Full MVP Plan</h3>
                    <p className="text-muted-foreground mb-4">Get detailed daily tasks, resource planning, and budget estimates.</p>
                    <Button onClick={() => setIsSubscribed(true)}>
                      <Zap className="w-4 h-4 mr-2" />
                      Upgrade to Pro
                    </Button>
                  </div>
                )}
                <div className={!isSubscribed ? 'filter blur-sm' : ''}>
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground mb-2">Daily Plan:</h4>
                    <div className="space-y-2">
                      {Array.isArray(cluster.mvp_1week.days) && cluster.mvp_1week.days.map((day, index) => (
                        <div key={index} className="flex items-start">
                          <div className="w-24 font-medium shrink-0">{day.split(': ')[0]}:</div>
                          <div>{day.split(': ')[1]}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 pt-2">
                    <div>
                      <h4 className="text-sm font-medium text-muted-foreground mb-1">Resources</h4>
                      <p>{cluster.mvp_1week.resources}</p>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-muted-foreground mb-1">Budget Estimate</h4>
                      <p>${cluster.mvp_1week.budget_usd}</p>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground mb-1">KPI & Go/No-Go Criteria</h4>
                  <p>{cluster.mvp_1week.kpi}</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="data" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Data & Methodology</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground">Sample Size</h4>
                    <p>X: 500 tweets, Reddit: 300 posts</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground">Time Window</h4>
                    <p>August 1, 2025 - August 7, 2025</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground">Hot Score Calculation</h4>
                    <p className="text-sm">The Hot Score combines growth rate, mention volume, engagement, and cross-platform presence. A higher score indicates a more promising trend.</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
        
        <DialogFooter className="flex justify-between items-center mt-6">
          <div className="flex space-x-2">
            <Button variant="outline" size="sm">
              <FileText className="w-4 h-4 mr-2" />
              Export PDF
            </Button>
            <Button variant="outline" size="sm">
              <Share2 className="w-4 h-4 mr-2" />
              Share
            </Button>
          </div>
          <Button size="sm">
            <CheckSquare className="w-4 h-4 mr-2" />
            Start MVP
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
