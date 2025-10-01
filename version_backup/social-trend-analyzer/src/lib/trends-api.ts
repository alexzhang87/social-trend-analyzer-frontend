import axios from 'axios';
import { authStorage } from './auth-api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

// Create axios instance for trends API
const trendsApi = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/trends`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add authentication token
trendsApi.interceptors.request.use(
  (config) => {
    const token = authStorage.getToken();
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
trendsApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      authStorage.clearAuth();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Type definitions
export interface ComprehensiveAnalysisRequest {
  keywords: string[];
  platforms: string[];
  time_filter: string;
  limit_per_platform?: number;
}

export interface KeyTheme {
  theme: string;
  summary: string;
  isEmerging: boolean;
}

export interface UserPersona {
  name: string;
  percentage: number;
  characteristics: string[];
}

export interface ActionableOpportunity {
  opportunity: string;
  description: string;
  targetPersona: string;
}

export interface TopMention {
  platform: string;
  mentions: number;
  url?: string;
  content?: string;
}

export interface TrendAnalysis {
  id: string;
  title: string;
  summary: string;
  hypeIndex: number;
  sentimentSpectrum: {
    positive: number;
    negative: number;
    neutral: number;
  };
  keyThemes: KeyTheme[];
  userPersonaSnapshot: UserPersona[];
  actionableOpportunities: ActionableOpportunity[];
  top_mentions: TopMention[];
  keywords: string[];
  user_tier: string;
}

export interface ComprehensiveAnalysisResponse {
  status: string;
  data: TrendAnalysis;
  processing_time: number;
  user_tier: string;
  remaining_requests: number;
}

// API client
export const trendsApiClient = {
  // Comprehensive analysis
  comprehensiveAnalysis: async (request: ComprehensiveAnalysisRequest): Promise<ComprehensiveAnalysisResponse> => {
    const response = await trendsApi.post('/comprehensive-analysis', request);
    return response.data;
  },

  // Get analysis history
  getAnalysisHistory: async (limit: number = 10): Promise<TrendAnalysis[]> => {
    const response = await trendsApi.get('/history', { params: { limit } });
    return response.data;
  },

  // Get cache stats
  getCacheStats: async () => {
    const response = await trendsApi.get('/cache/stats');
    return response.data;
  },

  // Clear cache (premium feature)
  clearCache: async () => {
    const response = await trendsApi.delete('/cache');
    return response.data;
  },
};

export default trendsApiClient;