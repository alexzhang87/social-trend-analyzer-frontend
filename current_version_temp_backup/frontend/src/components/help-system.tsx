import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { HelpCircle, X, ChevronRight, Search, Book, Video, MessageCircle, ExternalLink, Lightbulb, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';

interface HelpItem {
  id: string;
  title: string;
  description: string;
  content: string;
  category: 'getting-started' | 'features' | 'troubleshooting' | 'api' | 'billing';
  tags: string[];
  type: 'article' | 'video' | 'tutorial' | 'faq';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedTime?: string;
  relatedItems?: string[];
  lastUpdated: string;
}

interface ContextualHelp {
  page: string;
  suggestions: HelpItem[];
  quickActions: {
    label: string;
    action: () => void;
    icon: React.ComponentType<any>;
  }[];
}

const helpData: HelpItem[] = [
  {
    id: 'getting-started-overview',
    title: '快速开始指南',
    description: '了解如何使用社交趋势分析器的基本功能',
    content: `
# 快速开始指南

欢迎使用社交趋势分析器！本指南将帮助您快速上手。

## 第一步：创建账户
1. 点击右上角的"注册"按钮
2. 填写您的邮箱和密码
3. 验证邮箱地址

## 第二步：进行第一次分析
1. 在主页输入您想分析的关键词
2. 选择分析平台（Twitter、Reddit等）
3. 设置时间范围
4. 点击"开始分析"

## 第三步：查看结果
- 情感分析图表
- 热门话题
- 影响力用户
- 趋势预测
    `,
    category: 'getting-started',
    tags: ['新手', '入门', '基础'],
    type: 'tutorial',
    difficulty: 'beginner',
    estimatedTime: '5分钟',
    relatedItems: ['account-setup', 'first-analysis'],
    lastUpdated: '2024-01-15',
  },
  {
    id: 'trend-analysis-features',
    title: '趋势分析功能详解',
    description: '深入了解各种分析功能和指标含义',
    content: `
# 趋势分析功能详解

## 情感分析
- **正面情感**: 表达积极态度的内容比例
- **负面情感**: 表达消极态度的内容比例
- **中性情感**: 客观描述性内容比例

## 热门话题
- 基于提及频率和互动量识别
- 实时更新热门关键词
- 话题演变趋势

## 影响力分析
- 识别关键意见领袖
- 分析传播路径
- 评估影响力范围
    `,
    category: 'features',
    tags: ['分析', '功能', '指标'],
    type: 'article',
    difficulty: 'intermediate',
    estimatedTime: '10分钟',
    relatedItems: ['sentiment-analysis', 'influencer-detection'],
    lastUpdated: '2024-01-10',
  },
  {
    id: 'troubleshooting-common',
    title: '常见问题解决',
    description: '解决使用过程中遇到的常见问题',
    content: `
# 常见问题解决

## 分析结果为空
**可能原因：**
- 关键词过于具体，没有相关数据
- 时间范围设置过短
- 平台API限制

**解决方案：**
1. 尝试更通用的关键词
2. 扩大时间范围
3. 检查API配额

## 加载速度慢
**可能原因：**
- 网络连接问题
- 服务器负载高
- 数据量过大

**解决方案：**
1. 检查网络连接
2. 减少分析时间范围
3. 稍后重试
    `,
    category: 'troubleshooting',
    tags: ['问题', '解决', '故障'],
    type: 'faq',
    difficulty: 'beginner',
    estimatedTime: '3分钟',
    relatedItems: ['performance-tips', 'api-limits'],
    lastUpdated: '2024-01-12',
  },
];



export function HelpSystem({ trigger }: { trigger?: React.ReactNode }) {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedItem, setSelectedItem] = useState<HelpItem | null>(null);
  const [currentPage, setCurrentPage] = useState('');

  useEffect(() => {
    setCurrentPage(window.location.pathname);
  }, []);

  const contextualHelpData: Record<string, ContextualHelp> = {
    '/dashboard': {
      page: '仪表板',
      suggestions: helpData.filter(item => item.category === 'getting-started'),
      quickActions: [
        {
          label: '创建新分析',
          action: () => navigate('/analyze'),
          icon: Lightbulb,
        },
        {
          label: '查看历史记录',
          action: () => navigate('/history'),
          icon: Book,
        },
      ],
    },
    '/analyze': {
      page: '趋势分析',
      suggestions: helpData.filter(item => item.category === 'features'),
      quickActions: [
        {
          label: '分析功能说明',
          action: () => console.log('Show analysis help'),
          icon: HelpCircle,
        },
      ],
    },
  };

  const filteredHelpItems = helpData.filter(item => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      item.title.toLowerCase().includes(query) ||
      item.description.toLowerCase().includes(query) ||
      item.tags.some(tag => tag.toLowerCase().includes(query))
    );
  });

  const contextualHelp = contextualHelpData[currentPage];

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'getting-started': return Book;
      case 'features': return Lightbulb;
      case 'troubleshooting': return HelpCircle;
      case 'api': return ExternalLink;
      case 'billing': return MessageCircle;
      default: return HelpCircle;
    }
  };

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'getting-started': return '入门指南';
      case 'features': return '功能说明';
      case 'troubleshooting': return '问题解决';
      case 'api': return 'API文档';
      case 'billing': return '计费相关';
      default: return '其他';
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const renderHelpItem = (item: HelpItem) => {
    const CategoryIcon = getCategoryIcon(item.category);
    
    return (
      <Card 
        key={item.id} 
        className="cursor-pointer hover:shadow-md transition-shadow"
        onClick={() => setSelectedItem(item)}
      >
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-2">
              <CategoryIcon className="w-5 h-5 text-blue-600" />
              <CardTitle className="text-base">{item.title}</CardTitle>
            </div>
            <ChevronRight className="w-4 h-4 text-gray-400" />
          </div>
          <CardDescription className="text-sm">
            {item.description}
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Badge variant="outline" className={getDifficultyColor(item.difficulty)}>
                {item.difficulty === 'beginner' && '初级'}
                {item.difficulty === 'intermediate' && '中级'}
                {item.difficulty === 'advanced' && '高级'}
              </Badge>
              {item.estimatedTime && (
                <span className="text-xs text-gray-500">{item.estimatedTime}</span>
              )}
            </div>
            <div className="flex items-center space-x-1">
              {item.type === 'video' && <Video className="w-4 h-4 text-gray-400" />}
              {item.type === 'tutorial' && <Book className="w-4 h-4 text-gray-400" />}
              {item.type === 'article' && <ExternalLink className="w-4 h-4 text-gray-400" />}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  const renderHelpContent = (item: HelpItem) => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setSelectedItem(null)}
        >
          ← 返回列表
        </Button>
        <div className="flex items-center space-x-2">
          <Badge className={getDifficultyColor(item.difficulty)}>
            {item.difficulty === 'beginner' && '初级'}
            {item.difficulty === 'intermediate' && '中级'}
            {item.difficulty === 'advanced' && '高级'}
          </Badge>
          {item.estimatedTime && (
            <span className="text-sm text-gray-500">预计阅读时间: {item.estimatedTime}</span>
          )}
        </div>
      </div>
      
      <div>
        <h2 className="text-xl font-semibold mb-2">{item.title}</h2>
        <p className="text-gray-600 mb-4">{item.description}</p>
      </div>
      
      <Separator />
      
      <div className="prose prose-sm max-w-none">
        <div className="whitespace-pre-wrap">{item.content}</div>
      </div>
      
      {item.tags.length > 0 && (
        <div>
          <h4 className="text-sm font-medium mb-2">标签</h4>
          <div className="flex flex-wrap gap-1">
            {item.tags.map(tag => (
              <Badge key={tag} variant="secondary" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
        </div>
      )}
      
      {item.relatedItems && item.relatedItems.length > 0 && (
        <div>
          <h4 className="text-sm font-medium mb-2">相关文章</h4>
          <div className="space-y-2">
            {item.relatedItems.map(relatedId => {
              const relatedItem = helpData.find(h => h.id === relatedId);
              if (!relatedItem) return null;
              return (
                <button
                  key={relatedId}
                  onClick={() => setSelectedItem(relatedItem)}
                  className="flex items-center space-x-2 text-sm text-blue-600 hover:text-blue-800 transition-colors"
                >
                  <ArrowRight className="w-3 h-3" />
                  <span>{relatedItem.title}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}
      
      <div className="text-xs text-gray-500 pt-4 border-t">
        最后更新: {new Date(item.lastUpdated).toLocaleDateString()}
      </div>
    </div>
  );

  const defaultTrigger = (
    <Button variant="outline" size="sm">
      <HelpCircle className="w-4 h-4 mr-2" />
      帮助
    </Button>
  );

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {trigger || defaultTrigger}
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle>
            {selectedItem ? selectedItem.title : '帮助中心'}
          </DialogTitle>
          <DialogDescription>
            {selectedItem 
              ? selectedItem.description 
              : '查找答案、学习功能使用方法'
            }
          </DialogDescription>
        </DialogHeader>
        
        <div className="flex-1 overflow-hidden">
          {selectedItem ? (
            <ScrollArea className="h-[60vh]">
              {renderHelpContent(selectedItem)}
            </ScrollArea>
          ) : (
            <Tabs defaultValue="browse" className="h-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="browse">浏览</TabsTrigger>
                <TabsTrigger value="search">搜索</TabsTrigger>
                <TabsTrigger value="contextual">当前页面</TabsTrigger>
              </TabsList>
              
              <TabsContent value="browse" className="mt-4">
                <ScrollArea className="h-[50vh]">
                  <div className="space-y-4">
                    {Object.entries(
                      helpData.reduce((acc, item) => {
                        if (!acc[item.category]) acc[item.category] = [];
                        acc[item.category].push(item);
                        return acc;
                      }, {} as Record<string, HelpItem[]>)
                    ).map(([category, items]) => (
                      <div key={category}>
                        <h3 className="text-lg font-semibold mb-3 flex items-center">
                          {React.createElement(getCategoryIcon(category), { className: 'w-5 h-5 mr-2' })}
                          {getCategoryLabel(category)}
                        </h3>
                        <div className="space-y-2">
                          {items.map(renderHelpItem)}
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </TabsContent>
              
              <TabsContent value="search" className="mt-4">
                <div className="space-y-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <Input
                      placeholder="搜索帮助内容..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  
                  <ScrollArea className="h-[45vh]">
                    <div className="space-y-2">
                      {filteredHelpItems.length > 0 ? (
                        filteredHelpItems.map(renderHelpItem)
                      ) : (
                        <div className="text-center py-8 text-gray-500">
                          <Search className="w-12 h-12 mx-auto mb-4 opacity-50" />
                          <p>没有找到相关内容</p>
                          <p className="text-sm">尝试使用不同的关键词</p>
                        </div>
                      )}
                    </div>
                  </ScrollArea>
                </div>
              </TabsContent>
              
              <TabsContent value="contextual" className="mt-4">
                {contextualHelp ? (
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-lg font-semibold mb-2">
                        {contextualHelp.page} 页面帮助
                      </h3>
                      <p className="text-sm text-gray-600 mb-4">
                        以下是与当前页面相关的帮助内容
                      </p>
                    </div>
                    
                    {contextualHelp.quickActions.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium mb-2">快速操作</h4>
                        <div className="grid grid-cols-2 gap-2 mb-4">
                          {contextualHelp.quickActions.map((action, index) => {
                            const Icon = action.icon;
                            return (
                              <Button
                                key={index}
                                variant="outline"
                                size="sm"
                                onClick={action.action}
                                className="justify-start"
                              >
                                <Icon className="w-4 h-4 mr-2" />
                                {action.label}
                              </Button>
                            );
                          })}
                        </div>
                      </div>
                    )}
                    
                    <ScrollArea className="h-[35vh]">
                      <div className="space-y-2">
                        {contextualHelp.suggestions.map(renderHelpItem)}
                      </div>
                    </ScrollArea>
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <HelpCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>当前页面暂无特定帮助内容</p>
                    <p className="text-sm">请查看其他标签页的内容</p>
                  </div>
                )}
              </TabsContent>
            </Tabs>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

// 浮动帮助按钮
export function FloatingHelpButton() {
  return (
    <div className="fixed bottom-20 right-6 z-40">
      <HelpSystem
        trigger={
          <Button
            size="lg"
            variant="secondary"
            className="rounded-full shadow-lg hover:shadow-xl transition-shadow"
          >
            <HelpCircle className="w-5 h-5" />
          </Button>
        }
      />
    </div>
  );
}

// 内联帮助提示
export function InlineHelp({ content, title }: { content: string; title?: string }) {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm" className="p-1 h-auto">
          <HelpCircle className="w-4 h-4 text-gray-400 hover:text-gray-600" />
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>{title || '帮助信息'}</DialogTitle>
        </DialogHeader>
        <div className="text-sm text-gray-600 whitespace-pre-wrap">
          {content}
        </div>
      </DialogContent>
    </Dialog>
  );
}