import { useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { TrendingUp, MessageSquare, Users, ArrowUp, ArrowDown } from "lucide-react";
import { AreaChart, Area, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { TrendAnalysis } from "../declarations";

interface OverallTrendCardProps {
  data: TrendAnalysis;
}

export function OverallTrendCard({ data }: OverallTrendCardProps) {
  const summary = useMemo(() => {
    if (!data) {
      return {
        hypeScore: 0,
        totalMentions: "0",
        engagement: "0",
        chartData: [],
      };
    }

    // Generate mock daily trend data for the chart
    const generateMockChartData = () => {
      const chartData = [];
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(endDate.getDate() - 29); // 30 days of data
      
      let currentValue = data.hypeIndex.score / 2;

      for (let i = 0; i < 30; i++) {
        const date = new Date(startDate);
        date.setDate(startDate.getDate() + i);
        
        // Make the trend generally go up towards the final score
        const randomFactor = (Math.random() - 0.4) * 5;
        const increment = (data.hypeIndex.score / 30) + randomFactor;
        currentValue += increment;
        
        chartData.push({
          date: date.toISOString().split('T')[0],
          score: Math.max(0, Math.round(currentValue)),
        });
      }
      // Ensure the last value is close to the actual hype score
      chartData[29].score = data.hypeIndex.score;
      return chartData;
    };

    const totalMentions = data.top_mentions.length > 0 ? data.top_mentions.length * 15 : 250 + Math.floor(Math.random() * 100);
    const totalEngagement = data.top_mentions.reduce((sum, mention) => sum + mention.likes, 0) * 5;

    return {
      hypeScore: data.hypeIndex.score,
      totalMentions: totalMentions.toLocaleString(),
      engagement: totalEngagement > 1000 ? `${(totalEngagement / 1000).toFixed(1)}K` : totalEngagement.toLocaleString(),
      chartData: generateMockChartData(),
    };
  }, [data]);

  return (
    <Card className="col-span-1 lg:col-span-2 h-full flex flex-col">
      <CardHeader>
        <CardTitle className="text-base font-medium flex items-center">
          <TrendingUp className="w-5 h-5 mr-2" /> Mention Volume Trend
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-grow flex flex-col">
        <div className="flex-grow flex items-center justify-center">
          {summary.chartData.length > 1 ? (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={summary.chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="summaryChartColor" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0}/>
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
                <Area type="monotone" dataKey="score" stroke="hsl(var(--primary))" strokeWidth={2} fill="url(#summaryChartColor)" name="Volume" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-sm text-muted-foreground">Not enough data to display trend chart.</div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}