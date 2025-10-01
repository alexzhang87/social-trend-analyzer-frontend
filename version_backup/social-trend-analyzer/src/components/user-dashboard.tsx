import React, { useState, useEffect } from 'react';
import { useAuth } from '@/components/auth-provider';
import { useNavigate } from 'react-router-dom';
import { Header } from './header';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  TrendingUp, 
  Search, 
  Clock, 
  Star, 
  ArrowRight, 
  Zap,
  BarChart3,
  Users,
  Target,
  Crown,
  Sparkles
} from 'lucide-react';

// 示例数据 - 展示产品价值
const DEMO_ANALYSES = [
  {
    id: '1',
    keyword: 'AI创业',
    date: '2024-01-15',
    trend_score: 85,
    sentiment: 'positive',
    opportunities: 12,
    status: 'completed'
  },
  {
    id: '2', 
    keyword: '区块链应用',
    date: '2024-01-14',
    trend_score: 72,
    sentiment: 'neutral',
    opportunities: 8,
    status: 'completed'
  },
  {
    id: '3',
    keyword: '电商直播',
    date: '2024-01-13', 
    trend_score: 91,
    sentiment: 'positive',
    opportunities: 15,
    status: 'completed'
  }
];

const TRENDING_KEYWORDS = [
  { keyword: 'ChatGPT应用', growth: '+156%', category: 'AI科技' },
  { keyword: '新能源汽车', growth: '+89%', category: '汽车行业' },
  { keyword: '直播带货', growth: '+67%', category: '电商零售' },
  { keyword: '元宇宙游戏', growth: '+45%', category: '游戏娱乐' }
];

export function UserDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [analysisCount, setAnalysisCount] = useState(0);
  const [maxAnalyses, setMaxAnalyses] = useState(3);

  useEffect(() => {
    // 模拟获取用户使用情况
    if (user) {
      // 根据用户等级设置限制
      const userTier = user.subscription_tier || 'free';
      if (userTier === 'free') {
        setMaxAnalyses(3);
        setAnalysisCount(1); // 假设已使用1次
      } else if (userTier === 'pro') {
        setMaxAnalyses(-1); // 无限制
      }
    }
  }, [user]);

  const handleQuickAnalysis = (keyword: string) => {
    navigate(`/workspace?section=analysis&keywords=${encodeURIComponent(keyword)}`);
  };

  const handleViewAnalysis = (id: string) => {
    navigate(`/workspace?section=analysis&demo=${id}`);
  };

  const remainingAnalyses = maxAnalyses === -1 ? '无限制' : Math.max(0, maxAnalyses - analysisCount);
  const usageProgress = maxAnalyses === -1 ? 0 : (analysisCount / maxAnalyses) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        {/* 欢迎区域 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">
            欢迎回来，{user?.username || '用户'}！
          </h1>
          <p className="text-gray-300">
            发现下一个商业机会，让数据驱动您的创业决策
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* 使用统计卡片 */}
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">
                剩余分析次数
              </CardTitle>
              <Zap className="h-4 w-4 text-yellow-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white mb-2">
                {remainingAnalyses}
              </div>
              {maxAnalyses !== -1 && (
                <>
                  <Progress value={usageProgress} className="mb-2" />
                  <p className="text-xs text-gray-400">
                    已使用 {analysisCount}/{maxAnalyses} 次
                  </p>
                </>
              )}
            </CardContent>
          </Card>

          {/* 趋势洞察卡片 */}
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">
                发现的商机
              </CardTitle>
              <Target className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white mb-2">
                35+
              </div>
              <p className="text-xs text-gray-400">
                基于您的分析历史
              </p>
            </CardContent>
          </Card>

          {/* 会员状态卡片 */}
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">
                会员等级
              </CardTitle>
              <Crown className="h-4 w-4 text-purple-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white mb-2">
                {user?.subscription_tier === 'pro' ? 'Pro' : 'Free'}
              </div>
              {user?.subscription_tier !== 'pro' && (
                <Button 
                  size="sm" 
                  className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                  onClick={() => navigate('/pricing')}
                >
                  升级 Pro
                </Button>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 快速分析区域 */}
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-yellow-500" />
                热门趋势分析
              </CardTitle>
              <CardDescription className="text-gray-400">
                一键分析当前最热门的创业关键词
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {TRENDING_KEYWORDS.map((item, index) => (
                <div 
                  key={index}
                  className="flex items-center justify-between p-3 bg-gray-700/30 rounded-lg hover:bg-gray-700/50 transition-colors cursor-pointer"
                  onClick={() => handleQuickAnalysis(item.keyword)}
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-white font-medium">{item.keyword}</span>
                      <Badge variant="secondary" className="text-xs">
                        {item.category}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <TrendingUp className="h-3 w-3 text-green-500" />
                      <span className="text-green-500 text-sm font-medium">{item.growth}</span>
                    </div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-gray-400" />
                </div>
              ))}
            </CardContent>
          </Card>

          {/* 分析历史 */}
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Clock className="h-5 w-5 text-blue-500" />
                最近分析
              </CardTitle>
              <CardDescription className="text-gray-400">
                查看您的分析历史和发现的商机
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {DEMO_ANALYSES.map((analysis) => (
                <div 
                  key={analysis.id}
                  className="flex items-center justify-between p-3 bg-gray-700/30 rounded-lg hover:bg-gray-700/50 transition-colors cursor-pointer"
                  onClick={() => handleViewAnalysis(analysis.id)}
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-white font-medium">{analysis.keyword}</span>
                      <Badge 
                        variant={analysis.sentiment === 'positive' ? 'default' : 'secondary'}
                        className="text-xs"
                      >
                        {analysis.sentiment === 'positive' ? '积极' : '中性'}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-400">
                      <span className="flex items-center gap-1">
                        <BarChart3 className="h-3 w-3" />
                        趋势: {analysis.trend_score}%
                      </span>
                      <span className="flex items-center gap-1">
                        <Target className="h-3 w-3" />
                        {analysis.opportunities} 个商机
                      </span>
                    </div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-gray-400" />
                </div>
              ))}
              
              <Button 
                variant="outline" 
                className="w-full mt-4 border-gray-600 text-gray-300 hover:bg-gray-700"
                onClick={() => navigate('/workspace')}
              >
                开始新的分析
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* 升级提示 - 仅对免费用户显示 */}
        {user?.subscription_tier !== 'pro' && (
          <Card className="mt-6 bg-gradient-to-r from-purple-900/50 to-blue-900/50 border-purple-500/30">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-white mb-2">
                    解锁更多商业洞察
                  </h3>
                  <p className="text-gray-300 mb-4">
                    升级到 Pro 版本，获得无限分析次数、详细用户画像、竞品监控等高级功能
                  </p>
                  <div className="flex items-center gap-4 text-sm text-gray-400">
                    <span className="flex items-center gap-1">
                      <Users className="h-4 w-4" />
                      详细用户画像
                    </span>
                    <span className="flex items-center gap-1">
                      <BarChart3 className="h-4 w-4" />
                      竞品分析
                    </span>
                    <span className="flex items-center gap-1">
                      <Star className="h-4 w-4" />
                      PDF报告导出
                    </span>
                  </div>
                </div>
                <Button 
                  size="lg"
                  className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                  onClick={() => navigate('/pricing')}
                >
                  立即升级
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}