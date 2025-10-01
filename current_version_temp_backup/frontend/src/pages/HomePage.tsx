import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { TrendingUp, BarChart3, Users, Zap } from 'lucide-react';

export default function HomePage() {
  const navigate = useNavigate();



  const handleQuickValidation = () => {
    navigate('/register');
  };

  const handleProfessionAnalysis = () => {
    navigate('/register');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <TrendingUp className="h-8 w-8 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">趋势分析平台</h1>
          </div>
          <div className="space-x-4">
            <Link to="/login">
              <Button variant="outline">登录</Button>
            </Link>
            <Link to="/register">
              <Button>注册</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 text-center">
        <h2 className="text-5xl font-bold text-gray-900 mb-6">
          智能趋势分析，洞察未来
        </h2>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          利用先进的AI技术，为您提供精准的市场趋势分析和预测，助力您做出明智的商业决策
        </p>
        <div className="space-x-4">
          <Link to="/register">
            <Button size="lg" className="px-8 py-3 bg-teal-600 hover:bg-teal-700 text-white group transform hover:scale-105 active:scale-95 hover:shadow-lg hover:shadow-primary/25 active:shadow-primary/50 transition-all duration-300 ease-out">
              Get Started Free
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-arrow-right w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform">
                <path d="M5 12h14"></path>
                <path d="m12 5 7 7-7 7"></path>
              </svg>
            </Button>
          </Link>
                    立即登录
          <Link to="/pricing">
            <Button variant="outline" size="lg" className="px-8 py-3">
              查看定价
            </Button>
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-16">
        <h3 className="text-3xl font-bold text-center text-gray-900 mb-12">
          核心功能
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <Card>
            <CardHeader>
              <BarChart3 className="h-12 w-12 text-blue-600 mb-4" />
              <CardTitle>智能分析</CardTitle>
              <CardDescription>
                基于大数据和机器学习的智能趋势分析
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="text-sm text-gray-600 space-y-2">
                <li>• 实时数据处理</li>
                <li>• 多维度分析</li>
                <li>• 预测模型</li>
              </ul>
              <div className="mt-4">
                <Button 
                  onClick={handleQuickValidation}
                  className="w-full"
                  variant="outline"
                >
                  开始快速验证
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Users className="h-12 w-12 text-green-600 mb-4" />
              <CardTitle>团队协作</CardTitle>
              <CardDescription>
                支持团队共享和协作分析
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="text-sm text-gray-600 space-y-2">
                <li>• 共享仪表板</li>
                <li>• 权限管理</li>
                <li>• 协作注释</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Zap className="h-12 w-12 text-purple-600 mb-4" />
              <CardTitle>快速部署</CardTitle>
              <CardDescription>
                简单易用，快速上手
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="text-sm text-gray-600 space-y-2">
                <li>• 一键部署</li>
                <li>• API集成</li>
                <li>• 自定义配置</li>
              </ul>
              <div className="mt-4">
                <Button 
                  onClick={handleProfessionAnalysis}
                  className="w-full"
                  variant="outline"
                >
                  开始专业分析
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-blue-600 text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h3 className="text-3xl font-bold mb-4">
            准备开始您的趋势分析之旅？
          </h3>
          <p className="text-xl mb-8">
            立即注册，获得免费积分开始体验
          </p>
          <Link to="/register">
            <Button size="lg" variant="secondary" className="px-8 py-3">
              立即注册
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2024 趋势分析平台. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}