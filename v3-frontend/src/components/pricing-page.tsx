import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { useToast } from './ui/use-toast';
import { useAuth } from './auth-provider';
import { Check, Flame, Clock, Zap, Star, Rocket, TrendingUp, Award } from 'lucide-react';

interface PricingPlan {
  id: string;
  name: string;
  price: number | string;
  originalPrice?: number;
  discount?: number;
  creditsPerMonth: number | string;
  creditsPerAnalysis: number | string;
  features: string[];
  popular?: boolean;
  buttonText: string;
  buttonVariant: "default" | "outline" | "secondary";
  highlightColor: string;
  isCustom?: boolean;
}

const pricingPlans: PricingPlan[] = [
  {
    id: 'free',
    name: 'FREE',
    price: 0,
    creditsPerMonth: 5,
    creditsPerAnalysis: 1,
    features: [
      'Basic keyword analysis (5 times per month)',
      'Simplified market trend reports',
      'Community access',
      'Basic data export',
      '7-day data history',
      'Standard report format',
      'Basic data insights',
      'Getting started guide'
    ],
    buttonText: 'Start Free',
    buttonVariant: 'outline',
    highlightColor: 'border-gray-200'
  },
  {
    id: 'pro',
    name: 'PRO',
    price: 199,
    creditsPerMonth: 'Unlimited',
    creditsPerAnalysis: 'Included',
    popular: true,
    features: [
      'Unlimited keyword analysis',
      'Complete PMF analysis reports',
      'In-depth competitor comparison',
      'User feedback sentiment analysis',
      'Data integration workspace',
      'Priority customer support',
      'PDF report export',
      '30-day historical data',
      'Email customer support'
    ],
    buttonText: 'Upgrade Now',
    buttonVariant: 'default',
    highlightColor: 'border-blue-500'
  },
  {
    id: 'plus',
    name: 'PLUS',
    price: 599,
    creditsPerMonth: 'Unlimited',
    creditsPerAnalysis: 'Custom',
    features: [
      'All PRO features',
      'Advanced market prediction models',
      'Custom analysis dimensions',
      'API access',
      'Team collaboration (5 users)',
      'Dedicated customer success manager',
      'Unlimited historical data',
      'Advanced report templates'
    ],
    buttonText: 'Contact Sales',
    buttonVariant: 'outline',
    highlightColor: 'border-green-500'
  },
  {
    id: 'enterprise',
    name: 'ENTERPRISE',
    price: 'Custom Quote',
    creditsPerMonth: 'Unlimited',
    creditsPerAnalysis: 'Custom',
    features: [
      'Enterprise-level data analysis',
      'Customized analysis models',
      'Dedicated account manager',
      '24/7 dedicated technical support',
      'Unlimited data storage',
      'Advanced security protection',
      'Private deployment options',
      'Customized integration solutions',
      'Training and consulting services',
      'Enterprise-level SLA guarantee'
    ],
    buttonText: 'Contact Sales',
    buttonVariant: 'outline',
    highlightColor: 'border-purple-500'
  }
];

const PricingPage: React.FC = () => {
  const { isAuthenticated, register } = useAuth();
  const { toast } = useToast();
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);
  const [showRegistration, setShowRegistration] = useState(false);
  const [isTrialMode, setIsTrialMode] = useState(false);
  const [registrationData, setRegistrationData] = useState({
    email: '',
    username: '',
    password: '',
    fullName: ''
  });

  useEffect(() => {
    // Check if coming from trial mode
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('trial') === 'true') {
      setIsTrialMode(true);
      setShowRegistration(true);
      setSelectedPlan('free'); // Default to free plan for trial
    }
  }, []);

  const handleSelectPlan = (planId: string) => {
    if (!isAuthenticated) {
      if (planId === 'free') {
        // Free plan - show registration form
        setSelectedPlan(planId);
        setShowRegistration(true);
      } else {
        toast({
          title: 'Registration Required',
          description: 'Please register for a free account first to access paid plans.',
          variant: 'default'
        });
        setSelectedPlan('free');
        setShowRegistration(true);
      }
      return;
    }

    if (planId === 'enterprise') {
      // Handle enterprise contact sales
      window.open('mailto:sales@ideaeden.com?subject=Enterprise Plan Inquiry&body=Hi, I am interested in learning more about the Enterprise plan. Please contact me to discuss custom pricing and features.', '_blank');
      return;
    }

    setSelectedPlan(planId);
    toast({
      title: 'Plan Selected',
      description: `You have selected the ${pricingPlans.find(p => p.id === planId)?.name} plan.`
    });
    
    // Redirect to workspace after plan selection
    setTimeout(() => {
      window.location.href = '/workspace';
    }, 1500);
  };

  const handleRegistration = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await register(
        registrationData.email,
        registrationData.username,
        registrationData.password,
        registrationData.fullName
      );
      
      toast({
        title: 'Registration Successful!',
        description: 'Welcome! You now have access to our Free plan with 3 analyses per month.',
        variant: 'default'
      });
      
      // Redirect to workspace after successful registration
      setTimeout(() => {
        window.location.href = '/workspace';
      }, 2000);
    } catch (error: any) {
      toast({
        title: 'Registration Failed',
        description: error.message || 'Please try again.',
        variant: 'destructive'
      });
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden py-12 px-4 sm:px-6 bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950">
      {/* 复古未来主义背景 */}
      <div className="absolute inset-0 -z-10">
        {/* 3D 几何网格 */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(0,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,255,255,0.03)_1px,transparent_1px)] bg-[size:50px_50px]"></div>
        
        {/* 霓虹光球 */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gradient-to-br from-cyan-400/20 via-blue-500/20 to-purple-600/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-1/3 right-1/4 w-80 h-80 bg-gradient-to-br from-purple-400/20 via-pink-500/20 to-red-500/20 rounded-full blur-3xl animate-pulse" style={{animationDelay: '2s'}}></div>
        <div className="absolute bottom-1/4 left-1/3 w-72 h-72 bg-gradient-to-br from-emerald-400/20 via-teal-500/20 to-cyan-500/20 rounded-full blur-3xl animate-pulse" style={{animationDelay: '4s'}}></div>
        
        {/* 3D 装饰元素 */}
        <div className="absolute top-20 right-20 w-4 h-4 bg-cyan-400 rounded-full opacity-60 animate-bounce"></div>
        <div className="absolute top-40 left-20 w-6 h-6 bg-purple-400 transform rotate-45 opacity-40"></div>
        <div className="absolute bottom-40 right-40 w-8 h-8 bg-gradient-to-br from-pink-400 to-purple-500 rounded-full opacity-50"></div>
      </div>
      
      <div className="max-w-7xl mx-auto relative z-10">
        {/* 霓虹限时优惠横幅 */}
        <div className="relative bg-gradient-to-r from-slate-900/90 via-purple-900/80 to-slate-900/90 backdrop-blur-xl border border-cyan-500/30 text-center py-6 rounded-3xl mb-12 shadow-[0_20px_50px_rgba(0,255,255,0.2)] animate-pulse">
          <div className="absolute inset-0 rounded-3xl border border-cyan-400/20 animate-pulse"></div>
          <div className="flex items-center justify-center gap-3 mb-2">
            <Flame className="w-6 h-6 text-orange-400 animate-bounce" />
            <span className="font-bold text-xl bg-gradient-to-r from-cyan-300 via-blue-400 to-purple-400 bg-clip-text text-transparent">
              🚀 LIMITED TIME: 50% OFF Pro Plans + ROI Guarantee!
            </span>
            <Clock className="w-6 h-6 text-cyan-400 animate-pulse" />
          </div>
          <p className="text-cyan-200 font-medium">Valid until December 31, 2025 • Average ROI: 340% in first 6 months</p>
        </div>

        {/* 3D 标题区域 */}
        <div className="text-center mb-20 relative">
          {/* 背景装饰 */}
          <div className="absolute -top-10 left-1/2 transform -translate-x-1/2 w-32 h-32 bg-gradient-to-br from-cyan-400/20 to-purple-600/20 rounded-full blur-2xl"></div>
          
          <div className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-slate-900/90 to-purple-900/90 backdrop-blur-xl border border-purple-500/30 rounded-full text-purple-300 text-lg font-bold mb-8 shadow-[0_10px_30px_rgba(139,92,246,0.3)]">
            <TrendingUp className="w-5 h-5 mr-2 text-cyan-400" />
            💰 Data-Driven ROI: Average 340% Return in 6 Months
          </div>
          
          <h1 className="text-5xl md:text-7xl font-black mb-8 tracking-tight leading-tight">
            <span className="bg-gradient-to-r from-cyan-300 via-blue-400 to-purple-400 bg-clip-text text-transparent drop-shadow-[0_0_30px_rgba(0,255,255,0.5)]">
              Choose Your
            </span>
            <br />
            <span className="bg-gradient-to-r from-purple-300 via-pink-400 to-cyan-300 bg-clip-text text-transparent drop-shadow-[0_0_30px_rgba(139,92,246,0.5)]">
              Success Plan
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-300 max-w-4xl mx-auto leading-relaxed font-medium mb-8">
            🤖 AI-powered validation that turns ideas into profitable businesses
            <br />
            <span className="text-cyan-300 font-bold">Join 10,000+ entrepreneurs who increased their success rate by 340%</span>
          </p>
          
          {/* ROI 数据展示 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div className="bg-gradient-to-br from-slate-900/90 via-cyan-900/80 to-slate-900/90 backdrop-blur-xl border border-cyan-500/30 rounded-2xl p-6 text-center shadow-[0_20px_50px_rgba(0,255,255,0.2)]">
              <div className="text-3xl font-black bg-gradient-to-r from-cyan-300 to-blue-400 bg-clip-text text-transparent mb-2">340%</div>
              <div className="text-cyan-200 font-medium">Average ROI</div>
            </div>
            <div className="bg-gradient-to-br from-slate-900/90 via-purple-900/80 to-slate-900/90 backdrop-blur-xl border border-purple-500/30 rounded-2xl p-6 text-center shadow-[0_20px_50px_rgba(139,92,246,0.2)]">
              <div className="text-3xl font-black bg-gradient-to-r from-purple-300 to-pink-400 bg-clip-text text-transparent mb-2">6 Months</div>
              <div className="text-purple-200 font-medium">To Profitability</div>
            </div>
            <div className="bg-gradient-to-br from-slate-900/90 via-emerald-900/80 to-slate-900/90 backdrop-blur-xl border border-emerald-500/30 rounded-2xl p-6 text-center shadow-[0_20px_50px_rgba(0,255,136,0.2)]">
              <div className="text-3xl font-black bg-gradient-to-r from-emerald-300 to-teal-400 bg-clip-text text-transparent mb-2">85%</div>
              <div className="text-emerald-200 font-medium">Success Rate</div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl p-8 md:p-12 text-white mb-16 max-w-6xl mx-auto">
          <h3 className="text-3xl font-bold mb-4">Start Your Free Trial Now</h3>
          <p className="text-purple-100 mb-8 max-w-2xl mx-auto">
             Join thousands of entrepreneurs using AI-driven data analysis to validate your startup ideas and make every decision data-backed.
           </p>
          <Button size="lg" variant="secondary" className="bg-white text-purple-600 hover:bg-gray-100">
             Start Free Trial
          </Button>
        </div>



        {/* 3D 霓虹定价卡片 */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-7xl mx-auto mb-20">
          {pricingPlans.map((plan, index) => (
            <div key={plan.id} className="relative group perspective-1000">
              {/* 3D 卡片容器 */}
              <div className={`relative bg-gradient-to-br from-slate-900/90 via-purple-900/80 to-slate-900/90 backdrop-blur-xl border ${
                plan.popular ? 'border-cyan-500/50' : 'border-purple-500/30'
              } rounded-3xl p-8 text-center transform-gpu transition-all duration-700 group-hover:rotateY-12 group-hover:scale-105 group-hover:-translate-y-6 ${
                plan.popular 
                  ? 'shadow-[0_30px_60px_rgba(0,255,255,0.3)] group-hover:shadow-[0_40px_80px_rgba(0,255,255,0.5)]' 
                  : 'shadow-[0_20px_50px_rgba(139,92,246,0.2)] group-hover:shadow-[0_30px_60px_rgba(139,92,246,0.4)]'
              } flex flex-col h-full`}>
                
                {/* 最受欢迎标签 */}
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 text-white px-6 py-2 text-sm font-bold rounded-full shadow-[0_10px_30px_rgba(0,255,255,0.4)] animate-pulse">
                    ⭐ MOST POPULAR
                  </div>
                )}
                
                {/* 3D 几何装饰 */}
                <div className="absolute -top-3 -right-3 w-6 h-6 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-full opacity-60 animate-bounce"></div>
                <div className="absolute -bottom-2 -left-2 w-4 h-4 bg-gradient-to-br from-purple-400 to-pink-500 transform rotate-45 opacity-40"></div>
                
                {/* 卡片标题 */}
                <div className="mb-6">
                  <h3 className={`text-3xl font-black mb-4 ${
                    plan.popular 
                      ? 'bg-gradient-to-r from-cyan-300 via-blue-400 to-purple-400 bg-clip-text text-transparent drop-shadow-[0_0_20px_rgba(0,255,255,0.5)]'
                      : 'bg-gradient-to-r from-purple-300 via-pink-400 to-cyan-300 bg-clip-text text-transparent'
                  }`}>
                    {plan.name}
                  </h3>
                  
                  {/* 价格显示 */}
                  <div className="flex items-baseline justify-center gap-2 mb-4">
                    {plan.id === 'enterprise' ? (
                      <span className="text-4xl font-black bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                        {plan.price}
                      </span>
                    ) : (
                      <>
                        <span className="text-5xl font-black bg-gradient-to-r from-cyan-300 via-blue-400 to-purple-400 bg-clip-text text-transparent">
                          ${plan.price}
                        </span>
                        <span className="text-gray-300 font-medium text-lg">/month</span>
                      </>
                    )}
                  </div>
                  
                  {/* ROI 指标 */}
                  <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-bold ${
                    plan.popular 
                      ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border border-cyan-400/30 text-cyan-300'
                      : 'bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-400/30 text-purple-300'
                  }`}>
                    <TrendingUp className="w-4 h-4 mr-2" />
                    {plan.id === 'free' ? 'Start Free' : 
                     plan.id === 'pro' ? 'ROI: 340%' :
                     plan.id === 'plus' ? 'ROI: 450%' : 'Custom ROI'}
                  </div>
                </div>
                
                {/* 功能列表 */}
                <div className="flex-1 mb-8">
                  <ul className="space-y-3 text-left">
                    {plan.features.slice(0, 6).map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-start gap-3">
                        <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 ${
                          plan.popular 
                            ? 'bg-gradient-to-r from-cyan-400 to-blue-500'
                            : 'bg-gradient-to-r from-purple-400 to-pink-500'
                        }`}>
                          <Check className="w-3 h-3 text-white" />
                        </div>
                        <span className="text-sm font-medium text-gray-300 leading-relaxed">{feature}</span>
                      </li>
                    ))}
                    {plan.features.length > 6 && (
                      <li className="text-sm text-gray-400 italic">
                        +{plan.features.length - 6} more features...
                      </li>
                    )}
                  </ul>
                </div>
                
                {/* CTA 按钮 */}
                <div className="mt-auto">
                  <button
                    className={`w-full py-4 px-6 rounded-2xl font-bold text-lg transition-all duration-500 transform group-hover:scale-105 ${
                      plan.popular 
                        ? 'bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 text-white shadow-[0_10px_30px_rgba(0,255,255,0.4)] hover:shadow-[0_15px_40px_rgba(0,255,255,0.6)] hover:from-cyan-300 hover:via-blue-400 hover:to-purple-500'
                        : 'bg-gradient-to-r from-purple-500/20 to-pink-500/20 border-2 border-purple-400/40 text-purple-300 hover:bg-gradient-to-r hover:from-purple-500/30 hover:to-pink-500/30 hover:border-purple-300/60'
                    }`}
                    onClick={() => handleSelectPlan(plan.id)}
                  >
                    {plan.buttonText}
                  </button>
                </div>
                
                {/* 霓虹边框效果 */}
                <div className={`absolute inset-0 rounded-3xl border ${
                  plan.popular ? 'border-cyan-500/20' : 'border-purple-500/20'
                } group-hover:border-opacity-40 transition-all duration-300`}></div>
              </div>
            </div>
          ))}
        </div>

        {/* 复古未来主义 CTA 区域 */}
        <div className="relative mt-32 mb-20">
          {/* 3D 背景装饰 */}
          <div className="absolute inset-0 overflow-hidden">
            {/* 霓虹网格背景 */}
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-900/20 via-purple-900/20 to-pink-900/20 backdrop-blur-3xl"></div>
            
            {/* 3D 几何装饰 */}
            <div className="absolute top-10 left-10 w-32 h-32 bg-gradient-to-br from-cyan-400/20 to-blue-500/20 rounded-full blur-xl animate-pulse"></div>
            <div className="absolute bottom-10 right-10 w-40 h-40 bg-gradient-to-br from-purple-400/20 to-pink-500/20 rounded-full blur-xl animate-pulse delay-1000"></div>
            
            {/* 霓虹线条 */}
            <div className="absolute top-1/2 left-0 w-full h-px bg-gradient-to-r from-transparent via-cyan-400/50 to-transparent"></div>
            <div className="absolute top-1/2 left-0 w-full h-px bg-gradient-to-r from-transparent via-purple-400/50 to-transparent translate-y-2"></div>
          </div>

          {/* CTA 内容容器 */}
          <div className="relative z-10 max-w-4xl mx-auto text-center px-6">
            {/* 3D 标题区域 */}
            <div className="mb-12">
              <div className="inline-block mb-6">
                <div className="relative">
                  {/* 3D 图标容器 */}
                  <div className="w-20 h-20 mx-auto mb-6 relative">
                    <div className="absolute inset-0 bg-gradient-to-br from-cyan-400 to-purple-600 rounded-2xl blur-lg opacity-60 animate-pulse"></div>
                    <div className="relative w-full h-full bg-gradient-to-br from-cyan-400 to-purple-600 rounded-2xl flex items-center justify-center transform rotate-3 hover:rotate-6 transition-transform duration-500">
                      <Rocket className="w-10 h-10 text-white" />
                    </div>
                  </div>
                  
                  {/* 3D 标题 */}
                  <h2 className="text-5xl md:text-6xl font-black mb-4">
                    <span className="bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 bg-clip-text text-transparent drop-shadow-[0_4px_8px_rgba(0,255,255,0.3)]">
                      Ready to Dominate
                    </span>
                  </h2>
                  <h3 className="text-4xl md:text-5xl font-black">
                    <span className="bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-400 bg-clip-text text-transparent drop-shadow-[0_4px_8px_rgba(255,0,255,0.3)]">
                      Your Market?
                    </span>
                  </h3>
                </div>
              </div>

              {/* 副标题 */}
              <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-2xl mx-auto leading-relaxed">
                Join <span className="text-cyan-400 font-bold">10,000+</span> entrepreneurs who've already 
                <span className="text-purple-400 font-bold"> validated their ideas</span> and 
                <span className="text-pink-400 font-bold"> scaled to success</span>
              </p>

              {/* ROI 数据展示 */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 max-w-3xl mx-auto">
                <div className="relative group">
                  <div className="absolute inset-0 bg-gradient-to-br from-cyan-400/20 to-blue-500/20 rounded-2xl blur-lg group-hover:blur-xl transition-all duration-300"></div>
                  <div className="relative bg-black/40 backdrop-blur-sm border border-cyan-400/30 rounded-2xl p-6">
                    <div className="text-3xl font-black text-cyan-400 mb-2">95%</div>
                    <div className="text-sm text-gray-300">Success Rate</div>
                  </div>
                </div>
                <div className="relative group">
                  <div className="absolute inset-0 bg-gradient-to-br from-purple-400/20 to-pink-500/20 rounded-2xl blur-lg group-hover:blur-xl transition-all duration-300"></div>
                  <div className="relative bg-black/40 backdrop-blur-sm border border-purple-400/30 rounded-2xl p-6">
                    <div className="text-3xl font-black text-purple-400 mb-2">3.2x</div>
                    <div className="text-sm text-gray-300">ROI Average</div>
                  </div>
                </div>
                <div className="relative group">
                  <div className="absolute inset-0 bg-gradient-to-br from-pink-400/20 to-cyan-500/20 rounded-2xl blur-lg group-hover:blur-xl transition-all duration-300"></div>
                  <div className="relative bg-black/40 backdrop-blur-sm border border-pink-400/30 rounded-2xl p-6">
                    <div className="text-3xl font-black text-pink-400 mb-2">24h</div>
                    <div className="text-sm text-gray-300">Time to Insights</div>
                  </div>
                </div>
              </div>
            </div>

            {/* 3D CTA 按钮组 */}
            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
              {/* 主要 CTA 按钮 */}
              <div className="relative group">
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 rounded-2xl blur-lg opacity-60 group-hover:opacity-80 transition-all duration-500 animate-pulse"></div>
                <button
                  className="relative px-12 py-6 bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 rounded-2xl font-black text-xl text-white transform hover:scale-105 transition-all duration-500 shadow-[0_10px_30px_rgba(0,255,255,0.4)] hover:shadow-[0_15px_40px_rgba(0,255,255,0.6)]"
                  onClick={() => handleSelectPlan('pro')}
                >
                  <span className="flex items-center gap-3">
                    <Zap className="w-6 h-6" />
                    Start Free Trial
                    <TrendingUp className="w-6 h-6" />
                  </span>
                </button>
              </div>

              {/* 次要 CTA 按钮 */}
              <div className="relative group">
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-2xl blur-lg opacity-60 group-hover:opacity-80 transition-all duration-500"></div>
                <button
                  className="relative px-10 py-5 bg-black/40 backdrop-blur-sm border-2 border-purple-400/40 rounded-2xl font-bold text-lg text-purple-300 transform hover:scale-105 transition-all duration-500 hover:border-purple-300/60 hover:bg-purple-500/10"
                  onClick={() => handleSelectPlan('enterprise')}
                >
                  <span className="flex items-center gap-3">
                    <Award className="w-5 h-5" />
                    Enterprise Demo
                  </span>
                </button>
              </div>
            </div>

            {/* 信任标识 */}
            <div className="mt-12 flex flex-wrap justify-center items-center gap-8 text-sm text-gray-400">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                <span>No Credit Card Required</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-cyan-400 rounded-full animate-pulse delay-300"></div>
                <span>30-Day Money Back</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-purple-400 rounded-full animate-pulse delay-700"></div>
                <span>Cancel Anytime</span>
              </div>
            </div>
          </div>

          {/* 霓虹边框效果 */}
          <div className="absolute inset-0 rounded-3xl border border-cyan-500/20 hover:border-opacity-40 transition-all duration-300"></div>
        </div>

        {/* Registration Modal */}
        {showRegistration && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle className="text-center">
                  {isTrialMode ? 'Start Your Free Trial' : 'Create Your Account'}
                </CardTitle>
                <CardDescription className="text-center">
                  {isTrialMode 
                    ? 'Start with our Free plan - 3 analyses per month' 
                    : 'Join thousands of entrepreneurs using IdeaEden'
                  }
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleRegistration} className="space-y-4">
                  <div>
                    <Label htmlFor="fullName">Full Name</Label>
                    <Input
                      id="fullName"
                      type="text"
                      value={registrationData.fullName}
                      onChange={(e) => setRegistrationData({...registrationData, fullName: e.target.value})}
                      placeholder="Enter your full name"
                    />
                  </div>
                  <div>
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      required
                      value={registrationData.email}
                      onChange={(e) => setRegistrationData({...registrationData, email: e.target.value})}
                      placeholder="Enter your email"
                    />
                  </div>
                  <div>
                    <Label htmlFor="username">Username</Label>
                    <Input
                      id="username"
                      type="text"
                      required
                      value={registrationData.username}
                      onChange={(e) => setRegistrationData({...registrationData, username: e.target.value})}
                      placeholder="Choose a username"
                    />
                  </div>
                  <div>
                    <Label htmlFor="password">Password</Label>
                    <Input
                      id="password"
                      type="password"
                      required
                      value={registrationData.password}
                      onChange={(e) => setRegistrationData({...registrationData, password: e.target.value})}
                      placeholder="Create a password"
                    />
                  </div>
                  <div className="flex gap-2 pt-4">
                    <Button
                      type="button"
                      variant="outline"
                      className="flex-1"
                      onClick={() => setShowRegistration(false)}
                    >
                      Cancel
                    </Button>
                    <Button type="submit" className="flex-1">
                      {isTrialMode ? 'Start Free Trial' : 'Create Account'}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default PricingPage;