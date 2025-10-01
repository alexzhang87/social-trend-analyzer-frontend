import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Check, Star, Zap, Crown, Building2, Sparkles } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { useAuth } from './auth-provider';
import { paymentsApi, CheckoutSessionRequest } from '../services/paymentsApi';
import { useToast } from '../hooks/use-toast';

interface PricingPlan {
  id: string;
  name: string;
  price: string;
  originalPrice?: string;
  discount?: number;
  credits: number;
  features: string[];
  buttonText: string;
  popular?: boolean;
  highlight: string;
  icon: React.ComponentType<any>;
  description: string;
}

const plans: PricingPlan[] = [
  {
    id: 'starter',
    name: 'Starter',
    price: '0',
    credits: 50,
    features: [
      '50 Analysis Credits',
      'Basic Trend Analysis',
      'Social Media Monitoring',
      '14 Days Data History',
      'Email Support',
      'Basic Reports'
    ],
    buttonText: 'Get Started Free',
    highlight: 'bg-gray-100',
    icon: Star,
    description: 'Perfect for getting started with social trend analysis'
  },
  {
    id: 'pro',
    name: 'Pro',
    price: '19',
    originalPrice: '29',
    discount: 34,
    credits: 200,
    features: [
      '200 Analysis Credits',
      'Advanced Analytics',
      'Real-time Monitoring',
      '90 Days Data History',
      'Priority Support',
      'Custom Reports',
      'API Access',
      'Team Collaboration'
    ],
    buttonText: 'Start 14-Day Free Trial',
    popular: true,
    highlight: 'bg-blue-50 border-blue-200',
    icon: Zap,
    description: 'Most popular choice for growing businesses'
  },
  {
    id: 'plus',
    name: 'Plus',
    price: '49',
    originalPrice: '79',
    discount: 38,
    credits: 500,
    features: [
      '500 Analysis Credits',
      'Premium Analytics',
      'Advanced AI Insights',
      '1 Year Data History',
      '24/7 Priority Support',
      'White-label Reports',
      'Advanced API',
      'Team Management',
      'Custom Integrations'
    ],
    buttonText: 'Start 14-Day Free Trial',
    highlight: 'bg-purple-50 border-purple-200',
    icon: Crown,
    description: 'Advanced features for scaling teams'
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 'Custom',
    credits: 0,
    features: [
      'Unlimited Analysis Credits',
      'Custom Deployment',
      'Advanced Security',
      'Unlimited Team Members',
      '24/7 Dedicated Support',
      'Custom Integrations',
      'Training & Consulting',
      'SLA Guarantee',
      'Custom Features'
    ],
    buttonText: 'Contact Sales',
    highlight: 'bg-gradient-to-br from-gray-50 to-gray-100',
    icon: Building2,
    description: 'Tailored solutions for large organizations'
  }
];

const PricingPage: React.FC = () => {
  const { user, login } = useAuth();
  const { toast } = useToast();
  const [showRegisterModal, setShowRegisterModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<string>('');
  const [isTrialMode, setIsTrialMode] = useState(false);

  const handleSelectPlan = async (planId: string) => {
    if (!user) {
      setSelectedPlan(planId);
      setShowRegisterModal(true);
      return;
    }

    try {
      if (planId === 'starter') {
        // Free plan - redirect to workspace
        window.location.href = '/workspace';
      } else if (planId === 'enterprise') {
        // Enterprise plan - contact sales
        window.location.href = 'mailto:sales@ideaeden.com?subject=Enterprise Plan Inquiry';
      } else {
        // Paid plans - create checkout session
        const plan = plans.find(p => p.id === planId);
        if (!plan) {
          toast({
            title: "Error",
            description: "Plan not found",
            variant: "destructive"
          });
          return;
        }

        const checkoutRequest: CheckoutSessionRequest = {
           product_type: 'subscription',
           product_id: planId,
           success_url: `${window.location.origin}/workspace?plan=${planId}&success=true`,
           cancel_url: `${window.location.origin}/pricing?canceled=true`
         };

        const response = await paymentsApi.createCheckoutSession(checkoutRequest);
         
         if (response.checkout_url) {
           window.location.href = response.checkout_url;
         } else {
           toast({
             title: "Error",
             description: "Failed to create checkout session",
             variant: "destructive"
           });
         }
       }
     } catch (error) {
       console.error('Error selecting plan:', error);
       if (error.response?.status === 401) {
         toast({
           title: "Authentication Required",
           description: "Please log in to continue",
           variant: "destructive"
         });
         // Redirect to login or show login modal
       } else if (error.response?.status === 402) {
         toast({
           title: "Payment Required",
           description: "Please check your payment method.",
           variant: "destructive"
         });
       } else if (error.response?.status === 429) {
         toast({
           title: "Rate Limited",
           description: "Too many requests. Please try again later.",
           variant: "destructive"
         });
       } else {
         toast({
           title: "Error",
           description: "Failed to process plan selection. Please try again.",
           variant: "destructive"
         });
       }
     }
   };

  const handleRegister = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;

    try {
      await login(email, password);
      setShowRegisterModal(false);
      handleSelectPlan(selectedPlan);
    } catch (error) {
      console.error('Registration failed:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        
        {/* Header Section */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="inline-flex items-center px-4 py-2 rounded-full bg-blue-100 text-blue-800 text-sm font-medium mb-6"
          >
            <Star className="w-4 h-4 mr-2" />
            Choose Your Plan
          </motion.div>

          {/* Main heading */}
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="text-4xl md:text-6xl font-bold text-gray-900 mb-6"
          >
            Simple, Transparent Pricing
          </motion.h1>

          {/* Subtitle */}
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="text-xl text-gray-600 max-w-3xl mx-auto"
          >
            Start free and scale as you grow. All plans include our core features with no hidden fees.
          </motion.p>
        </motion.div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-20">
          {plans.map((plan, index) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className={`relative rounded-2xl p-8 ${plan.highlight} ${
                plan.popular ? 'ring-2 ring-blue-500 shadow-xl scale-105' : 'shadow-lg'
              } transition-all duration-300 hover:shadow-xl`}
            >
              {/* Most popular label */}
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-blue-500 text-white px-4 py-2 text-sm font-bold rounded-full">
                  Most Popular
                </div>
              )}

              {/* Plan Icon */}
              <div className="flex justify-center mb-4">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                  plan.popular 
                    ? 'bg-blue-500' 
                    : 'bg-gray-600'
                }`}>
                  <plan.icon className="w-6 h-6 text-white" />
                </div>
              </div>

              {/* Plan name */}
              <h3 className="text-2xl font-bold text-gray-900 text-center mb-2">
                {plan.name}
              </h3>

              {/* Description */}
              <p className="text-gray-600 text-center mb-6 text-sm">
                {plan.description}
              </p>

              {/* Price display */}
              <div className="text-center mb-6">
                {plan.id === 'enterprise' ? (
                  <div className="text-3xl font-bold text-gray-900">
                    {plan.price}
                  </div>
                ) : (
                  <div className="space-y-2">
                    {/* Discount badge */}
                    {plan.discount && (
                      <div className="flex justify-center">
                        <Badge className="bg-green-500 text-white">
                          Save {plan.discount}%
                        </Badge>
                      </div>
                    )}
                    
                    {/* Price section */}
                    <div className="flex items-baseline justify-center gap-2">
                      <span className="text-4xl font-bold text-gray-900">
                        ${plan.price}
                      </span>
                      {plan.price !== '0' && (
                        <span className="text-gray-500">/month</span>
                      )}
                    </div>
                    
                    {/* Original price */}
                    {plan.originalPrice && (
                      <div className="flex justify-center">
                        <span className="text-lg text-gray-400 line-through">
                          ${plan.originalPrice}/month
                        </span>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Feature list */}
              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="flex items-start">
                    <Check className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-600 text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              {/* CTA button */}
              <Button
                className={`w-full ${
                  plan.popular 
                    ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                    : 'bg-white hover:bg-gray-50 text-gray-900 border border-gray-300'
                }`}
                onClick={() => handleSelectPlan(plan.id)}
              >
                {plan.buttonText}
              </Button>
            </motion.div>
          ))}
        </div>

        {/* CTA Section */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="text-center bg-gray-50 rounded-2xl p-12"
        >
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Join thousands of businesses using IdeaEden to validate their ideas and track market trends.
          </p>
          
          {/* Stats */}
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            <div>
              <div className="text-3xl font-bold text-blue-600">10,000+</div>
              <div className="text-gray-600">Ideas Validated</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-green-600">95%</div>
              <div className="text-gray-600">Success Rate</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-purple-600">24h</div>
              <div className="text-gray-600">Time to Insights</div>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
            <Button 
              size="lg" 
              className="bg-blue-600 hover:bg-blue-700 text-white px-8"
              onClick={() => handleSelectPlan('starter')}
            >
              Start Free Trial
            </Button>
            <Button 
              size="lg" 
              variant="outline"
              onClick={() => handleSelectPlan('enterprise')}
            >
              Contact Sales
            </Button>
          </div>

          {/* Trust Indicators */}
          <div className="flex flex-wrap justify-center gap-6 text-sm text-gray-500">
            <span>✓ No Credit Card Required</span>
            <span>✓ 30-Day Money Back Guarantee</span>
            <span>✓ Cancel Anytime</span>
          </div>
        </motion.div>

        {/* Registration Modal */}
        {showRegisterModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <Card className="w-full max-w-md mx-4">
              <CardHeader>
                <CardTitle>Create Your Account</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleRegister} className="space-y-4">
                  <div>
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      required
                      placeholder="Enter your email"
                    />
                  </div>
                  <div>
                    <Label htmlFor="password">Password</Label>
                    <Input
                      id="password"
                      name="password"
                      type="password"
                      required
                      placeholder="Create a password"
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button type="submit" className="flex-1">
                      Create Account
                    </Button>
                    <Button 
                      type="button" 
                      variant="outline"
                      onClick={() => setShowRegisterModal(false)}
                    >
                      Cancel
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
