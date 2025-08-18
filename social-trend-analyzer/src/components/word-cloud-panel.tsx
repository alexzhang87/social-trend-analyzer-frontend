import { useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendCluster } from "./trend-analyzer";
import WordCloud from "react-wordcloud";
import 'tippy.js/dist/tippy.css';
import 'tippy.js/animations/scale.css';

interface WordCloudPanelProps {
  data: TrendCluster[];
}

const options: any = {
  rotations: 2,
  rotationAngles: [0, 0],
  fontSizes: [14, 48],
  padding: 2,
  enableTooltip: true,
  tooltipOptions: {
    animation: 'scale',
    theme: 'light',
  }
};

export function WordCloudPanel({ data }: WordCloudPanelProps) {
  const words = useMemo(() => {
    if (!data) {
      return [];
    }
    const wordMap = new Map<string, number>();
    data.forEach(cluster => {
      cluster.keywords.forEach(keyword => {
        wordMap.set(keyword, (wordMap.get(keyword) || 0) + 1);
      });
    });
    // Multiply value for better visual scaling in the cloud
    return Array.from(wordMap.entries()).map(([text, value]) => ({ text, value: value * 10 }));
  }, [data]);

  if (!data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Keyword Cloud</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64 text-muted-foreground">
            Loading...
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Keyword Cloud</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64 w-full">
          {words.length > 0 ? (
            <WordCloud words={words} options={options} />
          ) : (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              No keywords to display
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}