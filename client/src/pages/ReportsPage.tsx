import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useToast } from '@/hooks/use-toast';
import { reportsAPI } from '@/lib/api';
import type { ReportStatus, AnalysisReport } from '@/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { ReportCard } from '@/components/ReportCard';
import { 
  FileBarChart, 
  Search, 
  Loader2,
  RefreshCw
} from 'lucide-react';

export default function ReportsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [analysisTypeFilter, setAnalysisTypeFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: reports, isLoading, refetch } = useQuery({
    queryKey: ['reports', searchQuery, analysisTypeFilter, currentPage],
    queryFn: () => reportsAPI.list({
      search_query: searchQuery || undefined,
      analysis_type: analysisTypeFilter || undefined,
      page: currentPage,
      page_size: pageSize,
    }),
  });

  const deleteReportMutation = useMutation({
    mutationFn: reportsAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] });
      toast({
        title: 'Success',
        description: 'Report deleted successfully.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to delete report.',
        variant: 'destructive',
      });
    },
  });

  const handleDelete = (reportId: string) => {
    if (window.confirm('Are you sure you want to delete this report?')) {
      deleteReportMutation.mutate(reportId);
    }
  };

  const handleTaskComplete = (reportId: string, taskId: string, status: string) => {
    console.log(`Task ${taskId} completed for report ${reportId} with status: ${status}`);
    // Don't automatically refetch - the task status will update the UI
    // The progress indicator will show the updated status from the task info
  };

  const analysisTypes = [
    { value: '', label: 'All Types' },
    { value: 'comprehensive', label: 'Comprehensive' },
    { value: 'investment', label: 'Investment' },
    { value: 'risk', label: 'Risk Assessment' },
    { value: 'verify', label: 'Verification' },
  ];

  const totalPages = reports?.data?.total_pages || 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analysis Reports</h1>
          <p className="text-gray-600">View and manage your document analysis reports</p>
        </div>
        <Button
          onClick={() => refetch()}
          disabled={isLoading}
          variant="outline"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col space-y-4 sm:flex-row sm:space-y-0 sm:space-x-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search reports..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="sm:w-48">
              <select
                value={analysisTypeFilter}
                onChange={(e) => setAnalysisTypeFilter(e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              >
                {analysisTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Reports List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      ) : reports?.data?.reports?.length > 0 ? (
        <div className="space-y-4">
          {reports?.data?.reports?.map((report: AnalysisReport) => (
            <ReportCard
              key={report.id}
              report={report}
              onDelete={handleDelete}
              onRefetch={refetch}
              onTaskComplete={handleTaskComplete}
            />
          ))}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between pt-6">
              <div className="text-sm text-gray-700">
                Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, reports?.data?.total || 0)} of {reports?.data?.total || 0} results
              </div>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                  disabled={currentPage === 1}
                >
                  Previous
                </Button>
                <span className="text-sm text-gray-700">
                  Page {currentPage} of {totalPages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                  disabled={currentPage === totalPages}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </div>
      ) : (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <FileBarChart className="h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No reports found</h3>
            <p className="text-gray-500 text-center mb-6">
              {searchQuery || analysisTypeFilter
                ? 'No reports match your search criteria.'
                : 'You haven\'t generated any analysis reports yet.'
              }
            </p>
            <Button asChild>
              <a href="/analysis">Start Analysis</a>
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
