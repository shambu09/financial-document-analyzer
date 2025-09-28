import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/contexts/AuthContext';
import { documentsAPI, reportsAPI } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  FileText, 
  BarChart3, 
  Upload, 
  FileBarChart,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { Link } from 'react-router-dom';
import type { AnalysisReport, DocumentMetadata } from '@/types';

export default function DashboardPage() {
  const { user } = useAuth();

  const { data: documents } = useQuery({
    queryKey: ['documents'],
    queryFn: () => documentsAPI.list(),
  });

  const { data: reports } = useQuery({
    queryKey: ['reports'],
    queryFn: () => reportsAPI.list({ page_size: 5 }),
  });

  const { data: allReports } = useQuery({
    queryKey: ['reports-all'],
    queryFn: () => reportsAPI.list({ page_size: 50 }),
  });

  const { data: stats } = useQuery({
    queryKey: ['reports-stats'],
    queryFn: () => reportsAPI.getStats(),
  });

  const recentDocuments = documents?.data?.slice(0, 5) || [];
  const recentReports = reports?.data?.reports?.slice(0, 5) || [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Welcome back, {user?.username}!</h1>
        <p className="text-gray-600">Here's what's happening with your documents and analysis.</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Documents</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{documents?.data?.length || 0}</div>
            <p className="text-xs text-muted-foreground">
              Documents uploaded
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Analysis Reports</CardTitle>
            <FileBarChart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{allReports?.data?.total || 0}</div>
            <p className="text-xs text-muted-foreground">
              Reports generated
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed Analysis</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {allReports?.data?.reports?.filter((r: AnalysisReport) => r.status === 'completed').length || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Successfully processed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Analysis</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {allReports?.data?.reports?.filter((r: AnalysisReport) => r.status === 'pending' || r.status === 'in_progress').length || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              In progress
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Documents */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Recent Documents</CardTitle>
                <CardDescription>Your latest uploaded files</CardDescription>
              </div>
              <Button asChild variant="outline" size="sm">
                <Link to="/documents">View All</Link>
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {recentDocuments.length > 0 ? (
              <div className="space-y-3">
                {recentDocuments.map((doc: DocumentMetadata) => (
                  <div key={doc.id} className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      <FileText className="h-5 w-5 text-gray-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {doc.name}
                      </p>
                      <p className="text-sm text-gray-500">
                        {(doc.size_bytes / 1024).toFixed(1)} KB
                      </p>
                    </div>
                    <div className="flex-shrink-0">
                      <span className="text-xs text-gray-500">
                        {new Date(doc.modified_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6">
                <FileText className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No documents</h3>
                <p className="mt-1 text-sm text-gray-500">Get started by uploading a document.</p>
                <div className="mt-6">
                  <Button asChild>
                    <Link to="/documents">Upload Document</Link>
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Reports */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Recent Analysis</CardTitle>
                <CardDescription>Your latest analysis reports</CardDescription>
              </div>
              <Button asChild variant="outline" size="sm">
                <Link to="/reports">View All</Link>
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {recentReports.length > 0 ? (
              <div className="space-y-3">
                {recentReports.map((report: AnalysisReport) => (
                  <div key={report.id} className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      {report.status === 'completed' ? (
                        <CheckCircle className="h-5 w-5 text-green-500" />
                      ) : report.status === 'pending' ? (
                        <Clock className="h-5 w-5 text-yellow-500" />
                      ) : (
                        <AlertCircle className="h-5 w-5 text-red-500" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {report.file_name}
                      </p>
                      <p className="text-sm text-gray-500">
                        {report.analysis_type} • {report.status}
                      </p>
                    </div>
                    <div className="flex-shrink-0">
                      <span className="text-xs text-gray-500">
                        {new Date(report.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6">
                <BarChart3 className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No analysis yet</h3>
                <p className="mt-1 text-sm text-gray-500">Start analyzing your documents.</p>
                <div className="mt-6">
                  <Button asChild>
                    <Link to="/analysis">Start Analysis</Link>
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common tasks to get you started</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Button asChild variant="outline" className="h-20 flex-col">
              <Link to="/documents">
                <Upload className="h-6 w-6 mb-2" />
                Upload Document
              </Link>
            </Button>
            <Button asChild variant="outline" className="h-20 flex-col">
              <Link to="/analysis">
                <BarChart3 className="h-6 w-6 mb-2" />
                Analyze Document
              </Link>
            </Button>
            <Button asChild variant="outline" className="h-20 flex-col">
              <Link to="/reports">
                <FileBarChart className="h-6 w-6 mb-2" />
                View Reports
              </Link>
            </Button>
            <Button asChild variant="outline" className="h-20 flex-col">
              <Link to="/profile">
                <TrendingUp className="h-6 w-6 mb-2" />
                View Profile
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
