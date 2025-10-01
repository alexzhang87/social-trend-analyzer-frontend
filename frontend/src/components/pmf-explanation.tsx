import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Target, 
  Brain, 
  Clock, 
  TrendingUp, 
  Users, 
  BarChart3,
  Lightbulb,
  RefreshCw,
  Info
} from 'lucide-react';

export function PMFExplanation() {
  return (
    <div className="space-y-6">
      {/* What is PMF */}
      <Card className="glass-card border-white/10 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Target className="w-5 h-5 text-cyan-400" />
            What is Product-Market Fit (PMF)?
          </CardTitle>
          <CardDescription className="text-gray-300">
            Product-Market Fit is a key metric that measures how well a product matches target market demand
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-gray-300 leading-relaxed">
            PMF assessment helps you understand whether your product meets real market demand, which is a crucial milestone for startup success.
            Our system provides comprehensive PMF evaluation through multi-dimensional analysis.
          </p>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <h4 className="font-semibold text-white flex items-center gap-2">
                <Users className="w-4 h-4 text-green-400" />
                Core Metrics
              </h4>
              <ul className="space-y-2 text-sm text-gray-300">
                <li>• Market Demand Strength</li>
                <li>• Product Fit</li>
                <li>• User Satisfaction</li>
                <li>• Growth Potential</li>
                <li>• Competitive Advantage</li>
                <li>• Business Viability</li>
              </ul>
            </div>
            
            <div className="space-y-3">
              <h4 className="font-semibold text-white flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-purple-400" />
                Assessment Value
              </h4>
              <ul className="space-y-2 text-sm text-gray-300">
                <li>• Validate Business Assumptions</li>
                <li>• Optimize Product Direction</li>
                <li>• Reduce Investment Risk</li>
                <li>• Increase Success Probability</li>
                <li>• Guide Resource Allocation</li>
                <li>• Develop Growth Strategy</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* How it Works */}
      <Card className="glass-card border-white/10 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Brain className="w-5 h-5 text-cyan-400" />
            How Does PMF Assessment Work?
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            {/* Manual Assessment */}
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-cyan-500 to-purple-500 flex items-center justify-center">
                  <Users className="w-4 h-4 text-white" />
                </div>
                <div>
                  <h4 className="font-semibold text-white">Manual Assessment</h4>
                  <Badge variant="outline" className="mt-1 bg-white/10 border-white/20 text-gray-300">
                    Subjective Analysis
                  </Badge>
                </div>
              </div>
              
              <div className="space-y-3 pl-11">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-yellow-400" />
                  <span className="text-sm text-gray-300">Frequency: On-demand Assessment</span>
                </div>
                <p className="text-sm text-gray-300">
                  By answering a series of questions about customer satisfaction, market demand, product usability, etc.,
                  get PMF scores based on team experience and market insights.
                </p>
                <ul className="text-xs text-gray-400 space-y-1">
                  <li>• Suitable for early product stage and after major changes</li>
                  <li>• Recommended monthly or quarterly</li>
                  <li>• Better results when combined with team discussions</li>
                </ul>
              </div>
            </div>

            {/* Automated Assessment */}
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-green-500 to-blue-500 flex items-center justify-center">
                  <Brain className="w-4 h-4 text-white" />
                </div>
                <div>
                  <h4 className="font-semibold text-white">Automated Assessment</h4>
                  <Badge variant="outline" className="mt-1 bg-white/10 border-white/20 text-gray-300">
                    Data-Driven
                  </Badge>
                </div>
              </div>
              
              <div className="space-y-3 pl-11">
                <div className="flex items-center gap-2">
                  <RefreshCw className="w-4 h-4 text-green-400" />
                  <span className="text-sm text-gray-300">Frequency: Real-time Updates</span>
                </div>
                <p className="text-sm text-gray-300">
                  Based on keyword analysis data, automatically calculate market demand, competitive landscape, search trends and other indicators,
                  providing objective PMF assessment results.
                </p>
                <ul className="text-xs text-gray-400 space-y-1">
                  <li>• Automatically triggered after each keyword analysis</li>
                  <li>• Calculated based on real market data</li>
                  <li>• Provides trend change tracking</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Integration */}
          <Alert className="bg-white/5 border-white/10">
            <Info className="h-4 w-4 text-cyan-400" />
            <AlertDescription className="text-gray-300">
              <strong className="text-white">Smart Integration:</strong>
              Manual assessment provides subjective insights, while automated assessment provides objective data. When used together,
              they enable comprehensive understanding of product-market fit and identification of potential opportunities and risks.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      {/* Scoring System */}
      <Card className="glass-card border-white/10 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <BarChart3 className="w-5 h-5 text-cyan-400" />
            Scoring System Explanation
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="text-center p-4 rounded-lg bg-red-500/10 border border-red-500/20">
              <div className="text-2xl font-bold text-red-400 mb-2">0-4 Points</div>
              <div className="text-sm font-medium text-red-300 mb-1">Needs Improvement</div>
              <p className="text-xs text-gray-400">
                Low product-market fit, need to reassess product positioning or target market
              </p>
            </div>
            
            <div className="text-center p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
              <div className="text-2xl font-bold text-yellow-400 mb-2">5-7 Points</div>
              <div className="text-sm font-medium text-yellow-300 mb-1">Has Potential</div>
              <p className="text-xs text-gray-400">
                Shows some market potential, but still needs optimization of product features and market strategy
              </p>
            </div>
            
            <div className="text-center p-4 rounded-lg bg-green-500/10 border border-green-500/20">
              <div className="text-2xl font-bold text-green-400 mb-2">8-10 Points</div>
              <div className="text-sm font-medium text-green-300 mb-1">Excellent Match</div>
              <p className="text-xs text-gray-400">
                High product-market fit, can consider accelerating growth and expanding market share
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Best Practices */}
      <Card className="glass-card border-white/10 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Lightbulb className="w-5 h-5 text-cyan-400" />
            Usage Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h4 className="font-semibold text-white">Assessment Frequency Recommendations</h4>
              <ul className="space-y-2 text-sm text-gray-300">
                <li className="flex items-start gap-2">
                  <div className="w-2 h-2 rounded-full bg-cyan-400 mt-2 flex-shrink-0"></div>
                  <span><strong className="text-white">Early Stage:</strong>Manual assessment every 2 weeks</span>
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-2 h-2 rounded-full bg-purple-400 mt-2 flex-shrink-0"></div>
                  <span><strong className="text-white">Growth Stage:</strong>Monthly combination of automated and manual assessment</span>
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-2 h-2 rounded-full bg-green-400 mt-2 flex-shrink-0"></div>
                  <span><strong className="text-white">Mature Stage:</strong>Quarterly in-depth assessment</span>
                </li>
              </ul>
            </div>
            
            <div className="space-y-3">
              <h4 className="font-semibold text-white">Optimization Strategy</h4>
              <ul className="space-y-2 text-sm text-gray-300">
                <li className="flex items-start gap-2">
                  <div className="w-2 h-2 rounded-full bg-yellow-400 mt-2 flex-shrink-0"></div>
                  <span>Focus on score trend changes, not single results</span>
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-2 h-2 rounded-full bg-blue-400 mt-2 flex-shrink-0"></div>
                  <span>Combine user feedback to validate assessment results</span>
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-2 h-2 rounded-full bg-pink-400 mt-2 flex-shrink-0"></div>
                  <span>Develop specific improvement plans for low-scoring items</span>
                </li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
