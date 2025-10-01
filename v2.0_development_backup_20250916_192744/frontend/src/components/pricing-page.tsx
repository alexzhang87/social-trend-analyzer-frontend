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
    <div className="min-h-screen relative overflow-hidden py-12 px-4 sm:px-6">
      {/* Background decorative elements */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-1/4 left-1/4 w-72 h-72 gradient-primary rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float"></div>
        <div className="absolute top-1/3 right-1/4 w-72 h-72 gradient-secondary rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float" style={{animationDelay: '2s'}}></div>
        <div className="absolute bottom-1/4 left-1/3 w-72 h-72 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float" style={{animationDelay: '4s'}}></div>
      </div>
      
      <div className="max-w-7xl mx-auto relative z-10">
        {/* Limited Time Offer Banner */}
        <div className="glass-card bg-gradient-to-r from-red-500/90 to-pink-500/90 text-white text-center py-4 rounded-2xl mb-8 shadow-modern-lg animate-slide-up">
          <div className="flex items-center justify-center gap-2">
            <Flame className="w-5 h-5" />
            <span className="font-semibold">🎉 Limited Time Offer: 50% OFF on Pro plans!</span>
            <Clock className="w-5 h-5" />
          </div>
          <p className="text-sm opacity-90 mt-1">Valid until December 31, 2025</p>
        </div>

        <div className="text-center mb-16 animate-slide-up" style={{animationDelay: '0.2s'}}>
          <div className="inline-flex items-center px-4 py-2 bg-blue-500/10 border border-blue-500/20 rounded-full text-blue-400 text-sm font-medium mb-6">
            🎉 Limited Time Offer: 50% off Pro plan first month
          </div>
          <h1 className="text-4xl md:text-6xl font-black mb-6 tracking-tight leading-tight">
            <span className="bg-gradient-to-r from-cyan-300 to-purple-300 bg-clip-text text-transparent font-extrabold">
              Choose the Right
            </span>
            <br />
            <span className="bg-gradient-to-r from-purple-300 to-green-300 bg-clip-text text-transparent font-extrabold">
              Data Validation Plan
            </span>
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed font-medium">
            🤖 AI-driven multi-source data analysis for data-backed entrepreneurial decisions - Start free, upgrade as needed
          </p>
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



        {/* Pricing Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto mb-16 animate-fade-in" style={{animationDelay: '0.4s'}}>
          {pricingPlans.map((plan, index) => (
            <Card key={plan.id} className={`relative overflow-hidden glass-card shadow-modern-lg hover:shadow-modern-xl transition-all duration-500 glow-hover ${plan.popular ? 'ring-2 ring-blue-400/50' : ''} animate-slide-up flex flex-col h-full`} style={{animationDelay: `${0.6 + index * 0.1}s`}}>
              {plan.popular && (
                <div className="absolute top-0 right-0 bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-4 py-2 text-sm font-semibold rounded-bl-2xl shadow-lg">
                  ⭐ Most Popular
                </div>
              )}
              <CardHeader className="text-center pb-6">
                <CardTitle className="text-2xl font-black mb-4 text-white">{plan.name}</CardTitle>
                <div className="flex items-baseline justify-center gap-1 mt-2">
                  {plan.id === 'enterprise' ? (
                    <span className="text-5xl font-black bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">${plan.price}</span>
                  ) : (
                    <>
                      <span className="text-5xl font-black bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">${plan.price}</span>
                      <span className="text-white font-medium">/month</span>
                      {plan.originalPrice && (
                        <Badge variant="destructive" className="text-xs font-semibold px-2 py-1 rounded-full ml-2">
                          {plan.discount}% OFF
                        </Badge>
                      )}
                    </>
                  )}
                </div>
                <CardDescription className="mt-4 text-white font-medium text-base">
                  🎯 {plan.creditsPerMonth} analyses per month
                </CardDescription>
              </CardHeader>
              <CardContent className="px-6">
                <ul className="space-y-4 mb-8 min-h-[300px]">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <div className="w-5 h-5 rounded-full bg-gradient-to-r from-green-400 to-emerald-500 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <Check className="w-3 h-3 text-white" />
                      </div>
                      <span className="text-sm font-medium text-white leading-relaxed">{feature}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
              <CardFooter className="flex flex-col gap-4 px-6 pb-6 mt-auto">
                <Button
                  className={`w-full py-3 font-semibold text-base rounded-xl transition-all duration-300 ${
                    plan.popular 
                      ? 'bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white shadow-lg hover:shadow-xl transform hover:scale-105' 
                      : plan.buttonVariant === 'outline'
                      ? 'border-2 border-gray-300 hover:border-gray-400 bg-transparent hover:bg-gray-50 dark:hover:bg-gray-800'
                      : 'bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-700 hover:to-gray-800 text-white'
                  }`}
                  variant={plan.popular ? 'default' : plan.buttonVariant}
                  onClick={() => handleSelectPlan(plan.id)}
                >
                  {plan.buttonText}
                </Button>
              </CardFooter>
            </Card>
          ))}
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