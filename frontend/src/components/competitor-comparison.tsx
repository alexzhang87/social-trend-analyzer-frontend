import React from 'react';
import { Check, X, Star, Clock, Users, Target, Zap, TrendingUp } from 'lucide-react';

interface CompetitorData {
  name: string;
  logo: string;
  website: string;
  tagline: string;
  coreFeatures: string[];
  pricing: {
    model: string;
    startingPrice: string;
    freeOption: boolean;
  };
  speed: string;
  reportDepth: string;
  targetUsers: string[];
  uniqueStrengths: string[];
  limitations: string[];
  rating: number;
}

const competitorData: CompetitorData[] = [
  {
    name: "Atypica.AI",
    logo: "🧠",
    website: "atypica.ai",
    tagline: "AI Research Agent Simulating Consumers",
    coreFeatures: [
      "AI Persona Generation",
      "Consumer Behavior Simulation",
      "Interview Automation",
      "Emotional Pattern Analysis",
      "Multi-Platform Social Intelligence"
    ],
    pricing: {
      model: "Token-based + Subscription",
      startingPrice: "$16/1M tokens",
      freeOption: false
    },
    speed: "10-20 minutes",
    reportDepth: "Deep psychological insights",
    targetUsers: ["Market Researchers", "Product Managers", "UX Designers"],
    uniqueStrengths: [
      "85% human-like accuracy in behavioral simulation",
      "Emotional and cognitive factor analysis",
      "Real-time persona interviews"
    ],
    limitations: [
      "Higher learning curve",
      "Token-based pricing can be expensive",
      "Limited free options"
    ],
    rating: 4.2
  },
  {
    name: "Validator.AI",
    logo: "✅",
    website: "validatorai.com",
    tagline: "AI Startup Mentor & Idea Validator",
    coreFeatures: [
      "Startup Idea Scoring",
      "Value Proposition Writing",
      "Competition Analysis",
      "Customer Simulation",
      "Launch Strategy Advice"
    ],
    pricing: {
      model: "Freemium",
      startingPrice: "Free basic validation",
      freeOption: true
    },
    speed: "Instant analysis",
    reportDepth: "Comprehensive startup guidance",
    targetUsers: ["Entrepreneurs", "Startup Founders", "Business Students"],
    uniqueStrengths: [
      "AI mentor with personalized advice",
      "Free basic validation available",
      "Startup-focused methodology"
    ],
    limitations: [
      "Less detailed market research",
      "Limited advanced features in free tier",
      "Primarily startup-focused"
    ],
    rating: 4.0
  },
  {
    name: "DimeADozen.AI",
    logo: "💎",
    website: "dimeadozen.ai",
    tagline: "AI Business Validation in Seconds",
    coreFeatures: [
      "Instant Business Validation",
      "40+ Page Reports",
      "Competitor Analysis",
      "Market Trend Analysis",
      "Growth Strategy Recommendations"
    ],
    pricing: {
      model: "Pay-per-report",
      startingPrice: "~$39/report",
      freeOption: true
    },
    speed: "Under 20 seconds",
    reportDepth: "Comprehensive 40+ page reports",
    targetUsers: ["Entrepreneurs", "Consultants", "Venture Studios"],
    uniqueStrengths: [
      "Ultra-fast report generation",
      "Comprehensive market intelligence",
      "100,000+ ideas validated"
    ],
    limitations: [
      "Less personalized insights",
      "Report quality varies by industry",
      "Limited real-time interaction"
    ],
    rating: 4.3
  }
];

const CompetitorComparison: React.FC = () => {
  const renderFeatureList = (features: string[], maxItems: number = 3) => (
    <ul className="space-y-1">
      {features.slice(0, maxItems).map((feature, index) => (
        <li key={index} className="flex items-center text-sm">
          <Check className="w-3 h-3 text-green-500 mr-2 flex-shrink-0" />
          <span>{feature}</span>
        </li>
      ))}
      {features.length > maxItems && (
        <li className="text-xs text-gray-500">+{features.length - maxItems} more</li>
      )}
    </ul>
  );

  const renderRating = (rating: number) => (
    <div className="flex items-center space-x-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <Star
          key={star}
          className={`w-4 h-4 ${
            star <= rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
          }`}
        />
      ))}
      <span className="text-sm text-gray-600 ml-1">{rating}</span>
    </div>
  );

  return (
    <div className="bg-white py-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            How We Compare to Leading AI Validation Tools
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            See how our comprehensive business validation platform stacks up against other popular AI tools in the market.
          </p>
        </div>

        {/* Comparison Table */}
        <div className="overflow-x-auto">
          <div className="inline-block min-w-full align-middle">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Our Product Column */}
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border-2 border-blue-200 relative">
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <span className="bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                    Our Solution
                  </span>
                </div>
                
                <div className="text-center mb-6 mt-4">
                  <div className="text-4xl mb-2">🚀</div>
                  <h3 className="text-xl font-bold text-gray-900">IdeaEden</h3>
                  <p className="text-sm text-gray-600">Comprehensive Business Intelligence Platform</p>
                </div>

                <div className="space-y-6">
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                      <Zap className="w-4 h-4 mr-2 text-blue-600" />
                      Core Features
                    </h4>
                    {renderFeatureList([
                      "Multi-source Data Integration",
                      "Real-time Market Analysis",
                      "PMF Assessment",
                      "Competitive Intelligence",
                      "Social Media Insights"
                    ])}
                  </div>

                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                      <Target className="w-4 h-4 mr-2 text-blue-600" />
                      Pricing
                    </h4>
                    <div className="text-sm">
                      <p className="font-medium text-green-600">Freemium Model</p>
                      <p className="text-gray-600">Free tier + Pro plans</p>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                      <Clock className="w-4 h-4 mr-2 text-blue-600" />
                      Analysis Speed
                    </h4>
                    <p className="text-sm text-gray-700">2-5 minutes</p>
                  </div>

                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                      <TrendingUp className="w-4 h-4 mr-2 text-blue-600" />
                      Report Depth
                    </h4>
                    <p className="text-sm text-gray-700">Multi-dimensional analysis with actionable insights</p>
                  </div>

                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                      <Users className="w-4 h-4 mr-2 text-blue-600" />
                      Target Users
                    </h4>
                    {renderFeatureList([
                      "Entrepreneurs",
                      "Product Managers",
                      "Market Researchers",
                      "Consultants"
                    ])}
                  </div>

                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Rating</h4>
                    {renderRating(4.8)}
                  </div>
                </div>
              </div>

              {/* Competitor Columns */}
              {competitorData.map((competitor, index) => (
                <div key={index} className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
                  <div className="text-center mb-6">
                    <div className="text-4xl mb-2">{competitor.logo}</div>
                    <h3 className="text-xl font-bold text-gray-900">{competitor.name}</h3>
                    <p className="text-sm text-gray-600">{competitor.tagline}</p>
                    <a 
                      href={`https://${competitor.website}`} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-xs text-blue-600 hover:underline"
                    >
                      {competitor.website}
                    </a>
                  </div>

                  <div className="space-y-6">
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                        <Zap className="w-4 h-4 mr-2 text-gray-600" />
                        Core Features
                      </h4>
                      {renderFeatureList(competitor.coreFeatures)}
                    </div>

                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                        <Target className="w-4 h-4 mr-2 text-gray-600" />
                        Pricing
                      </h4>
                      <div className="text-sm">
                        <p className="font-medium">{competitor.pricing.model}</p>
                        <p className="text-gray-600">{competitor.pricing.startingPrice}</p>
                        <div className="flex items-center mt-1">
                          {competitor.pricing.freeOption ? (
                            <Check className="w-3 h-3 text-green-500 mr-1" />
                          ) : (
                            <X className="w-3 h-3 text-red-500 mr-1" />
                          )}
                          <span className="text-xs">Free option</span>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                        <Clock className="w-4 h-4 mr-2 text-gray-600" />
                        Analysis Speed
                      </h4>
                      <p className="text-sm text-gray-700">{competitor.speed}</p>
                    </div>

                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                        <TrendingUp className="w-4 h-4 mr-2 text-gray-600" />
                        Report Depth
                      </h4>
                      <p className="text-sm text-gray-700">{competitor.reportDepth}</p>
                    </div>

                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                        <Users className="w-4 h-4 mr-2 text-gray-600" />
                        Target Users
                      </h4>
                      {renderFeatureList(competitor.targetUsers)}
                    </div>

                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Rating</h4>
                      {renderRating(competitor.rating)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Key Differentiators */}
        <div className="mt-12 bg-gray-50 rounded-xl p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            Why Choose IdeaEden?
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Zap className="w-8 h-8 text-blue-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Comprehensive Analysis</h4>
              <p className="text-sm text-gray-600">
                Multi-source data integration provides the most complete picture of your market opportunity.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Target className="w-8 h-8 text-green-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Actionable Insights</h4>
              <p className="text-sm text-gray-600">
                Not just data, but clear recommendations on what to do next to validate and launch your idea.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Users className="w-8 h-8 text-purple-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">User-Friendly</h4>
              <p className="text-sm text-gray-600">
                Designed for entrepreneurs of all levels, from first-time founders to experienced business leaders.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompetitorComparison;
