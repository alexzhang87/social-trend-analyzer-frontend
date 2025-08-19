import { useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendCluster } from "./trend-analyzer";
import WordCloud from 'react-d3-cloud';

interface WordCloudPanelProps {
  data: TrendCluster[];
}

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
    // react-d3-cloud expects data in the format { text: string, value: number }
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

  const fontSizeMapper = (word: { value: number }) => Math.log2(word.value) * 5 + 16;
  const rotate = () => (Math.random() - 0.5) * 30;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Keyword Cloud</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64 w-full">
          {words.length > 0 ? (
            <WordCloud
              data={words}
              width={500}
              height={250}
              font="Inter"
              fontSize={fontSizeMapper}
              rotate={rotate}
              padding={5}
            />
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
