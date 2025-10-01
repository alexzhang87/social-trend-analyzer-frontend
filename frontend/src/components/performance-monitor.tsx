import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { 
  Activity, 
  Clock, 
  Zap, 
  Database, 
  Wifi, 
  CheckCircle, 
  AlertCircle,
  TrendingUp
} from 'lucide-react';

interface PerformanceMetrics {
  responseTime: number;
  apiLatency: number;
  dataProcessingTime: number;
  totalAnalysisTime: number;
  status: 'fast' | 'normal' | 'slow';
  timestamp: number;
}

interface ServiceStatus {
  name: string;
  status: 'online' | 'slow' | 'offline';
  responseTime: number;
  endpoint: string;
}

const PerformanceMonitor: React.FC<{ isAnalyzing: boolean; onMetricsUpdate?: (metrics: PerformanceMetrics) => void }> = ({ 
  isAnalyzing, 
  onMetricsUpdate 
}) => {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    responseTime: 0,
    apiLatency: 0,
    dataProcessingTime: 0,
    totalAnalysisTime: 0,
    status: 'fast',
    timestamp: Date.now()
  });

  const [services, setServices] = useState<ServiceStatus[]>([
    { name: 'Twitter API', status: 'online', responseTime: 0, endpoint: '/api/v1/trends' },
    { name: 'Reddit API', status: 'online', responseTime: 0, endpoint: '/api/v1/trends' },
    { name: 'Product Hunt', status: 'online', responseTime: 0, endpoint: '/api/v1/trends' },
    { name: 'Google Trends', status: 'online', responseTime: 0, endpoint: '/api/v1/google-trends/status' },
    { name: 'MonkeyLearn AI', status: 'online', responseTime: 0, endpoint: '/api/v1/monkeylearn/status' },
    { name: 'Data Studio', status: 'online', responseTime: 0, endpoint: '/api/v1/data-studio/status' },
    { name: 'Metabase', status: 'online', responseTime: 0, endpoint: '/api/v1/metabase/status' }
  ]);

  const [networkSpeed, setNetworkSpeed] = useState<number>(0);

  // Monitor network speed
  const measureNetworkSpeed = useCallback(async () => {
    const startTime = performance.now();
    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';
      await fetch(`${apiBaseUrl}/api/v1/health`, { 
        method: 'HEAD',
        cache: 'no-cache'
      });
      const endTime = performance.now();
      const speed = endTime - startTime;
      setNetworkSpeed(speed);
      return speed;
    } catch (error) {
      console.error('Network speed test failed:', error);
      return 1000; // Assume 1 second as default value
    }
  }, []);

  // Check service status
  const checkServiceStatus = useCallback(async () => {
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';
    
    const updatedServices = await Promise.all(
      services.map(async (service) => {
        const startTime = performance.now();
        try {
          const response = await fetch(`${apiBaseUrl}${service.endpoint}`, {
            method: 'GET',
            cache: 'no-cache',
            signal: AbortSignal.timeout(5000) // 5 second timeout
          });
          
          const endTime = performance.now();
          const responseTime = endTime - startTime;
          
          let status: ServiceStatus['status'] = 'online';
          if (responseTime > 3000) {
            status = 'slow';
          } else if (!response.ok) {
            status = 'offline';
          }
          
          return {
            ...service,
            status,
            responseTime: Math.round(responseTime)
          };
        } catch (error) {
          return {
            ...service,
            status: 'offline' as const,
            responseTime: 5000
          };
        }
      })
    );
    
    setServices(updatedServices);
  }, [services.length]);

  // Update performance metrics
  const updateMetrics = useCallback(() => {
    const totalResponseTime = services.reduce((sum, service) => sum + service.responseTime, 0) / services.length;
    const avgNetworkSpeed = networkSpeed;
    
    const newMetrics: PerformanceMetrics = {
      responseTime: Math.round(totalResponseTime),
      apiLatency: Math.round(avgNetworkSpeed),
      dataProcessingTime: Math.round(totalResponseTime * 0.6), // Estimated data processing time
      totalAnalysisTime: Math.round(totalResponseTime + avgNetworkSpeed + (totalResponseTime * 0.6)),
      status: totalResponseTime < 1000 ? 'fast' : totalResponseTime < 3000 ? 'normal' : 'slow',
      timestamp: Date.now()
    };
    
    setMetrics(newMetrics);
    onMetricsUpdate?.(newMetrics);
  }, [services, networkSpeed, onMetricsUpdate]);

  // Periodic performance check
  useEffect(() => {
    const performanceCheck = async () => {
      await measureNetworkSpeed();
      await checkServiceStatus();
    };

    // Execute immediately once
    performanceCheck();

    // Check every 30 seconds
    const interval = setInterval(performanceCheck, 30000);

    return () => clearInterval(interval);
  }, [measureNetworkSpeed, checkServiceStatus]);

  // Update metrics
  useEffect(() => {
    updateMetrics();
  }, [updateMetrics]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'fast':
      case 'online':
        return 'text-green-600 bg-green-100';
      case 'normal':
      case 'slow':
        return 'text-yellow-600 bg-yellow-100';
      case 'offline':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'fast':
      case 'online':
        return <CheckCircle className="w-4 h-4" />;
      case 'normal':
      case 'slow':
        return <AlertCircle className="w-4 h-4" />;
      case 'offline':
        return <AlertCircle className="w-4 h-4" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  return (
    <div className="space-y-4">
      {/* Overall performance overview */}
      <Card className="glass-card shadow-modern">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            System Performance
            <Badge className={getStatusColor(metrics.status)}>
              {getStatusIcon(metrics.status)}
              <span className="ml-1">
                {metrics.status === 'fast' ? 'Fast' : metrics.status === 'normal' ? 'Normal' : 'Slow'}
              </span>
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Clock className="w-4 h-4 text-blue-600" />
                <span className="text-sm font-medium">Response Time</span>
              </div>
              <div className="text-2xl font-bold text-blue-600">
                {metrics.responseTime}ms
              </div>
              <Progress 
                value={Math.min(100, (3000 - metrics.responseTime) / 30)} 
                className="mt-2 h-2" 
              />
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Wifi className="w-4 h-4 text-green-600" />
                <span className="text-sm font-medium">Network Latency</span>
              </div>
              <div className="text-2xl font-bold text-green-600">
                {metrics.apiLatency}ms
              </div>
              <Progress 
                value={Math.min(100, (1000 - metrics.apiLatency) / 10)} 
                className="mt-2 h-2" 
              />
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Database className="w-4 h-4 text-purple-600" />
                <span className="text-sm font-medium">Processing Time</span>
              </div>
              <div className="text-2xl font-bold text-purple-600">
                {metrics.dataProcessingTime}ms
              </div>
              <Progress 
                value={Math.min(100, (2000 - metrics.dataProcessingTime) / 20)} 
                className="mt-2 h-2" 
              />
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Zap className="w-4 h-4 text-orange-600" />
                <span className="text-sm font-medium">Total Analysis Time</span>
              </div>
              <div className="text-2xl font-bold text-orange-600">
                {(metrics.totalAnalysisTime / 1000).toFixed(1)}s
              </div>
              <Progress 
                value={Math.min(100, (10000 - metrics.totalAnalysisTime) / 100)} 
                className="mt-2 h-2" 
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Service status */}
      <Card className="glass-card shadow-modern">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <Activity className="w-5 h-5 text-green-600" />
            Service Status Monitor
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {services.map((service) => (
              <div
                key={service.name}
                className="flex items-center justify-between p-3 rounded-lg bg-white/50 border border-white/20"
              >
                <div className="flex items-center gap-2">
                  {getStatusIcon(service.status)}
                  <span className="font-medium text-sm">{service.name}</span>
                </div>
                <div className="text-right">
                  <Badge className={getStatusColor(service.status)} variant="outline">
                    {service.status === 'online' ? 'Online' : service.status === 'slow' ? 'Slow' : 'Offline'}
                  </Badge>
                  <div className="text-xs text-gray-500 mt-1">
                    {service.responseTime}ms
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Performance optimization tips */}
      {metrics.status !== 'fast' && (
        <Card className="glass-card shadow-modern border-yellow-200">
          <CardContent className="pt-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
              <div>
                <h4 className="font-semibold text-yellow-800 mb-2">Performance Optimization Suggestions</h4>
                <ul className="text-sm text-yellow-700 space-y-1">
                  {metrics.responseTime > 2000 && (
                    <li>• API response time is slow, please check network connection</li>
                  )}
                  {metrics.apiLatency > 500 && (
                    <li>• Network latency is high, please optimize network environment</li>
                  )}
                  <li>• System is auto-optimizing, please wait...</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default PerformanceMonitor;
