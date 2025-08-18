import { useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendCluster } from "./trend-analyzer";

interface KeywordsPanelProps {
  data: TrendCluster[];
}

export function KeywordsPanel({ data }: KeywordsPanelProps) {
  const topKeywords = useMemo(() => {
    // Defensive check: ensure data is a valid array before processing
    if (!data || !Array.isArray(data) || data.length === 0) {
      return [];
    }

    const keywordCounts: { [key: string]: number } = {};
    
    data.forEach(cluster => {
      // Defensive check for each cluster and its keywords
      if (cluster && Array.isArray(cluster.keywords)) {
        cluster.keywords.forEach(keyword => {
          if (typeof keyword === 'string') {
            keywordCounts[keyword] = (keywordCounts[keyword] || 0) + 1;
          }
        });
      }
    });

    return Object.entries(keywordCounts)
      .map(([keyword, count]) => ({
        keyword,
        count,
        // Mock trend data as it's not in the source
        trend: Array.from({ length: 5 }, () => Math.floor(Math.random() * 10) + 2)
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 8);
  }, [data]);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Top Keywords</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {topKeywords.length > 0 ? (
          topKeywords.map((item, index) => (
            <div key={item.keyword} className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
              <div className="flex items-center space-x-2">
                <span className="text-xs text-gray-500 w-4">#{index + 1}</span>
                <Badge variant="secondary" className="text-xs">
                  {item.keyword}
                </Badge>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-xs text-gray-600">{item.count}</span>
                <div className="flex space-x-0.5">
                  {item.trend.map((height, i) => (
                    <div 
                      key={i}
                      className="w-1 bg-blue-400 rounded-sm"
                      style={{ height: `${height * 2}px` }}
                    />
                  ))}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center text-sm text-muted-foreground p-4">
            No keyword data available.
          </div>
        )}
      </CardContent>
    </Card>
  );
}