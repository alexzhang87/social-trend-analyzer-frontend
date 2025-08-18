import { TrendCluster } from "./trend-analyzer";
import { TrendList } from "./trend-list";
import { OverallTrendCard } from "./overall-trend-card";
import { KeywordsPanel } from "./keywords-panel";
import { WordCloudPanel } from "./word-cloud-panel";

interface AnalysisResultsProps {
  data: TrendCluster[];
  onClusterClick: (cluster: TrendCluster) => void;
}

export function AnalysisResults({ data, onClusterClick }: AnalysisResultsProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
      <div className="lg:col-span-2 space-y-8">
        <OverallTrendCard data={data} />
        <TrendList data={data} onClusterClick={onClusterClick} />
      </div>
      <div className="lg:col-span-1">
        <div className="space-y-8">
          <WordCloudPanel data={data} />
          <KeywordsPanel data={data} />
        </div>
      </div>
    </div>
  );
}