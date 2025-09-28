import { useState, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import { analysisAPI, documentsAPI } from '@/lib/api';
import type { DocumentMetadata } from '@/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Upload, 
  FileText, 
  BarChart3, 
  TrendingUp, 
  Shield, 
  CheckCircle,
  Loader2,
  AlertCircle
} from 'lucide-react';

const analysisSchema = z.object({
  file: z.any().refine((file) => file instanceof File, 'Please select a file'),
  query: z.string().min(1, 'Query is required'),
  analysisType: z.enum(['comprehensive', 'investment', 'risk', 'verify']),
});

type AnalysisFormData = z.infer<typeof analysisSchema>;

const analysisTypes = [
  {
    id: 'comprehensive',
    name: 'Comprehensive Analysis',
    description: 'Complete financial document analysis with detailed insights',
    icon: BarChart3,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
  },
  {
    id: 'investment',
    name: 'Investment Analysis',
    description: 'Focus on investment opportunities and recommendations',
    icon: TrendingUp,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
  },
  {
    id: 'risk',
    name: 'Risk Assessment',
    description: 'Evaluate potential risks and mitigation strategies',
    icon: Shield,
    color: 'text-red-600',
    bgColor: 'bg-red-50',
  },
  {
    id: 'verify',
    name: 'Document Verification',
    description: 'Verify if the document is a valid financial record',
    icon: CheckCircle,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
  },
];

export default function AnalysisPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: documents } = useQuery({
    queryKey: ['documents'],
    queryFn: () => documentsAPI.list(),
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm<AnalysisFormData>({
    resolver: zodResolver(analysisSchema),
    defaultValues: {
      analysisType: 'comprehensive',
      query: 'Analyze this financial document for comprehensive insights',
    },
  });

  const analysisMutation = useMutation({
    mutationFn: async (data: AnalysisFormData) => {
      switch (data.analysisType) {
        case 'comprehensive':
          return analysisAPI.comprehensive(data.file, data.query);
        case 'investment':
          return analysisAPI.investment(data.file, data.query);
        case 'risk':
          return analysisAPI.risk(data.file, data.query);
        case 'verify':
          return analysisAPI.verify(data.file, data.query);
        default:
          throw new Error('Invalid analysis type');
      }
    },
    onSuccess: (response) => {
      const report = response.data;
      toast({
        title: 'Analysis Started',
        description: `Your document analysis has been initiated with status: ${report.status}. Redirecting to reports...`,
      });
      // Invalidate reports queries to refresh the list
      queryClient.invalidateQueries({ queryKey: ['reports'] });
      queryClient.invalidateQueries({ queryKey: ['reports-all'] });
      // Reset form
      setSelectedFile(null);
      setValue('file', null);
      setValue('query', '');
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      // Redirect to reports page
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

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setValue('file', file);
    }
  };

  const onSubmit = (data: AnalysisFormData) => {
    analysisMutation.mutate(data);
  };

  const selectedAnalysisType = watch('analysisType');
  const selectedTypeInfo = analysisTypes.find(type => type.id === selectedAnalysisType);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Document Analysis</h1>
        <p className="text-gray-600">Upload a document and get AI-powered financial analysis</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Analysis Form */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Start New Analysis</CardTitle>
              <CardDescription>
                Upload a financial document and choose the type of analysis you need
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                {/* File Upload */}
                <div>
                  <Label htmlFor="file">Document File</Label>
                  <div className="mt-2">
                    <input
                      ref={fileInputRef}
                      type="file"
                      onChange={handleFileSelect}
                      accept=".pdf,.doc,.docx,.txt,.xlsx,.xls"
                      className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-primary-foreground hover:file:bg-primary/90"
                    />
                    {errors.file && (
                      <p className="mt-1 text-sm text-red-600">{errors.file.message as string}</p>
                    )}
                    {selectedFile && (
                      <div className="mt-2 flex items-center space-x-2 text-sm text-gray-600">
                        <FileText className="h-4 w-4" />
                        <span>{selectedFile.name}</span>
                        <span>({(selectedFile.size / 1024).toFixed(1)} KB)</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Analysis Type */}
                <div>
                  <Label>Analysis Type</Label>
                  <div className="mt-2 grid grid-cols-1 gap-3 sm:grid-cols-2">
                    {analysisTypes.map((type) => {
                      const Icon = type.icon;
                      return (
                        <label
                          key={type.id}
                          className={`relative flex cursor-pointer rounded-lg p-4 focus:outline-none ${
                            selectedAnalysisType === type.id
                              ? 'ring-2 ring-primary ring-offset-2'
                              : 'ring-1 ring-gray-300'
                          }`}
                        >
                          <input
                            type="radio"
                            value={type.id}
                            {...register('analysisType')}
                            className="sr-only"
                          />
                          <div className="flex items-center">
                            <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${type.bgColor}`}>
                              <Icon className={`h-6 w-6 ${type.color}`} />
                            </div>
                            <div className="ml-3">
                              <p className="text-sm font-medium text-gray-900">{type.name}</p>
                              <p className="text-xs text-gray-500">{type.description}</p>
                            </div>
                          </div>
                        </label>
                      );
                    })}
                  </div>
                </div>

                {/* Query */}
                <div>
                  <Label htmlFor="query">Analysis Query</Label>
                  <Input
                    id="query"
                    {...register('query')}
                    placeholder="Enter your specific analysis requirements..."
                    className={errors.query ? 'border-red-500' : ''}
                  />
                  {errors.query && (
                    <p className="mt-1 text-sm text-red-600">{errors.query.message}</p>
                  )}
                </div>

                <Button
                  type="submit"
                  disabled={analysisMutation.isPending || !selectedFile}
                  className="w-full"
                >
                  {analysisMutation.isPending ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <BarChart3 className="mr-2 h-4 w-4" />
                  )}
                  {analysisMutation.isPending ? 'Starting Analysis...' : 'Start Analysis'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Analysis Type Info */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Analysis Information</CardTitle>
            </CardHeader>
            <CardContent>
              {selectedTypeInfo && (
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${selectedTypeInfo.bgColor}`}>
                      <selectedTypeInfo.icon className={`h-6 w-6 ${selectedTypeInfo.color}`} />
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">{selectedTypeInfo.name}</h3>
                      <p className="text-sm text-gray-500">{selectedTypeInfo.description}</p>
                    </div>
                  </div>
                  
                  <div className="space-y-2 text-sm text-gray-600">
                    <p>• Upload supported file formats: PDF and text</p>
                    <p>• Analysis typically takes 2-5 minutes</p>
                    <p>• Results will appear in your reports</p>
                    <p>• You can track progress in real-time</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recent Documents */}
          {documents?.data && documents.data.length > 0 && (
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Recent Documents</CardTitle>
                <CardDescription>Quick access to your uploaded files</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {documents.data.slice(0, 3).map((doc: DocumentMetadata) => (
                    <div key={doc.id} className="flex items-center space-x-2 text-sm">
                      <FileText className="h-4 w-4 text-gray-400" />
                      <span className="truncate">{doc.name}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
