import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Header } from "./header";
import { useAuth } from "@/components/auth-provider";
import { useToast } from "@/components/ui/use-toast";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  PieChart, 
  Download, 
  Share2, 
  ArrowLeft,
  Calendar,
  Globe,
  Users,
  MessageSquare,
  Heart,
  Repeat2
} from "lucide-react";
import type { TrendAnalysis } from "../declarations";

export function AnalysisDetail() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  
  const [analysis, setAnalysis] = useState<TrendAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) {
      toast({
        title: "Login Required",
        description: "Please login to view analysis details",
        variant: "destructive",
      });
      navigate('/pricing');
      return;
    }

    if (!id) {
      toast({
        title: "Invalid Analysis ID",
        description: "The specified analysis result was not found",
        variant: "destructive",
      });
      navigate('/workspace');
      return;
    }

    fetchAnalysisDetail();
  }, [id, user]);

  const fetchAnalysisDetail = async () => {
    if (!id || !user) return;

    try {
      setLoading(true);
      setError(null);

      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      
      const response = await fetch(`${apiBaseUrl}/api/v1/analysis/${id}`, {
        headers: {
          'Authorization': `Bearer ${user.token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Analysis result does not exist');
        }
        throw new Error(`Failed to get analysis details: ${response.status}`);
      }

      const data = await response.json();
      setAnalysis(data);
    } catch (error) {
      console.error('Error fetching analysis detail:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred while getting analysis details';
      setError(errorMessage);
      
      toast({
        title: "Fetch Failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async () => {
    if (!analysis || !user) return;

    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      
      const response = await fetch(`${apiBaseUrl}/api/v1/reports/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`,
        },
        body: JSON.stringify({
          analysis_id: id,
          format: 'pdf'
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate report');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `analysis-report-${id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast({
        title: "Download Successful",
        description: "Analysis report has been downloaded locally",
      });
    } catch (error) {
      console.error('Error downloading report:', error);
      toast({
        title: "Download Failed",
        description: "An error occurred while generating the report",
        variant: "destructive",
      });
    }
  };

  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      toast({
        title: "Link Copied",
        description: "Analysis details link has been copied to clipboard",
      });
    } catch (error) {
      toast({
        title: "Copy Failed",
        description: "Unable to copy link to clipboard",
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
                <span className="text-white font-medium">Loading analysis details...</span>
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="glass-card rounded-xl p-8 border border-white/10 text-center">
              <h3 className="text-xl font-semibold text-white mb-4">Loading Failed</h3>
              <p className="text-gray-300 mb-6">{error || 'Analysis result not found'}</p>
              <div className="flex gap-4 justify-center">
                <Button onClick={() => navigate('/workspace')} variant="outline">
                  Back to Dashboard
                </Button>
                <Button onClick={fetchAnalysisDetail}>
                  Retry
                </Button>
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
          {/* Header Section */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/workspace')}
                className="text-gray-300 hover:text-white"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                 Back to Dashboard
               </Button>
               <div>
                 <h1 className="text-3xl font-bold text-white">Analysis Details</h1>
                 <p className="text-gray-300 mt-1">
                   Keywords: {analysis.keywords?.join(', ') || 'Unknown'}
                 </p>
               </div>
             </div>
             <div className="flex gap-3">
               <Button onClick={handleShare} variant="outline" size="sm">
                 <Share2 className="w-4 h-4 mr-2" />
                 Share
               </Button>
               <Button onClick={handleDownloadReport} size="sm">
                 <Download className="w-4 h-4 mr-2" />
                 Download Report
              </Button>
            </div>
          </div>

          {/* Analysis Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card className="glass-card border-white/10">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-gray-300 flex items-center gap-2">
                   <TrendingUp className="w-4 h-4" />
                   Trend Score
                 </CardTitle>
               </CardHeader>
               <CardContent>
                 <div className="text-2xl font-bold text-white">
                   {analysis.trend_score || 0}/100
                 </div>
                 <Badge variant={analysis.trend_score > 70 ? "default" : analysis.trend_score > 40 ? "secondary" : "destructive"}>
                   {analysis.trend_score > 70 ? "Strong" : analysis.trend_score > 40 ? "Moderate" : "Weak"}
                 </Badge>
               </CardContent>
             </Card>
 
             <Card className="glass-card border-white/10">
               <CardHeader className="pb-3">
                 <CardTitle className="text-sm font-medium text-gray-300 flex items-center gap-2">
                   <Users className="w-4 h-4" />
                   Engagement
                 </CardTitle>
               </CardHeader>
               <CardContent>
                 <div className="text-2xl font-bold text-white">
                   {analysis.engagement_metrics?.total_engagement || 0}
                 </div>
                 <p className="text-xs text-gray-400">Total Interactions</p>
               </CardContent>
             </Card>
 
             <Card className="glass-card border-white/10">
               <CardHeader className="pb-3">
                 <CardTitle className="text-sm font-medium text-gray-300 flex items-center gap-2">
                   <Globe className="w-4 h-4" />
                   Reach
                 </CardTitle>
               </CardHeader>
               <CardContent>
                 <div className="text-2xl font-bold text-white">
                   {analysis.reach_metrics?.total_reach || 0}
                 </div>
                 <p className="text-xs text-gray-400">Total Reach</p>
               </CardContent>
             </Card>
 
             <Card className="glass-card border-white/10">
               <CardHeader className="pb-3">
                 <CardTitle className="text-sm font-medium text-gray-300 flex items-center gap-2">
                   <Calendar className="w-4 h-4" />
                   Analysis Time
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-sm font-medium text-white">
                  {analysis.created_at ? new Date(analysis.created_at).toLocaleDateString('en-US') : 'Unknown'}
                </div>
                <p className="text-xs text-gray-400">Created Date</p>
              </CardContent>
            </Card>
          </div>

          {/* Detailed Analysis Tabs */}
          <Tabs defaultValue="trends" className="space-y-6">
            <TabsList className="grid w-full grid-cols-4 glass-card border-white/10">
              <TabsTrigger value="trends">Trend Analysis</TabsTrigger>
              <TabsTrigger value="sentiment">Sentiment Analysis</TabsTrigger>
              <TabsTrigger value="demographics">User Demographics</TabsTrigger>
              <TabsTrigger value="insights">Deep Insights</TabsTrigger>
            </TabsList>

            <TabsContent value="trends" className="space-y-6">
              <Card className="glass-card border-white/10">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <BarChart3 className="w-5 h-5" />
                    Trend Changes
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {analysis.trend_data?.map((trend, index) => (
                      <div key={index} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                        <div>
                          <h4 className="font-medium text-white">{trend.keyword}</h4>
                          <p className="text-sm text-gray-300">{trend.description}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          {trend.change > 0 ? (
                            <TrendingUp className="w-4 h-4 text-green-400" />
                          ) : (
                            <TrendingDown className="w-4 h-4 text-red-400" />
                          )}
                          <span className={`font-medium ${trend.change > 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {trend.change > 0 ? '+' : ''}{trend.change}%
                          </span>
                        </div>
                      </div>
                    )) || (
                      <p className="text-gray-400 text-center py-8">No trend data available</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="sentiment" className="space-y-6">
              <Card className="glass-card border-white/10">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Heart className="w-5 h-5" />
                    Sentiment Distribution
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-green-500/10 rounded-lg border border-green-500/20">
                      <div className="text-2xl font-bold text-green-400">
                        {analysis.sentiment_analysis?.positive || 0}%
                      </div>
                      <p className="text-sm text-green-300">Positive</p>
                    </div>
                    <div className="text-center p-4 bg-yellow-500/10 rounded-lg border border-yellow-500/20">
                      <div className="text-2xl font-bold text-yellow-400">
                        {analysis.sentiment_analysis?.neutral || 0}%
                      </div>
                      <p className="text-sm text-yellow-300">Neutral</p>
                    </div>
                    <div className="text-center p-4 bg-red-500/10 rounded-lg border border-red-500/20">
                      <div className="text-2xl font-bold text-red-400">
                        {analysis.sentiment_analysis?.negative || 0}%
                      </div>
                      <p className="text-sm text-red-300">Negative</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="demographics" className="space-y-6">
              <Card className="glass-card border-white/10">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <PieChart className="w-5 h-5" />
                    User Demographics
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium text-white mb-3">Age Distribution</h4>
                      <div className="space-y-2">
                        {analysis.demographics?.age_groups?.map((group, index) => (
                          <div key={index} className="flex justify-between items-center">
                            <span className="text-gray-300">{group.range}</span>
                            <span className="text-white font-medium">{group.percentage}%</span>
                          </div>
                        )) || <p className="text-gray-400">No data available</p>}
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium text-white mb-3">Geographic Distribution</h4>
                      <div className="space-y-2">
                        {analysis.demographics?.locations?.map((location, index) => (
                          <div key={index} className="flex justify-between items-center">
                            <span className="text-gray-300">{location.region}</span>
                            <span className="text-white font-medium">{location.percentage}%</span>
                          </div>
                        )) || <p className="text-gray-400">No data available</p>}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="insights" className="space-y-6">
              <Card className="glass-card border-white/10">
                <CardHeader>
                  <CardTitle className="text-white">Deep Insights</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {analysis.insights?.map((insight, index) => (
                      <div key={index} className="p-4 bg-white/5 rounded-lg">
                        <h4 className="font-medium text-white mb-2">{insight.title}</h4>
                        <p className="text-gray-300">{insight.description}</p>
                        {insight.confidence && (
                          <div className="mt-2">
                             <Badge variant="outline">
                               Confidence: {insight.confidence}%
                             </Badge>
                           </div>
                        )}
                      </div>
                    )) || (
                      <p className="text-gray-400 text-center py-8">No deep insights available</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  );
}