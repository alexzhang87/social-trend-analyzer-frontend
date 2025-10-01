import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { FilterState } from "./trend-analyzer";
import { Calendar } from "lucide-react";

interface FilterBarProps {
  filters: FilterState;
  setFilters: (filters: FilterState) => void;
}

export function FilterBar({ filters, setFilters }: FilterBarProps) {
  const timeRangeOptions = ["1 Week", "1 Month", "3 Months", "6 Months"];



  const updateFilter = (key: keyof FilterState, value: string) => {
    setFilters({ ...filters, [key]: value });
  };

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-md border p-4">
      <div className="flex justify-center">
        {/* Time Range Selector */}
        <div className="flex items-center gap-2 max-w-xs">
          <Calendar className="w-5 h-5 text-gray-500" />
          <Select value={filters.timeRange} onValueChange={(value) => updateFilter("timeRange", value)}>
            <SelectTrigger className="bg-white/50 min-w-[180px]">
              <SelectValue placeholder="Select Time Range" />
            </SelectTrigger>
            <SelectContent>
              {timeRangeOptions.map((option) => (
                <SelectItem key={option} value={option}>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
}
