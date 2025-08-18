import { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { TrendCluster } from "@/components/trend-analyzer";
import { AreaChart, Area, ResponsiveContainer } from "recharts";
import { ChevronRight, Flame, Layers } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { XLogo } from "@/components/ui/x-logo";
import { RedditLogo } from "@/components/ui/reddit-logo";

type SortKey = "hot_score" | "title";

interface TrendListProps {
  data: TrendCluster[];
  onClusterClick: (cluster: TrendCluster) => void;
}

export function TrendList({ data, onClusterClick }: TrendListProps) {
  const [sortKey, setSortKey] = useState<SortKey>("hot_score");

  const sortedData = useMemo(() => {
    if (!data) {
      return [];
    }
    return [...data].sort((a, b) => {
      if (sortKey === "hot_score") {
        return b.hot_score - a.hot_score;
      }
      if (sortKey === "title") {
        return a.title.localeCompare(b.title);
      }
      return 0;
    });
  }, [data, sortKey]);

  if (!data) {
    return (
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">Trending Topics (0)</h2>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-muted-foreground">Sort by:</span>
            <Select value={sortKey} onValueChange={(value: SortKey) => setSortKey(value)}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="hot_score">Hot Score</SelectItem>
                <SelectItem value="title">Alphabetical</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <div className="flex items-center justify-center h-64 text-muted-foreground">
          Loading trends...
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Trending Topics ({data.length})</h2>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-muted-foreground">Sort by:</span>
          <Select value={sortKey} onValueChange={(value: SortKey) => setSortKey(value)}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="hot_score">Hot Score</SelectItem>
              <SelectItem value="title">Alphabetical</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <div className="space-y-4">
        {sortedData.map((cluster) => {
          // Defensive check in case a cluster is null or undefined
          if (!cluster) return null;

          return (
            <Card 
              key={cluster.cluster_id} 
              className="hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => onClusterClick(cluster)}
            >
              <CardContent className="p-4 grid grid-cols-12 gap-4 items-center">
                {/* Hot Score */}
                <div className="col-span-2 flex flex-col items-center justify-center text-center border-r pr-4">
                  <Flame className="w-8 h-8 text-red-500 mb-1" />
                  <div className="text-4xl font-bold text-red-500">{cluster.hot_score || 0}</div>
                  <div className="text-sm text-muted-foreground">Hot Score</div>
                </div>

                {/* Main Content */}
                <div className="col-span-7 space-y-3">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      {cluster.platforms?.includes("x") && <XLogo className="w-5 h-5" />}
                      {cluster.platforms?.includes("reddit") && <RedditLogo className="w-5 h-5 text-orange-600" />}
                      <h3 className="font-bold text-lg leading-tight" title={cluster.title}>{cluster.title || 'No Title'}</h3>
                    </div>
                    <div className="flex items-center text-xs text-muted-foreground">
                      <Layers className="w-3 h-3 mr-1.5" />
                      <span>{cluster.category || 'No Category'}</span>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {(cluster.keywords || []).slice(0, 4).map((keyword) => (
                      <Badge key={keyword} variant="secondary" className="font-normal">
                        {keyword}
                      </Badge>
                    ))}
                    {(cluster.keywords?.length || 0) > 4 && <Badge variant="outline" className="font-normal">+{cluster.keywords.length - 4}</Badge>}
                  </div>
                </div>

                {/* Mini Chart & Action */}
                <div className="col-span-3 flex items-center justify-between pl-4">
                  <div className="w-32 h-16">
                    {cluster.trend_history && cluster.trend_history.length > 1 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={cluster.trend_history}>
                          <defs>
                            <linearGradient id={`list-chart-${cluster.cluster_id}`} x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3}/>
                              <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0}/>
                            </linearGradient>
                          </defs>
                          <Area type="monotone" dataKey="score" stroke="hsl(var(--primary))" strokeWidth={2} fill={`url(#list-chart-${cluster.cluster_id})`} />
                        </AreaChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="text-xs text-muted-foreground text-center flex items-center justify-center h-full">No trend data</div>
                    )}
                  </div>
                  <Button variant="ghost" size="icon" className="ml-2">
                    <ChevronRight className="w-6 h-6" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  );
}