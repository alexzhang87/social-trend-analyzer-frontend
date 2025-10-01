import React from 'react';

interface ProgressProps {
  value?: number;
  max?: number;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'success' | 'warning' | 'error';
}

const Progress: React.FC<ProgressProps> = ({ 
  value = 0, 
  max = 100, 
  className = '', 
  size = 'md',
  variant = 'default'
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  
  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3'
  };
  
  const variantClasses = {
    default: 'bg-blue-500',
    success: 'bg-green-500',
    warning: 'bg-yellow-500',
    error: 'bg-red-500'
  };
  
  return (
    <div className={`w-full bg-gray-200 rounded-full overflow-hidden ${sizeClasses[size]} ${className}`}>
      <div 
        className={`${variantClasses[variant]} ${sizeClasses[size]} rounded-full transition-all duration-300 ease-in-out`}
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
};

export { Progress };
export type { ProgressProps };