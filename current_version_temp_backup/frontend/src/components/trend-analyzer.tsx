import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Progress } from './ui/progress';

interface TrendData {
  id: string;
  keyword: string;
  score: number;
  category: string;
  source: string;
  timestamp: string;
}

export default function TrendAnalyzer() {
  const [keyword, setKeyword] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [trends, setTrends] = useState<TrendData[]>([]);
  const [progress, setProgress] = useState(0);

  const handleAnalyze = async () => {
    if (!keyword.trim()) return;
    
    setIsAnalyzing(true);
    setProgress(0);
    
    try {
      // 模拟分析进度
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);
      
      const response = await fetch('/api/v1/trends/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ keyword })
      });
      
      clearInterval(progressInterval);
      setProgress(100);
      
      if (response.ok) {
        const data = await response.json();
        setTrends(data.trends || []);
      } else {
        console.error('Analysis failed:', response.statusText);
      }
    } catch (error) {
      console.error('Analysis error:', error);
    } finally {
      setIsAnalyzing(false);
      setTimeout(() => setProgress(0), 1000);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>趋势分析</CardTitle>
          <CardDescription>
            输入关键词来分析当前的社交媒体趋势
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-2">
            <Input
              placeholder="输入关键词..."
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
              disabled={isAnalyzing}
            />
            <Button 
              onClick={handleAnalyze} 
              disabled={isAnalyzing || !keyword.trim()}
            >
              {isAnalyzing ? '分析中...' : '分析'}
            </Button>
          </div>
          
          {isAnalyzing && (
            <div className="mt-4">
              <Progress value={progress} className="w-full" />
              <p className="text-sm text-gray-500 mt-2">正在分析趋势数据...</p>
            </div>
          )}
        </CardContent>
      </Card>

      {trends.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>分析结果</CardTitle>
            <CardDescription>
              找到 {trends.length} 个相关趋势
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="list" className="w-full">
              <TabsList>
                <TabsTrigger value="list">列表视图</TabsTrigger>
                <TabsTrigger value="chart">图表视图</TabsTrigger>
              </TabsList>
              
              <TabsContent value="list" className="space-y-4">
                {trends.map((trend) => (
                  <div key={trend.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h3 className="font-medium">{trend.keyword}</h3>
                      <p className="text-sm text-gray-500">{trend.source}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="secondary">{trend.category}</Badge>
                      <span className="font-bold text-lg">{trend.score}</span>
                    </div>
                  </div>
                ))}
              </TabsContent>
              
              <TabsContent value="chart">
                <div className="h-64 flex items-center justify-center border rounded-lg">
                  <p className="text-gray-500">图表视图开发中...</p>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  );
}