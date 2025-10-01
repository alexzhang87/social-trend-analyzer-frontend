'use client';

import { useState } from "react";
import { motion } from "framer-motion";
import { Sparkles, TrendingUp, Target, Zap, BarChart3, Users, Lightbulb, Search, ArrowRight, CheckCircle, DollarSign, Star, Shield, Globe, Brain, Rocket, Award, ChevronRight, Clock, Database } from "lucide-react";
import Link from "next/link";

export default function HomePage() {
  const [keyword, setKeyword] = useState("");

  const handleSearchClick = () => {
    if (keyword.trim()) {
      window.location.href = `/chat?keyword=${encodeURIComponent(keyword)}`;
    }
  };

  const handleQuickAnalysis = () => {
    if (keyword.trim()) {
      window.location.href = `/analysis?mode=quick&keyword=${encodeURIComponent(keyword)}`;
    }
  };

  const handleProfessionalAnalysis = () => {
    if (keyword.trim()) {
      window.location.href = `/analysis?mode=professional&keyword=${encodeURIComponent(keyword)}`;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <Brain className="w-8 h-8 text-primary" />
              <span className="text-xl font-bold">IdeaEden</span>
            </div>
            <div className="flex items-center gap-4">
              <Link href="/chat" className="text-muted-foreground hover:text-foreground transition-colors">
                AI聊天
              </Link>
              <Link href="/dashboard" className="text-muted-foreground hover:text-foreground transition-colors">
                用户面板
              </Link>
              <Link href="/analysis" className="text-muted-foreground hover:text-foreground transition-colors">
                专业分析
              </Link>
            </div>
          </div>
        </div>
      </nav>
      
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
          <div className="text-center">
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-8"
            >
              <Sparkles className="w-4 h-4" />
              AI驱动的创业想法验证平台
            </motion.div>

            {/* Main heading */}
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-4xl md:text-6xl lg:text-7xl font-bold text-foreground mb-6 leading-tight"
            >
              用真实数据验证创业想法
              <span className="block bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
                而非凭空猜测
              </span>
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-lg md:text-xl text-muted-foreground mb-12 max-w-3xl mx-auto leading-relaxed"
            >
              2分钟快速验证 vs 传统6个月调研，节省5万+咨询费用。
              AI驱动的多源数据分析，以20%的价格提供80%的Brandwatch功能。
            </motion.p>

            {/* Search Input */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="max-w-2xl mx-auto mb-16"
            >
              <div className="relative">
                <input
                  type="text"
                  placeholder="输入您的产品或服务关键词..."
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearchClick()}
                  className="w-full px-6 py-4 text-lg rounded-2xl border border-border bg-card/50 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-200"
                />
                <button
                  type="button"
                  onClick={handleSearchClick}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 hover:bg-primary/10 rounded-full transition-colors"
                >
                  <Zap className="w-5 h-5 text-primary" />
                </button>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Choose Your Analysis Mode */}
      <section className="py-20 bg-muted/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-3xl md:text-4xl font-bold text-foreground mb-4"
            >
              选择您的分析模式
            </motion.h2>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-lg text-muted-foreground max-w-2xl mx-auto"
            >
              根据您的需求选择合适的分析深度
            </motion.p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* Quick Analysis Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="group relative h-full"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-primary to-secondary rounded-2xl opacity-0 group-hover:opacity-10 transition-opacity duration-300" />
              <div className="relative bg-card border border-border rounded-2xl p-8 text-center hover:shadow-lg transition-all duration-300 h-full flex flex-col">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Zap className="w-8 h-8 text-primary" />
                </div>
                
                <h3 className="text-2xl font-bold text-foreground mb-4">
                  快速验证
                </h3>
                
                <p className="text-muted-foreground mb-6 text-sm leading-relaxed">
                  闪电般的市场验证，用于快速想法筛选。2分钟获得核心洞察，替代传统6个月调研周期。
                </p>
                
                <div className="bg-primary/5 border border-primary/20 rounded-lg p-3 mb-6">
                  <div className="flex items-center mb-1">
                    <Zap className="w-4 h-4 text-primary mr-2" />
                    <span className="text-sm font-medium text-primary">适用于：初步筛选</span>
                  </div>
                  <p className="text-xs text-primary/80">节省1万+市场调研成本</p>
                </div>
                
                <div className="flex-grow">
                  <ul className="text-muted-foreground mb-8 space-y-3 text-left">
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                      <span>即时市场规模估算</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                      <span>基础竞争对手扫描</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                      <span>AI驱动的可行性评分</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                      <span>关键风险预警</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                      <span>社交情感快照</span>
                    </li>
                  </ul>
                </div>

                <button
                  onClick={handleQuickAnalysis}
                  className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold py-3 px-6 rounded-xl transition-colors duration-200 mt-auto flex items-center justify-center gap-2"
                >
                  <Zap className="w-4 h-4" />
                  开始快速分析
                </button>
              </div>
            </motion.div>

            {/* Professional Analysis Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="group relative h-full"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-secondary to-accent rounded-2xl opacity-0 group-hover:opacity-10 transition-opacity duration-300" />
              <div className="relative bg-card border border-border rounded-2xl p-8 text-center hover:shadow-lg transition-all duration-300 h-full flex flex-col">
                <div className="w-16 h-16 bg-secondary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Target className="w-8 h-8 text-secondary" />
                </div>
                
                <h3 className="text-2xl font-bold text-foreground mb-4">
                  专业分析
                </h3>
                
                <p className="text-muted-foreground mb-6 text-sm leading-relaxed">
                  企业级分析，多源数据整合。以20%的成本获得Brandwatch级别的洞察，适合认真的创业者。
                </p>
                
                <div className="bg-secondary/5 border border-secondary/20 rounded-lg p-3 mb-6">
                  <div className="flex items-center mb-1">
                    <Target className="w-4 h-4 text-secondary mr-2" />
                    <span className="text-sm font-medium text-secondary">适用于：投资准备</span>
                  </div>
                  <p className="text-xs text-secondary/80">替代5万+咨询费用</p>
                </div>
                
                <div className="flex-grow">
                  <ul className="text-muted-foreground mb-8 space-y-3 text-left">
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-secondary rounded-full mt-2 flex-shrink-0"></div>
                      <span>多平台数据聚合（Reddit、Twitter、新闻）</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-secondary rounded-full mt-2 flex-shrink-0"></div>
                      <span>高级竞争情报与定位分析</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-secondary rounded-full mt-2 flex-shrink-0"></div>
                      <span>PMF概率评分与置信区间</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-secondary rounded-full mt-2 flex-shrink-0"></div>
                      <span>战略性市场进入建议</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-secondary rounded-full mt-2 flex-shrink-0"></div>
                      <span>投资路演就绪数据包</span>
                    </li>
                  </ul>
                </div>

                <button
                  onClick={handleProfessionalAnalysis}
                  className="w-full bg-secondary hover:bg-secondary/90 text-secondary-foreground font-semibold py-3 px-6 rounded-xl transition-colors duration-200 mt-auto flex items-center justify-center gap-2"
                >
                  <Target className="w-4 h-4" />
                  开始专业分析
                </button>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Data Sources Section */}
      <section className="py-20 bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-3xl md:text-4xl font-bold text-foreground mb-4"
            >
              基于真实社媒数据源
            </motion.h2>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-lg text-muted-foreground max-w-2xl mx-auto"
            >
              我们的AI分析基于真实的社交媒体数据，而非虚构信息
            </motion.p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="bg-card border border-border rounded-2xl p-6 text-center"
            >
              <div className="w-12 h-12 bg-orange-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <Globe className="w-6 h-6 text-orange-500" />
              </div>
              <h3 className="text-xl font-bold text-foreground mb-2">Reddit数据</h3>
              <p className="text-muted-foreground text-sm">
                实时抓取Reddit讨论，获取真实用户需求和痛点
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="bg-card border border-border rounded-2xl p-6 text-center"
            >
              <div className="w-12 h-12 bg-blue-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="w-6 h-6 text-blue-500" />
              </div>
              <h3 className="text-xl font-bold text-foreground mb-2">趋势分析</h3>
              <p className="text-muted-foreground text-sm">
                Google Trends整合，识别市场趋势和季节性变化
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="bg-card border border-border rounded-2xl p-6 text-center"
            >
              <div className="w-12 h-12 bg-green-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <Database className="w-6 h-6 text-green-500" />
              </div>
              <h3 className="text-xl font-bold text-foreground mb-2">多源整合</h3>
              <p className="text-muted-foreground text-sm">
                新闻、社交媒体、论坛数据的智能整合分析
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-muted/30">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-3xl md:text-4xl font-bold text-foreground mb-6"
          >
            准备验证您的创业想法了吗？
          </motion.h2>
          
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto"
          >
            立即开始，用真实数据验证您的商业想法，避免昂贵的市场调研费用
          </motion.p>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <Link
              href="/chat"
              className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold py-3 px-8 rounded-xl transition-colors duration-200 flex items-center justify-center gap-2"
            >
              <Brain className="w-5 h-5" />
              开始AI对话
            </Link>
            <Link
              href="/analysis"
              className="bg-secondary hover:bg-secondary/90 text-secondary-foreground font-semibold py-3 px-8 rounded-xl transition-colors duration-200 flex items-center justify-center gap-2"
            >
              <BarChart3 className="w-5 h-5" />
              专业分析
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-4">
              <Brain className="w-6 h-6 text-primary" />
              <span className="text-lg font-bold">IdeaEden</span>
            </div>
            <p className="text-muted-foreground text-sm">
              AI驱动的创业想法验证平台 - 用数据而非猜测验证您的商业想法
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}