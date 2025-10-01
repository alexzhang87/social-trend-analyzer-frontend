import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Cloud, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";

interface WordData {
  text: string;
  value: number;
  color?: string;
}

interface WordCloudPanelProps {
  keywords?: string[];
  className?: string;
}

export function WordCloudPanel({ keywords = [], className }: WordCloudPanelProps) {
  const [wordData, setWordData] = useState<WordData[]>([]);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    // Generate word cloud data based on keywords
    const generateWordCloudData = () => {
      const baseWords: WordData[] = keywords.map((keyword, index) => ({
        text: keyword.trim(),
        value: 100 - (index * 15),
        color: getWordColor(index)
      }));

      // Add some related trending words
      const relatedWords = [
        { text: "Hot Discussion", value: 85, color: "#ef4444" },
      { text: "User Focus", value: 75, color: "#f97316" },
      { text: "Market Trends", value: 70, color: "#eab308" },
      { text: "Social Impact", value: 65, color: "#22c55e" },
      { text: "Brand Voice", value: 60, color: "#3b82f6" },
      { text: "User Feedback", value: 55, color: "#8b5cf6" },
      { text: "Industry News", value: 50, color: "#ec4899" },
      { text: "Innovation", value: 45, color: "#06b6d4" }
      ];

      return [...baseWords, ...relatedWords.slice(0, 6)];
    };

    setWordData(generateWordCloudData());
    setIsAnimating(true);
    
    const timer = setTimeout(() => setIsAnimating(false), 2000);
    return () => clearTimeout(timer);
  }, [keywords]);

  const getWordColor = (index: number): string => {
    const colors = [
      "#ef4444", "#f97316", "#eab308", "#22c55e", 
      "#3b82f6", "#8b5cf6", "#ec4899", "#06b6d4"
    ];
    return colors[index % colors.length];
  };

  const getFontSize = (value: number): string => {
    const minSize = 14;
    const maxSize = 32;
    const size = minSize + (value / 100) * (maxSize - minSize);
    return `${size}px`;
  };

  const getWordPosition = (index: number, total: number) => {
    // Create a word cloud-like layout algorithm
    const centerX = 50;
    const centerY = 50;
    const radius = Math.min(40, total * 3);
    
    const angle = (index * 360 / total) * (Math.PI / 180);
    const distance = radius * (0.3 + Math.random() * 0.7);
    
    const x = centerX + Math.cos(angle) * distance;
    const y = centerY + Math.sin(angle) * distance;
    
    return {
      left: `${Math.max(5, Math.min(85, x))}%`,
      top: `${Math.max(10, Math.min(80, y))}%`
    };
  };

  return (
    <Card className={`h-full ${className}`}>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg font-semibold text-gray-800 flex items-center">
          <div className="flex items-center justify-center bg-gradient-to-r from-purple-100 to-blue-100 rounded-full w-8 h-8 mr-3">
            <Cloud className="w-4 h-4 text-purple-600" />
          </div>
          Smart Word Cloud Analysis
          <Badge className="ml-2 bg-gradient-to-r from-purple-500 to-blue-500 text-white">
            <Sparkles className="w-3 h-3 mr-1" />
            AI Enhanced
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="h-80 relative overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 rounded-lg"></div>
        
        {/* Decorative grid */}
        <div className="absolute inset-0 opacity-30">
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:20px_20px]"></div>
        </div>
        
        {/* Word cloud container */}
        <div className="relative h-full w-full">
          {wordData.map((word, index) => {
            const position = getWordPosition(index, wordData.length);
            const fontSize = getFontSize(word.value);
            
            return (
              <div
                key={`${word.text}-${index}`}
                className={`absolute transform -translate-x-1/2 -translate-y-1/2 font-bold cursor-pointer
                  transition-all duration-1000 ease-out hover:scale-110 hover:z-10
                  ${isAnimating ? 'animate-pulse scale-0 opacity-0' : 'scale-100 opacity-100'}
                `}
                style={{
                  ...position,
                  fontSize,
                  color: word.color,
                  textShadow: '0 2px 4px rgba(0,0,0,0.1)',
                  animationDelay: `${index * 200}ms`,
                  zIndex: Math.floor(word.value / 10)
                }}
                title={`Weight: ${word.value}`}
              >
                <span className="select-none whitespace-nowrap px-2 py-1 rounded-lg bg-white/20 backdrop-blur-sm border border-white/30">
                  {word.text}
                </span>
              </div>
            );
          })}
          
          {/* Center decoration */}
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
            <div className="w-16 h-16 bg-gradient-to-r from-purple-400 to-blue-400 rounded-full opacity-10 animate-pulse"></div>
          </div>
        </div>
        
        {/* Bottom description */}
        <div className="absolute bottom-2 left-2 text-xs text-gray-500 bg-white/80 px-2 py-1 rounded">
          Smart word cloud generated from {keywords.length} keywords
        </div>
        
        {/* Top-right metrics */}
        <div className="absolute top-2 right-2 text-xs text-gray-500 bg-white/80 px-2 py-1 rounded">
          Vocabulary Richness: {wordData.length} words
        </div>
      </CardContent>
    </Card>
  );
}
