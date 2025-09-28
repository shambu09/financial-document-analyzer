// User types
export interface User {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
  is_active?: boolean;
  is_admin?: boolean;
}

export interface UserLogin {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
}

// Document types
export interface DocumentMetadata {
  id: string;
  name: string;
  size_bytes: number;
  modified_at: string;
  path: string;
  download_url: string;
}

// Analysis types
export type ReportStatus = 'pending' | 'in_progress' | 'completed' | 'failed';

export interface AnalysisReport {
  id: string;
  user_id: string;
  document_id: string | null;
  analysis_type: string;
  query: string;
  file_name: string;
  summary: string | null;
  report_path: string;
  status: ReportStatus;
  created_at: string;
  updated_at: string;
  download_url: string | null;
}

export interface ReportContentResponse {
  content: string;
  report_id: string;
}

export interface AnalysisReportListResponse {
  reports: AnalysisReport[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface AnalysisReportUpdate {
  summary?: string;
}

// API Error types
export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}

export interface HTTPValidationError {
  detail: ValidationError[];
}

// Form types
export interface LoginFormData {
  username: string;
  password: string;
}

export interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface ChangePasswordFormData {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

export interface AnalysisFormData {
  file: File | null;
  query: string;
  analysisType: 'comprehensive' | 'investment' | 'risk' | 'verify';
}

// UI State types
export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface DocumentState {
  documents: DocumentMetadata[];
  isLoading: boolean;
  error: string | null;
}

export interface ReportsState {
  reports: AnalysisReport[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
}
