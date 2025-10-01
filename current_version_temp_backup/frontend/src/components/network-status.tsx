import React, { useState, useEffect } from 'react';
import { Wifi, WifiOff, AlertTriangle, CheckCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

interface NetworkState {
  isOnline: boolean;
  isSlowConnection: boolean;
  lastOnlineTime?: Date;
  connectionType?: string;
}

export function NetworkStatusProvider({ children }: { children: React.ReactNode }) {
  const [networkState, setNetworkState] = useState<NetworkState>({
    isOnline: navigator.onLine,
    isSlowConnection: false,
  });
  const [showOfflineAlert, setShowOfflineAlert] = useState(false);

  useEffect(() => {
    const updateOnlineStatus = () => {
      const isOnline = navigator.onLine;
      setNetworkState(prev => ({
        ...prev,
        isOnline,
        lastOnlineTime: isOnline ? new Date() : prev.lastOnlineTime,
      }));

      if (isOnline) {
        setShowOfflineAlert(false);
        toast.success('网络连接已恢复');
      } else {
        setShowOfflineAlert(true);
        toast.error('网络连接已断开');
      }
    };

    const detectSlowConnection = () => {
      if ('connection' in navigator) {
        const connection = (navigator as any).connection;
        const isSlowConnection = 
          connection.effectiveType === 'slow-2g' || 
          connection.effectiveType === '2g' ||
          connection.downlink < 1;
        
        setNetworkState(prev => ({
          ...prev,
          isSlowConnection,
          connectionType: connection.effectiveType,
        }));

        if (isSlowConnection) {
          toast.warning('检测到网络连接较慢，可能影响使用体验');
        }
      }
    };

    // 监听网络状态变化
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);

    // 监听连接变化（如果支持）
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      connection.addEventListener('change', detectSlowConnection);
    }

    // 初始检测
    detectSlowConnection();

    return () => {
      window.removeEventListener('online', updateOnlineStatus);
      window.removeEventListener('offline', updateOnlineStatus);
      if ('connection' in navigator) {
        const connection = (navigator as any).connection;
        connection.removeEventListener('change', detectSlowConnection);
      }
    };
  }, []);

  return (
    <>
      {children}
      <NetworkStatusIndicator 
        networkState={networkState}
        showOfflineAlert={showOfflineAlert}
        onDismissAlert={() => setShowOfflineAlert(false)}
      />
    </>
  );
}

interface NetworkStatusIndicatorProps {
  networkState: NetworkState;
  showOfflineAlert: boolean;
  onDismissAlert: () => void;
}

function NetworkStatusIndicator({ 
  networkState, 
  showOfflineAlert, 
  onDismissAlert 
}: NetworkStatusIndicatorProps) {
  const [showRetryButton, setShowRetryButton] = useState(false);

  useEffect(() => {
    if (!networkState.isOnline) {
      const timer = setTimeout(() => {
        setShowRetryButton(true);
      }, 5000); // 5秒后显示重试按钮
      return () => clearTimeout(timer);
    } else {
      setShowRetryButton(false);
    }
  }, [networkState.isOnline]);

  const handleRetry = () => {
    window.location.reload();
  };

  const formatLastOnlineTime = (date?: Date) => {
    if (!date) return '';
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return '刚刚';
    if (minutes < 60) return `${minutes}分钟前`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}小时前`;
    return date.toLocaleDateString();
  };

  return (
    <>
      {/* 固定在右上角的网络状态指示器 */}
      <div className="fixed top-4 right-4 z-40">
        <div className="flex items-center space-x-2">
          {/* 网络状态图标 */}
          <div className={`p-2 rounded-full ${
            networkState.isOnline 
              ? 'bg-green-100 text-green-600' 
              : 'bg-red-100 text-red-600'
          }`}>
            {networkState.isOnline ? (
              <Wifi className="w-4 h-4" />
            ) : (
              <WifiOff className="w-4 h-4" />
            )}
          </div>
          
          {/* 慢速连接警告 */}
          {networkState.isOnline && networkState.isSlowConnection && (
            <div className="p-2 rounded-full bg-yellow-100 text-yellow-600">
              <AlertTriangle className="w-4 h-4" />
            </div>
          )}
        </div>
      </div>

      {/* 离线状态全屏提示 */}
      {showOfflineAlert && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto">
                <WifiOff className="w-8 h-8 text-red-600" />
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  网络连接已断开
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  请检查您的网络连接，然后重试
                </p>
                
                {networkState.lastOnlineTime && (
                  <p className="text-xs text-gray-500">
                    最后在线时间: {formatLastOnlineTime(networkState.lastOnlineTime)}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <div className="text-xs text-gray-500 space-y-1">
                  <p><strong>可能的解决方案：</strong></p>
                  <ul className="list-disc list-inside text-left space-y-1">
                    <li>检查WiFi或移动数据连接</li>
                    <li>尝试刷新页面</li>
                    <li>检查路由器连接</li>
                    <li>联系网络服务提供商</li>
                  </ul>
                </div>
              </div>

              <div className="flex gap-2">
                <Button 
                  onClick={onDismissAlert} 
                  variant="outline" 
                  size="sm"
                  className="flex-1"
                >
                  继续离线使用
                </Button>
                
                {showRetryButton && (
                  <Button 
                    onClick={handleRetry} 
                    size="sm"
                    className="flex-1"
                  >
                    重新加载
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 慢速连接提示条 */}
      {networkState.isOnline && networkState.isSlowConnection && (
        <div className="fixed top-0 left-0 right-0 z-30">
          <Alert className="rounded-none border-x-0 border-t-0 bg-yellow-50 border-yellow-200">
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
            <AlertDescription className="text-yellow-800">
              <span className="font-medium">网络连接较慢</span>
              {networkState.connectionType && (
                <span className="ml-2 text-sm">({networkState.connectionType})</span>
              )}
              - 某些功能可能需要更长时间加载
            </AlertDescription>
          </Alert>
        </div>
      )}
    </>
  );
}

// Hook for checking network status
export function useNetworkStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isSlowConnection, setIsSlowConnection] = useState(false);

  useEffect(() => {
    const updateOnlineStatus = () => {
      setIsOnline(navigator.onLine);
    };

    const checkConnectionSpeed = () => {
      if ('connection' in navigator) {
        const connection = (navigator as any).connection;
        const isSlowConnection = 
          connection.effectiveType === 'slow-2g' || 
          connection.effectiveType === '2g' ||
          connection.downlink < 1;
        setIsSlowConnection(isSlowConnection);
      }
    };

    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      connection.addEventListener('change', checkConnectionSpeed);
    }

    checkConnectionSpeed();

    return () => {
      window.removeEventListener('online', updateOnlineStatus);
      window.removeEventListener('offline', updateOnlineStatus);
      if ('connection' in navigator) {
        const connection = (navigator as any).connection;
        connection.removeEventListener('change', checkConnectionSpeed);
      }
    };
  }, []);

  return { isOnline, isSlowConnection };
}

// 网络状态检查工具函数
export const networkUtils = {
  // 检查网络连接
  checkConnection: async (): Promise<boolean> => {
    try {
      const response = await fetch('/api/health', {
        method: 'HEAD',
        cache: 'no-cache',
      });
      return response.ok;
    } catch {
      return false;
    }
  },

  // 测试网络延迟
  measureLatency: async (): Promise<number> => {
    const start = performance.now();
    try {
      await fetch('/api/ping', {
        method: 'HEAD',
        cache: 'no-cache',
      });
      return performance.now() - start;
    } catch {
      return -1; // 表示无法连接
    }
  },

  // 获取连接信息
  getConnectionInfo: () => {
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      return {
        effectiveType: connection.effectiveType,
        downlink: connection.downlink,
        rtt: connection.rtt,
        saveData: connection.saveData,
      };
    }
    return null;
  },
};