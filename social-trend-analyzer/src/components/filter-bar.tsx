import { Search, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { FilterState } from "./trend-analyzer"
import { XLogo } from "@/components/ui/x-logo"
import { RedditLogo } from "@/components/ui/reddit-logo"

interface FilterBarProps {
  filters: FilterState
  setFilters: (filters: FilterState) => void
  onAnalyze: () => void
  isAnalyzing: boolean
}

export function FilterBar({ filters, setFilters, onAnalyze, isAnalyzing }: FilterBarProps) {
  const timeRangeOptions = filters.platform === "Reddit" || filters.platform === "Both" 
    ? ["1 Week", "1 Month"]
    : ["1 Week", "1 Month", "3 Months", "6 Months"]

  const categories = [
    "All Categories",
    "Technology & AI",
    "Health & Fitness", 
    "Finance & Crypto",
    "E-commerce & Retail",
    "Food & Beverage",
    "Travel & Lifestyle",
    "Education & Learning",
    "Gaming & Entertainment",
    "Business & Marketing",
    "Sustainability & Green Tech"
  ]

  const updateFilter = (key: keyof FilterState, value: string) => {
    const newFilters = { ...filters, [key]: value }
    
    if (key === "platform" && (value === "Reddit" || value === "Both")) {
      if (!["1 Week", "1 Month"].includes(newFilters.timeRange)) {
        newFilters.timeRange = "1 Week"
      }
    }
    
    setFilters(newFilters)
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg border p-6 mb-8">
      <div className="flex flex-col lg:flex-row gap-4 items-center">
        <div className="text-sm text-gray-500 font-medium lg:mr-4">
          FILTER BY:
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 flex-1 w-full">
          <div className="flex-1">
            <Select value={filters.platform} onValueChange={(value) => updateFilter("platform", value)}>
              <SelectTrigger>
                <SelectValue placeholder="Platform" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="X">
                  <div className="flex items-center">
                    <XLogo className="w-4 h-4 mr-2" /> X
                  </div>
                </SelectItem>
                <SelectItem value="Reddit">
                  <div className="flex items-center">
                    <RedditLogo className="w-4 h-4 mr-2" /> Reddit
                  </div>
                </SelectItem>
                <SelectItem value="Both">
                  <div className="flex items-center">
                    <XLogo className="w-4 h-4 mr-1" />
                    <RedditLogo className="w-4 h-4 mr-2" /> Both
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex-1">
            <Select value={filters.timeRange} onValueChange={(value) => updateFilter("timeRange", value)}>
              <SelectTrigger>
                <SelectValue placeholder="Time Range" />
              </SelectTrigger>
              <SelectContent>
                {timeRangeOptions.map(option => (
                  <SelectItem key={option} value={option}>{option}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex-1">
            <Select value={filters.category} onValueChange={(value) => updateFilter("category", value)}>
              <SelectTrigger>
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                {categories.map(category => (
                  <SelectItem key={category} value={category}>{category}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Enter keyword..."
                value={filters.keyword}
                onChange={(e) => updateFilter("keyword", e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        </div>

        <Button 
          onClick={onAnalyze}
          disabled={isAnalyzing}
          className="bg-blue-600 hover:bg-blue-700 px-8 py-2 min-w-[120px] w-full lg:w-auto"
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Analyzing...
            </>
          ) : (
            "Analyze"
          )}
        </Button>
      </div>
    </div>
  )
}