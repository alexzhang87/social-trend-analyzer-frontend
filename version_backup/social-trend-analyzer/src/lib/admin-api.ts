// File scope: adminApiClient (using environment variables for unified backend address)
import axios from 'axios';

const API_BASE_URL = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'}/api/v1`;

// Create axios instance
const adminApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add authentication token
adminApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admin_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors
adminApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('admin_token');
      window.location.href = '/admin/login';
    }
    return Promise.reject(error);
  }
);

// API interface definitions
// File scope: export adminApiClient object, add credits adjustment method
export const adminApiClient = {
  // User management
  users: {
    getAll: (params?: { skip?: number; limit?: number; search?: string; role?: string; subscription_tier?: string; is_active?: boolean }) => 
      adminApi.get('/admin/users', { params }),
    getById: (id: number) => adminApi.get(`/admin/users/${id}`),
    create: (userData: any) => adminApi.post('/admin/users', userData),
    update: (id: number, userData: any) => adminApi.put(`/admin/users/${id}`, userData),
    delete: (id: number) => adminApi.delete(`/admin/users/${id}`),
    getUsage: (id: number) => adminApi.get(`/admin/users/${id}/usage`),
  },
  
  // System statistics
  stats: {
    getSystem: () => adminApi.get('/admin/stats'),
    getDetailed: (days?: number) => adminApi.get('/admin/stats/detailed', { params: { days } }),
    getActivity: (days?: number) => adminApi.get('/admin/stats/activity', { params: { days } }),
  },
  
  // Subscription management
  subscriptions: {
    getPlans: () => adminApi.get('/admin/subscription-plans'),
    getAnalysis: () => adminApi.get('/admin/subscriptions/analysis'),
    batchUpdate: (data: any) => adminApi.post('/admin/subscriptions/batch-update', data),
    getLogs: (days?: number, action?: string) => adminApi.get('/admin/subscriptions/logs', { params: { days, action } }),
  },
  
  // System configuration
  config: {
    get: () => adminApi.get('/admin/config'),
    healthCheck: () => adminApi.get('/admin/health'),
  },
  // New: Admin credits adjustment
  credits: {
    adjustByUserId: (id: number, data: { amount: number; description?: string }) =>
      adminApi.post(`/admin/users/${id}/credits/adjust`, data),
    adjustByEmail: (email: string, data: { amount: number; description?: string }) =>
      adminApi.post(`/admin/users/by-email/${encodeURIComponent(email)}/credits/adjust`, data),
  },
};

export default adminApi;