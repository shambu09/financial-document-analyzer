import { useState, useEffect, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { tasksAPI, taskMappingsAPI } from '@/lib/api';
import type { TaskInfo, TaskReportMapping } from '@/types';

interface UseTaskStatusOptions {
  reportId: string;
  enabled?: boolean;
  pollingInterval?: number; // in milliseconds
  reportStatus?: 'pending' | 'in_progress' | 'completed' | 'failed'; // Report status to help determine when to stop polling
  onTaskComplete?: (taskId: string, status: string) => void; // Callback when task completes
}

interface TaskStatusData {
  taskInfo: TaskInfo | null;
  mapping: TaskReportMapping | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useTaskStatus({
  reportId,
  enabled = true,
  pollingInterval = 10000, // 10 seconds
  reportStatus,
  onTaskComplete
}: UseTaskStatusOptions): TaskStatusData {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [shouldPoll, setShouldPoll] = useState(true);

  // Get task mapping for this report
  const {
    data: mappingData,
    isLoading: mappingLoading,
    error: mappingError,
    refetch: refetchMapping
  } = useQuery({
    queryKey: ['task-mapping', reportId],
    queryFn: () => taskMappingsAPI.getByReportId(reportId),
    enabled: enabled && !!reportId,
    retry: 1,
  });

  // Get task status
  const {
    data: taskData,
    isLoading: taskLoading,
    error: taskError,
    refetch: refetchTask
  } = useQuery({
    queryKey: ['task-status', taskId],
    queryFn: () => tasksAPI.getStatus(taskId!),
    enabled: enabled && !!taskId && shouldPoll,
    refetchInterval: shouldPoll ? pollingInterval : false,
    retry: 1,
  });

  // Update taskId when mapping changes
  useEffect(() => {
    if (mappingData?.data?.task_id) {
      setTaskId(mappingData.data.task_id);
    }
  }, [mappingData]);

  // Stop polling when task is completed or failed
  useEffect(() => {
    if (taskData?.data?.status) {
      const status = taskData.data.status;
      console.log(`Task ${taskId} current status: ${status}`);
      if (status === 'completed' || status === 'failed' || status === 'cancelled') {
        console.log(`Task ${taskId} finished with status: ${status}. Stopping polling.`);
        setShouldPoll(false);
        // Call the callback to notify parent component
        if (onTaskComplete && taskId) {
          onTaskComplete(taskId, status);
        }
      }
    }
  }, [taskData, taskId, onTaskComplete]);

  // Stop polling when report status changes to completed or failed
  useEffect(() => {
    if (reportStatus === 'completed' || reportStatus === 'failed') {
      console.log(`Report ${reportId} status changed to: ${reportStatus}. Stopping polling.`);
      setShouldPoll(false);
    }
  }, [reportStatus, reportId]);

  // Reset polling state when taskId changes (new task)
  useEffect(() => {
    if (taskId) {
      console.log(`Starting polling for task ${taskId} (report ${reportId})`);
      setShouldPoll(true);
    }
  }, [taskId, reportId]);

  const refetch = useCallback(() => {
    refetchMapping();
    if (taskId) {
      refetchTask();
    }
  }, [refetchMapping, refetchTask, taskId]);

  return {
    taskInfo: taskData?.data || null,
    mapping: mappingData?.data || null,
    isLoading: mappingLoading || taskLoading,
    error: mappingError?.message || taskError?.message || null,
    refetch,
  };
}

export default useTaskStatus;

