import { useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { TrendingUp, MessageSquare, Users, ArrowUp, ArrowDown, Info } from "lucide-react";
import { AreaChart, Area, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { TrendCluster } from "./trend-analyzer";
import { Tooltip as ShadTooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface OverallTrendCardProps {
  data: TrendCluster[];
}

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="p-2 text-xs bg-background border rounded-lg shadow-sm">
        <p className="font-bold">{`Volume: ${payload[0].value}`}</p>
      </div>
    );
  }
  return null;
};

export function OverallTrendCard({ data }: OverallTrendCardProps) {
  const summary = useMemo(() => {
    if (!data || data.length === 0) {
      return {
        avgHotScore: 0,
        totalMentions: "0",
        engagement: "0",
        trendChange: 0,
        chartData: [],
      };
    }

    const totalHotScore = data.reduce((sum, cluster) => sum + (cluster.hot_score || 0), 0);
    const avgHotScore = totalHotScore / data.length;
    const totalMentions = data.length * 415; // Mock
    const engagement = data.length * 2900; // Mock
    const trendChange = Math.round(avgHotScore - 80); // Mock

    // New logic for aggregating trend_history data
    const aggregatedChartData = new Map<string, number>();
    data.forEach(cluster => {
      if (cluster.trend_history) {
        cluster.trend_history.forEach(historyPoint => {
          const currentScore = aggregatedChartData.get(historyPoint.date) || 0;
          aggregatedChartData.set(historyPoint.date, currentScore + historyPoint.score);
        });
      }
    });

    const finalChartData = Array.from(aggregatedChartData.entries())
      .map(([date, score]) => ({ date, score: score / data.length })) // Averaging the score
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());


    return {
      avgHotScore: Math.round(avgHotScore),
      totalMentions: totalMentions.toLocaleString(),
      engagement: (engagement / 1000).toFixed(1) + 'K',
      trendChange: trendChange,
      chartData: finalChartData,
    };
  }, [data]);

  const TrendIcon = summary.trendChange >= 0 ? ArrowUp : ArrowDown;
  const trendColor = summary.trendChange >= 0 ? "text-green-500" : "text-red-500";

  return (
    <TooltipProvider>
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Overall Trend Summary</CardTitle>
          <CardDescription>A high-level overview of the analyzed trends.</CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2 bg-muted/40 p-4 rounded-lg">
            <div className="flex justify-between items-start mb-1">
              <div>
                <p className="text-sm text-muted-foreground">Average Hot Score</p>
                <p className="text-4xl font-bold">{summary.avgHotScore}</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-muted-foreground">Change vs. Baseline</p>
                <div className={`flex items-center justify-end ${trendColor}`}>
                  <TrendIcon className="w-5 h-5" />
                  <span className="font-semibold text-lg">{Math.abs(summary.trendChange)}%</span>
                </div>
              </div>
            </div>
            <p className="text-xs text-muted-foreground mb-2">
              The chart below shows the aggregated average Hot Score over the selected period, reflecting the overall trend momentum.
            </p>
            <div className="h-40 flex items-center justify-center">
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
                    <Area type="monotone" dataKey="score" stroke="hsl(var(--primary))" strokeWidth={2} fill="url(#summaryChartColor)" name="Avg. Score" />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-sm text-muted-foreground">Not enough data to display trend chart.</div>
              )}
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-start p-3 bg-muted/40 rounded-lg">
              <div className="p-2 bg-primary/10 rounded-md"><TrendingUp className="w-5 h-5 text-primary" /></div>
              <div className="ml-3">
                <p className="text-sm text-muted-foreground">Total Trends Found</p>
                <p className="text-xl font-bold">{data.length}</p>
              </div>
            </div>
            <div className="flex items-start p-3 bg-muted/40 rounded-lg">
              <div className="p-2 bg-primary/10 rounded-md"><MessageSquare className="w-5 h-5 text-primary" /></div>
              <div className="ml-3">
                <p className="text-sm text-muted-foreground">Total Mentions (Sim.)</p>
                <p className="text-xl font-bold">{summary.totalMentions}</p>
              </div>
            </div>
            <div className="flex items-start p-3 bg-muted/40 rounded-lg">
              <div className="p-2 bg-primary/10 rounded-md"><Users className="w-5 h-5 text-primary" /></div>
              <div className="ml-3">
                <p className="text-sm text-muted-foreground">Engagement (Sim.)</p>
                <p className="text-xl font-bold">{summary.engagement}</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </TooltipProvider>
  );
}
