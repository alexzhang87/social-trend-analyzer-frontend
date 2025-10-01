import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001/api/v1';

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
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
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 支付相关接口
export interface CheckoutSessionRequest {
  product_type: 'subscription' | 'credits';
  product_id: string;
  success_url?: string;
  cancel_url?: string;
}

export interface CheckoutSessionResponse {
  checkout_url: string;
  session_id: string;
}

export interface SubscriptionInfo {
  id: string;
  user_id: string;
  tier: 'free' | 'starter' | 'pro' | 'plus' | 'enterprise';
  status: 'active' | 'canceled' | 'past_due' | 'trialing';
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  stripe_subscription_id?: string;
}

export interface CreditPackage {
  id: string;
  name: string;
  credits: number;
  price: number;
  description: string;
}

export interface UserCredits {
  total_credits: number;
  used_credits: number;
  remaining_credits: number;
  last_updated: string;
}

// 支付API服务类
export class PaymentsApiService {
  // 创建结账会话
  static async createCheckoutSession(request: CheckoutSessionRequest): Promise<CheckoutSessionResponse> {
    try {
      const response = await api.post('/payments/create-checkout-session', request);
      return response.data;
    } catch (error) {
      console.error('Create checkout session failed:', error);
      throw error;
    }
  }

  // 获取用户订阅信息
  static async getSubscription(): Promise<SubscriptionInfo> {
    try {
      const response = await api.get('/payments/subscription');
      return response.data;
    } catch (error) {
      console.error('Get subscription failed:', error);
      throw error;
    }
  }

  // 取消订阅
  static async cancelSubscription(): Promise<void> {
    try {
      await api.post('/payments/cancel-subscription');
    } catch (error) {
      console.error('Cancel subscription failed:', error);
      throw error;
    }
  }

  // 恢复订阅
  static async resumeSubscription(): Promise<void> {
    try {
      await api.post('/payments/resume-subscription');
    } catch (error) {
      console.error('Resume subscription failed:', error);
      throw error;
    }
  }

  // 获取可用的积分包
  static async getCreditPackages(): Promise<CreditPackage[]> {
    try {
      const response = await api.get('/payments/credit-packages');
      return response.data;
    } catch (error) {
      console.error('Get credit packages failed:', error);
      throw error;
    }
  }

  // 获取用户积分信息
  static async getUserCredits(): Promise<UserCredits> {
    try {
      const response = await api.get('/payments/credits');
      return response.data;
    } catch (error) {
      console.error('Get user credits failed:', error);
      throw error;
    }
  }

  // 获取支付历史
  static async getPaymentHistory(limit: number = 10): Promise<any[]> {
    try {
      const response = await api.get(`/payments/history?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Get payment history failed:', error);
      throw error;
    }
  }

  // 获取发票
  static async getInvoices(limit: number = 10): Promise<any[]> {
    try {
      const response = await api.get(`/payments/invoices?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Get invoices failed:', error);
      throw error;
    }
  }

  // 下载发票
  static async downloadInvoice(invoiceId: string): Promise<string> {
    try {
      const response = await api.get(`/payments/invoices/${invoiceId}/download`);
      return response.data.download_url;
    } catch (error) {
      console.error('Download invoice failed:', error);
      throw error;
    }
  }

  // 更新支付方式
  static async updatePaymentMethod(): Promise<string> {
    try {
      const response = await api.post('/payments/update-payment-method');
      return response.data.setup_url;
    } catch (error) {
      console.error('Update payment method failed:', error);
      throw error;
    }
  }

  // 验证支付状态
  static async verifyPayment(sessionId: string): Promise<{ status: string; subscription?: SubscriptionInfo }> {
    try {
      const response = await api.get(`/payments/verify/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('Verify payment failed:', error);
      throw error;
    }
  }
}

// 导出默认实例
export const paymentsApi = PaymentsApiService;
