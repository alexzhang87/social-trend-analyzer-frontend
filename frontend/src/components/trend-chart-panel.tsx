import { useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp } from "lucide-react";
import { AreaChart, Area, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { HypeIndex } from "../declarations";

interface TrendChartPanelProps {
  hypeIndex: HypeIndex;
  timeRange?: string;
}

export function TrendChartPanel({ hypeIndex, timeRange = "1 Month" }: TrendChartPanelProps) {
  const chartData = useMemo(() => {
    // Generate mock daily trend data for the chart based on time range
    const data = [];
    const endDate = new Date();
    const startDate = new Date();
    
    // Map time range to days
    const timeRangeMap: Record<string, number> = {
      "1 Week": 7,
      "1 Month": 30,
      "3 Months": 90,
      "6 Months": 180
    };
    
    const days = timeRangeMap[timeRange] || 30;
    startDate.setDate(endDate.getDate() - (days - 1));
    
    let currentValue = hypeIndex.score / 2;

    for (let i = 0; i < days; i++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      
      // Make the trend generally go up towards the final score
      const randomFactor = (Math.random() - 0.4) * 5;
      const increment = (hypeIndex.score / days) + randomFactor;
      currentValue += increment;
      
      data.push({
        date: date.toISOString().split('T')[0],
        score: Math.max(0, Math.round(currentValue)),
      });
    }
    // Ensure the last value is close to the actual hype score
    data[days - 1].score = hypeIndex.score;
    return data;
  }, [hypeIndex.score, timeRange]);

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-foreground flex items-center">
          <div className="flex items-center justify-center bg-accent/20 rounded-full w-8 h-8 mr-3">
            <TrendingUp className="w-4 h-4 text-accent" />
          </div>
          Trend Chart
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-48 w-full">
          {chartData.length > 1 ? (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="trendChartColor" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(str) => new Date(str).toLocaleDateString('en-us', { month: 'short', day: 'numeric' })}
                  tick={{ fontSize: 10 }} 
                  tickLine={false} 
                  axisLine={false} 
                />
                <YAxis tick={{ fontSize: 10 }} tickLine={false} axisLine={false} />
                <Tooltip 
                    contentStyle={{
                      backgroundColor: 'hsl(var(--background))',
                      borderColor: 'hsl(var(--border))',
                      fontSize: '12px',
                      padding: '4px 8px'
                    }}
                    labelFormatter={(label) => new Date(label).toLocaleDateString('en-us', { weekday: 'short', month: 'short', day: 'numeric' })}
                />
                <Area 
                  type="monotone" 
                  dataKey="score" 
                  stroke="#8b5cf6" 
                  strokeWidth={2} 
                  fill="url(#trendChartColor)" 
                  name="Hype Score" 
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-48 flex items-center justify-center text-muted-foreground">
              <p>Not enough data to display trend chart</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
