import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { motion } from 'framer-motion';
import { 
  Zap, 
  Target, 
  Brain, 
  ArrowRight, 
  Clock, 
  CheckCircle,
  Star,
  TrendingUp,
  Users,
  BarChart3,
  Lightbulb
} from 'lucide-react';

interface AnalysisSelectionProps {
  onModeSelect: (mode: 'quick' | 'professional', keyword: string) => void;
  isLoading?: boolean;
  defaultKeyword?: string;
}

export function AnalysisSelection({ onModeSelect, isLoading = false, defaultKeyword = '' }: AnalysisSelectionProps) {
  const [keyword, setKeyword] = useState(defaultKeyword);

  const handleQuickAnalysis = () => {
    if (keyword.trim()) {
      onModeSelect('quick', keyword.trim());
    }
  };

  const handleProfessionalAnalysis = () => {
    if (keyword.trim()) {
      onModeSelect('professional', keyword.trim());
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && keyword.trim()) {
      handleQuickAnalysis(); // Default to quick analysis on Enter
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-4"
      >
        <h1 className="text-4xl font-bold text-gray-900">Keyword Analysis</h1>
        <p className="text-xl text-gray-600">
          Choose your analysis type and enter your startup idea or keyword
        </p>
      </motion.div>

      {/* Keyword Input */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="max-w-2xl mx-auto"
      >
        <Card className="border-2 border-gray-200 hover:border-gray-300 transition-colors">
          <CardContent className="p-6">
            <div className="space-y-4">
              <label className="text-sm font-medium text-gray-700">
                Enter your startup idea or keyword
              </label>
              <Input
                type="text"
                placeholder="e.g., AI-powered productivity tool, sustainable fashion, fintech app..."
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                onKeyPress={handleKeyPress}
                className="text-lg py-3"
                disabled={isLoading}
              />
              <p className="text-sm text-gray-500">
                Be specific about your product or service for better analysis results
              </p>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Analysis Options */}
      <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
        {/* Quick Analysis */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="h-full border-2 border-blue-200 hover:border-blue-400 hover:shadow-xl transition-all duration-300 group cursor-pointer">
            <CardHeader className="text-center pb-4">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-blue-200 transition-colors">
                <Zap className="w-8 h-8 text-blue-600" />
              </div>
              <CardTitle className="text-2xl text-gray-900">Quick Analysis</CardTitle>
              <CardDescription className="text-base">
                Fast market validation in under 2 minutes
              </CardDescription>
              <div className="flex items-center justify-center gap-2 mt-2">
                <Clock className="w-4 h-4 text-blue-600" />
                <span className="text-sm font-medium text-blue-600">~2 minutes</span>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-3">
                <h4 className="font-semibold text-gray-900">What you'll get:</h4>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-gray-700">Market validation score</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-gray-700">Search volume & trends</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-gray-700">Competition level</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-gray-700">Sentiment analysis</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-gray-700">Quick insights & recommendations</span>
                  </li>
                </ul>
              </div>

              <div className="pt-4 border-t border-gray-100">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm font-medium text-gray-700">Perfect for:</span>
                  <Badge variant="secondary" className="bg-blue-100 text-blue-700">
                    Beginners
                  </Badge>
                </div>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Initial idea validation</li>
                  <li>• Quick market checks</li>
                  <li>• Brainstorming sessions</li>
                </ul>
              </div>

              <Button 
                onClick={handleQuickAnalysis}
                disabled={!keyword.trim() || isLoading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3"
                size="lg"
              >
                {isLoading ? (
                  <>
                    <Brain className="w-4 h-4 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Zap className="w-4 h-4 mr-2" />
                    Start Quick Analysis
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </motion.div>

        {/* Professional Analysis */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="h-full border-2 border-purple-200 hover:border-purple-400 hover:shadow-xl transition-all duration-300 group cursor-pointer relative">
            <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
              <Badge className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-3 py-1">
                <Star className="w-3 h-3 mr-1" />
                Recommended
              </Badge>
            </div>
            <CardHeader className="text-center pb-4">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-purple-200 transition-colors">
                <Target className="w-8 h-8 text-purple-600" />
              </div>
              <CardTitle className="text-2xl text-gray-900">Professional Analysis</CardTitle>
              <CardDescription className="text-base">
                Comprehensive market intelligence & strategy
              </CardDescription>
              <div className="flex items-center justify-center gap-2 mt-2">
                <Clock className="w-4 h-4 text-purple-600" />
                <span className="text-sm font-medium text-purple-600">~5-8 minutes</span>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-3">
                <h4 className="font-semibold text-gray-900">Everything in Quick Analysis, plus:</h4>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-gray-700">Detailed competitor analysis</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-gray-700">User personas & demographics</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-gray-700">Business opportunities</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-gray-700">Risk assessment</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-gray-700">Financial projections</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-gray-700">Strategic recommendations</span>
                  </li>
                </ul>
              </div>

              <div className="pt-4 border-t border-gray-100">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm font-medium text-gray-700">Perfect for:</span>
                  <Badge variant="secondary" className="bg-purple-100 text-purple-700">
                    Entrepreneurs
                  </Badge>
                </div>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Business planning</li>
                  <li>• Investment pitches</li>
                  <li>• Strategic decisions</li>
                </ul>
              </div>

              <Button 
                onClick={handleProfessionalAnalysis}
                disabled={!keyword.trim() || isLoading}
                className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white py-3"
                size="lg"
              >
                {isLoading ? (
                  <>
                    <Brain className="w-4 h-4 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Target className="w-4 h-4 mr-2" />
                    Start Professional Analysis
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Feature Comparison */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="max-w-4xl mx-auto"
      >
        <Card className="bg-gradient-to-r from-gray-50 to-gray-100 border-gray-200">
          <CardHeader className="text-center">
            <CardTitle className="text-xl text-gray-900">Why Choose Professional Analysis?</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-6 text-center">
              <div className="space-y-2">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto">
                  <TrendingUp className="w-6 h-6 text-blue-600" />
                </div>
                <h4 className="font-semibold text-gray-900">Market Intelligence</h4>
                <p className="text-sm text-gray-600">
                  Deep market insights with competitor positioning and growth opportunities
                </p>
              </div>
              <div className="space-y-2">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                  <Users className="w-6 h-6 text-green-600" />
                </div>
                <h4 className="font-semibold text-gray-900">User Understanding</h4>
                <p className="text-sm text-gray-600">
                  Detailed user personas with pain points and motivations
                </p>
              </div>
              <div className="space-y-2">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto">
                  <Lightbulb className="w-6 h-6 text-purple-600" />
                </div>
                <h4 className="font-semibold text-gray-900">Strategic Guidance</h4>
                <p className="text-sm text-gray-600">
                  Actionable recommendations and financial projections
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}