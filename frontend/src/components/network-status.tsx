import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Wifi, WifiOff, AlertTriangle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

interface NetworkState {
  isOnline: boolean;
  isSlowConnection: boolean;
  lastChecked: Date;
  latency?: number;
}

interface NetworkContextType {
  networkState: NetworkState;
  checkConnection: () => Promise<void>;
  retryConnection: () => Promise<void>;
}

const NetworkContext = createContext<NetworkContextType | undefined>(undefined);

interface NetworkStatusProviderProps {
  children: ReactNode;
}

export function NetworkStatusProvider({ children }: NetworkStatusProviderProps) {
  const [networkState, setNetworkState] = useState<NetworkState>({
    isOnline: navigator.onLine,
    isSlowConnection: false,
    lastChecked: new Date(),
  });

  const checkConnection = async () => {
    const startTime = Date.now();
    
    try {
      // Try to fetch a small resource to test connection
      const response = await fetch('/api/v1/health/', {
        method: 'GET',
        cache: 'no-cache',
        signal: AbortSignal.timeout(5000), // 5 second timeout
      });
      
      const latency = Date.now() - startTime;
      const isSlowConnection = latency > 3000; // Consider slow if > 3 seconds
      
      setNetworkState({
        isOnline: response.ok,
        isSlowConnection,
        lastChecked: new Date(),
        latency,
      });

      if (isSlowConnection) {
        toast.warning('Slow network connection detected');
      }
    } catch (error) {
      setNetworkState(prev => ({
        ...prev,
        isOnline: false,
        lastChecked: new Date(),
      }));
    }
  };

  const retryConnection = async () => {
    toast.info('Checking connection...');
    await checkConnection();
  };

  useEffect(() => {
    // Initial connection check
    checkConnection();

    // Listen for online/offline events
    const handleOnline = () => {
      setNetworkState(prev => ({ ...prev, isOnline: true }));
      toast.success('Connection restored');
      checkConnection();
    };

    const handleOffline = () => {
      setNetworkState(prev => ({ ...prev, isOnline: false }));
      toast.error('Connection lost');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Periodic connection check
    const interval = setInterval(checkConnection, 30000); // Check every 30 seconds

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearInterval(interval);
    };
  }, []);

  const value: NetworkContextType = {
    networkState,
    checkConnection,
    retryConnection,
  };

  return (
    <NetworkContext.Provider value={value}>
      {children}
      {!networkState.isOnline && <OfflineOverlay />}
      {networkState.isOnline && networkState.isSlowConnection && <SlowConnectionAlert />}
    </NetworkContext.Provider>
  );
}

function OfflineOverlay() {
  const { retryConnection } = useNetworkStatus();

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg p-8 max-w-md w-full text-center">
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <WifiOff className="w-8 h-8 text-red-600" />
        </div>
        
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          No Internet Connection
        </h2>
        
        <p className="text-gray-600 mb-6">
          Please check your internet connection and try again.
        </p>
        
        <Button onClick={retryConnection} className="w-full">
          <Wifi className="w-4 h-4 mr-2" />
          Retry Connection
        </Button>
        
        <div className="mt-4 text-sm text-gray-500">
          <p>Troubleshooting tips:</p>
          <ul className="text-left mt-2 space-y-1">
            <li>• Check your WiFi or mobile data</li>
            <li>• Restart your router</li>
            <li>• Try refreshing the page</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

function SlowConnectionAlert() {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;

  return (
    <div className="fixed top-4 right-4 z-40 max-w-sm">
      <Alert className="border-yellow-200 bg-yellow-50">
        <AlertTriangle className="h-4 w-4 text-yellow-600" />
        <AlertDescription className="text-yellow-800">
          <div className="flex items-center justify-between">
            <span className="text-sm">Slow connection detected</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsVisible(false)}
              className="h-auto p-1 text-yellow-600 hover:text-yellow-800"
            >
              ×
            </Button>
          </div>
        </AlertDescription>
      </Alert>
    </div>
  );
}

// Hook to use network status
export function useNetworkStatus() {
  const context = useContext(NetworkContext);
  if (context === undefined) {
    throw new Error('useNetworkStatus must be used within a NetworkStatusProvider');
  }
  return context;
}

// Network status indicator component
export function NetworkStatusIndicator() {
  const { networkState } = useNetworkStatus();

  if (!networkState.isOnline) {
    return (
      <div className="flex items-center space-x-2 text-red-600">
        <WifiOff className="w-4 h-4" />
        <span className="text-sm">Offline</span>
      </div>
    );
  }

  if (networkState.isSlowConnection) {
    return (
      <div className="flex items-center space-x-2 text-yellow-600">
        <AlertTriangle className="w-4 h-4" />
        <span className="text-sm">Slow</span>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-2 text-green-600">
      <Wifi className="w-4 h-4" />
      <span className="text-sm">Online</span>
      {networkState.latency && (
        <span className="text-xs text-gray-500">
          ({networkState.latency}ms)
        </span>
      )}
    </div>
  );
}

// Hook for handling network-dependent operations
export function useNetworkAwareOperation() {
  const { networkState, retryConnection } = useNetworkStatus();

  const executeWhenOnline = async <T>(
    operation: () => Promise<T>,
    options?: {
      retryOnFailure?: boolean;
      showOfflineMessage?: boolean;
    }
  ): Promise<T> => {
    if (!networkState.isOnline) {
      if (options?.showOfflineMessage !== false) {
        toast.error('No internet connection. Please check your connection and try again.');
      }
      throw new Error('No internet connection');
    }

    try {
      return await operation();
    } catch (error) {
      if (options?.retryOnFailure && !networkState.isOnline) {
        toast.info('Connection lost. Retrying...');
        await retryConnection();
        if (networkState.isOnline) {
          return await operation();
        }
      }
      throw error;
    }
  };

  return { executeWhenOnline, isOnline: networkState.isOnline };
}

export default NetworkStatusProvider;
