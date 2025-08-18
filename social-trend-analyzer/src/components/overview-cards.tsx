import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TrendCluster } from "./trend-analyzer"
import { useMemo } from "react"

interface OverviewCardsProps {
  data: TrendCluster[]
}

export function OverviewCards({ data }: OverviewCardsProps) {
  const overviewMetrics = useMemo(() => {
    if (!data || data.length === 0) {
      return {
        avgHotScore: "0.0",
        totalMentions: "0",
        engagement: "0.0K",
        trendChange: 0, // Store as number for logic
      }
    }

    const totalHotScore = data.reduce((sum, cluster) => sum + cluster.hot_score, 0)
    const avgHotScore = data.length > 0 ? totalHotScore / data.length : 0

    const totalMentions = data.length * 415; // Mock calculation
    const engagement = data.length * 2900; // Mock calculation
    const trendChange = Math.round(avgHotScore - 80); // Mock calculation

    return {
      avgHotScore: avgHotScore.toFixed(1),
      totalMentions: totalMentions.toLocaleString(),
      engagement: (engagement / 1000).toFixed(1) + 'K',
      trendChange: trendChange, // Keep as number
    }
  }, [data])

  const trendChangeColor = overviewMetrics.trendChange > 0 ? 'text-green-600' : overviewMetrics.trendChange < 0 ? 'text-red-600' : 'text-gray-600';
  const trendChangeText = `${overviewMetrics.trendChange >= 0 ? '+' : ''}${overviewMetrics.trendChange}%`;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Key Metrics</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 divide-y md:divide-y-0 md:divide-x -mt-2">
        {/* Metric 1: Avg. Hot Score */}
        <div className="flex flex-col justify-center text-center pt-4 md:pt-0">
          <p className="text-sm text-muted-foreground mb-1">Avg. Hot Score</p>
          <p className="text-3xl font-bold text-blue-600">{overviewMetrics.avgHotScore}</p>
          <p className="text-xs text-muted-foreground mt-1">Based on {data.length} trends</p>
        </div>

        {/* Metric 2: Total Mentions */}
        <div className="flex flex-col justify-center text-center pt-4 md:pt-0">
          <p className="text-sm text-muted-foreground mb-1">Total Mentions</p>
          <p className="text-3xl font-bold text-amber-500">{overviewMetrics.totalMentions}</p>
          <p className="text-xs text-muted-foreground mt-1">(Simulated)</p>
        </div>

        {/* Metric 3: Engagement */}
        <div className="flex flex-col justify-center text-center pt-4 md:pt-0">
          <p className="text-sm text-muted-foreground mb-1">Engagement</p>
          <p className="text-3xl font-bold text-purple-600">{overviewMetrics.engagement}</p>
          <p className="text-xs text-muted-foreground mt-1">Likes, replies, etc. (Sim.)</p>
        </div>

        {/* Metric 4: Trend Change */}
        <div className="flex flex-col justify-center text-center pt-4 md:pt-0">
          <p className="text-sm text-muted-foreground mb-1">Trend Change</p>
          <p className={`text-3xl font-bold ${trendChangeColor}`}>{trendChangeText}</p>
          <p className="text-xs text-muted-foreground mt-1">vs. baseline (Sim.)</p>
        </div>
      </CardContent>
    </Card>
  )
}
