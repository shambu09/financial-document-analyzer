import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useToast } from '@/hooks/use-toast';
import { reportsAPI } from '@/lib/api';
import type { ReportStatus, AnalysisReport } from '@/types';
import { marked } from 'marked';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  FileBarChart, 
  Search, 
  Download, 
  Trash2, 
  Filter,
  CheckCircle,
  Clock,
  AlertCircle,
  Loader2,
  Eye,
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

  const handleDelete = (reportId: string) => {
    if (window.confirm('Are you sure you want to delete this report?')) {
      deleteReportMutation.mutate(reportId);
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

  const getStatusIcon = (status: ReportStatus) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      case 'in_progress':
        return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: ReportStatus) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-50';
      case 'pending':
        return 'text-yellow-600 bg-yellow-50';
      case 'in_progress':
        return 'text-blue-600 bg-blue-50';
      case 'failed':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
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
            <Card key={report.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3 mb-2">
                      <FileBarChart className="h-5 w-5 text-gray-400" />
                      <h3 className="text-lg font-medium text-gray-900 truncate">
                        {report.file_name}
                      </h3>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(report.status)}`}>
                        {getStatusIcon(report.status)}
                        <span className="ml-1 capitalize">{report.status}</span>
                      </span>
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
                      onClick={() => handleDelete(report.id)}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
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
