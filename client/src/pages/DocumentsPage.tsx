import { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import { documentsAPI, analysisAPI } from '@/lib/api';
import type { DocumentMetadata } from '@/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Upload, 
  Search, 
  FileText, 
  Download, 
  Trash2, 
  Plus,
  Loader2,
  AlertCircle,
  BarChart3,
  TrendingUp,
  Shield,
  CheckCircle,
  MoreVertical
} from 'lucide-react';

export default function DocumentsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [customFileName, setCustomFileName] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [showAnalysisMenu, setShowAnalysisMenu] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const { data: documents, isLoading } = useQuery({
    queryKey: ['documents', searchQuery],
    queryFn: () => documentsAPI.list(searchQuery || undefined),
  });

  const deleteDocumentMutation = useMutation({
    mutationFn: documentsAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      toast({
        title: 'Success',
        description: 'Document deleted successfully.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to delete document.',
        variant: 'destructive',
      });
    },
  });

  const uploadDocumentMutation = useMutation({
    mutationFn: ({ file, name }: { file: File; name: string }) => documentsAPI.upload(file, name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      toast({
        title: 'Success',
        description: 'Document uploaded successfully.',
      });
      setIsUploading(false);
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to upload document.',
        variant: 'destructive',
      });
      setIsUploading(false);
    },
  });

  const analysisMutation = useMutation({
    mutationFn: async ({ documentId, analysisType, query }: { documentId: string; analysisType: string; query: string }) => {
      switch (analysisType) {
        case 'comprehensive':
          return analysisAPI.comprehensive(undefined, query, documentId);
        case 'investment':
          return analysisAPI.investment(undefined, query, documentId);
        case 'risk':
          return analysisAPI.risk(undefined, query, documentId);
        case 'verify':
          return analysisAPI.verify(undefined, query, documentId);
        default:
          throw new Error('Invalid analysis type');
      }
    },
    onSuccess: (response) => {
      const report = response.data;
      queryClient.invalidateQueries({ queryKey: ['reports'] });
      queryClient.invalidateQueries({ queryKey: ['reports-all'] });
      toast({
        title: 'Analysis Started',
        description: `Your document analysis has been initiated with status: ${report.status}. Redirecting to reports...`,
      });
      setShowAnalysisMenu(null);
      setTimeout(() => {
        navigate('/reports');
      }, 2000);
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to start analysis.',
        variant: 'destructive',
      });
    },
  });

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);
    setCustomFileName(file.name);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    try {
      await uploadDocumentMutation.mutateAsync({ 
        file: selectedFile, 
        name: customFileName || selectedFile.name 
      });
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      setSelectedFile(null);
      setCustomFileName('');
    } catch (error) {
      // Error is handled by the mutation
    }
  };

  const handleDownload = async (filename: string) => {
    try {
      const response = await documentsAPI.download(filename);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      toast({
        title: 'Error',
        description: 'Failed to download document.',
        variant: 'destructive',
      });
    }
  };

  const handleDelete = (documentId: string) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      deleteDocumentMutation.mutate(documentId);
    }
  };

  const handleQuickAnalysis = (documentId: string, analysisType: string) => {
    const defaultQueries = {
      comprehensive: 'Analyze this financial document for comprehensive insights',
      investment: 'Analyze this financial document for investment opportunities',
      risk: 'Analyze this financial document for risk assessment',
      verify: 'Verify if this is a valid financial document'
    };
    
    analysisMutation.mutate({
      documentId,
      analysisType,
      query: defaultQueries[analysisType as keyof typeof defaultQueries]
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Close analysis menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (showAnalysisMenu && !(event.target as Element).closest('.analysis-menu')) {
        setShowAnalysisMenu(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showAnalysisMenu]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
          <p className="text-gray-600">Manage your uploaded documents</p>
        </div>
        <div className="flex items-center space-x-4">
          <Button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
          >
            <Plus className="mr-2 h-4 w-4" />
            Select Document
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileUpload}
            className="hidden"
            accept=".pdf,.txt"
          />
        </div>
      </div>

      {/* Search */}
      <div className="flex items-center space-x-2">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search documents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* File Upload Section */}
      {selectedFile && (
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <FileText className="h-8 w-8 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">{selectedFile.name}</p>
                  <p className="text-sm text-gray-500">
                    {(selectedFile.size / 1024).toFixed(1)} KB
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Input
                  placeholder="Custom file name (optional)"
                  value={customFileName}
                  onChange={(e) => setCustomFileName(e.target.value)}
                  className="w-64"
                />
                <Button
                  onClick={handleUpload}
                  disabled={isUploading}
                >
                  {isUploading ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Upload className="mr-2 h-4 w-4" />
                  )}
                  {isUploading ? 'Uploading...' : 'Upload'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setSelectedFile(null);
                    setCustomFileName('');
                    if (fileInputRef.current) {
                      fileInputRef.current.value = '';
                    }
                  }}
                >
                  Cancel
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Documents Grid */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      ) : documents?.data && documents.data.length > 0 ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {documents.data.map((doc: DocumentMetadata) => (
            <Card key={doc.id} className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-2">
                    <FileText className="h-5 w-5 text-gray-400" />
                    <CardTitle className="text-sm font-medium truncate">
                      {doc.name}
                    </CardTitle>
                  </div>
                </div>
                <CardDescription className="text-xs">
                  {formatFileSize(doc.size_bytes)} • {new Date(doc.modified_at).toLocaleDateString()}
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="flex items-center justify-between gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleDownload(doc.name)}
                    className="flex-1"
                  >
                    <Download className="h-4 w-4 mr-1" />
                    Download
                  </Button>
                  
                  {/* Analysis Dropdown */}
                  <div className="relative analysis-menu">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setShowAnalysisMenu(showAnalysisMenu === doc.id ? null : doc.id)}
                      disabled={analysisMutation.isPending}
                      className="px-2"
                    >
                      {analysisMutation.isPending ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <MoreVertical className="h-4 w-4" />
                      )}
                    </Button>
                    
                    {showAnalysisMenu === doc.id && (
                      <div className="absolute right-0 top-full mt-2 w-56 bg-white border border-gray-200 rounded-lg shadow-xl z-20">
                        <div className="py-2">
                          <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide border-b border-gray-100">
                            Quick Analysis
                          </div>
                          <button
                            onClick={() => handleQuickAnalysis(doc.id, 'comprehensive')}
                            className="flex items-center w-full px-4 py-3 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-700 transition-colors"
                          >
                            <BarChart3 className="h-4 w-4 mr-3 text-blue-600" />
                            <div className="text-left">
                              <div className="font-medium">Comprehensive Analysis</div>
                              <div className="text-xs text-gray-500">Complete financial insights</div>
                            </div>
                          </button>
                          <button
                            onClick={() => handleQuickAnalysis(doc.id, 'investment')}
                            className="flex items-center w-full px-4 py-3 text-sm text-gray-700 hover:bg-green-50 hover:text-green-700 transition-colors"
                          >
                            <TrendingUp className="h-4 w-4 mr-3 text-green-600" />
                            <div className="text-left">
                              <div className="font-medium">Investment Analysis</div>
                              <div className="text-xs text-gray-500">Investment opportunities</div>
                            </div>
                          </button>
                          <button
                            onClick={() => handleQuickAnalysis(doc.id, 'risk')}
                            className="flex items-center w-full px-4 py-3 text-sm text-gray-700 hover:bg-red-50 hover:text-red-700 transition-colors"
                          >
                            <Shield className="h-4 w-4 mr-3 text-red-600" />
                            <div className="text-left">
                              <div className="font-medium">Risk Assessment</div>
                              <div className="text-xs text-gray-500">Risk evaluation</div>
                            </div>
                          </button>
                          <button
                            onClick={() => handleQuickAnalysis(doc.id, 'verify')}
                            className="flex items-center w-full px-4 py-3 text-sm text-gray-700 hover:bg-purple-50 hover:text-purple-700 transition-colors"
                          >
                            <CheckCircle className="h-4 w-4 mr-3 text-purple-600" />
                            <div className="text-left">
                              <div className="font-medium">Document Verification</div>
                              <div className="text-xs text-gray-500">Validate financial record</div>
                            </div>
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleDelete(doc.id)}
                    className="text-red-600 hover:text-red-700 hover:bg-red-50 px-2"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <FileText className="h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No documents found</h3>
            <p className="text-gray-500 text-center mb-6">
              {searchQuery 
                ? 'No documents match your search criteria.'
                : 'Get started by uploading your first document.'
              }
            </p>
            <Button
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload className="mr-2 h-4 w-4" />
              Select Document
            </Button>
            <input
              ref={fileInputRef}
              type="file"
              onChange={handleFileUpload}
              className="hidden"
              accept=".pdf,.txt"
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
