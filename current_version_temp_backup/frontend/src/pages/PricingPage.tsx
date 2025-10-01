import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Check, Star, Zap, Crown, Building, ArrowRight } from 'lucide-react';
import { useAuth } from '../components/auth-provider';
import { useLoading } from '../components/loading-provider';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

interface PricingPlan {
  id: string;
  name: string;
  price: number;
  period: string;
  description: string;
  features: string[];
  popular?: boolean;
  icon: React.ReactNode;
  credits: number;
}

const pricingPlans: PricingPlan[] = [
  {
    id: 'starter',
    name: 'Starter',
    price: 9.99,
    period: '月',
    description: '适合个人用户和小型项目',
    features: [
      '25 积分/月',
      '基础趋势分析',
      '5个关键词监控',
      '邮件支持',
      '数据导出 (CSV)'
    ],
    icon: <Zap className="h-6 w-6" />,
    credits: 25
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 29.99,
    period: '月',
    description: '适合专业用户和中小企业',
    features: [
      '60 积分/月',
      '高级趋势分析',
      '20个关键词监控',
      '实时数据更新',
      '优先客服支持',
      '数据导出 (CSV, JSON)',
      'API访问'
    ],
    popular: true,
    icon: <Star className="h-6 w-6" />,
    credits: 60
  },
  {
    id: 'plus',
    name: 'Plus',
    price: 59.99,
    period: '月',
    description: '适合大型团队和企业',
    features: [
      '150 积分/月',
      '企业级分析',
      '50个关键词监控',
      '自定义报告',
      '团队协作功能',
      '专属客户经理',
      '高级API访问',
      '白标解决方案'
    ],
    icon: <Crown className="h-6 w-6" />,
    credits: 150
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 199.99,
    period: '月',
    description: '适合大型企业和机构',
    features: [
      '500 积分/月',
      '无限关键词监控',
      '定制化分析模型',
      '专属服务器部署',
      '24/7 技术支持',
      '高级安全保障',
      '定制化集成',
      'SLA保证'
    ],
    icon: <Building className="h-6 w-6" />,
    credits: 500
  }
];

interface CreditPackage {
  id: string;
  name: string;
  credits: number;
  price: number;
  bonus?: number;
  popular?: boolean;
}

const creditPackages: CreditPackage[] = [
  {
    id: 'small',
    name: '小包装',
    credits: 10,
    price: 9.99
  },
  {
    id: 'medium',
    name: '中包装',
    credits: 30,
    price: 24.99,
    bonus: 5,
    popular: true
  },
  {
    id: 'large',
    name: '大包装',
    credits: 75,
    price: 49.99,
    bonus: 15
  }
];

export default function PricingPage() {
  const { user } = useAuth();
  const { setLoading } = useLoading();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'subscription' | 'credits'>('subscription');
  const [stripeConfig, setStripeConfig] = useState<any>(null);

  useEffect(() => {
    // 获取Stripe配置
    fetch('/api/v1/payments/config')
      .then(res => res.json())
      .then(data => setStripeConfig(data))
      .catch(err => console.error('获取Stripe配置失败:', err));
  }, []);

  const handleSubscribe = async (planId: string) => {
    if (!user) {
      toast.error('请先登录');
      return;
    }

    try {
      setLoading(true, '正在创建支付会话...');
      
      const response = await fetch('/api/v1/payments/create-checkout-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          product_type: 'subscription',
          product_id: planId
        })
      });

      if (!response.ok) {
        throw new Error('创建支付会话失败');
      }

      const data = await response.json();
      
      // 重定向到Stripe结账页面
      window.location.href = data.checkout_url;
      
    } catch (error) {
      console.error('订阅失败:', error);
      toast.error('订阅失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleBuyCredits = async (packageId: string) => {
    if (!user) {
      toast.error('请先登录');
      return;
    }

    try {
      setLoading(true, '正在创建支付会话...');
      
      const response = await fetch('/api/v1/payments/create-checkout-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          product_type: 'credits',
          product_id: packageId
        })
      });

      if (!response.ok) {
        throw new Error('创建支付会话失败');
      }

      const data = await response.json();
      
      // 重定向到Stripe结账页面
      window.location.href = data.checkout_url;
      
    } catch (error) {
      console.error('购买积分失败:', error);
      toast.error('购买积分失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          选择适合您的方案
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          从个人用户到企业级解决方案，我们为每种需求提供合适的定价方案
        </p>
      </div>

      {/* 标签切换 */}
      <div className="flex justify-center mb-8">
        <div className="bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('subscription')}
            className={`px-6 py-2 rounded-md font-medium transition-colors ${
              activeTab === 'subscription'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            订阅方案
          </button>
          <button
            onClick={() => setActiveTab('credits')}
            className={`px-6 py-2 rounded-md font-medium transition-colors ${
              activeTab === 'credits'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            积分包
          </button>
        </div>
      </div>

      {activeTab === 'subscription' ? (
        /* 订阅方案 */
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 max-w-7xl mx-auto">
          {pricingPlans.map((plan) => (
            <Card key={plan.id} className={`relative ${plan.popular ? 'border-blue-500 shadow-lg' : ''} flex flex-col`}>
              {plan.popular && (
                <Badge className="absolute -top-2 left-1/2 transform -translate-x-1/2 bg-blue-500">
                  最受欢迎
                </Badge>
              )}
              <CardHeader className="text-center pb-4">
                <div className="flex justify-center mb-2">
                  <div className="p-2 bg-blue-100 rounded-lg text-blue-600">
                    {plan.icon}
                  </div>
                </div>
                <CardTitle className="text-lg">{plan.name}</CardTitle>
                <CardDescription className="text-sm">{plan.description}</CardDescription>
                <div className="mt-3">
                  <span className="text-2xl font-bold">${plan.price}</span>
                  <span className="text-gray-600 text-sm">/{plan.period}</span>
                </div>
              </CardHeader>
              <CardContent className="flex-1 pb-4">
                <ul className="space-y-1.5">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start">
                      <Check className="h-3.5 w-3.5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                      <span className="text-xs leading-relaxed">{feature}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
              <CardFooter className="pt-0">
                <Button 
                  className="w-full text-sm" 
                  variant={plan.popular ? 'default' : 'outline'}
                  onClick={() => handleSubscribe(plan.id)}
                  disabled={!stripeConfig}
                >
                  {user?.subscription_tier === plan.id ? '当前方案' : '选择方案'}
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      ) : (
        /* 积分包 */
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {creditPackages.map((pkg) => (
            <Card key={pkg.id} className={`relative ${pkg.popular ? 'border-blue-500 shadow-lg' : ''}`}>
              {pkg.popular && (
                <Badge className="absolute -top-2 left-1/2 transform -translate-x-1/2 bg-blue-500">
                  最划算
                </Badge>
              )}
              <CardHeader className="text-center">
                <CardTitle className="text-xl">{pkg.name}</CardTitle>
                <div className="mt-4">
                  <span className="text-3xl font-bold">{pkg.credits}</span>
                  <span className="text-gray-600"> 积分</span>
                  {pkg.bonus && (
                    <div className="text-sm text-green-600 font-medium">
                      +{pkg.bonus} 赠送积分
                    </div>
                  )}
                </div>
                <div className="text-2xl font-bold text-blue-600">
                  ${pkg.price}
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-center text-sm text-gray-600">
                  <p>积分永不过期</p>
                  <p>可用于所有分析功能</p>
                  {pkg.bonus && <p className="text-green-600 font-medium">限时赠送 {pkg.bonus} 积分</p>}
                </div>
              </CardContent>
              <CardFooter>
                <Button 
                  className="w-full" 
                  variant={pkg.popular ? 'default' : 'outline'}
                  onClick={() => handleBuyCredits(pkg.id)}
                  disabled={!stripeConfig}
                >
                  立即购买
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}

      {/* 常见问题 */}
      <div className="mt-16 max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold text-center mb-8">常见问题</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold mb-2">什么是积分？</h3>
            <p className="text-gray-600 text-sm">
              积分是我们平台的虚拟货币，用于支付各种分析服务。每次分析消耗不同数量的积分。
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">可以随时取消订阅吗？</h3>
            <p className="text-gray-600 text-sm">
              是的，您可以随时取消订阅。取消后，您仍可使用服务直到当前计费周期结束。
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">积分会过期吗？</h3>
            <p className="text-gray-600 text-sm">
              通过积分包购买的积分永不过期。订阅方案中的积分在下个计费周期会重置。
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">支持哪些支付方式？</h3>
            <p className="text-gray-600 text-sm">
              我们支持所有主要的信用卡和借记卡，支付由Stripe安全处理。
            </p>
          </div>
        </div>
      </div>

      {/* CTA按钮 - 按需购买选项 */}
      <div className="mt-16 text-center">
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-8 max-w-4xl mx-auto">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            需要更灵活的方案？
          </h3>
          <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
            我们还提供按需购买选项，包括Credits包、功能包和混合方案，让您根据实际需求灵活选择
          </p>
          <Button 
            onClick={() => navigate('/flexible-pricing')}
            className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-8 py-3 rounded-lg font-medium transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            查看按需购买选项
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}