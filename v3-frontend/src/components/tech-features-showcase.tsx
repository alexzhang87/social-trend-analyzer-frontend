import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { 
  Brain, 
  BarChart3, 
  Database, 
  Cpu, 
  Sparkles, 
  Target, 
  Zap, 
  TrendingUp,
  Eye,
  Layers,
  ArrowRight,
  Check
} from 'lucide-react';

interface ToolFeature {
  id: string;
  name: string;
  category: 'analysis' | 'visualization' | 'ai';
  icon: React.ComponentType<any>;
  description: string;
  features: string[];
  tier: 'free' | 'starter' | 'pro';
  isNew?: boolean;
}

const toolFeatures: ToolFeature[] = [
  {
    id: 'multilevel-sentiment',
    name: 'Multi-level Sentiment Analysis',
    category: 'analysis',
    icon: Brain,
    description: 'Combines VADER, TextBlob, NLTK algorithms for more accurate sentiment insights',
    features: [
      'VADER algorithm optimized for social media text',
      'TextBlob confidence validation',
      'NLTK entity recognition and keyword extraction',
      'Multi-algorithm cross-validation'
    ],
    tier: 'starter',
    isNew: true
  },
  {
    id: 'monkeylearn-ai',
    name: 'MonkeyLearn AI Enhancement',
    category: 'ai',
    icon: Sparkles,
    description: 'Cloud AI provides advanced analysis features like topic classification and intent detection',
    features: [
      'Smart topic classification',
      'User intent detection',
      'Graceful degradation mechanism',
      'Smart API quota management'
    ],
    tier: 'starter',
    isNew: true
  },
  {
    id: 'comprehensive-analysis',
    name: 'Comprehensive Multi-Platform Analysis',
    category: 'analysis',
    icon: Layers,
    description: 'Integrates data from Twitter, Reddit, Product Hunt, and Google Trends platforms',
    features: [
      'Twitter real-time trending data',
      'Reddit community discussion analysis',
      'Product Hunt product trends',
      'Google Trends search volume'
    ],
    tier: 'pro',
    isNew: true
  },
  {
    id: 'google-data-studio',
    name: 'Google Data Studio',
    category: 'visualization',
    icon: BarChart3,
    description: 'Professional data visualization through Google Sheets, completely free',
    features: [
      'One-click data export to Google Sheets',
      'Pre-configured dashboard templates',
      'Real-time data updates',
      'Professional charts and reports'
    ],
    tier: 'starter',
    isNew: true
  },
  {
    id: 'metabase-bi',
    name: 'Metabase Open Source BI',
    category: 'visualization',
    icon: Database,
    description: 'Enterprise-level open source BI tool with 40+ chart types, replacing expensive commercial solutions',
    features: [
      'One-click Docker deployment',
      '40+ professional chart types',
      'SQL query editor',
      'Custom dashboard creation'
    ],
    tier: 'pro',
    isNew: true
  },
  {
    id: 'smart-insights',
    name: 'Smart Insights Generation',
    category: 'ai',
    icon: Eye,
    description: 'Automatically generates business insights and opportunity identification based on multi-platform data',
    features: [
      'Trend strength scoring algorithm',
      'Automatic business opportunity identification',
      'Competitive landscape analysis',
      'Market value assessment'
    ],
    tier: 'pro'
  }
];

const tierColors = {
  free: 'bg-muted text-muted-foreground',
  starter: 'bg-blue-500/20 text-blue-400',
  pro: 'bg-purple-500/20 text-purple-400'
};

const categoryIcons = {
  analysis: Target,
  visualization: TrendingUp,
  ai: Cpu
};

export function TechFeaturesShowcase() {
  const categories = ['analysis', 'visualization', 'ai'] as const;
  
  return (
    <section className="py-16 px-4 bg-gradient-to-br from-background to-card">
      <div className="max-w-7xl mx-auto">
        {/* Title section */}
        <div className="text-center mb-12 animate-slide-up">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            <span className="bg-gradient-to-r from-cyan-300 to-purple-300 bg-clip-text text-transparent">
              Professional Analysis Tools
            </span>
            <br />
            <span className="text-foreground">Startup Pricing</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-3xl mx-auto mb-6">
            We integrate the most advanced open-source tools and AI technology to provide you with professional-grade data analysis and visualization capabilities
          </p>
          <div className="flex justify-center gap-4 flex-wrap">
            <Badge className="bg-green-100 text-green-800 px-4 py-2">
              <Check className="w-4 h-4 mr-2" />
              100% Open Source Free
            </Badge>
            <Badge className="bg-blue-100 text-blue-800 px-4 py-2">
              <Zap className="w-4 h-4 mr-2" />
              Quick Deployment
            </Badge>
            <Badge className="bg-purple-100 text-purple-800 px-4 py-2">
              <Sparkles className="w-4 h-4 mr-2" />
              AI Enhanced
            </Badge>
          </div>
        </div>

        {/* Category display */}
        {categories.map((category, categoryIndex) => {
          const CategoryIcon = categoryIcons[category];
          const categoryTools = toolFeatures.filter(tool => tool.category === category);
          
          const categoryNames = {
            analysis: 'Data Analysis Engine',
            visualization: 'Visualization Tools',
            ai: 'AI Intelligent Analysis'
          };

          return (
            <div key={category} className="mb-16">
              {/* Category title */}
              <div className="flex items-center gap-3 mb-8 animate-fade-in" style={{animationDelay: `${categoryIndex * 0.2}s`}}>
                <div className="p-3 rounded-xl gradient-primary">
                  <CategoryIcon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-foreground">
                  {categoryNames[category]}
                </h3>
                <div className="flex-1 h-px bg-gradient-to-r from-gray-300 to-transparent"></div>
              </div>

              {/* Tool card grid */}
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {categoryTools.map((tool, toolIndex) => {
                  const ToolIcon = tool.icon;
                  
                  return (
                    <Card 
                      key={tool.id} 
                      className="glass-card shadow-modern hover:shadow-modern-lg transition-all duration-300 transform hover:-translate-y-2 animate-slide-up"
                      style={{animationDelay: `${(categoryIndex * 0.2) + (toolIndex * 0.1)}s`}}
                    >
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg gradient-secondary">
                              <ToolIcon className="w-5 h-5 text-white" />
                            </div>
                            <div>
                              <CardTitle className="text-lg font-semibold flex items-center gap-2">
                                {tool.name}
                                {tool.isNew && (
                                  <Badge className="bg-gradient-to-r from-red-500 to-pink-500 text-white text-xs animate-pulse">
                                    NEW
                                  </Badge>
                                )}
                              </CardTitle>
                            </div>
                          </div>
                          <Badge className={tierColors[tool.tier]}>
                            {tool.tier.toUpperCase()}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
                          {tool.description}
                        </p>
                      </CardHeader>
                      
                      <CardContent>
                        <div className="space-y-2 mb-4">
                          {tool.features.map((feature, index) => (
                            <div key={index} className="flex items-start gap-2 text-sm">
                              <Check className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                              <span className="text-foreground">{feature}</span>
                            </div>
                          ))}
                        </div>
                        
                        <Button 
                          className="w-full group gradient-primary text-white shadow-modern hover:shadow-modern-lg transition-all duration-300"
                          size="sm"
                        >
                          Try Now
                          <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                        </Button>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>
          );
        })}

        {/* Bottom CTA */}
        <div className="text-center mt-16 animate-fade-in" style={{animationDelay: '1s'}}>
          <div className="glass-card rounded-2xl p-8 shadow-modern-lg">
            <h3 className="text-2xl font-bold mb-4 gradient-primary bg-clip-text text-transparent">
              Ready to Experience Professional Analysis Capabilities?
            </h3>
            <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
              Our tool suite allows you to gain the most professional data insights at minimal cost. Start now and experience the power of AI-driven social media analysis.
            </p>
            <div className="flex justify-center gap-4 flex-wrap">
              <Button className="gradient-primary text-white px-8 py-3 text-lg shadow-modern glow-hover">
                Start Free Trial
                <Sparkles className="w-5 h-5 ml-2" />
              </Button>
              <Button variant="outline" className="px-8 py-3 text-lg border-border hover:bg-accent/10">
                View Pricing
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default TechFeaturesShowcase;