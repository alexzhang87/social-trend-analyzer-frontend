import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Check, Zap, Package, Layers, ArrowLeft, Star } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/auth-provider';
import { useLoading } from '../components/loading-provider';
import { toast } from 'sonner';

interface FlexiblePlan {
  id: string;
  name: string;
  price: number;
  description: string;
  features: string[];
  popular?: boolean;
  icon: React.ReactNode;
  type: 'credits' | 'feature' | 'hybrid';
  credits?: number;
  bonus?: number;
}

const creditPackages: FlexiblePlan[] = [
  {
    id: 'credits-small',
    name: '基础包',
    price: 9.99,
    description: '适合偶尔使用的用户',
    features: [
      '50 积分',
      '永不过期',
      '所有基础功能',
      '邮件支持'
    ],
    icon: <Zap className="h-6 w-6" />,
    type: 'credits',
    credits: 50
  },
  {
    id: 'credits-medium',
    name: '标准包',
    price: 24.99,
    description: '最受欢迎的选择',
    features: [
      '150 积分',
      '+25 赠送积分',
      '永不过期',
      '所有功能',
      '优先支持'
    ],
    popular: true,
    icon: <Zap className="h-6 w-6" />,
    type: 'credits',
    credits: 150,
    bonus: 25
  },
  {
    id: 'credits-large',
    name: '超值包',
    price: 49.99,
    description: '最划算的选择',
    features: [
      '350 积分',
      '+100 赠送积分',
      '永不过期',
      '所有高级功能',
      '专属客服'
    ],
    icon: <Zap className="h-6 w-6" />,
    type: 'credits',
    credits: 350,
    bonus: 100
  }
];

const featurePackages: FlexiblePlan[] = [
  {
    id: 'feature-analysis',
    name: '分析专家包',
    price: 19.99,
    description: '专注于深度分析功能',
    features: [
      '30天使用期',
      '高级趋势分析',
      '竞品对比分析',
      'PMF评估工具',
      '无限关键词监控',
      '数据导出 (所有格式)'
    ],
    icon: <Package className="h-6 w-6" />,
    type: 'feature'
  },
  {
    id: 'feature-reports',
    name: '报告大师包',
    price: 15.99,
    description: '专业报告生成工具',
    features: [
      '30天使用期',
      '自定义报告模板',
      '白标报告',
      '自动报告生成',
      '多格式导出',
      '报告分享功能'
    ],
    icon: <Package className="h-6 w-6" />,
    type: 'feature'
  },
  {
    id: 'feature-collaboration',
    name: '团队协作包',
    price: 29.99,
    description: '团队协作和管理功能',
    features: [
      '30天使用期',
      '团队工作区',
      '权限管理',
      '协作分析',
      '共享仪表板',
      '团队报告'
    ],
    popular: true,
    icon: <Package className="h-6 w-6" />,
    type: 'feature'
  }
];

const hybridPackages: FlexiblePlan[] = [
  {
    id: 'hybrid-starter',
    name: '灵活入门',
    price: 39.99,
    description: '订阅+积分的完美组合',
    features: [
      '基础订阅功能 (30天)',
      '100 额外积分',
      '所有分析工具',
      '优先客服支持',
      '数据导出权限'
    ],
    icon: <Layers className="h-6 w-6" />,
    type: 'hybrid',
    credits: 100
  },
  {
    id: 'hybrid-pro',
    name: '灵活专业',
    price: 69.99,
    description: '专业用户的最佳选择',
    features: [
      'Pro订阅功能 (30天)',
      '200 额外积分',
      '高级分析工具',
      'API访问权限',
      '自定义报告',
      '专属客户经理'
    ],
    popular: true,
    icon: <Layers className="h-6 w-6" />,
    type: 'hybrid',
    credits: 200
  }
];

export default function FlexiblePricingPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { setLoading } = useLoading();
  const [activeTab, setActiveTab] = useState<'credits' | 'feature' | 'hybrid'>('credits');

  const handlePurchase = async (planId: string) => {
    if (!user) {
      toast.error('请先登录');
      return;
    }

    setLoading(true);
    try {
      // 这里应该调用实际的支付API
      toast.success('正在跳转到支付页面...');
      // 模拟支付流程
      console.log('购买方案:', planId);
    } catch (error) {
      console.error('购买失败:', error);
      toast.error('购买失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const getCurrentPackages = () => {
    switch (activeTab) {
      case 'credits':
        return creditPackages;
      case 'feature':
        return featurePackages;
      case 'hybrid':
        return hybridPackages;
      default:
        return creditPackages;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* 返回按钮 */}
      <div className="mb-6">
        <Button 
          variant="ghost" 
          onClick={() => navigate('/pricing')}
          className="text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          返回定价页面
        </Button>
      </div>

      {/* 页面标题 */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          灵活的按需购买方案
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          根据您的具体需求选择最适合的方案，无需长期承诺，灵活付费
        </p>
      </div>

      {/* 标签切换 */}
      <div className="flex justify-center mb-8">
        <div className="bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('credits')}
            className={`px-6 py-2 rounded-md font-medium transition-colors ${
              activeTab === 'credits'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Credits包
          </button>
          <button
            onClick={() => setActiveTab('feature')}
            className={`px-6 py-2 rounded-md font-medium transition-colors ${
              activeTab === 'feature'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            功能包
          </button>
          <button
            onClick={() => setActiveTab('hybrid')}
            className={`px-6 py-2 rounded-md font-medium transition-colors ${
              activeTab === 'hybrid'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            混合方案
          </button>
        </div>
      </div>

      {/* 方案卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
        {getCurrentPackages().map((plan) => (
          <Card key={plan.id} className={`relative ${plan.popular ? 'border-blue-500 shadow-lg' : ''} flex flex-col`}>
            {plan.popular && (
              <Badge className="absolute -top-2 left-1/2 transform -translate-x-1/2 bg-blue-500">
                <Star className="w-3 h-3 mr-1" />
                推荐
              </Badge>
            )}
            <CardHeader className="text-center">
              <div className="flex justify-center mb-3">
                <div className="p-3 bg-blue-100 rounded-lg text-blue-600">
                  {plan.icon}
                </div>
              </div>
              <CardTitle className="text-xl">{plan.name}</CardTitle>
              <CardDescription className="text-sm">{plan.description}</CardDescription>
              <div className="mt-4">
                <span className="text-3xl font-bold">${plan.price}</span>
                {plan.type === 'credits' && plan.credits && (
                  <div className="text-sm text-gray-600 mt-1">
                    {plan.credits} 积分
                    {plan.bonus && (
                      <span className="text-green-600 font-medium"> +{plan.bonus} 赠送</span>
                    )}
                  </div>
                )}
                {plan.type === 'hybrid' && plan.credits && (
                  <div className="text-sm text-gray-600 mt-1">
                    +{plan.credits} 额外积分
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent className="flex-1">
              <ul className="space-y-2">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-start">
                    <Check className="h-4 w-4 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
            <CardFooter>
              <Button 
                className="w-full" 
                variant={plan.popular ? 'default' : 'outline'}
                onClick={() => handlePurchase(plan.id)}
              >
                立即购买
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>

      {/* 说明信息 */}
      <div className="mt-16 max-w-4xl mx-auto">
        <div className="bg-gray-50 rounded-xl p-8">
          <h2 className="text-2xl font-bold text-center mb-6">方案说明</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="p-3 bg-blue-100 rounded-lg text-blue-600 w-12 h-12 mx-auto mb-3 flex items-center justify-center">
                <Zap className="h-6 w-6" />
              </div>
              <h3 className="font-semibold mb-2">Credits包</h3>
              <p className="text-gray-600 text-sm">
                购买积分，按需使用。积分永不过期，适合使用频率不固定的用户。
              </p>
            </div>
            <div className="text-center">
              <div className="p-3 bg-green-100 rounded-lg text-green-600 w-12 h-12 mx-auto mb-3 flex items-center justify-center">
                <Package className="h-6 w-6" />
              </div>
              <h3 className="font-semibold mb-2">功能包</h3>
              <p className="text-gray-600 text-sm">
                针对特定功能的组合包，30天内无限使用指定功能，适合有明确需求的用户。
              </p>
            </div>
            <div className="text-center">
              <div className="p-3 bg-purple-100 rounded-lg text-purple-600 w-12 h-12 mx-auto mb-3 flex items-center justify-center">
                <Layers className="h-6 w-6" />
              </div>
              <h3 className="font-semibold mb-2">混合方案</h3>
              <p className="text-gray-600 text-sm">
                订阅功能+额外积分的组合，既有稳定的功能访问，又有灵活的积分使用。
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 常见问题 */}
      <div className="mt-16 max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold text-center mb-8">常见问题</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold mb-2">Credits包的积分会过期吗？</h3>
            <p className="text-gray-600 text-sm">
              不会。通过Credits包购买的积分永不过期，您可以随时使用。
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">功能包可以续费吗？</h3>
            <p className="text-gray-600 text-sm">
              可以。功能包到期后，您可以重新购买相同或不同的功能包。
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">混合方案的积分如何使用？</h3>
            <p className="text-gray-600 text-sm">
              混合方案中的额外积分可以用于任何需要积分的功能，积分永不过期。
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">可以同时购买多个方案吗？</h3>
            <p className="text-gray-600 text-sm">
              可以。您可以根据需要组合不同的方案，获得最大的灵活性。
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}