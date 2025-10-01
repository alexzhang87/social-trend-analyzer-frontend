import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { useAuth } from '../components/auth-provider';
import { useLoading } from '../components/loading-provider';
import { 
  TrendingUp, 
  Users, 
  MessageSquare, 
  BarChart3, 
  Search, 
  Filter,
  Download,
  RefreshCw,
  Calendar,
  Globe,
  Heart,
  Share2,
  Eye
} from 'lucide-react';

interface TrendData {
  id: string;
  keyword: string;
  platform: string;
  mentions: number;
  sentiment: 'positive' | 'negative' | 'neutral';
  growth: number;
  lastUpdated: string;
}

interface AnalyticsData {
  totalMentions: number;
  totalKeywords: number;
  activePlatforms: number;
  sentimentScore: number;
}

const DashboardPage: React.FC = () => {
  const { user, logout } = useAuth();
  const { setLoading } = useLoading();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPlatform, setSelectedPlatform] = useState('all');
  const [trendData, setTrendData] = useState<TrendData[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsData>({
    totalMentions: 0,
    totalKeywords: 0,
    activePlatforms: 0,
    sentimentScore: 0
  });

  // 模拟数据
  useEffect(() => {
    const mockTrendData: TrendData[] = [
      {
        id: '1',
        keyword: 'AI技术',
        platform: 'Twitter',
        mentions: 15420,
        sentiment: 'positive',
        growth: 12.5,
        lastUpdated: '2024-01-15 14:30'
      },
      {
        id: '2',
        keyword: '区块链',
        platform: 'Reddit',
        mentions: 8930,
        sentiment: 'neutral',
        growth: -3.2,
        lastUpdated: '2024-01-15 14:25'
      },
      {
        id: '3',
        keyword: '元宇宙',
        platform: 'Instagram',
        mentions: 12100,
        sentiment: 'positive',
        growth: 8.7,
        lastUpdated: '2024-01-15 14:20'
      },
      {
        id: '4',
        keyword: '可持续发展',
        platform: 'LinkedIn',
        mentions: 6750,
        sentiment: 'positive',
        growth: 15.3,
        lastUpdated: '2024-01-15 14:15'
      }
    ];

    const mockAnalytics: AnalyticsData = {
      totalMentions: 43200,
      totalKeywords: 156,
      activePlatforms: 8,
      sentimentScore: 72.5
    };

    setTrendData(mockTrendData);
    setAnalytics(mockAnalytics);
  }, []);

  const handleRefresh = async () => {
    setLoading(true);
    // 模拟API调用
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'bg-green-100 text-green-800';
      case 'negative': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return '😊';
      case 'negative': return '😞';
      default: return '😐';
    }
  };

  const filteredData = trendData.filter(item => {
    const matchesSearch = item.keyword.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesPlatform = selectedPlatform === 'all' || item.platform.toLowerCase() === selectedPlatform.toLowerCase();
    return matchesSearch && matchesPlatform;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航 */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">社交媒体趋势分析</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">欢迎, {user?.username}</span>
              <Button variant="outline" size="sm" onClick={logout}>
                退出登录
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <MessageSquare className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">总提及数</p>
                  <p className="text-2xl font-bold text-gray-900">{analytics.totalMentions.toLocaleString()}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <TrendingUp className="h-6 w-6 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">关键词数量</p>
                  <p className="text-2xl font-bold text-gray-900">{analytics.totalKeywords}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Globe className="h-6 w-6 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">活跃平台</p>
                  <p className="text-2xl font-bold text-gray-900">{analytics.activePlatforms}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-yellow-100 rounded-lg">
                  <Heart className="h-6 w-6 text-yellow-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">情感评分</p>
                  <p className="text-2xl font-bold text-gray-900">{analytics.sentimentScore}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 搜索和过滤 */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>趋势分析</CardTitle>
            <CardDescription>实时监控社交媒体趋势和关键词表现</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col sm:flex-row gap-4 mb-6">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="搜索关键词..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <select
                  value={selectedPlatform}
                  onChange={(e) => setSelectedPlatform(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">所有平台</option>
                  <option value="twitter">Twitter</option>
                  <option value="reddit">Reddit</option>
                  <option value="instagram">Instagram</option>
                  <option value="linkedin">LinkedIn</option>
                </select>
                <Button variant="outline" onClick={handleRefresh}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  刷新
                </Button>
                <Button variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  导出
                </Button>
              </div>
            </div>

            {/* 趋势数据表格 */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium text-gray-600">关键词</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">平台</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">提及数</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">情感</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">增长率</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">更新时间</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600">操作</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredData.map((item) => (
                    <tr key={item.id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <div className="font-medium text-gray-900">{item.keyword}</div>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant="outline">{item.platform}</Badge>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center">
                          <Eye className="h-4 w-4 text-gray-400 mr-1" />
                          {item.mentions.toLocaleString()}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <Badge className={getSentimentColor(item.sentiment)}>
                          {getSentimentIcon(item.sentiment)} {item.sentiment}
                        </Badge>
                      </td>
                      <td className="py-3 px-4">
                        <div className={`flex items-center ${
                          item.growth > 0 ? 'text-green-600' : item.growth < 0 ? 'text-red-600' : 'text-gray-600'
                        }`}>
                          <TrendingUp className="h-4 w-4 mr-1" />
                          {item.growth > 0 ? '+' : ''}{item.growth}%
                        </div>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        <div className="flex items-center">
                          <Calendar className="h-4 w-4 mr-1" />
                          {item.lastUpdated}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex space-x-2">
                          <Button variant="outline" size="sm">
                            <BarChart3 className="h-4 w-4" />
                          </Button>
                          <Button variant="outline" size="sm">
                            <Share2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {filteredData.length === 0 && (
              <div className="text-center py-8">
                <p className="text-gray-500">没有找到匹配的数据</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DashboardPage;