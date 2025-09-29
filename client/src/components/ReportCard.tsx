import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ProgressIndicator } from '@/components/ui/progress-indicator';
import { useTaskStatus } from '@/hooks/useTaskStatus';
import { marked } from 'marked';
import { useToast } from '@/hooks/use-toast';
import { reportsAPI } from '@/lib/api';
import type { AnalysisReport, ReportStatus } from '@/types';
import { 
  FileBarChart, 
  Download, 
  Trash2, 
  Eye
} from 'lucide-react';

interface ReportCardProps {
  report: AnalysisReport;
  onDelete: (reportId: string) => void;
  onRefetch?: () => void;
  onTaskComplete?: (reportId: string, taskId: string, status: string) => void;
}

export function ReportCard({ report, onDelete, onRefetch, onTaskComplete }: ReportCardProps) {
  const { toast } = useToast();
  
  // Get task status for this report
  // Only poll if report is in progress or pending, and stop when completed or failed
  const shouldPollTask = report.status === 'in_progress' || report.status === 'pending';
  const { taskInfo, isLoading: taskLoading } = useTaskStatus({
    reportId: report.id,
    enabled: shouldPollTask,
    reportStatus: report.status,
    onTaskComplete: (taskId, status) => {
      console.log(`Task completed for report ${report.id}: ${status}`);
      if (onTaskComplete) {
        onTaskComplete(report.id, taskId, status);
      }
      // Don't automatically refetch - let the task status update handle the UI
    }
  });

  const handleDownload = async (reportId: string, filename: string) => {
    try {
      const response = await reportsAPI.download(reportId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Ensure the filename has .md extension
      const downloadFilename = filename.endsWith('.md') ? filename : `${filename}.md`;
      link.setAttribute('download', downloadFilename);
      
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      toast({
        title: 'Error',
        description: 'Failed to download report.',
        variant: 'destructive',
      });
    }
  };

  const handleViewContent = async (reportId: string) => {
    try {
      const response = await reportsAPI.getContent(reportId);
      const content = response.data.content;
      
      // Create a new tab with the markdown content
      const newTab = window.open('', '_blank');
      if (newTab) {
        const htmlContent = marked(content);
        newTab.document.write(`
          <!DOCTYPE html>
          <html>
            <head>
              <title>Analysis Report</title>
              <meta charset="utf-8">
              <style>
                body {
                  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                  max-width: 800px;
                  margin: 0 auto;
                  padding: 20px;
                  line-height: 1.6;
                  color: #333;
                }
                h1, h2, h3, h4, h5, h6 {
                  color: #2c3e50;
                  margin-top: 24px;
                  margin-bottom: 16px;
                }
                pre {
                  background: #f6f8fa;
                  padding: 16px;
                  border-radius: 6px;
                  overflow-x: auto;
                }
                code {
                  background: #f6f8fa;
                  padding: 2px 4px;
                  border-radius: 3px;
                  font-family: 'SFMono-Regular', Consolas, monospace;
                }
                blockquote {
                  border-left: 4px solid #dfe2e5;
                  padding-left: 16px;
                  color: #6a737d;
                }
                table {
                  border-collapse: collapse;
                  width: 100%;
                }
                th, td {
                  border: 1px solid #dfe2e5;
                  padding: 8px 12px;
                  text-align: left;
                }
                th {
                  background: #f6f8fa;
                  font-weight: 600;
                }
              </style>
            </head>
            <body>
              <div id="content">${htmlContent}</div>
            </body>
          </html>
        `);
        newTab.document.close();
      }
    } catch (error: any) {
      toast({
        title: 'Error',
        description: 'Failed to load report content.',
        variant: 'destructive',
      });
    }
  };

  // Calculate progress based on task status
  const getProgress = (): number | undefined => {
    // If we have task info, use that for more accurate status
    if (taskInfo) {
      if (taskInfo.status === 'completed') return 100;
      if (taskInfo.status === 'failed' || taskInfo.status === 'cancelled') return 0;
      if (taskInfo.status === 'in_progress' || taskInfo.status === 'retrying') {
        // For in-progress tasks, show indeterminate progress (undefined)
        // This will show a 30% bar with "Processing..." text
        return undefined;
      }
      if (taskInfo.status === 'pending') return 0;
    }
    
    // Fallback to report status if no task info
    if (report.status === 'completed') return 100;
    if (report.status === 'failed') return 0;
    if (report.status === 'in_progress') return undefined;
    if (report.status === 'pending') return 0;
    
    return 0;
  };

  // Get the appropriate status label
  const getStatusLabel = (): string => {
    // If we have task info, use that for more accurate status
    if (taskInfo) {
      if (taskInfo.status === 'completed') return 'Completed';
      if (taskInfo.status === 'failed') return 'Failed';
      if (taskInfo.status === 'cancelled') return 'Cancelled';
      if (taskInfo.status === 'in_progress') return 'Processing';
      if (taskInfo.status === 'retrying') return 'Retrying';
      if (taskInfo.status === 'pending') return 'Pending';
    }
    
    // Fallback to report status if no task info
    if (report.status === 'completed') return 'Completed';
    if (report.status === 'failed') return 'Failed';
    if (report.status === 'in_progress') return 'In Progress';
    if (report.status === 'pending') return 'Pending';
    
    return 'Unknown';
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-3 mb-2">
              <FileBarChart className="h-5 w-5 text-gray-400" />
              <h3 className="text-lg font-medium text-gray-900 truncate">
                {report.file_name}
              </h3>
            </div>
            
            {/* Progress Indicator */}
            <div className="mb-4">
              <ProgressIndicator
                status={report.status}
                taskStatus={taskInfo?.status}
                progress={getProgress()}
                customStatusText={getStatusLabel()}
                showProgressBar={report.status === 'in_progress' || report.status === 'pending'}
                size="md"
              />
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-gray-600">
              <div>
                <span className="font-medium">Analysis Type:</span>
                <p className="capitalize">{report.analysis_type}</p>
              </div>
              <div>
                <span className="font-medium">Query:</span>
                <p className="truncate">{report.query}</p>
              </div>
              <div>
                <span className="font-medium">Created:</span>
                <p>{new Date(report.created_at).toLocaleDateString()}</p>
              </div>
              <div>
                <span className="font-medium">Updated:</span>
                <p>{new Date(report.updated_at).toLocaleDateString()}</p>
              </div>
            </div>

            {report.summary && (
              <div className="mt-3">
                <span className="font-medium text-sm text-gray-700">Summary:</span>
                <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                  {report.summary}
                </p>
              </div>
            )}

            {/* Task-specific information */}
            {taskInfo && (report.status === 'in_progress' || report.status === 'pending') && (
              <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium">Task ID:</span>
                    <code className="text-xs bg-gray-200 px-1 py-0.5 rounded">
                      {taskInfo.task_id}
                    </code>
                  </div>
                  {taskInfo.worker && (
                    <div className="mt-1">
                      <span className="font-medium">Worker:</span>
                      <span className="ml-1">{taskInfo.worker}</span>
                    </div>
                  )}
                  {taskInfo.queue && (
                    <div className="mt-1">
                      <span className="font-medium">Queue:</span>
                      <span className="ml-1">{taskInfo.queue}</span>
                    </div>
                  )}
                  {taskInfo.retries && taskInfo.retries > 0 && (
                    <div className="mt-1">
                      <span className="font-medium">Retries:</span>
                      <span className="ml-1">{taskInfo.retries}</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="flex items-center space-x-2 ml-4">
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleViewContent(report.id)}
            >
              <Eye className="h-4 w-4 mr-1" />
              View
            </Button>
            {report.status === 'completed' && report.download_url && (
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleDownload(report.id, report.file_name)}
              >
                <Download className="h-4 w-4 mr-1" />
                Download
              </Button>
            )}
            <Button
              size="sm"
              variant="outline"
              onClick={() => onDelete(report.id)}
              className="text-red-600 hover:text-red-700 hover:bg-red-50"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default ReportCard;
