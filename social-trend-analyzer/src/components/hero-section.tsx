import { Search, Loader2, Lightbulb, Droplets, Rocket } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { FilterState } from "./trend-analyzer"
import { XLogo } from "@/components/ui/x-logo"
import { RedditLogo } from "@/components/ui/reddit-logo"

interface HeroSectionProps {
  filters: FilterState
  setFilters: (filters: FilterState) => void
  onAnalyze: () => void
  isAnalyzing: boolean
}

export function HeroSection({ filters, setFilters, onAnalyze, isAnalyzing }: HeroSectionProps) {
  const timeRangeOptions = ["1 Week", "1 Month", "3 Months"]

  const categories = [
    "All Categories",
    "AI & SaaS",
    "Health & Wellness", 
    "FinTech & Crypto",
    "E-commerce & DTC",
    "Creator Economy",
    "Gaming & Metaverse",
    "Future of Work",
    "GreenTech & Sustainability"
  ]

  const updateFilter = (key: keyof FilterState, value: string) => {
    setFilters({ ...filters, [key]: value })
  }

  return (
    <section className="text-center pt-16 pb-20" aria-labelledby="hero-title">
      <h1 id="hero-title" className="text-4xl md:text-5xl font-bold mb-4 tracking-tight leading-tight md:leading-tight bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-400 bg-clip-text text-transparent">
        Where Great Ideas Find Fertile Ground
      </h1>
      <p className="text-lg md:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed mt-4 mb-16">
        Plant a business idea, and we'll analyze social trends to find consumer pain points, validate your concept, and uncover its true potential.
      </p>

      <div className="max-w-4xl mx-auto px-4">
        <div className="relative" role="search">
          <Search className="absolute left-6 top-1/2 transform -translate-y-1/2 text-gray-400 w-6 h-6" />
          <Input
            placeholder="Analyze a trend, product, or industry..."
            value={filters.keyword}
            onChange={(e) => updateFilter("keyword", e.target.value)}
            className="h-20 pl-16 pr-40 text-xl rounded-2xl shadow-lg border-2 border-transparent focus:border-teal-500 transition-all"
            aria-label="Keyword for social trend analysis"
          />
          <Button 
            onClick={onAnalyze}
            disabled={isAnalyzing || !filters.keyword}
            className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-teal-600 hover:bg-teal-700 text-white font-bold h-14 px-8 rounded-xl text-lg transition-all shadow-md hover:shadow-lg disabled:bg-teal-400 disabled:cursor-not-allowed"
            aria-label="Start Analysis"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-6 h-6 mr-2 animate-spin" />
                Analyzing...
              </>
            ) : (
              "Analyze Now"
            )}
          </Button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4" aria-label="Analysis Filters">
          <Select value={filters.platform} onValueChange={(value) => updateFilter("platform", value)}>
            <SelectTrigger className="h-12 text-base bg-white/70 backdrop-blur-sm">
              <SelectValue placeholder="Platform" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="X">
                <div className="flex items-center"><XLogo className="w-4 h-4 mr-2" /> X (Twitter)</div>
              </SelectItem>
              <SelectItem value="Reddit">
                <div className="flex items-center"><RedditLogo className="w-4 h-4 mr-2" /> Reddit</div>
              </SelectItem>
              <SelectItem value="Both">
                <div className="flex items-center"><XLogo className="w-4 h-4 mr-1" /><RedditLogo className="w-4 h-4 mr-2" /> Both</div>
              </SelectItem>
            </SelectContent>
          </Select>

          <Select value={filters.timeRange} onValueChange={(value) => updateFilter("timeRange", value)}>
            <SelectTrigger className="h-12 text-base bg-white/70 backdrop-blur-sm">
              <SelectValue placeholder="Time Range" />
            </SelectTrigger>
            <SelectContent>
              {timeRangeOptions.map(option => (
                <SelectItem key={option} value={option}>{option}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={filters.category} onValueChange={(value) => updateFilter("category", value)}>
            <SelectTrigger className="h-12 text-base bg-white/70 backdrop-blur-sm">
              <SelectValue placeholder="Category" />
            </SelectTrigger>
            <SelectContent>
              {categories.map(category => (
                <SelectItem key={category} value={category}>{category}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="max-w-5xl mx-auto mt-16 px-4">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">How Your Idea Grows in the Eden</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
          <div className="flex flex-col items-center md:items-start">
            <div className="flex items-center justify-center bg-emerald-100 rounded-full w-12 h-12 mb-4">
              <Lightbulb className="w-6 h-6 text-emerald-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">1. Plant the Seed</h3>
            <p className="text-gray-600">Start with a spark of an idea. Our AI explores social conversations to uncover related pain points and market needs.</p>
          </div>
          <div className="flex flex-col items-center md:items-start">
            <div className="flex items-center justify-center bg-teal-100 rounded-full w-12 h-12 mb-4">
              <Droplets className="w-6 h-6 text-teal-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">2. Water with Data</h3>
            <p className="text-gray-600">We enrich your concept with real-time data, validating its potential and refining its direction with market sentiment.</p>
          </div>
          <div className="flex flex-col items-center md:items-start">
            <div className="flex items-center justify-center bg-cyan-100 rounded-full w-12 h-12 mb-4">
              <Rocket className="w-6 h-6 text-cyan-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">3. Harvest the Plan</h3>
            <p className="text-gray-600">Receive a concrete action plan, including key features, target audience insights, and a 7-day MVP launch plan.</p>
          </div>
        </div>
      </div>
    </section>
  )
}
