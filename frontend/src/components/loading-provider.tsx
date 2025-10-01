import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import { Loader2, X } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';

interface LoadingState {
  isLoading: boolean;
  message?: string;
  progress?: number;
  canCancel?: boolean;
  onCancel?: () => void;
}

interface LoadingContextType {
  loadingState: LoadingState;
  setLoading: (loading: boolean, options?: Partial<LoadingState>) => void;
  setProgress: (progress: number) => void;
  setMessage: (message: string) => void;
  clearLoading: () => void;
}

const LoadingContext = createContext<LoadingContextType | undefined>(undefined);

interface LoadingProviderProps {
  children: ReactNode;
}

export function LoadingProvider({ children }: LoadingProviderProps) {
  const [loadingState, setLoadingState] = useState<LoadingState>({
    isLoading: false,
  });

  const setLoading = useCallback((loading: boolean, options?: Partial<LoadingState>) => {
    setLoadingState(prev => ({
      ...prev,
      isLoading: loading,
      ...options,
    }));
  }, []);

  const setProgress = useCallback((progress: number) => {
    setLoadingState(prev => ({
      ...prev,
      progress: Math.max(0, Math.min(100, progress)),
    }));
  }, []);

  const setMessage = useCallback((message: string) => {
    setLoadingState(prev => ({
      ...prev,
      message,
    }));
  }, []);

  const clearLoading = useCallback(() => {
    setLoadingState({
      isLoading: false,
    });
  }, []);

  const value: LoadingContextType = {
    loadingState,
    setLoading,
    setProgress,
    setMessage,
    clearLoading,
  };

  return (
    <LoadingContext.Provider value={value}>
      {children}
      {loadingState.isLoading && <LoadingOverlay />}
    </LoadingContext.Provider>
  );
}

function LoadingOverlay() {
  const { loadingState } = useLoading();

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardContent className="p-6">
          <div className="flex flex-col items-center space-y-4">
            {/* Loading spinner */}
            <div className="relative">
              <Loader2 className="w-12 h-12 animate-spin text-blue-600" />
            </div>

            {/* Loading message */}
            {loadingState.message && (
              <p className="text-center text-gray-700 font-medium">
                {loadingState.message}
              </p>
            )}

            {/* Progress bar */}
            {typeof loadingState.progress === 'number' && (
              <div className="w-full space-y-2">
                <Progress value={loadingState.progress} className="w-full" />
                <p className="text-sm text-gray-500 text-center">
                  {Math.round(loadingState.progress)}%
                </p>
              </div>
            )}

            {/* Cancel button */}
            {loadingState.canCancel && loadingState.onCancel && (
              <Button
                variant="outline"
                size="sm"
                onClick={loadingState.onCancel}
                className="mt-4"
              >
                <X className="w-4 h-4 mr-2" />
                Cancel
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Hook to use loading context
export function useLoading() {
  const context = useContext(LoadingContext);
  if (context === undefined) {
    throw new Error('useLoading must be used within a LoadingProvider');
  }
  return context;
}

// Hook for async operations with loading states
export function useAsyncOperation() {
  const { setLoading, setProgress, setMessage, clearLoading } = useLoading();

  const executeAsync = useCallback(async <T>(
    operation: () => Promise<T>,
    options?: {
      loadingMessage?: string;
      showProgress?: boolean;
      successMessage?: string;
      errorMessage?: string;
      canCancel?: boolean;
    }
  ): Promise<T> => {
    let cancelled = false;
    
    const onCancel = options?.canCancel ? () => {
      cancelled = true;
      clearLoading();
    } : undefined;

    try {
      setLoading(true, {
        message: options?.loadingMessage || 'Loading...',
        progress: options?.showProgress ? 0 : undefined,
        canCancel: options?.canCancel,
        onCancel,
      });

      if (options?.showProgress) {
        // Simulate progress for operations without real progress tracking
        const progressInterval = setInterval(() => {
          if (cancelled) {
            clearInterval(progressInterval);
            return;
          }
          setProgress(prev => Math.min(90, (prev || 0) + Math.random() * 20));
        }, 200);

        const result = await operation();
        
        clearInterval(progressInterval);
        if (!cancelled) {
          setProgress(100);
          if (options?.successMessage) {
            setMessage(options.successMessage);
            await new Promise(resolve => setTimeout(resolve, 1000));
          }
        }
        
        return result;
      } else {
        return await operation();
      }
    } catch (error) {
      if (!cancelled) {
        if (options?.errorMessage) {
          setMessage(options.errorMessage);
          await new Promise(resolve => setTimeout(resolve, 2000));
        }
      }
      throw error;
    } finally {
      if (!cancelled) {
        clearLoading();
      }
    }
  }, [setLoading, setProgress, setMessage, clearLoading]);

  return { executeAsync };
}

// Simple loading component for local use
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

// Skeleton loader component
export function SkeletonLoader({ 
  lines = 3, 
  className = '' 
}: { 
  lines?: number; 
  className?: string; 
}) {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: lines }).map((_, index) => (
        <div
          key={index}
          className="h-4 bg-gray-200 rounded animate-pulse"
          style={{
            width: `${Math.random() * 40 + 60}%`,
          }}
        />
      ))}
    </div>
  );
}

export default LoadingProvider;
