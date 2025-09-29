import { CheckCircle, Clock, Loader2, XCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface ProgressIndicatorProps {
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  taskStatus?: 'pending' | 'in_progress' | 'completed' | 'failed' | 'retrying' | 'cancelled';
  progress?: number; // 0-100
  className?: string;
  showProgressBar?: boolean;
  size?: 'sm' | 'md' | 'lg';
  customStatusText?: string; // Override the default status text
}

export function ProgressIndicator({
  status,
  taskStatus,
  progress,
  className,
  showProgressBar = true,
  size = 'md',
  customStatusText
}: ProgressIndicatorProps) {
  const getStatusIcon = () => {
    if (status === 'completed' || taskStatus === 'completed') {
      return <CheckCircle className={cn("text-green-500", size === 'sm' ? 'h-4 w-4' : size === 'lg' ? 'h-6 w-6' : 'h-5 w-5')} />;
    }
    if (status === 'failed' || taskStatus === 'failed' || taskStatus === 'cancelled') {
      return <XCircle className={cn("text-red-500", size === 'sm' ? 'h-4 w-4' : size === 'lg' ? 'h-6 w-6' : 'h-5 w-5')} />;
    }
    if (status === 'in_progress' || taskStatus === 'in_progress' || taskStatus === 'retrying') {
      return <Loader2 className={cn("text-blue-500 animate-spin", size === 'sm' ? 'h-4 w-4' : size === 'lg' ? 'h-6 w-6' : 'h-5 w-5')} />;
    }
    return <Clock className={cn("text-yellow-500", size === 'sm' ? 'h-4 w-4' : size === 'lg' ? 'h-6 w-6' : 'h-5 w-5')} />;
  };

  const getStatusText = () => {
    // Use custom status text if provided
    if (customStatusText) {
      return customStatusText;
    }
    
    if (status === 'completed' || taskStatus === 'completed') {
      return 'Completed';
    }
    if (status === 'failed' || taskStatus === 'failed') {
      return 'Failed';
    }
    if (taskStatus === 'cancelled') {
      return 'Cancelled';
    }
    if (status === 'in_progress' || taskStatus === 'in_progress') {
      return 'In Progress';
    }
    if (taskStatus === 'retrying') {
      return 'Retrying';
    }
    return 'Pending';
  };

  const getStatusColor = () => {
    if (status === 'completed' || taskStatus === 'completed') {
      return 'text-green-600 bg-green-50 border-green-200';
    }
    if (status === 'failed' || taskStatus === 'failed' || taskStatus === 'cancelled') {
      return 'text-red-600 bg-red-50 border-red-200';
    }
    if (status === 'in_progress' || taskStatus === 'in_progress' || taskStatus === 'retrying') {
      return 'text-blue-600 bg-blue-50 border-blue-200';
    }
    return 'text-yellow-600 bg-yellow-50 border-yellow-200';
  };

  const getProgressColor = () => {
    if (status === 'completed' || taskStatus === 'completed') {
      return 'bg-green-500';
    }
    if (status === 'failed' || taskStatus === 'failed' || taskStatus === 'cancelled') {
      return 'bg-red-500';
    }
    return 'bg-blue-500';
  };

  const isInProgress = status === 'in_progress' || taskStatus === 'in_progress' || taskStatus === 'retrying';
  const isCompleted = status === 'completed' || taskStatus === 'completed';

  return (
    <div className={cn("flex items-center space-x-2", className)}>
      <div className="flex items-center space-x-2">
        {getStatusIcon()}
        <span className={cn(
          "text-sm font-medium px-2 py-1 rounded-full border",
          getStatusColor()
        )}>
          {getStatusText()}
        </span>
      </div>
      
      {showProgressBar && (isInProgress || isCompleted) && (
        <div className="flex-1 min-w-0">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={cn(
                "h-2 rounded-full transition-all duration-300",
                getProgressColor()
              )}
              style={{
                width: isCompleted ? '100%' : (progress !== undefined ? `${Math.min(100, Math.max(0, progress))}%` : '30%')
              }}
            />
          </div>
          {isCompleted ? (
            <div className="text-xs text-gray-500 mt-1">100%</div>
          ) : progress !== undefined ? (
            <div className="text-xs text-gray-500 mt-1">
              {Math.round(progress)}%
            </div>
          ) : (
            <div className="text-xs text-gray-500 mt-1">
              Processing...
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default ProgressIndicator;
