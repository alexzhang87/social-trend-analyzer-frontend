import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  TrendingUp, 
  Users, 
  Target, 
  BarChart3, 
  Heart,
  MessageCircle,
  Share2,
  Eye,
  ArrowRight,
  Sparkles,
  Crown,
  Lock
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/components/auth-provider';

// 示例分析数据
const DEMO_ANALYSES = {
  'AI Startup': {
    keyword: 'AI Startup',
    trend_score: 92,
    sentiment: {
      positive: 68,
      neutral: 25,
      negative: 7
    },
    keyThemes: [
      { theme: 'ChatGPT App Development', mentions: 1250, sentiment: 'positive' },
      { theme: 'AI Tool Startup', mentions: 890, sentiment: 'positive' },
      { theme: 'Machine Learning Platform', mentions: 650, sentiment: 'neutral' },
      { theme: 'AI Content Generation', mentions: 520, sentiment: 'positive' }
    ],
    topMentions: [
      { platform: 'Twitter', content: 'Just built a small tool with ChatGPT, got 100 user registrations in one day! AI startup really has potential', engagement: 2340 },
      { platform: 'Reddit', content: 'Sharing my AI startup journey: from idea to MVP in just 2 weeks', engagement: 1890 },
      { platform: 'LinkedIn', content: 'AI startup funding trend analysis: seed round valuations up 40%', engagement: 1560 }
    ],
    opportunities: [
      { title: 'AI Writing Assistant Tool', potential: 'High', market_size: '$2.3B', competition: 'Medium' },
      { title: 'AI Customer Service Chatbot', potential: 'High', market_size: '$1.8B', competition: 'High' },
      { title: 'AI Data Analytics Platform', potential: 'Medium', market_size: '$5.2B', competition: 'High' }
    ],
    userPersonas: [
      { type: 'Tech Entrepreneurs', percentage: 45, description: 'Technical background, seeking AI application scenarios' },
      { type: 'Traditional Business Owners', percentage: 30, description: 'Looking to improve business efficiency with AI' },
      { type: 'Investors', percentage: 25, description: 'Focused on AI startup investment opportunities' }
    ]
  },
  'Live Commerce': {
    keyword: 'Live Commerce',
    trend_score: 85,
    sentiment: {
      positive: 72,
      neutral: 20,
      negative: 8
    },
    keyThemes: [
      { theme: 'TikTok Live Streaming', mentions: 2100, sentiment: 'positive' },
      { theme: 'Social Commerce', mentions: 1650, sentiment: 'positive' },
      { theme: 'Product Selection Strategy', mentions: 1200, sentiment: 'neutral' },
      { theme: 'Influencer Training', mentions: 980, sentiment: 'positive' }
    ],
    topMentions: [
      { platform: 'TikTok', content: 'Made $30K in my first month of live commerce as a beginner, sharing my experience', engagement: 5670 },
      { platform: 'Instagram', content: 'Live commerce product selection guide: these categories have the highest conversion rates', engagement: 3240 },
      { platform: 'Twitter', content: '2024 live commerce market size expected to exceed $200B', engagement: 2890 }
    ],
    opportunities: [
      { title: 'Live Commerce Analytics Tool', potential: 'High', market_size: '$800M', competition: 'Medium' },
      { title: 'Influencer Training Platform', potential: 'Medium', market_size: '$1.2B', competition: 'Medium' },
      { title: 'Live Stream Data Analytics', potential: 'High', market_size: '$600M', competition: 'Low' }
    ],
    userPersonas: [
      { type: 'New Streamers', percentage: 40, description: 'Just starting live commerce, need guidance' },
      { type: 'Brand Partners', percentage: 35, description: 'Looking for suitable influencer collaborations' },
      { type: 'MCN Agencies', percentage: 25, description: 'Managing multiple streamers, need data support' }
    ]
  },
  'Electric Vehicles': {
    keyword: 'Electric Vehicles',
    trend_score: 88,
    sentiment: {
      positive: 65,
      neutral: 28,
      negative: 7
    },
    keyThemes: [
      { theme: 'Charging Infrastructure', mentions: 1800, sentiment: 'positive' },
      { theme: 'Battery Technology', mentions: 1500, sentiment: 'positive' },
      { theme: 'Autonomous Driving', mentions: 1200, sentiment: 'neutral' },
      { theme: 'Government Incentives', mentions: 950, sentiment: 'positive' }
    ],
    topMentions: [
      { platform: 'Twitter', content: 'Electric vehicle sales hit new record high, traditional automakers accelerate transformation', engagement: 4200 },
      { platform: 'LinkedIn', content: 'Charging station industry investment analysis: trillion-dollar market opportunity', engagement: 3100 },
      { platform: 'Reddit', content: 'EV battery recycling startup: win-win model of environmental protection + profit', engagement: 2650 }
    ],
    opportunities: [
      { title: 'Charging Station Platform', potential: 'High', market_size: '$15B', competition: 'Medium' },
      { title: 'Battery Recycling Service', potential: 'High', market_size: '$8B', competition: 'Low' },
      { title: 'EV Insurance Platform', potential: 'Medium', market_size: '$12B', competition: 'High' }
    ],
    userPersonas: [
      { type: 'Investment Firms', percentage: 35, description: 'Focus on clean energy supply chain investments' },
      { type: 'Entrepreneurs', percentage: 40, description: 'Seeking clean energy related business opportunities' },
      { type: 'Traditional Automakers', percentage: 25, description: 'Planning electrification transformation strategy' }
    ]
  }
};

export function DemoAnalysisShowcase() {
  const [selectedDemo, setSelectedDemo] = useState<keyof typeof DEMO_ANALYSES>('AI Startup');
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const currentDemo = DEMO_ANALYSES[selectedDemo];

  const handleTryAnalysis = () => {
    if (!user) {
      navigate('/pricing?trial=true');
    } else {
      navigate('/workspace');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      {/* 关键词选择 */}
      <div className="flex justify-center mb-8">
        <div className="flex gap-2 p-1 bg-gray-800/50 rounded-lg">
          {Object.keys(DEMO_ANALYSES).map((keyword) => (
            <button
              key={keyword}
              onClick={() => setSelectedDemo(keyword as keyof typeof DEMO_ANALYSES)}
              className={`px-4 py-2 rounded-md transition-all ${
                selectedDemo === keyword
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:text-white hover:bg-gray-700'
              }`}
            >
              {keyword}
            </button>
          ))}
        </div>
      </div>

      {/* Title Section */}
      <div className="text-center mb-8">
        <h2 className="text-4xl md:text-6xl font-black mb-6 tracking-tight leading-tight md:leading-tight">
          <span className="bg-gradient-to-r from-cyan-300 to-green-300 bg-clip-text text-transparent font-extrabold">
            Real-Time Trend Analysis Showcase
          </span>
        </h2>
        <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed mt-6 mb-12 font-medium">
          📊 Explore real AI analysis outputs
        </p>
      </div>

      {/* 分析结果展示 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">

        {/* Trend Overview */}
        <Card className="bg-gray-800/50 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white text-center">
              Trend Heat Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Heat Index</span>
                <span className="text-2xl font-bold text-green-500">{currentDemo.trend_score}%</span>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Positive Sentiment</span>
                  <span className="text-green-500">{currentDemo.sentiment.positive}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full" 
                    style={{ width: `${currentDemo.sentiment.positive}%` }}
                  ></div>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Neutral Sentiment</span>
                  <span className="text-yellow-500">{currentDemo.sentiment.neutral}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-yellow-500 h-2 rounded-full" 
                    style={{ width: `${currentDemo.sentiment.neutral}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Key Themes */}
        <Card className="bg-gray-800/50 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white text-center">
              Popular Discussion Topics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {currentDemo.keyThemes.slice(0, 4).map((theme, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="text-white font-medium">{theme.theme}</div>
                    <div className="text-sm text-gray-400">{theme.mentions.toLocaleString()} mentions</div>
                  </div>
                  <Badge 
                    variant={theme.sentiment === 'positive' ? 'default' : 'secondary'}
                    className="ml-2"
                  >
                    {theme.sentiment === 'positive' ? 'Positive' : 'Neutral'}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 详细分析结果 - 付费功能预览 */}
      <Tabs defaultValue="mentions" className="w-full">
        <TabsList className="grid w-full grid-cols-3 bg-gray-800/50">
          <TabsTrigger value="mentions" className="text-gray-300 data-[state=active]:text-white">
            Top Mentions
          </TabsTrigger>
          <TabsTrigger value="opportunities" className="text-gray-300 data-[state=active]:text-white">
            Business Opportunities <Crown className="ml-1 h-3 w-3 text-yellow-500" />
          </TabsTrigger>
          <TabsTrigger value="personas" className="text-gray-300 data-[state=active]:text-white">
            User Personas <Crown className="ml-1 h-3 w-3 text-yellow-500" />
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="mentions" className="mt-6">
          <div className="grid gap-4">
            {currentDemo.topMentions.map((mention, index) => (
              <Card key={index} className="bg-gray-800/30 border-gray-700">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <Badge variant="outline" className="text-xs">
                      {mention.platform}
                    </Badge>
                    <div className="flex items-center gap-1 text-gray-400 text-sm">
                      <Heart className="h-3 w-3" />
                      {mention.engagement.toLocaleString()}
                    </div>
                  </div>
                  <p className="text-gray-300">{mention.content}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
        
        <TabsContent value="opportunities" className="mt-6">
          <div className="relative">
            {/* 模糊遮罩效果 */}
            <div className="absolute inset-0 bg-gray-900/80 backdrop-blur-sm z-10 flex items-center justify-center rounded-lg">
              <div className="text-center">
                <Lock className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">Pro Feature</h3>
                <p className="text-gray-300 mb-4">Upgrade to Pro to unlock business opportunity analysis</p>
                <Button 
                  className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                  onClick={() => navigate('/pricing')}
                >
                  Upgrade Now
                </Button>
              </div>
            </div>
            
            <div className="grid gap-4 blur-sm">
              {currentDemo.opportunities.map((opp, index) => (
                <Card key={index} className="bg-gray-800/30 border-gray-700">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-white font-medium">{opp.title}</h4>
                      <Badge 
                        variant={opp.potential === '高' ? 'default' : 'secondary'}
                      >
                        {opp.potential} Potential
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-400">
                      <span>Market Size: {opp.market_size}</span>
                      <span>Competition: {opp.competition}</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </TabsContent>
        
        <TabsContent value="personas" className="mt-6">
          <div className="relative">
            {/* 模糊遮罩效果 */}
            <div className="absolute inset-0 bg-gray-900/80 backdrop-blur-sm z-10 flex items-center justify-center rounded-lg">
              <div className="text-center">
                <Lock className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">Pro Feature</h3>
                <p className="text-gray-300 mb-4">Upgrade to Pro to unlock user persona analysis</p>
                <Button 
                  className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                  onClick={() => navigate('/pricing')}
                >
                  Upgrade Now
                </Button>
              </div>
            </div>
            
            <div className="grid gap-4 blur-sm">
              {currentDemo.userPersonas.map((persona, index) => (
                <Card key={index} className="bg-gray-800/30 border-gray-700">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-white font-medium">{persona.type}</h4>
                      <span className="text-blue-500 font-bold">{persona.percentage}%</span>
                    </div>
                    <p className="text-gray-400 text-sm">{persona.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </TabsContent>
      </Tabs>

      {/* 行动召唤 */}
      <div className="text-center mt-12">
        <Card className="bg-gradient-to-r from-purple-900/50 to-blue-900/50 border-purple-500/30 max-w-2xl mx-auto">
          <CardContent className="p-8">
            <h3 className="text-2xl font-bold text-white mb-4">
              Start Analyzing Your Keywords
            </h3>
            <p className="text-gray-300 mb-6">
              {user ? 'Start your trend analysis now' : 'Sign up to get 3 free analysis opportunities'}
            </p>
            <Button 
              size="lg"
              className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
              onClick={handleTryAnalysis}
            >
              {user ? 'Start Analysis' : 'Try Free'}
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}