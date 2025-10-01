import React from "react";
import type { TrendAnalysis } from "../declarations";
import { OverviewCards } from "./overview-cards";
import { KeyThemesPanel } from "./key-themes-panel";
import { TrendChartPanel } from "./trend-chart-panel";
import { UserPersonaPanel } from "./user-persona-panel";
import { OpportunitiesPanel } from "./opportunities-panel";
import { TopMentionsPanel } from "./top-mentions-panel";
import { WordCloudPanel } from "./word-cloud-panel";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Separator } from "./ui/separator";
import { SubscriptionGate, useFeatureAccess } from "./subscription-gate";
import { Download, FileText, TrendingUp, Users, MessageCircle, BarChart3, Crown, Zap, Star } from "lucide-react";
import { useState } from "react";
import { useAuth } from "./auth-provider";

interface AnalysisResultsProps {
  data: TrendAnalysis | any; // Allow both TrendAnalysis and transformed data from workspace
  keywords?: string[];
  timeRange?: string;
  userTier?: string;
}

export function AnalysisResults({ data, keywords = [], timeRange, userTier = 'free' }: AnalysisResultsProps) {
  const [isExporting, setIsExporting] = useState(false);
  const { user } = useAuth();
  const { hasProAccess } = useFeatureAccess();
  
  // Handle both API response format and legacy format
  const analysisData = data.apiResponse || data;
  const keyThemes = analysisData.keyThemes || [];
  const sentimentSpectrum = analysisData.sentimentSpectrum || data.sentiment_analysis || { positive: 0, negative: 0, neutral: 0 };
  const topMentions = analysisData.top_mentions || data.top_mentions || [];
  const userPersonaSnapshot = analysisData.userPersonaSnapshot || data.user_personas || [];
  const actionableOpportunities = analysisData.actionableOpportunities || data.opportunities || [];
  
  // Determine available features based on subscription tier
  const tierConfig = {
    free: { 
      color: 'bg-gray-100 text-gray-800', 
      icon: Users, 
      label: 'FREE',
      features: ['Basic Trend Analysis', 'Simple Sentiment Analysis', 'Keyword Statistics']
    },
    starter: { 
      color: 'bg-blue-100 text-blue-800', 
      icon: Zap, 
      label: 'STARTER',
      features: ['AI Deep Insights', 'Smart Topic Extraction', 'User Persona Analysis', 'Word Cloud Visualization']
    },
    pro: { 
      color: 'bg-purple-100 text-purple-800', 
      icon: Crown, 
      label: 'PRO',
      features: ['Business Opportunity Identification', 'Competitive Analysis', 'PDF Report Export', 'Advanced Charts']
    }
  };
  
  const currentTier = tierConfig[userTier as keyof typeof tierConfig] || tierConfig.free;

  const handleExportReport = async () => {
    setIsExporting(true);
    try {
      // Fix: Use correct port number and environment variables
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';
      
      // Check if authentication token exists
      const token = localStorage.getItem('access_token');
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      
      // If token exists, add authentication header
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }
      
      const response = await fetch(`${apiBaseUrl}/api/v1/reports/generate-pdf-report`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          analysis_data: data,
          keywords: keywords
        }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `social_media_analysis_report_${new Date().toISOString().slice(0, 10)}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        const errorData = await response.json().catch(() => null);
        let errorMessage = 'Export failed, please try again later';
        
        // Handle authentication errors
        if (response.status === 401) {
          errorMessage = 'Login required to export report.';
        } else if (response.status === 403) {
          errorMessage = 'Your subscription plan does not support report export.';
        } else if (errorData?.detail) {
          errorMessage = errorData.detail;
        }
        
        console.error('Export report failed');
        alert(errorMessage);
      }
    } catch (error) {
      console.error('Export report error:', error);
      alert('Export failed, please try again later');
    } finally {
      setIsExporting(false);
    }
  };

  const handleDownloadSampleReport = async () => {
    try {
      // Fix: Use correct port number and environment variables
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';
      const response = await fetch(`${apiBaseUrl}/api/v1/reports/sample-report`);
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'sample_social_media_analysis_report.pdf';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        console.error('Download sample report failed');
        alert('Download sample report failed, please try again later');
      }
    } catch (error) {
      console.error('Download sample report error:', error);
      alert('Download sample report failed, please try again later');
    }
  };

  return (
    <div className="space-y-8 animate-slide-up">
      {/* Analysis overview header - modern design */}
      <div className="glass-card gradient-secondary rounded-xl border border-white/20 p-6 shadow-modern-lg">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-lg bg-white/20 backdrop-blur-sm">
                  <TrendingUp className="w-6 h-6 text-white animate-float" />
                </div>
                <h2 className="text-2xl font-bold text-white drop-shadow-lg">Trend Analysis Results</h2>
              </div>
              <Badge className={`${currentTier.color} shadow-modern animate-glow-pulse`}>
                {React.createElement(currentTier.icon, { className: "w-4 h-4 mr-1" })}
                {currentTier.label}
              </Badge>
            </div>
            <div className="flex flex-wrap gap-2">
              {keywords.map((keyword, index) => (
                <Badge key={index} variant="outline" className="bg-white/90 backdrop-blur-sm border-white/30 text-gray-800 shadow-sm hover:shadow-modern transition-all duration-300">
                  {keyword.trim()}
                </Badge>
              ))}
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-3">
            {userTier === 'pro' ? (
              <Button
                onClick={handleExportReport}
                disabled={isExporting}
                className="bg-white/20 backdrop-blur-sm border-white/30 text-white hover:bg-white/30 shadow-modern glow-hover transition-all duration-300 transform hover:scale-105"
              >
                <Download className="w-4 h-4 mr-2" />
                {isExporting ? 'Generating...' : 'Export Professional Report'}
              </Button>
            ) : (
              <Button
                variant="outline"
                disabled
                className="bg-white/10 border-white/30 text-white/70 opacity-60 cursor-not-allowed"
              >
                <Crown className="w-4 h-4 mr-2" />
                Upgrade to PRO
              </Button>
            )}
            <Button
              onClick={handleDownloadSampleReport}
              variant="outline"
              className="bg-white/20 backdrop-blur-sm border-white/30 text-white hover:bg-white/30 shadow-modern transition-all duration-300"
            >
              <FileText className="w-4 h-4 mr-2" />
              Sample Report
            </Button>
          </div>
        </div>
        

      </div>

      {/* Core Metrics Section */}
      <div className="bg-gradient-to-r from-blue-50/50 to-indigo-50/50 rounded-xl p-6 space-y-6">
        <div className="flex items-center gap-3">
          <div className="bg-blue-100 rounded-lg p-2">
            <BarChart3 className="w-5 h-5 text-blue-600" />
          </div>
          <div>
             <h2 className="text-xl font-semibold text-foreground">Core Metrics</h2>
             <p className="text-sm text-slate-600 dark:text-slate-300">Essential performance indicators and sentiment analysis</p>
           </div>
          <Badge variant="secondary" className="bg-green-100 text-green-700 ml-auto">
            Free
          </Badge>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {data.hypeIndex && data.sentimentSpectrum && (
            <OverviewCards hypeIndex={data.hypeIndex} sentimentSpectrum={data.sentimentSpectrum} />
          )}
        </div>
      </div>
      
      {/* Key Themes Section */}
      <div className="bg-gradient-to-r from-purple-50/50 to-pink-50/50 rounded-xl p-6 space-y-6">
        <div className="flex items-center gap-3">
          <div className="bg-purple-100 rounded-lg p-2">
            <MessageCircle className="w-5 h-5 text-purple-600" />
          </div>
          <div>
             <h2 className="text-xl font-semibold text-foreground">Key Themes</h2>
             <p className="text-sm text-slate-600 dark:text-slate-300">Discussion topics and emerging trends analysis</p>
           </div>
          <Badge variant="secondary" className="bg-green-100 text-green-700 ml-auto">
             Free
           </Badge>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <KeyThemesPanel themes={keyThemes} />
          {analysisData.hypeIndex && <TrendChartPanel hypeIndex={analysisData.hypeIndex} timeRange={timeRange} />}
        </div>
      </div>
      
      {/* Social Evidence Section */}
      {topMentions.length > 0 && (
        <div className="bg-gradient-to-r from-green-50/50 to-emerald-50/50 rounded-xl p-6 space-y-6">
          <div className="flex items-center gap-3">
            <div className="bg-green-100 rounded-lg p-2">
              <Users className="w-5 h-5 text-green-600" />
            </div>
            <div>
             <h2 className="text-xl font-semibold text-foreground">Social Evidence</h2>
             <p className="text-sm text-slate-600 dark:text-slate-300">Real user mentions and community discussions</p>
           </div>
            <Badge variant="secondary" className="bg-green-100 text-green-700 ml-auto">
              Free
            </Badge>
          </div>
          <TopMentionsPanel mentions={topMentions} />
        </div>
      )}
      
      {/* Advanced Insights Section - Starter+ */}
      <div className="bg-gradient-to-r from-orange-50/50 to-amber-50/50 rounded-xl p-6 space-y-6">
        <div className="flex items-center gap-3">
          <div className="bg-orange-100 rounded-lg p-2">
            <TrendingUp className="w-5 h-5 text-orange-600" />
          </div>
          <div>
             <h2 className="text-xl font-semibold text-foreground">Advanced Insights</h2>
             <p className="text-sm text-slate-600 dark:text-slate-300">Trend analysis and data visualization</p>
           </div>
          <Badge variant="secondary" className="bg-indigo-100 text-indigo-700 ml-auto">
             PRO
           </Badge>
        </div>
        <SubscriptionGate requiredTier="starter" userTier={userTier}>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {userTier === 'starter' || userTier === 'pro' ? (
              <WordCloudPanel keywords={keywords} />
            ) : null}
          </div>
        </SubscriptionGate>
      </div>
      
      {/* Business Insights Section - PRO users only */}
      <div className="bg-gradient-to-r from-indigo-50/50 to-violet-50/50 rounded-xl p-6 space-y-6">
        <div className="flex items-center gap-3">
          <div className="bg-indigo-100 rounded-lg p-2">
            <Star className="w-5 h-5 text-indigo-600" />
          </div>
          <div>
             <h2 className="text-xl font-semibold text-foreground">Business Insights</h2>
             <p className="text-sm text-slate-600 dark:text-slate-300">Market opportunities and user personas</p>
           </div>
          <Badge variant="secondary" className="bg-indigo-100 text-indigo-700 ml-auto">
            PRO
          </Badge>
        </div>
        <SubscriptionGate requiredTier="pro" userTier={userTier}>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <OpportunitiesPanel opportunities={actionableOpportunities} />
            <UserPersonaPanel snapshot={userPersonaSnapshot} />
          </div>
        </SubscriptionGate>
      </div>
      
      {/* Upgrade prompt - non-PRO users */}
      {userTier !== 'pro' && (
        <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
          <CardContent className="p-6">
            <div className="text-center space-y-4">
              <div className="flex justify-center">
                <div className="bg-blue-100 rounded-full p-3">
                  <Crown className="w-8 h-8 text-blue-600" />
                </div>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-foreground">Unlock Professional Features</h3>
                <p className="text-muted-foreground mt-2">
                  Upgrade to PRO to access business opportunity identification, user persona analysis, PDF report export, and advanced analytics features.
                </p>
              </div>
              <div className="flex justify-center gap-3">
                <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                  <Crown className="w-4 h-4 mr-2" />
                  Upgrade to PRO
                </Button>
                <Button variant="outline" className="border-blue-300 text-blue-600">
                  View Pricing
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
