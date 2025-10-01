import type { HypeIndex, SentimentSpectrum } from "../declarations";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import { Flame, Smile } from "lucide-react";

interface OverviewCardsProps {
  hypeIndex: HypeIndex;
  sentimentSpectrum: SentimentSpectrum;
}

const SENTIMENT_COLORS = {
  positive: "hsl(var(--chart-1))",
  neutral: "hsl(var(--chart-2))",
  negative: "hsl(var(--chart-3))",
  questioning: "hsl(var(--chart-4))",
};

// Simple Gauge component replacement
function SimpleGauge({ value, size = "large" }: { value: number; size?: string }) {
  const radius = size === "large" ? 80 : 60; // Increase radius
  const strokeWidth = 12; // Increase stroke width
  const normalizedRadius = radius - strokeWidth * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDasharray = `${circumference} ${circumference}`;
  const strokeDashoffset = circumference - (value / 100) * circumference;

  const getColor = (score: number) => {
    if (score > 75) return "#ef4444"; // red-500
    if (score > 50) return "#f97316"; // orange-500
    return "#eab308"; // yellow-500
  };

  return (
    <div className="relative flex flex-col items-center">
      <svg
        height={radius * 2}
        width={radius * 2}
        className="transform -rotate-90"
      >
        <circle
          stroke="#e5e7eb"
          fill="transparent"
          strokeWidth={strokeWidth}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
        />
        <circle
          stroke={getColor(value)}
          fill="transparent"
          strokeWidth={strokeWidth}
          strokeDasharray={strokeDasharray}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          r={normalizedRadius}
          cx={radius}
          cy={radius}
          className="transition-all duration-1000 ease-out animate-pulse" // Enhanced animation effect
          style={{
            animation: 'dashOffset 2s ease-out forwards, pulse 2s infinite'
          }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className={`text-5xl font-black animate-bounce ${value > 75 ? "text-red-500" : value > 50 ? "text-orange-500" : "text-yellow-500"}`}>
          {value}
        </span>
      </div>
      <style>
        {`
          @keyframes dashOffset {
            from {
              stroke-dashoffset: ${circumference};
            }
            to {
              stroke-dashoffset: ${strokeDashoffset};
            }
          }
        `}
      </style>
    </div>
  );
}

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="p-2 text-sm bg-background border rounded-lg shadow-lg">
        <p className="font-bold capitalize">{data.name}</p>
        <p>{`Percentage: ${data.value}%`}</p>
      </div>
    );
  }
  return null;
};

export function OverviewCards({ hypeIndex, sentimentSpectrum }: OverviewCardsProps) {
  const sentimentData = [
    { name: 'positive', value: sentimentSpectrum.positive },
    { name: 'neutral', value: sentimentSpectrum.neutral },
    { name: 'negative', value: sentimentSpectrum.negative },
    { name: 'questioning', value: sentimentSpectrum.questioning },
  ];

  return (
    <>
      {/* Hype Index Card */}
      <Card className="flex flex-col">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-gray-800 flex items-center">
            <div className="flex items-center justify-center bg-red-100 rounded-full w-8 h-8 mr-3">
              <Flame className="w-4 h-4 text-red-600" />
            </div>
            Hype Index
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-grow flex flex-col items-center justify-center text-center p-4">
          <SimpleGauge value={hypeIndex.score} size="large" />
          <CardDescription className="mt-4 px-2 text-sm text-gray-600">
            Based on analysis of 500+ social media posts
          </CardDescription>
        </CardContent>
      </Card>

      {/* Sentiment Spectrum Card */}
      <Card className="flex flex-col">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-gray-800 flex items-center">
            <div className="flex items-center justify-center bg-blue-100 rounded-full w-8 h-8 mr-3">
              <Smile className="w-4 h-4 text-blue-600" />
            </div>
            Sentiment Spectrum
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-grow p-4">
          <div className="flex items-center justify-between">
            {/* Pie Chart */}
            <div className="w-32 h-32">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Tooltip content={<CustomTooltip />} />
                  <Pie
                    data={sentimentData}
                    cx="50%"
                    cy="50%"
                    innerRadius={25}
                    outerRadius={45}
                    paddingAngle={2}
                    dataKey="value"
                    nameKey="name"
                    cornerRadius={2}
                  >
                    {sentimentData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={SENTIMENT_COLORS[entry.name as keyof typeof SENTIMENT_COLORS]} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
            
            {/* Legend as custom list */}
            <div className="flex-1 ml-6">
              <div className="space-y-2">
                {sentimentData.map((entry, index) => (
                  <div key={entry.name} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div 
                        className="w-3 h-3 rounded-full mr-2" 
                        style={{ backgroundColor: SENTIMENT_COLORS[entry.name as keyof typeof SENTIMENT_COLORS] }}
                      ></div>
                      <span className="text-sm text-gray-600 capitalize">{entry.name}</span>
                    </div>
                    <span className="text-sm font-medium text-gray-800">{entry.value}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>


    </>
  );
}