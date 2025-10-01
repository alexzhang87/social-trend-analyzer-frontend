import React from 'react';
import { useAuth } from '@/components/auth-provider';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useNavigate } from 'react-router-dom';
import { 
  Lock, 
  Crown, 
  Sparkles, 
  ArrowRight,
  Star,
  Zap
} from 'lucide-react';

interface SubscriptionGateProps {
  feature?: string;
  requiredTier: 'free' | 'starter' | 'pro';
  userTier?: string;
  children: React.ReactNode;
  showPreview?: boolean;
  previewLines?: number;
}

const TIER_HIERARCHY = {
  free: 0,
  starter: 1,
  pro: 2
};

const FEATURE_DESCRIPTIONS = {
  'detailed-analysis': {
    title: 'Detailed Analysis Reports',
    description: 'Get comprehensive trend analysis, user profiles, and business opportunity identification',
    benefits: ['Complete User Profile Analysis', 'Business Opportunity Identification', 'Competitor Monitoring', 'PDF Report Export']
  },
  'unlimited-analysis': {
    title: 'Unlimited Analysis',
    description: 'No longer limited by analysis count, analyze any keywords anytime',
    benefits: ['Unlimited Keyword Analysis', 'Historical Data Comparison', 'Real-time Trend Monitoring', 'Batch Analysis Features']
  },
  'advanced-insights': {
    title: 'Advanced Business Insights',
    description: 'AI-driven deep market analysis and investment recommendations',
    benefits: ['AI Investment Recommendations', 'Market Size Forecasting', 'Risk Assessment', 'Competitive Landscape Analysis']
  },
  'export-features': {
    title: 'Data Export Features',
    description: 'Export analysis results to PDF, Excel and other formats',
    benefits: ['PDF Report Export', 'Excel Data Export', 'Custom Report Templates', 'Brand Customization']
  },
  'api-access': {
    title: 'API Access',
    description: 'Integrate our analysis capabilities into your system via API',
    benefits: ['RESTful API', 'Real-time Data Push', 'Custom Integration', 'Technical Support']
  }
};

export function SubscriptionGate({ 
  feature, 
  requiredTier, 
  userTier: propUserTier,
  children, 
  showPreview = false, 
  previewLines = 3 
}: SubscriptionGateProps) {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const userTier = propUserTier || user?.subscription_tier || 'free';
  const hasAccess = TIER_HIERARCHY[userTier as keyof typeof TIER_HIERARCHY] >= TIER_HIERARCHY[requiredTier];
  
  const featureInfo = FEATURE_DESCRIPTIONS[feature as keyof typeof FEATURE_DESCRIPTIONS];
  
  if (hasAccess) {
    return <>{children}</>;
  }
  
  return (
    <div className="relative">
      {/* Preview content (blurred effect) */}
      <div className="relative">
        <div className="filter blur-sm pointer-events-none">
          {children}
        </div>
        
        {/* Upgrade prompt overlay */}
        <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-black/60 via-purple-900/40 to-black/60 backdrop-blur-sm">
          <div className="bg-white/95 backdrop-blur-xl rounded-3xl p-8 max-w-md mx-4 text-center shadow-2xl border border-purple-200/50">
            
            {/* Icon and badge */}
            <div className="relative mb-6">
              <div className="w-20 h-20 mx-auto bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
                <Crown className="w-10 h-10 text-white" />
              </div>
              <div className="absolute -top-2 -right-2 bg-gradient-to-r from-orange-400 to-red-500 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg animate-pulse">
                PRO
              </div>
            </div>
            
            {/* Title and description */}
            <h3 className="text-2xl font-bold text-gray-800 mb-3">
              Unlock Premium Features
            </h3>
            <p className="text-gray-600 mb-6 leading-relaxed">
              Get access to advanced analytics, unlimited searches, and exclusive insights to supercharge your business growth.
            </p>
            
            {/* Feature list */}
            <div className="text-left mb-6 space-y-2">
              <div className="flex items-center gap-3 text-sm text-gray-700">
                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                <span>Unlimited trend analysis</span>
              </div>
              <div className="flex items-center gap-3 text-sm text-gray-700">
                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                <span>Advanced AI insights</span>
              </div>
              <div className="flex items-center gap-3 text-sm text-gray-700">
                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                <span>Priority support</span>
              </div>
            </div>
            
            {/* Upgrade button */}
            <Button 
              onClick={() => navigate('/pricing')}
              className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold py-3 px-6 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
            >
              <Crown className="w-4 h-4 mr-2" />
              Upgrade to Pro
            </Button>
            
            {/* Price hint */}
            <p className="text-xs text-gray-500 mt-3">
              Cancel anytime • 30-day money-back guarantee
            </p>
          </div>
        </div>
      </div>
      
      {/* Upgrade prompt overlay */}
      <div className={`${
        showPreview ? 'absolute inset-0' : ''
      } bg-gray-900/90 backdrop-blur-sm flex items-center justify-center rounded-lg p-6`}>
        <Card className="bg-gradient-to-r from-purple-900/80 to-blue-900/80 border-purple-500/50 max-w-md w-full">
          <CardContent className="p-6 text-center">
            {/* Icon and badge */}
            <div className="flex justify-center mb-4">
              {requiredTier === 'pro' ? (
                <div className="relative">
                  <Crown className="h-12 w-12 text-yellow-500" />
                  <Sparkles className="h-4 w-4 text-yellow-300 absolute -top-1 -right-1" />
                </div>
              ) : (
                <div className="relative">
                  <Lock className="h-12 w-12 text-purple-500" />
                  <Star className="h-4 w-4 text-purple-300 absolute -top-1 -right-1" />
                </div>
              )}
            </div>
            
            {/* Title and description */}
            <div className="mb-4">
              <Badge 
                variant="outline" 
                className="mb-2 border-yellow-500 text-yellow-500"
              >
                Pro Feature
              </Badge>
              <h3 className="text-xl font-bold text-white mb-2">
                {featureInfo?.title || 'Advanced Features'}
              </h3>
              <p className="text-gray-300 text-sm">
                {featureInfo?.description || 'Upgrade to unlock more advanced features'}
              </p>
            </div>
            
            {/* Feature list */}
            {featureInfo?.benefits && (
              <div className="mb-6">
                <div className="grid grid-cols-1 gap-2 text-left">
                  {featureInfo.benefits.slice(0, 3).map((benefit, index) => (
                    <div key={index} className="flex items-center gap-2 text-sm text-gray-300">
                      <Zap className="h-3 w-3 text-yellow-500 flex-shrink-0" />
                      <span>{benefit}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Upgrade button */}
            <div className="space-y-3">
              <Button 
                className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                onClick={() => navigate('/pricing')}
              >
                Upgrade to Pro
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
              
              {!user && (
                <Button 
                  variant="outline"
                  className="w-full border-gray-600 text-gray-300 hover:bg-gray-700"
                  onClick={() => navigate('/pricing?trial=true')}
                >
                  Free Trial
                </Button>
              )}
            </div>
            
            {/* Price hint */}
            <p className="text-xs text-gray-400 mt-3">
              Only $29/month, cancel anytime
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// Hook for analysis usage limits
export function useAnalysisLimit() {
  const { user } = useAuth();
  
  const getAnalysisLimit = () => {
    const tier = user?.subscription_tier || 'free';
    switch (tier) {
      case 'free':
        return { max: 3, current: 1 }; // Simulate 1 usage
      case 'pro':
      case 'enterprise':
        return { max: -1, current: 0 }; // Unlimited
      default:
        return { max: 3, current: 0 };
    }
  };
  
  const { max, current } = getAnalysisLimit();
  const remaining = max === -1 ? -1 : Math.max(0, max - current);
  const canAnalyze = max === -1 || remaining > 0;
  
  return {
    maxAnalyses: max,
    currentUsage: current,
    remainingAnalyses: remaining,
    canAnalyze,
    isUnlimited: max === -1
  };
}

// Hook for feature access control
export function useFeatureAccess() {
  const { user } = useAuth();
  
  const hasFeatureAccess = (requiredTier: 'free' | 'starter' | 'pro') => {
    const userTier = user?.subscription_tier || 'free';
    return TIER_HIERARCHY[userTier as keyof typeof TIER_HIERARCHY] >= TIER_HIERARCHY[requiredTier];
  };
  
  return {
    hasStarterAccess: hasFeatureAccess('starter'),
    hasProAccess: hasFeatureAccess('pro'),

    userTier: user?.subscription_tier || 'free',
    isLoggedIn: !!user
  };
}
