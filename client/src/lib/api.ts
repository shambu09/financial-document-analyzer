import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          
          const { access_token, refresh_token: newRefreshToken } = response.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', newRefreshToken);
          
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials: { username: string; password: string }) =>
    api.post('/auth/login', credentials),
  register: (userData: { username: string; email: string; password: string }) =>
    api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  getCurrentUser: () => api.get('/auth/me'),
  updateUser: (data: { username?: string; email?: string }) =>
    api.put('/auth/me', data),
  changePassword: (data: { current_password: string; new_password: string }) =>
    api.post('/auth/change-password', data),
};

// Documents API
export const documentsAPI = {
  list: (searchQuery?: string) =>
    api.get('/documents/', { params: { q: searchQuery } }),
  upload: (file: File, name?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (name) formData.append('name', name);
    return api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  download: (filename: string) =>
    api.get(`/documents/download/${filename}`, { responseType: 'blob' }),
  delete: (documentId: string) => api.delete(`/documents/${documentId}`),
};

// Analysis API
export const analysisAPI = {
  comprehensive: (file?: File, query?: string, documentId?: string) => {
    const formData = new FormData();
    if (file) formData.append('file', file);
    if (query) formData.append('query', query);
    if (documentId) formData.append('document_id', documentId);
    return api.post('/analysis/comprehensive', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  investment: (file?: File, query?: string, documentId?: string) => {
    const formData = new FormData();
    if (file) formData.append('file', file);
    if (query) formData.append('query', query);
    if (documentId) formData.append('document_id', documentId);
    return api.post('/analysis/investment', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  risk: (file?: File, query?: string, documentId?: string) => {
    const formData = new FormData();
    if (file) formData.append('file', file);
    if (query) formData.append('query', query);
    if (documentId) formData.append('document_id', documentId);
    return api.post('/analysis/risk', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  verify: (file?: File, query?: string, documentId?: string) => {
    const formData = new FormData();
    if (file) formData.append('file', file);
    if (query) formData.append('query', query);
    if (documentId) formData.append('document_id', documentId);
    return api.post('/analysis/verify', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getTypes: () => api.get('/analysis/types'),
};

// Reports API
export const reportsAPI = {
  list: (params?: {
    analysis_type?: string;
    search_query?: string;
    page?: number;
    page_size?: number;
  }) => api.get('/reports/', { params }),
  get: (reportId: string) => api.get(`/reports/${reportId}`),
  update: (reportId: string, data: { summary?: string }) =>
    api.put(`/reports/${reportId}`, data),
  delete: (reportId: string) => api.delete(`/reports/${reportId}`),
  download: (reportId: string) =>
    api.get(`/reports/${reportId}/download`, { responseType: 'blob' }),
  getContent: (reportId: string) => api.get(`/reports/${reportId}/content`),
  getStats: () => api.get('/reports/stats/summary'),
};

// Tasks API
export const tasksAPI = {
  getStatus: (taskId: string) => api.get(`/tasks/${taskId}/status`),
  cancel: (taskId: string) => api.post(`/tasks/${taskId}/cancel`),
  getActive: () => api.get('/tasks/active'),
  getStats: () => api.get('/tasks/stats'),
  getQueueInfo: () => api.get('/tasks/queues'),
};

// Task Mappings API
export const taskMappingsAPI = {
  getByTaskId: (taskId: string) => api.get(`/task-mappings/by-task/${taskId}`),
  getByReportId: (reportId: string) => api.get(`/task-mappings/by-report/${reportId}`),
  getUserMappings: (params?: { page?: number; page_size?: number }) =>
    api.get('/task-mappings/', { params }),
  deleteByTaskId: (taskId: string) => api.delete(`/task-mappings/by-task/${taskId}`),
  deleteByReportId: (reportId: string) => api.delete(`/task-mappings/by-report/${reportId}`),
  cleanup: (daysOld?: number) => api.post('/task-mappings/cleanup', null, { params: { days_old: daysOld } }),
};
