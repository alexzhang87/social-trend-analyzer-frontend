import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001/api/v1';

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30秒超时
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加认证token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token过期，清除本地存储并重定向到登录页
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 分析请求接口
export interface AnalysisRequest {
  keywords: string[];
  platforms?: string[];
  timeframe?: string;
  filters?: {
    platform?: string;
    timeRange?: string;
    category?: string;
  };
}

// 分析结果接口
export interface AnalysisResult {
  id: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  keywords: string[];
  platforms: string[];
  timeframe: string;
  result_data?: {
    heat_index?: number;
    sentiment_distribution?: {
      positive: number;
      negative: number;
      neutral: number;
    };
    ai_insights?: string;
    business_opportunities?: string[];
    market_value?: string;
    competitive_analysis?: string;
    trend_data?: any[];
    word_cloud_data?: any[];
  };
  created_at: string;
  completed_at?: string;
  error_message?: string;
}

// 快速验证结果接口
export interface QuickValidationResult {
  validation_score: number;
  market_potential: string;
  key_insights: string[];
  recommendations: string[];
  risk_factors: string[];
}

// 专业分析结果接口
export interface ProfessionalAnalysisResult {
  comprehensive_score: number;
  detailed_insights: {
    market_analysis: string;
    competitive_landscape: string;
    growth_opportunities: string[];
    risk_assessment: string;
  };
  business_recommendations: string[];
  market_data: {
    search_volume: number;
    trend_direction: 'up' | 'down' | 'stable';
    seasonality: any[];
  };
  export_data?: {
    pdf_url?: string;
    excel_url?: string;
  };
}

// 趋势分析API服务类
export class TrendsApiService {
  // 综合分析
  static async comprehensiveAnalysis(request: AnalysisRequest): Promise<AnalysisResult> {
    try {
      const response = await api.post('/trends/comprehensive-analysis', request);
      return response.data;
    } catch (error) {
      console.error('Comprehensive analysis failed:', error);
      throw error;
    }
  }

  // 快速验证
  static async quickValidation(keywords: string[]): Promise<QuickValidationResult> {
    try {
      const response = await api.post('/trends/quick-validate', { keywords });
      return response.data;
    } catch (error) {
      console.error('Quick validation failed:', error);
      throw error;
    }
  }

  // 专业分析
  static async professionalAnalysis(request: AnalysisRequest): Promise<ProfessionalAnalysisResult> {
    try {
      const response = await api.post('/trends/professional', request);
      return response.data;
    } catch (error) {
      console.error('Professional analysis failed:', error);
      throw error;
    }
  }

  // 获取分析结果
  static async getAnalysisResult(analysisId: string): Promise<AnalysisResult> {
    try {
      const response = await api.get(`/trends/analysis/${analysisId}`);
      return response.data;
    } catch (error) {
      console.error('Get analysis result failed:', error);
      throw error;
    }
  }

  // 获取分析历史
  static async getAnalysisHistory(limit: number = 10): Promise<AnalysisResult[]> {
    try {
      const response = await api.get(`/trends/history?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Get analysis history failed:', error);
      throw error;
    }
  }

  // 删除分析结果
  static async deleteAnalysis(analysisId: string): Promise<void> {
    try {
      await api.delete(`/trends/analysis/${analysisId}`);
    } catch (error) {
      console.error('Delete analysis failed:', error);
      throw error;
    }
  }

  // 导出分析结果
  static async exportAnalysis(analysisId: string, format: 'pdf' | 'excel'): Promise<string> {
    try {
      const response = await api.post(`/trends/analysis/${analysisId}/export`, { format });
      return response.data.download_url;
    } catch (error) {
      console.error('Export analysis failed:', error);
      throw error;
    }
  }

  // 检查用户积分余额
  static async checkCredits(): Promise<{ remaining: number; used: number; total: number }> {
    try {
      const response = await api.get('/auth/credits');
      return response.data;
    } catch (error) {
      console.error('Check credits failed:', error);
      throw error;
    }
  }

  // 获取用户订阅信息
  static async getSubscription(): Promise<{ tier: string; expires_at?: string; features: string[] }> {
    try {
      const response = await api.get('/auth/subscription');
      return response.data;
    } catch (error) {
      console.error('Get subscription failed:', error);
      throw error;
    }
  }
}

// 导出默认实例
export const trendsApi = TrendsApiService;
