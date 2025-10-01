import React, { createContext, useContext, useState, ReactNode } from 'react';
import { Loader2, AlertCircle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';

interface LoadingState {
  isLoading: boolean;
  message?: string;
  progress?: number;
  error?: string;
  canCancel?: boolean;
}

interface LoadingContextType {
  loadingState: LoadingState;
  setLoading: (loading: boolean, message?: string, progress?: number) => void;
  setProgress: (progress: number) => void;
  setError: (error: string) => void;
  clearError: () => void;
  setCanCancel: (canCancel: boolean) => void;
  cancelLoading: () => void;
}

const LoadingContext = createContext<LoadingContextType | undefined>(undefined);

export function LoadingProvider({ children }: { children: ReactNode }) {
  const [loadingState, setLoadingState] = useState<LoadingState>({
    isLoading: false,
    message: '',
    progress: 0,
    error: '',
    canCancel: false,
  });

  const setLoading = (loading: boolean, message?: string, progress?: number) => {
    setLoadingState(prev => ({
      ...prev,
      isLoading: loading,
      message: message || '',
      progress: progress || 0,
      error: loading ? '' : prev.error, // 清除错误当开始新的加载
    }));
  };

  const setProgress = (progress: number) => {
    setLoadingState(prev => ({
      ...prev,
      progress: Math.max(0, Math.min(100, progress)),
    }));
  };

  const setError = (error: string) => {
    setLoadingState(prev => ({
      ...prev,
      error,
      isLoading: false,
    }));
  };

  const clearError = () => {
    setLoadingState(prev => ({
      ...prev,
      error: '',
    }));
  };

  const setCanCancel = (canCancel: boolean) => {
    setLoadingState(prev => ({
      ...prev,
      canCancel,
    }));
  };

  const cancelLoading = () => {
    setLoadingState(prev => ({
      ...prev,
      isLoading: false,
      message: '',
      progress: 0,
      canCancel: false,
    }));
  };

  const contextValue: LoadingContextType = {
    loadingState,
    setLoading,
    setProgress,
    setError,
    clearError,
    setCanCancel,
    cancelLoading,
  };

  return (
    <LoadingContext.Provider value={contextValue}>
      {children}
      {(loadingState.isLoading || loadingState.error) && (
        <LoadingOverlay
          isLoading={loadingState.isLoading}
          message={loadingState.message}
          progress={loadingState.progress}
          error={loadingState.error}
          canCancel={loadingState.canCancel}
          onCancel={cancelLoading}
          onRetry={clearError}
        />
      )}
    </LoadingContext.Provider>
  );
}

interface LoadingOverlayProps {
  isLoading: boolean;
  message?: string;
  progress?: number;
  error?: string;
  canCancel?: boolean;
  onCancel?: () => void;
  onRetry?: () => void;
}

function LoadingOverlay({
  isLoading,
  message,
  progress = 0,
  error,
  canCancel,
  onCancel,
  onRetry,
}: LoadingOverlayProps) {
  if (!isLoading && !error) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardContent className="p-6">
          {error ? (
            // 错误状态
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto">
                <AlertCircle className="w-8 h-8 text-red-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-red-600 mb-2">
                  操作失败
                </h3>
                <p className="text-sm text-gray-600">{error}</p>
              </div>
              <div className="flex gap-2 justify-center">
                <Button onClick={onRetry} variant="default" size="sm">
                  重试
                </Button>
                <Button onClick={onCancel} variant="outline" size="sm">
                  取消
                </Button>
              </div>
            </div>
          ) : (
            // 加载状态
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto">
                <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2">
                  {message || '正在处理...'}
                </h3>
                {progress > 0 && (
                  <div className="space-y-2">
                    <Progress value={progress} className="w-full" />
                    <p className="text-sm text-gray-500">{progress}%</p>
                  </div>
                )}
              </div>
              {canCancel && (
                <Button onClick={onCancel} variant="outline" size="sm">
                  取消
                </Button>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// Hook for using loading context
export function useLoading() {
  const context = useContext(LoadingContext);
  if (context === undefined) {
    throw new Error('useLoading must be used within a LoadingProvider');
  }
  return context;
}

// Hook for async operations with loading states
export function useAsyncOperation() {
  const { setLoading, setProgress, setError, clearError } = useLoading();

  async function executeAsync<T>(
    operation: () => Promise<T>,
    options?: {
      loadingMessage?: string;
      successMessage?: string;
      errorMessage?: string;
      showProgress?: boolean;
      onProgress?: (progress: number) => void;
    }
  ): Promise<T | null> {
    try {
      clearError();
      setLoading(true, options?.loadingMessage || '正在处理...');

      // 如果需要显示进度
      if (options?.showProgress && options?.onProgress) {
        options.onProgress(0);
      }

      const result = await operation();

      if (options?.showProgress) {
        setProgress(100);
        // 短暂显示完成状态
        await new Promise(resolve => setTimeout(resolve, 500));
      }

      setLoading(false);
      
      if (options?.successMessage) {
        // 这里可以集成toast通知
        console.log(options.successMessage);
      }

      return result;
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : options?.errorMessage || '操作失败';
      
      setError(errorMessage);
      return null;
    }
  }

  return { executeAsync };
}

// 简化的加载组件，用于局部加载
export function LoadingSpinner({ 
  size = 'default', 
  message 
}: { 
  size?: 'sm' | 'default' | 'lg'; 
  message?: string; 
}) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    default: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  return (
    <div className="flex items-center justify-center space-x-2">
      <Loader2 className={`${sizeClasses[size]} animate-spin text-blue-600`} />
      {message && (
        <span className="text-sm text-gray-600">{message}</span>
      )}
    </div>
  );
}

// 骨架屏组件
export function SkeletonLoader({ 
  lines = 3, 
  className = '' 
}: { 
  lines?: number; 
  className?: string; 
}) {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="h-4 bg-gray-200 rounded animate-pulse"
          style={{
            width: `${Math.random() * 40 + 60}%`,
          }}
        />
      ))}
    </div>
  );
}