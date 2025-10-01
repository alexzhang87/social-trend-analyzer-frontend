import React, { useState, useEffect, useMemo } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ScatterChart,
  Scatter,
  ComposedChart,
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart as PieChartIcon,
  Activity,
  Download,
  Settings,
  Maximize2,
  RefreshCw,
  Filter,
  Eye,
  EyeOff,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useSmartLoading } from '@/components/smart-loading';

// Color palettes for different themes
const colorPalettes = {
  default: ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1', '#d084d0'],
  business: ['#2563eb', '#059669', '#dc2626', '#7c3aed', '#ea580c', '#0891b2'],
  pastel: ['#fecaca', '#fed7d7', '#fde68a', '#d1fae5', '#dbeafe', '#e0e7ff'],
  vibrant: ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6', '#8b5cf6'],
  monochrome: ['#374151', '#6b7280', '#9ca3af', '#d1d5db', '#e5e7eb', '#f3f4f6'],
};

interface ChartData {
  [key: string]: any;
}

interface EnhancedChartProps {
  data: ChartData[];
  title?: string;
  description?: string;
  type?: 'line' | 'area' | 'bar' | 'pie' | 'radar' | 'scatter' | 'composed';
  xKey?: string;
  yKeys?: string[];
  colorPalette?: keyof typeof colorPalettes;
  showLegend?: boolean;
  showGrid?: boolean;
  showTooltip?: boolean;
  animated?: boolean;
  height?: number;
  className?: string;
  onDataPointClick?: (data: any) => void;
  customTooltip?: React.ComponentType<any>;
  exportable?: boolean;
  refreshable?: boolean;
  onRefresh?: () => void;
  loading?: boolean;
}

export function EnhancedChart({
  data,
  title,
  description,
  type = 'line',
  xKey = 'name',
  yKeys = ['value'],
  colorPalette = 'default',
  showLegend = true,
  showGrid = true,
  showTooltip = true,
  animated = true,
  height = 300,
  className,
  onDataPointClick,
  customTooltip,
  exportable = false,
  refreshable = false,
  onRefresh,
  loading = false,
}: EnhancedChartProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [visibleSeries, setVisibleSeries] = useState<Set<string>>(new Set(yKeys));
  const [chartSettings, setChartSettings] = useState({
    strokeWidth: 2,
    opacity: 0.8,
    animationDuration: 1000,
  });

  const colors = colorPalettes[colorPalette];
  const { isLoading } = useSmartLoading();

  const filteredData = useMemo(() => {
    return data.map(item => {
      const filtered: any = { [xKey]: item[xKey] };
      yKeys.forEach(key => {
        if (visibleSeries.has(key)) {
          filtered[key] = item[key];
        }
      });
      return filtered;
    });
  }, [data, xKey, yKeys, visibleSeries]);

  const toggleSeries = (seriesKey: string) => {
    const newVisible = new Set(visibleSeries);
    if (newVisible.has(seriesKey)) {
      newVisible.delete(seriesKey);
    } else {
      newVisible.add(seriesKey);
    }
    setVisibleSeries(newVisible);
  };

  const exportChart = () => {
    // Implementation for chart export (SVG/PNG)
    const chartElement = document.querySelector('.recharts-wrapper');
    if (chartElement) {
      // Export logic here
      console.log('Exporting chart...');
    }
  };

  const CustomTooltip = customTooltip || (({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900">{`${xKey}: ${label}`}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {`${entry.dataKey}: ${entry.value}`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  });

  const renderChart = () => {
    const commonProps = {
      data: filteredData,
      margin: { top: 5, right: 30, left: 20, bottom: 5 },
      onClick: onDataPointClick,
    };

    switch (type) {
      case 'area':
        return (
          <AreaChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey={xKey} />
            <YAxis />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            {yKeys.map((key, index) => (
              visibleSeries.has(key) && (
                <Area
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stackId="1"
                  stroke={colors[index % colors.length]}
                  fill={colors[index % colors.length]}
                  fillOpacity={chartSettings.opacity}
                  strokeWidth={chartSettings.strokeWidth}
                  animationDuration={animated ? chartSettings.animationDuration : 0}
                />
              )
            ))}
          </AreaChart>
        );

      case 'bar':
        return (
          <BarChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey={xKey} />
            <YAxis />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            {yKeys.map((key, index) => (
              visibleSeries.has(key) && (
                <Bar
                  key={key}
                  dataKey={key}
                  fill={colors[index % colors.length]}
                  fillOpacity={chartSettings.opacity}
                  animationDuration={animated ? chartSettings.animationDuration : 0}
                />
              )
            ))}
          </BarChart>
        );

      case 'pie':
        return (
          <PieChart {...commonProps}>
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            <Pie
              data={filteredData}
              cx="50%"
              cy="50%"
              labelLine={false}
              outerRadius={80}
              fill="#8884d8"
              dataKey={yKeys[0]}
              animationDuration={animated ? chartSettings.animationDuration : 0}
            >
              {filteredData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Pie>
          </PieChart>
        );

      case 'radar':
        return (
          <RadarChart {...commonProps}>
            <PolarGrid />
            <PolarAngleAxis dataKey={xKey} />
            <PolarRadiusAxis />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            {yKeys.map((key, index) => (
              visibleSeries.has(key) && (
                <Radar
                  key={key}
                  name={key}
                  dataKey={key}
                  stroke={colors[index % colors.length]}
                  fill={colors[index % colors.length]}
                  fillOpacity={chartSettings.opacity}
                  strokeWidth={chartSettings.strokeWidth}
                  animationDuration={animated ? chartSettings.animationDuration : 0}
                />
              )
            ))}
          </RadarChart>
        );

      case 'scatter':
        return (
          <ScatterChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey={xKey} />
            <YAxis dataKey={yKeys[0]} />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            <Scatter
              name={yKeys[0]}
              data={filteredData}
              fill={colors[0]}
              animationDuration={animated ? chartSettings.animationDuration : 0}
            />
          </ScatterChart>
        );

      case 'composed':
        return (
          <ComposedChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey={xKey} />
            <YAxis />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            {yKeys.map((key, index) => {
              if (!visibleSeries.has(key)) return null;
              
              if (index % 2 === 0) {
                return (
                  <Bar
                    key={key}
                    dataKey={key}
                    fill={colors[index % colors.length]}
                    fillOpacity={chartSettings.opacity}
                  />
                );
              } else {
                return (
                  <Line
                    key={key}
                    type="monotone"
                    dataKey={key}
                    stroke={colors[index % colors.length]}
                    strokeWidth={chartSettings.strokeWidth}
                  />
                );
              }
            })}
          </ComposedChart>
        );

      default: // line
        return (
          <LineChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey={xKey} />
            <YAxis />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            {yKeys.map((key, index) => (
              visibleSeries.has(key) && (
                <Line
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={colors[index % colors.length]}
                  strokeWidth={chartSettings.strokeWidth}
                  dot={{ fill: colors[index % colors.length] }}
                  activeDot={{ r: 6 }}
                  animationDuration={animated ? chartSettings.animationDuration : 0}
                />
              )
            ))}
          </LineChart>
        );
    }
  };

  return (
    <Card className={cn("w-full", className, isFullscreen && "fixed inset-0 z-50 m-0 rounded-none")}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div className="space-y-1">
          {title && <CardTitle className="text-base font-medium">{title}</CardTitle>}
          {description && <CardDescription>{description}</CardDescription>}
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Series Toggle */}
          <div className="flex items-center space-x-1">
            {yKeys.map((key, index) => (
              <Button
                key={key}
                variant="ghost"
                size="sm"
                onClick={() => toggleSeries(key)}
                className={cn(
                  "h-6 px-2 text-xs",
                  visibleSeries.has(key) ? "bg-primary/10" : "opacity-50"
                )}
              >
                <div
                  className="w-2 h-2 rounded-full mr-1"
                  style={{ backgroundColor: colors[index % colors.length] }}
                />
                {key}
                {visibleSeries.has(key) ? <Eye className="w-3 h-3 ml-1" /> : <EyeOff className="w-3 h-3 ml-1" />}
              </Button>
            ))}
          </div>

          {refreshable && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onRefresh}
              disabled={loading}
              className="h-8 w-8 p-0"
            >
              <RefreshCw className={cn("w-4 h-4", loading && "animate-spin")} />
            </Button>
          )}

          {exportable && (
            <Button
              variant="ghost"
              size="sm"
              onClick={exportChart}
              className="h-8 w-8 p-0"
            >
              <Download className="w-4 h-4" />
            </Button>
          )}

          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="h-8 w-8 p-0"
          >
            <Maximize2 className="w-4 h-4" />
          </Button>
        </div>
      </CardHeader>

      <CardContent>
        <div style={{ height: isFullscreen ? 'calc(100vh - 200px)' : height }}>
          <ResponsiveContainer width="100%" height="100%">
            {renderChart()}
          </ResponsiveContainer>
        </div>

        {isFullscreen && (
          <div className="mt-4 p-4 border-t">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Chart Settings */}
              <div className="space-y-3">
                <Label className="text-sm font-medium">Chart Settings</Label>
                
                <div className="space-y-2">
                  <Label className="text-xs">Stroke Width: {chartSettings.strokeWidth}</Label>
                  <Slider
                    value={[chartSettings.strokeWidth]}
                    onValueChange={([value]) => setChartSettings(prev => ({ ...prev, strokeWidth: value }))}
                    max={5}
                    min={1}
                    step={1}
                    className="w-full"
                  />
                </div>

                <div className="space-y-2">
                  <Label className="text-xs">Opacity: {Math.round(chartSettings.opacity * 100)}%</Label>
                  <Slider
                    value={[chartSettings.opacity * 100]}
                    onValueChange={([value]) => setChartSettings(prev => ({ ...prev, opacity: value / 100 }))}
                    max={100}
                    min={10}
                    step={10}
                    className="w-full"
                  />
                </div>
              </div>

              {/* Display Options */}
              <div className="space-y-3">
                <Label className="text-sm font-medium">Display Options</Label>
                
                <div className="flex items-center space-x-2">
                  <Switch
                    id="show-grid"
                    checked={showGrid}
                    onCheckedChange={setShowGrid}
                  />
                  <Label htmlFor="show-grid" className="text-xs">Show Grid</Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Switch
                    id="show-legend"
                    checked={showLegend}
                    onCheckedChange={setShowLegend}
                  />
                  <Label htmlFor="show-legend" className="text-xs">Show Legend</Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Switch
                    id="animated"
                    checked={animated}
                    onCheckedChange={setAnimated}
                  />
                  <Label htmlFor="animated" className="text-xs">Animations</Label>
                </div>
              </div>

              {/* Color Palette */}
              <div className="space-y-3">
                <Label className="text-sm font-medium">Color Palette</Label>
                <Select value={colorPalette} onValueChange={(value: keyof typeof colorPalettes) => setColorPalette(value)}>
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.keys(colorPalettes).map((palette) => (
                      <SelectItem key={palette} value={palette}>
                        <div className="flex items-center space-x-2">
                          <div className="flex space-x-1">
                            {colorPalettes[palette as keyof typeof colorPalettes].slice(0, 3).map((color, index) => (
                              <div
                                key={index}
                                className="w-3 h-3 rounded-full"
                                style={{ backgroundColor: color }}
                              />
                            ))}
                          </div>
                          <span className="capitalize">{palette}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Chart Dashboard Component
interface ChartDashboardProps {
  charts: Array<{
    id: string;
    title: string;
    description?: string;
    data: ChartData[];
    type: EnhancedChartProps['type'];
    xKey?: string;
    yKeys?: string[];
    colorPalette?: keyof typeof colorPalettes;
  }>;
  className?: string;
}

export function ChartDashboard({ charts, className }: ChartDashboardProps) {
  const [selectedChart, setSelectedChart] = useState<string | null>(null);
  const [layout, setLayout] = useState<'grid' | 'tabs'>('grid');

  if (layout === 'tabs') {
    return (
      <div className={cn("w-full", className)}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Analytics Dashboard</h2>
          <div className="flex items-center space-x-2">
            <Button
              variant={layout === 'grid' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setLayout('grid')}
            >
              Grid
            </Button>
            <Button
              variant={layout === 'tabs' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setLayout('tabs')}
            >
              Tabs
            </Button>
          </div>
        </div>

        <Tabs value={selectedChart || charts[0]?.id} onValueChange={setSelectedChart}>
          <TabsList className="grid w-full grid-cols-4">
            {charts.map((chart) => (
              <TabsTrigger key={chart.id} value={chart.id}>
                {chart.title}
              </TabsTrigger>
            ))}
          </TabsList>
          
          {charts.map((chart) => (
            <TabsContent key={chart.id} value={chart.id}>
              <EnhancedChart
                {...chart}
                height={400}
                exportable
                refreshable
              />
            </TabsContent>
          ))}
        </Tabs>
      </div>
    );
  }

  return (
    <div className={cn("w-full", className)}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Analytics Dashboard</h2>
        <div className="flex items-center space-x-2">
          <Button
            variant={layout === 'grid' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setLayout('grid')}
          >
            Grid
          </Button>
          <Button
            variant={layout === 'tabs' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setLayout('tabs')}
          >
            Tabs
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {charts.map((chart) => (
          <EnhancedChart
            key={chart.id}
            {...chart}
            height={300}
            exportable
            refreshable
          />
        ))}
      </div>
    </div>
  );
}

export default EnhancedChart;
