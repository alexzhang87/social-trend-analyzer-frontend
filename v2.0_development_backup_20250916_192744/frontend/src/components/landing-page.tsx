import { useState } from "react";
import { Header } from "./header";
import { HeroSection } from "./hero-section";
import { DemoAnalysisShowcase } from "./demo-analysis-showcase";
import { useAuth } from "@/components/auth-provider";
import { useToast } from "@/components/ui/use-toast";
import { useNavigate } from "react-router-dom";
import { TrendingUp, Target, BarChart3, Users, Lightbulb, Rocket } from "lucide-react";
import { Button } from "@/components/ui/button";

// Define the shape of the filters
export interface FilterState {
  platform: string;
  timeRange: string;
  category: string;
}

// Simple animation for the cards
const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: i * 0.2,
      duration: 0.5,
    },
  }),
};

// A simple motion component stub to avoid dependency issues
const motion = {
  div: ({ variants, initial, whileInView, viewport, custom, className, children, ...props }: any) => {
    return <div className={className} {...props}>{children}</div>;
  }
};

export default function LandingPage() {
  const { user } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const [keywords, setKeywords] = useState('');
  const [filters, setFilters] = useState<FilterState>({
    platform: 'twitter',
    timeRange: '7d',
    category: 'all'
  });

  const handleAnalyze = async () => {
    if (!keywords.trim()) {
      toast({
        title: "Please enter keywords",
        description: "Keywords are required to start analysis",
        variant: "destructive",
      });
      return;
    }

    // Check if user is authenticated
    if (!user) {
      // New user - redirect to registration with free trial
      navigate('/pricing?trial=true');
    } else {
      // Existing user - redirect to workspace keyword analysis with keywords
      navigate(`/workspace?section=analysis&keywords=${encodeURIComponent(keywords)}`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="space-y-8">
          <HeroSection 
            keywords={keywords}
            setKeywords={setKeywords}
            onAnalyze={handleAnalyze}
            isAnalyzing={false}
            filters={filters}
            setFilters={setFilters}
          />

          <DemoAnalysisShowcase />

          <div className="text-center py-16">
            <div className="max-w-3xl mx-auto">
              <h3 className="text-3xl md:text-4xl font-bold text-white mb-6">
                Validate Your
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600">
                  {" "}Startup Ideas{" "}
                </span>
                with AI
              </h3>
              <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto leading-relaxed">
                Don't rely on guesswork. Use our AI-powered platform to analyze market trends, 
                validate demand, and make data-driven decisions for your next big idea.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button
                  onClick={() => navigate('/analysis')}
                  size="lg"
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 text-lg font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
                >
                  <Rocket className="w-5 h-5 mr-2" />
                  Start Analysis
                </Button>
                <Button
                  onClick={() => navigate('/pricing')}
                  variant="outline"
                  size="lg"
                  className="border-white/20 text-white hover:bg-white/10 px-8 py-4 text-lg font-semibold rounded-xl"
                >
                  View Pricing
                </Button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}