import { useState, useEffect } from 'react';
// Card components removed - using glass-card div instead
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Zap, 
  Target, 
  Clock, 
  Star, 
  TrendingUp, 
  Users, 
  BarChart3, 
  FileText,
  ArrowRight,
  CheckCircle,
  Sparkles,
  Brain,
  Rocket
} from 'lucide-react';
import { useAuth } from '@/components/auth-provider';
import { useToast } from '@/components/ui/use-toast';
import { trendsApiClient } from '@/lib/trends-api';

interface AnalysisMode {
  id: 'quick' | 'professional';
  title: string;
  subtitle: string;
  description: string;
  features: string[];
  cost: number;
  duration: string;
  icon: React.ComponentType<any>;
  color: string;
  recommended?: boolean;
}

const analysisModes: AnalysisMode[] = [
  {
    id: 'quick',
    title: 'Quick Validation',
    subtitle: 'Instant Market Check',
    description: 'Validate your idea in 30 seconds with AI-powered insights',
    features: [
      'One-click analysis',
      'Market demand score',
      'Trend momentum',
      'Competition level',
      'Instant recommendations'
    ],
    cost: 1,
    duration: '30 seconds',
    icon: Zap,
    color: 'bg-blue-500'
  },
  {
    id: 'professional',
    title: 'Professional Analysis',
    subtitle: 'Complete Market Intelligence',
    description: 'Deep dive analysis with actionable business insights',
    features: [
      'Multi-source data integration',
      'PMF assessment score',
      'Competitor landscape mapping',
      'User persona analysis',
      'Revenue opportunity sizing',
      'Strategic recommendations'
    ],
    cost: 3,
    duration: '2-5 minutes',
    icon: Target,
    color: 'bg-purple-500',
    recommended: true
  }
];

interface DualTrackAnalysisProps {
  onModeSelect: (mode: 'quick' | 'professional', keyword: string) => void;
  isLoading?: boolean;
}

export function DualTrackAnalysis({ onModeSelect, isLoading = false }: DualTrackAnalysisProps) {
  const [keyword, setKeyword] = useState('');
  const [selectedMode, setSelectedMode] = useState<'quick' | 'professional' | null>(null);
  const [userCredits, setUserCredits] = useState(0);
  const { user } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    if (user) {
      fetchUserCredits();
    }
  }, [user]);

  const fetchUserCredits = async () => {
    try {
      const response = await fetch('/api/user/credits', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setUserCredits(data.credits || 0);
      }
    } catch (error) {
      console.error('Failed to fetch user credits:', error);
    }
  };

  const handleModeSelect = async (modeId: string) => {
    const mode = modeId as 'quick' | 'professional';
    setSelectedMode(mode);
    onModeSelect(mode, "market analysis");
  };

  const getRecommendationText = () => {
    if (!user) return null;
    
    // Simple recommendation logic based on user behavior
    const isFirstTime = userCredits === 10; // Assuming new users get 10 credits
    
    if (isFirstTime) {
      return {
        mode: 'quick',
        text: 'Recommended for first-time users',
        icon: <Star className="w-4 h-4" />
      };
    }
    
    return {
      mode: 'professional',
      text: 'Recommended for detailed insights',
      icon: <Sparkles className="w-4 h-4" />
    };
  };

  const recommendation = getRecommendationText();

  return (
    <div className="w-full max-w-6xl mx-auto p-8">
      <div className="text-center mb-12">
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
          Choose Your Analysis Path
        </h2>
        <p className="text-lg text-gray-300 max-w-3xl mx-auto">
          Select the analysis mode that best fits your needs. Each path is designed to provide targeted insights for different validation scenarios.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {analysisModes.map((mode, index) => {
          const Icon = mode.icon;
          
          return (
            <div
              key={mode.id}
              onClick={() => handleModeSelect(mode.id)}
              className="relative group cursor-pointer transform transition-all duration-500 hover:scale-105 hover:-translate-y-2"
            >
              {/* Main card with optimized gradient background */}
              <div 
                className="relative overflow-hidden rounded-2xl border border-white/15 backdrop-blur-sm transition-all duration-500 group-hover:border-white/25 group-hover:shadow-2xl group-hover:shadow-cyan-500/20 h-full flex flex-col"
                style={{
                  background: mode.id === 'quick' 
                    ? 'linear-gradient(135deg, rgb(6, 182, 212, 0.12), rgb(37, 99, 235, 0.18))'
                    : 'linear-gradient(135deg, rgb(168, 85, 247, 0.08), rgb(236, 72, 153, 0.12))',
                }}
              >
                {/* Subtle animated background effects */}
                <div className="absolute inset-0 bg-gradient-to-br from-white/3 to-transparent"></div>
                <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-cyan-400/8 to-transparent rounded-full blur-2xl group-hover:from-cyan-400/12 transition-all duration-500"></div>
                <div className="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-tr from-purple-400/6 to-transparent rounded-full blur-xl group-hover:from-purple-400/10 transition-all duration-500"></div>
                
                {mode.recommended && (
                  <div className="absolute top-4 right-4 bg-gradient-to-r from-yellow-400 to-orange-500 text-black px-3 py-1 rounded-full text-sm font-semibold z-20 shadow-lg">
                    Most Popular
                  </div>
                )}
                
                <div className="relative z-10 p-8 flex flex-col h-full">
                  {/* Header section */}
                  <div className="flex items-center mb-6">
                    <div className="p-3 rounded-xl bg-gradient-to-br from-white/15 to-white/8 mr-4 group-hover:from-white/20 group-hover:to-white/12 transition-all duration-300">
                      <Icon className="w-8 h-8 text-white" />
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-white group-hover:text-cyan-100 transition-colors duration-300">{mode.title}</h3>
                      <p className="text-gray-300 text-sm">{mode.subtitle}</p>
                    </div>
                  </div>
                  
                  {/* Content section - flex-grow to push button to bottom */}
                  <div className="flex-grow mb-6">
                    <p className="text-gray-200 text-base leading-relaxed mb-4">
                      {mode.description}
                    </p>
                    
                    <div className="space-y-3">
                      {mode.features.map((feature, idx) => (
                        <div key={idx} className="flex items-center text-gray-300">
                          <CheckCircle className="w-5 h-5 text-green-400 mr-3 flex-shrink-0" />
                          <span className="text-sm">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {/* Enhanced info section with better visibility */}
                  <div className="bg-white/5 rounded-lg p-4 mb-6 border border-white/10">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <Clock className="w-5 h-5 mr-2 text-cyan-400" />
                        <div>
                          <div className="text-cyan-300 text-xs uppercase tracking-wide font-medium">Duration</div>
                          <div className="text-white font-semibold">{mode.duration}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-cyan-300 text-xs uppercase tracking-wide font-medium">Cost</div>
                        <div className="text-white font-semibold text-lg">{mode.cost} Credit{mode.cost > 1 ? 's' : ''}</div>
                      </div>
                    </div>
                  </div>

                  {/* Optimized Action Button */}
                  <Button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleModeSelect(mode.id);
                    }}
                    className="w-full bg-gradient-to-r from-gray-700/80 to-gray-600/80 hover:from-gray-600/90 hover:to-gray-500/90 text-white font-semibold border border-white/20 hover:border-white/30 transition-all duration-300 shadow-lg hover:shadow-xl"
                    size="lg"
                  >
                    {isLoading && selectedMode === mode.id ? (
                      <>
                        <Brain className="w-4 h-4 mr-2 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        Start Analysis
                        <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform duration-300" />
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
