import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { Loader2, AlertCircle, CheckCircle, X } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface LoadingState {
  id: string;
  message: string;
  progress?: number;
  type: 'loading' | 'success' | 'error';
  startTime: number;
  canCancel?: boolean;
  onCancel?: () => void;
  estimatedDuration?: number;
}

interface SmartLoadingContextType {
  loadingStates: LoadingState[];
  startLoading: (id: string, message: string, options?: Partial<LoadingState>) => void;
  updateLoading: (id: string, updates: Partial<LoadingState>) => void;
  finishLoading: (id: string, type: 'success' | 'error', message?: string) => void;
  cancelLoading: (id: string) => void;
  clearLoading: (id: string) => void;
  isLoading: (id?: string) => boolean;
}

const SmartLoadingContext = createContext<SmartLoadingContextType | undefined>(undefined);

interface SmartLoadingProviderProps {
  children: ReactNode;
  maxConcurrentLoading?: number;
  autoHideDelay?: number;
}

export function SmartLoadingProvider({ 
  children, 
  maxConcurrentLoading = 3,
  autoHideDelay = 3000 
}: SmartLoadingProviderProps) {
  const [loadingStates, setLoadingStates] = useState<LoadingState[]>([]);

  const startLoading = useCallback((
    id: string, 
    message: string, 
    options: Partial<LoadingState> = {}
  ) => {
    setLoadingStates(prev => {
      // Remove existing state with same id
      const filtered = prev.filter(state => state.id !== id);
      
      // Limit concurrent loading states
      const limited = filtered.slice(-(maxConcurrentLoading - 1));
      
      return [...limited, {
        id,
        message,
        type: 'loading',
        startTime: Date.now(),
        progress: 0,
        ...options,
      }];
    });
  }, [maxConcurrentLoading]);

  const updateLoading = useCallback((id: string, updates: Partial<LoadingState>) => {
    setLoadingStates(prev => 
      prev.map(state => 
        state.id === id ? { ...state, ...updates } : state
      )
    );
  }, []);

  const finishLoading = useCallback((
    id: string, 
    type: 'success' | 'error', 
    message?: string
  ) => {
    setLoadingStates(prev => 
      prev.map(state => 
        state.id === id 
          ? { 
              ...state, 
              type, 
              progress: 100,
              message: message || state.message 
            }
          : state
      )
    );

    // Auto-hide after delay
    setTimeout(() => {
      setLoadingStates(prev => prev.filter(state => state.id !== id));
    }, autoHideDelay);
  }, [autoHideDelay]);

  const cancelLoading = useCallback((id: string) => {
    const state = loadingStates.find(s => s.id === id);
    if (state?.onCancel) {
      state.onCancel();
    }
    setLoadingStates(prev => prev.filter(state => state.id !== id));
  }, [loadingStates]);

  const clearLoading = useCallback((id: string) => {
    setLoadingStates(prev => prev.filter(state => state.id !== id));
  }, []);

  const isLoading = useCallback((id?: string) => {
    if (id) {
      return loadingStates.some(state => state.id === id && state.type === 'loading');
    }
    return loadingStates.some(state => state.type === 'loading');
  }, [loadingStates]);

  const value: SmartLoadingContextType = {
    loadingStates,
    startLoading,
    updateLoading,
    finishLoading,
    cancelLoading,
    clearLoading,
    isLoading,
  };

  return (
    <SmartLoadingContext.Provider value={value}>
      {children}
      <LoadingOverlay />
    </SmartLoadingContext.Provider>
  );
}

function LoadingOverlay() {
  const { loadingStates, cancelLoading, clearLoading } = useSmartLoading();

  if (loadingStates.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2 max-w-sm">
      {loadingStates.map((state) => (
        <LoadingCard key={state.id} state={state} onCancel={cancelLoading} onClear={clearLoading} />
      ))}
    </div>
  );
}

interface LoadingCardProps {
  state: LoadingState;
  onCancel: (id: string) => void;
  onClear: (id: string) => void;
}

function LoadingCard({ state, onCancel, onClear }: LoadingCardProps) {
  const [timeElapsed, setTimeElapsed] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setTimeElapsed(Date.now() - state.startTime);
    }, 1000);

    return () => clearInterval(interval);
  }, [state.startTime]);

  const formatTime = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    return minutes > 0 ? `${minutes}m ${seconds % 60}s` : `${seconds}s`;
  };

  const getIcon = () => {
    switch (state.type) {
      case 'loading':
        return <Loader2 className="w-4 h-4 animate-spin" />;
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-600" />;
    }
  };

  const getProgressColor = () => {
    switch (state.type) {
      case 'success':
        return 'bg-green-600';
      case 'error':
        return 'bg-red-600';
      default:
        return 'bg-blue-600';
    }
  };

  return (
    <Card className={cn(
      "w-full transition-all duration-300 ease-in-out",
      state.type === 'success' && "border-green-200 bg-green-50",
      state.type === 'error' && "border-red-200 bg-red-50"
    )}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between space-x-3">
          <div className="flex items-center space-x-2 flex-1">
            {getIcon()}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {state.message}
              </p>
              <div className="flex items-center space-x-2 mt-1">
                <span className="text-xs text-gray-500">
                  {formatTime(timeElapsed)}
                </span>
                {state.estimatedDuration && state.type === 'loading' && (
                  <span className="text-xs text-gray-400">
                    / ~{formatTime(state.estimatedDuration)}
                  </span>
                )}
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-1">
            {state.type === 'loading' && state.canCancel && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onCancel(state.id)}
                className="h-6 w-6 p-0 text-gray-400 hover:text-gray-600"
              >
                <X className="w-3 h-3" />
              </Button>
            )}
            {state.type !== 'loading' && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onClear(state.id)}
                className="h-6 w-6 p-0 text-gray-400 hover:text-gray-600"
              >
                <X className="w-3 h-3" />
              </Button>
            )}
          </div>
        </div>
        
        {typeof state.progress === 'number' && (
          <div className="mt-3">
            <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
              <span>Progress</span>
              <span>{Math.round(state.progress)}%</span>
            </div>
            <Progress 
              value={state.progress} 
              className="h-2"
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Hook to use smart loading
export function useSmartLoading() {
  const context = useContext(SmartLoadingContext);
  if (context === undefined) {
    throw new Error('useSmartLoading must be used within a SmartLoadingProvider');
  }
  return context;
}

// Hook for async operations with smart loading
export function useAsyncWithLoading() {
  const { startLoading, updateLoading, finishLoading, isLoading } = useSmartLoading();

  const execute = useCallback(async <T>(
    operation: (updateProgress?: (progress: number, message?: string) => void) => Promise<T>,
    options: {
      id: string;
      message: string;
      canCancel?: boolean;
      onCancel?: () => void;
      estimatedDuration?: number;
    }
  ): Promise<T> => {
    const { id, message, canCancel, onCancel, estimatedDuration } = options;

    startLoading(id, message, { canCancel, onCancel, estimatedDuration });

    try {
      const updateProgress = (progress: number, newMessage?: string) => {
        updateLoading(id, { 
          progress, 
          message: newMessage || message 
        });
      };

      const result = await operation(updateProgress);
      finishLoading(id, 'success', 'Completed successfully');
      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Operation failed';
      finishLoading(id, 'error', errorMessage);
      throw error;
    }
  }, [startLoading, updateLoading, finishLoading]);

  return { execute, isLoading };
}

// Skeleton loader component
export function SkeletonLoader({ 
  lines = 3, 
  className = "",
  animated = true 
}: { 
  lines?: number; 
  className?: string;
  animated?: boolean;
}) {
  return (
    <div className={cn("space-y-3", className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className={cn(
            "h-4 bg-gray-200 rounded",
            animated && "animate-pulse",
            i === lines - 1 && "w-3/4" // Last line is shorter
          )}
        />
      ))}
    </div>
  );
}

// Smart loading button component
interface SmartLoadingButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  loadingId?: string;
  loadingMessage?: string;
  children: ReactNode;
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  size?: 'default' | 'sm' | 'lg' | 'icon';
}

export function SmartLoadingButton({
  loadingId,
  loadingMessage = "Processing...",
  children,
  onClick,
  disabled,
  ...props
}: SmartLoadingButtonProps) {
  const { isLoading } = useSmartLoading();
  const isCurrentlyLoading = loadingId ? isLoading(loadingId) : false;

  return (
    <Button
      {...props}
      disabled={disabled || isCurrentlyLoading}
      onClick={onClick}
    >
      {isCurrentlyLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
      {children}
    </Button>
  );
}

export default SmartLoadingProvider;
