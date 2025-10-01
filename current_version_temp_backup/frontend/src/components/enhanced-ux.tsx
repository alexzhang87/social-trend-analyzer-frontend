import React, { useState, useEffect, useCallback, useMemo, memo } from 'react';
import { Loader2, Wifi, WifiOff, Zap, Clock, TrendingUp, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useLoading } from './loading-provider';

// 智能加载状态组件
interface SmartLoadingProps {
  isLoading: boolean;
  loadingType?: 'analysis' | 'search' | 'export' | 'general';
  estimatedTime?: number;
  onCancel?: () => void;
  tips?: string[];
}

export const SmartLoading = memo(({ 
  isLoading, 
  loadingType = 'general', 
  estimatedTime, 
  onCancel,
  tips = []
}: SmartLoadingProps) => {
  const [currentTip, setCurrentTip] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(0);
  
  const loadingMessages = useMemo(() => ({
    analysis: [
      '正在分析数据趋势...',
      '处理情感分析...',
      '生成洞察报告...',
      '优化分析结果...'
    ],
    search: [
      '搜索相关内容...',
      '筛选数据源...',
      '整理搜索结果...',
      '准备展示数据...'
    ],
    export: [
      '准备导出数据...',
      '格式化内容...',
      '生成文件...',
      '完成导出...'
    ],
    general: [
      '正在处理请求...',
      '获取数据...',
      '准备结果...',
      '即将完成...'
    ]
  }), []);
  
  const currentMessages = loadingMessages[loadingType];
  const allTips = tips.length > 0 ? tips : [
    '💡 提示：您可以在设置中调整分析精度以获得更快的结果',
    '🚀 提示：使用关键词过滤可以提高搜索效率',
    '📊 提示：定期清理缓存可以提升系统性能',
    '⭐提示：收藏常用的分析配置可以节省时间'
  ];
  
  useEffect(() => {
    if (!isLoading) {
      setElapsedTime(0);
      setCurrentTip(0);
      return;
    }
    
    const messageInterval = setInterval(() => {
      setCurrentTip(prev => (prev + 1) % currentMessages.length);
    }, 2000);
    
    const timeInterval = setInterval(() => {
      setElapsedTime(prev => prev + 1);
    }, 1000);
    
    return () => {
      clearInterval(messageInterval);
      clearInterval(timeInterval);
    };
  }, [isLoading, currentMessages.length]);
  
  if (!isLoading) return null;
  
  const progress = estimatedTime ? Math.min((elapsedTime / estimatedTime) * 100, 95) : undefined;
  
  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center">
      <Card className="w-96 mx-4">
        <CardHeader className="text-center">
          <div className="flex items-center justify-center mb-2">
            <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
          </div>
          <CardTitle className="text-lg">{currentMessages[currentTip]}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {progress !== undefined && (
            <div className="space-y-2">
              <Progress value={progress} className="h-2" />
              <div className="flex justify-between text-sm text-gray-500">
                <span>已用时: {elapsedTime}s</span>
                {estimatedTime && (
                  <span>预计: {estimatedTime}s</span>
                )}
              </div>
            </div>
          )}
          
          <div className="bg-blue-50 p-3 rounded-lg">
            <p className="text-sm text-blue-700">
              {allTips[Math.floor(elapsedTime / 5) % allTips.length]}
            </p>
          </div>
          
          {onCancel && (
            <Button 
              variant="outline" 
              onClick={onCancel}
              className="w-full"
            >
              取消操作
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  );
});

// 网络状态指示器
export const NetworkStatus = memo(() => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [connectionSpeed, setConnectionSpeed] = useState<'fast' | 'slow' | 'offline'>('fast');
  
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setConnectionSpeed('fast');
    };
    
    const handleOffline = () => {
      setIsOnline(false);
      setConnectionSpeed('offline');
    };
    
    // 检测网络速度
    const checkConnectionSpeed = async () => {
      if (!navigator.onLine) return;
      
      const startTime = Date.now();
      try {
        await fetch('/api/v1/health', { method: 'HEAD' });
        const endTime = Date.now();
        const responseTime = endTime - startTime;
        
        setConnectionSpeed(responseTime > 1000 ? 'slow' : 'fast');
      } catch {
        setConnectionSpeed('slow');
      }
    };
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    // 定期检查网络速度
    const speedCheckInterval = setInterval(checkConnectionSpeed, 30000);
    checkConnectionSpeed();
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearInterval(speedCheckInterval);
    };
  }, []);
  
  if (isOnline && connectionSpeed === 'fast') return null;
  
  return (
    <div className={`fixed top-4 right-4 z-50 p-3 rounded-lg shadow-lg ${
      !isOnline ? 'bg-red-500 text-white' : 'bg-yellow-500 text-white'
    }`}>
      <div className="flex items-center space-x-2">
        {!isOnline ? (
          <WifiOff className="h-4 w-4" />
        ) : (
          <Wifi className="h-4 w-4" />
        )}
        <span className="text-sm font-medium">
          {!isOnline ? '网络连接已断开' : '网络连接较慢'}
        </span>
      </div>
    </div>
  );
});

// 性能监控组件
interface PerformanceMonitorProps {
  onPerformanceIssue?: (issue: string) => void;
}

export const PerformanceMonitor = memo(({ onPerformanceIssue }: PerformanceMonitorProps) => {
  const [performanceMetrics, setPerformanceMetrics] = useState({
    responseTime: 0,
    memoryUsage: 0,
    renderTime: 0
  });
  
  useEffect(() => {
    let frameCount = 0;
    let lastTime = performance.now();
    
    const measurePerformance = () => {
      const currentTime = performance.now();
      frameCount++;
      
      if (frameCount % 60 === 0) { // 每60帧检查一次
        const fps = 1000 / ((currentTime - lastTime) / 60);
        
        // 检查内存使用（如果支持）
        const memoryInfo = (performance as any).memory;
        if (memoryInfo) {
          const memoryUsage = (memoryInfo.usedJSHeapSize / memoryInfo.totalJSHeapSize) * 100;
          setPerformanceMetrics(prev => ({ ...prev, memoryUsage }));
          
          if (memoryUsage > 80) {
            onPerformanceIssue?.('内存使用率过高，建议刷新页面');
          }
        }
        
        if (fps < 30) {
          onPerformanceIssue?.('页面渲染性能较低，建议关闭其他标签页');
        }
        
        lastTime = currentTime;
      }
      
      requestAnimationFrame(measurePerformance);
    };
    
    requestAnimationFrame(measurePerformance);
  }, [onPerformanceIssue]);
  
  return null; // 这是一个监控组件，不渲染UI
});

// 智能提示组件
interface SmartTooltipProps {
  content: string;
  children: React.ReactNode;
  delay?: number;
  position?: 'top' | 'bottom' | 'left' | 'right';
}

export const SmartTooltip = memo(({ 
  content, 
  children, 
  delay = 500,
  position = 'top'
}: SmartTooltipProps) => {
  const [isVisible, setIsVisible] = useState(false);
  const [timeoutId, setTimeoutId] = useState<NodeJS.Timeout | null>(null);
  
  const showTooltip = useCallback(() => {
    const id = setTimeout(() => setIsVisible(true), delay);
    setTimeoutId(id);
  }, [delay]);
  
  const hideTooltip = useCallback(() => {
    if (timeoutId) {
      clearTimeout(timeoutId);
      setTimeoutId(null);
    }
    setIsVisible(false);
  }, [timeoutId]);
  
  const positionClasses = {
    top: 'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 transform -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 transform -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 transform -translate-y-1/2 ml-2'
  };
  
  return (
    <div 
      className="relative inline-block"
      onMouseEnter={showTooltip}
      onMouseLeave={hideTooltip}
    >
      {children}
      {isVisible && (
        <div className={`absolute z-50 px-2 py-1 text-sm text-white bg-gray-900 rounded shadow-lg whitespace-nowrap ${positionClasses[position]}`}>
          {content}
          <div className={`absolute w-2 h-2 bg-gray-900 transform rotate-45 ${
            position === 'top' ? 'top-full left-1/2 -translate-x-1/2 -mt-1' :
            position === 'bottom' ? 'bottom-full left-1/2 -translate-x-1/2 -mb-1' :
            position === 'left' ? 'left-full top-1/2 -translate-y-1/2 -ml-1' :
            'right-full top-1/2 -translate-y-1/2 -mr-1'
          }`} />
        </div>
      )}
    </div>
  );
});

// 响应式数据表格
interface ResponsiveTableProps {
  data: any[];
  columns: {
    key: string;
    label: string;
    render?: (value: any, row: any) => React.ReactNode;
    sortable?: boolean;
    width?: string;
  }[];
  loading?: boolean;
  onSort?: (key: string, direction: 'asc' | 'desc') => void;
  onRowClick?: (row: any) => void;
}

export const ResponsiveTable = memo(({ 
  data, 
  columns, 
  loading = false,
  onSort,
  onRowClick
}: ResponsiveTableProps) => {
  const [sortConfig, setSortConfig] = useState<{ key: string; direction: 'asc' | 'desc' } | null>(null);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  
  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  const handleSort = useCallback((key: string) => {
    const direction = sortConfig?.key === key && sortConfig.direction === 'asc' ? 'desc' : 'asc';
    setSortConfig({ key, direction });
    onSort?.(key, direction);
  }, [sortConfig, onSort]);
  
  if (loading) {
    return (
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-12 bg-gray-200 rounded animate-pulse" />
        ))}
      </div>
    );
  }
  
  if (isMobile) {
    // 移动端卡片布局
    return (
      <div className="space-y-3">
        {data.map((row, index) => (
          <Card 
            key={index} 
            className={`cursor-pointer hover:shadow-md transition-shadow ${
              onRowClick ? 'hover:bg-gray-50' : ''
            }`}
            onClick={() => onRowClick?.(row)}
          >
            <CardContent className="p-4">
              {columns.map(column => (
                <div key={column.key} className="flex justify-between items-center py-1">
                  <span className="font-medium text-gray-600">{column.label}:</span>
                  <span className="text-right">
                    {column.render ? column.render(row[column.key], row) : row[column.key]}
                  </span>
                </div>
              ))}
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }
  
  // 桌面端表格布局
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b">
            {columns.map(column => (
              <th 
                key={column.key}
                className={`text-left p-3 font-medium text-gray-600 ${
                  column.sortable ? 'cursor-pointer hover:bg-gray-50' : ''
                }`}
                style={{ width: column.width }}
                onClick={() => column.sortable && handleSort(column.key)}
              >
                <div className="flex items-center space-x-1">
                  <span>{column.label}</span>
                  {column.sortable && (
                    <TrendingUp className={`h-4 w-4 transition-transform ${
                      sortConfig?.key === column.key 
                        ? sortConfig.direction === 'desc' ? 'rotate-180' : ''
                        : 'opacity-50'
                    }`} />
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr 
              key={index}
              className={`border-b hover:bg-gray-50 transition-colors ${
                onRowClick ? 'cursor-pointer' : ''
              }`}
              onClick={() => onRowClick?.(row)}
            >
              {columns.map(column => (
                <td key={column.key} className="p-3">
                  {column.render ? column.render(row[column.key], row) : row[column.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
});

// 快捷操作面板
interface QuickActionPanelProps {
  actions: {
    id: string;
    label: string;
    icon: React.ReactNode;
    onClick: () => void;
    disabled?: boolean;
    badge?: string | number;
  }[];
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
}

export const QuickActionPanel = memo(({ actions, position = 'bottom-right' }: QuickActionPanelProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const positionClasses = {
    'bottom-right': 'bottom-6 right-6',
    'bottom-left': 'bottom-6 left-6',
    'top-right': 'top-6 right-6',
    'top-left': 'top-6 left-6'
  };
  
  return (
    <div className={`fixed ${positionClasses[position]} z-40`}>
      <div className={`flex flex-col space-y-2 transition-all duration-300 ${
        isExpanded ? 'opacity-100 scale-100' : 'opacity-0 scale-95 pointer-events-none'
      }`}>
        {actions.map(action => (
          <Button
            key={action.id}
            onClick={action.onClick}
            disabled={action.disabled}
            className="relative h-12 w-12 rounded-full shadow-lg"
            title={action.label}
          >
            {action.icon}
            {action.badge && (
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                {action.badge}
              </span>
            )}
          </Button>
        ))}
      </div>
      
      <Button
        onClick={() => setIsExpanded(!isExpanded)}
        className="h-14 w-14 rounded-full shadow-lg mt-2"
      >
        <Zap className={`h-6 w-6 transition-transform ${
          isExpanded ? 'rotate-45' : ''
        }`} />
      </Button>
    </div>
  );
});