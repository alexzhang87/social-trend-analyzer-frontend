import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { RefreshCw, Server, Database, Cpu, HardDrive, Wifi } from 'lucide-react';
import { adminApiClient } from '@/lib/admin-api';

interface SystemMetrics {
  cpu: {
    usage: number;
    cores: number;
  };
  memory: {
    used: number;
    total: number;
    percentage: number;
  };
  disk: {
    used: number;
    total: number;
    percentage: number;
  };
  network: {
    inbound: number;
    outbound: number;
  };
  database: {
    connections: number;
    maxConnections: number;
    queryTime: number;
  };
  uptime: number;
  status: 'healthy' | 'warning' | 'error';
}

export function SystemMonitoring() {
  const [metrics, setMetrics] = useState<SystemMetrics>({
    cpu: { usage: 0, cores: 0 },
    memory: { used: 0, total: 0, percentage: 0 },
    disk: { used: 0, total: 0, percentage: 0 },
    network: { inbound: 0, outbound: 0 },
    database: { connections: 0, maxConnections: 0, queryTime: 0 },
    uptime: 0,
    status: 'healthy'
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);

  const fetchMetrics = async () => {
    try {
      setError(null);
      const response = await adminApiClient.getSystemMetrics();
      setMetrics(response.data);
    } catch (err) {
      setError('Failed to fetch system metrics');
      console.error('Failed to fetch system metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(fetchMetrics, 30000); // Refresh every 30 seconds
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600';
      case 'warning': return 'text-yellow-600';
      case 'error': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-gray-400" />
        <span className="ml-2 text-gray-600">Loading...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page title */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">System Monitoring</h1>
          <p className="text-gray-600">Real-time system performance and health status</p>
        </div>
        <div className="flex space-x-2">
          <Button 
            onClick={() => setAutoRefresh(!autoRefresh)}
            variant={autoRefresh ? 'default' : 'outline'}
            size="sm"
          >
            {autoRefresh ? 'Stop Auto Refresh' : 'Start Auto Refresh'}
          </Button>
          <Button onClick={fetchMetrics} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <p className="text-red-600">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* System status overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Server className={`h-5 w-5 ${getStatusColor(metrics.status)}`} />
            <span>System Status</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Badge 
                variant={metrics.status === 'healthy' ? 'default' : 
                        metrics.status === 'warning' ? 'secondary' : 'destructive'}
              >
                {metrics.status === 'healthy' ? 'Healthy' :
             metrics.status === 'warning' ? 'Warning' : 'Error'}
              </Badge>
              <span className="text-sm text-gray-600">
                Uptime: {formatUptime(metrics.uptime)}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Performance metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* CPU usage */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">CPU Usage</CardTitle>
            <Cpu className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.cpu.usage}%</div>
            <Progress value={metrics.cpu.usage} className="mt-2" />
            <p className="text-xs text-gray-500 mt-1">
              {metrics.cpu.cores} cores
            </p>
          </CardContent>
        </Card>

        {/* Memory usage */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Memory Usage</CardTitle>
            <HardDrive className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.memory.percentage}%</div>
            <Progress value={metrics.memory.percentage} className="mt-2" />
            <p className="text-xs text-gray-500 mt-1">
              {formatBytes(metrics.memory.used)} / {formatBytes(metrics.memory.total)}
            </p>
          </CardContent>
        </Card>

        {/* Disk usage */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Disk Usage</CardTitle>
            <HardDrive className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.disk.percentage}%</div>
            <Progress value={metrics.disk.percentage} className="mt-2" />
            <p className="text-xs text-gray-500 mt-1">
              {formatBytes(metrics.disk.used)} / {formatBytes(metrics.disk.total)}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Network and database */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Network traffic */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Wifi className="h-5 w-5 text-blue-600" />
              <span>Network Traffic</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Inbound</span>
                <span className="font-medium">{formatBytes(metrics.network.inbound)}/s</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Outbound</span>
                <span className="font-medium">{formatBytes(metrics.network.outbound)}/s</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Database status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Database className="h-5 w-5 text-green-600" />
              <span>Database Status</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Active Connections</span>
                <span className="font-medium">
                  {metrics.database.connections} / {metrics.database.maxConnections}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Avg Query Time</span>
                <span className="font-medium">{metrics.database.queryTime}ms</span>
              </div>
              <Progress 
                value={(metrics.database.connections / metrics.database.maxConnections) * 100} 
                className="mt-2" 
              />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
