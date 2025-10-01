import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

// Create axios instance
const authApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - automatically add auth token
authApi.interceptors.request.use(
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

// Response interceptor - handle authentication errors
authApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, clear local storage and redirect
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Authentication related interfaces
export interface LoginData {
  username: string; // Actually is email
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  role: string;
  subscription_tier: string;
  created_at: string;
  // optional: credits & subscription extra fields (from /credits/balance)
  credits_balance?: number;
  monthly_credits?: number;
  subscription_expires_at?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface CreditsBalanceResponse {
  credits_balance: number;
  subscription_tier: string;
  monthly_credits: number;
  subscription_expires_at?: string;
}

export const authApiClient = {
  // User login
  login: async (loginData: LoginData): Promise<AuthResponse> => {
    const formData = new FormData();
    formData.append('username', loginData.username); // FastAPI's OAuth2PasswordRequestForm expects username field
    formData.append('password', loginData.password);
    
    const response = await authApi.post('/api/v1/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  // User registration
  register: async (registerData: RegisterData): Promise<User> => {
    const response = await authApi.post('/api/v1/auth/register', registerData);
    return response.data;
  },

  // Get current user information
  getCurrentUser: async (): Promise<User> => {
    const response = await authApi.get('/api/v1/auth/me');
    return response.data;
  },

  // Get current user's credits balance and subscription info
  getCreditsBalance: async (): Promise<CreditsBalanceResponse> => {
    const response = await authApi.get('/api/v1/credits/balance');
    return response.data;
  },

  // Logout
  logout: async (): Promise<void> => {
    try {
      await authApi.post('/api/v1/auth/logout');
    } catch (error) {
      // Clear local tokens even if backend returns error
      console.warn('Logout request failed, but clearing local tokens anyway');
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  },
};

// Create authenticated API instance for use by other modules
export const createAuthenticatedApi = () => {
  return axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
    transformRequest: [(data, headers) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }
      return JSON.stringify(data);
    }],
  });
};

// Authentication state management
export const authStorage = {
  setAuth: (authData: AuthResponse) => {
    localStorage.setItem('access_token', authData.access_token);
    localStorage.setItem('refresh_token', authData.refresh_token);
    localStorage.setItem('user', JSON.stringify(authData.user));
  },

  getToken: (): string | null => {
    return localStorage.getItem('access_token');
  },

  getUser: (): User | null => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  isAuthenticated: (): boolean => {
    return !!localStorage.getItem('access_token');
  },

  clearAuth: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },
};

export default authApi;