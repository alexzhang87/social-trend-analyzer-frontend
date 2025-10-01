import { Search, Loader2, Calendar } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { FilterBar } from "./filter-bar"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

// Define FilterState inline to avoid circular dependency
interface FilterState {
  platform: string;
  timeRange: string;
  category: string;
}

interface HeroSectionProps {
  keywords: string;
  setKeywords: (keywords: string) => void;
  onAnalyze: () => void;
  isAnalyzing: boolean;
  filters: FilterState;
  setFilters: (filters: FilterState) => void;
}

export function HeroSection({ keywords, setKeywords, onAnalyze, isAnalyzing, filters, setFilters }: HeroSectionProps) {
  
  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      onAnalyze();
    }
  };

  return (
    <section className="text-center pt-16 pb-4 relative overflow-hidden" aria-labelledby="hero-title">
      {/* Background decorative elements */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-1/4 left-1/4 w-72 h-72 gradient-primary rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float"></div>
        <div className="absolute top-1/3 right-1/4 w-72 h-72 gradient-secondary rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float" style={{animationDelay: '2s'}}></div>
        <div className="absolute bottom-1/4 left-1/3 w-72 h-72 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float" style={{animationDelay: '4s'}}></div>
      </div>
      
      <div className="animate-slide-up">
        <h1 id="hero-title" className="text-4xl md:text-6xl font-black mb-6 tracking-tight leading-tight md:leading-tight">
          <span className="bg-gradient-to-r from-cyan-300 to-purple-300 bg-clip-text text-transparent font-extrabold">
            Validate Startup Ideas with Data
          </span>
          <br />
          <span className="bg-gradient-to-r from-purple-300 to-green-300 bg-clip-text text-transparent font-extrabold">
            Make Decisions Based on Data, Not Guesswork
          </span>
        </h1>
        <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed mt-6 mb-12 font-medium">
          🤖 AI-driven multi-source data analysis for real-time market insights - Support every startup decision with data
        </p>
      </div>

      <div className="max-w-4xl mx-auto px-4">
        <div className="relative mb-4 animate-fade-in" role="search" style={{animationDelay: '0.5s'}}>
          <div className="glass-card rounded-3xl p-2 shadow-modern-lg glow-hover transition-all duration-500">
            <Search className="absolute left-8 top-1/2 transform -translate-y-1/2 text-gray-400 w-6 h-6 z-10" />
            <Input
              placeholder="Enter keywords to analyze social trends..."
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              onKeyDown={handleKeyDown}
              className="h-20 pl-20 pr-96 text-xl bg-transparent border-none focus:ring-0 focus:outline-none placeholder:text-gray-400"
              aria-label="Keywords for social trend analysis"
            />
            
            {/* Time Range Selector inside input */}
            <div className="absolute right-52 top-1/2 transform -translate-y-1/2 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-gray-500" />
              <Select value={filters.timeRange} onValueChange={(value) => setFilters({ ...filters, timeRange: value })}>
                <SelectTrigger className="glass-card border-white/30 min-w-[120px] h-10 text-sm backdrop-blur-sm">
                  <SelectValue placeholder="Time Range" />
                </SelectTrigger>
                <SelectContent className="glass-card backdrop-blur-lg">
                  <SelectItem value="1 Week">1 Week</SelectItem>
                  <SelectItem value="1 Month">1 Month</SelectItem>
                  <SelectItem value="3 Months">3 Months</SelectItem>
                  <SelectItem value="6 Months">6 Months</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <Button 
              onClick={onAnalyze}
              disabled={isAnalyzing || !keywords}
              className="absolute right-4 top-1/2 transform -translate-y-1/2 gradient-primary text-white font-bold h-12 px-8 rounded-xl text-base transition-all shadow-modern hover:shadow-modern-lg disabled:opacity-50 disabled:cursor-not-allowed glow-hover transform hover:scale-105 duration-300"
              aria-label="Start Analysis"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-6 h-6 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <span>Analyze Now</span>
                  <div className="ml-2 w-2 h-2 bg-white rounded-full animate-pulse"></div>
                </>
              )}
            </Button>
          </div>
        </div>
        
        {/* FilterBar is now integrated into the input field above */}
      </div>
    </section>
  )
}