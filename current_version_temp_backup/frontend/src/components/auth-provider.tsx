import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { toast } from 'sonner';

interface User {
  id: string;
  email: string;
  username: string;
  credits: number;
  subscription_tier?: string;
  subscription_status?: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  register: (userData: { username: string; email: string; password: string }) => Promise<boolean>;
  googleAuth: () => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setIsLoading(false);
        return;
      }

      const response = await fetch('/api/v1/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        localStorage.removeItem('access_token');
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('access_token');
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        setUser(data.user);
        toast.success('登录成功');
        return true;
      } else {
        const error = await response.json();
        toast.error(error.detail || '登录失败');
        return false;
      }
    } catch (error) {
      console.error('Login failed:', error);
      toast.error('登录失败，请重试');
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
    toast.success('已退出登录');
  };

  const register = async (userData: { username: string; email: string; password: string }): Promise<boolean> => {
    try {
      const response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        setUser(data.user);
        toast.success('注册成功');
        return true;
      } else {
        const error = await response.json();
        toast.error(error.detail || '注册失败');
        return false;
      }
    } catch (error) {
      console.error('Register failed:', error);
      toast.error('注册失败，请重试');
      return false;
    }
  };

  const googleAuth = async (): Promise<void> => {
    try {
      // 重定向到Google OAuth授权页面
      window.location.href = '/api/v1/auth/google';
    } catch (error) {
      console.error('Google auth failed:', error);
      toast.error('Google登录失败，请重试');
    }
  };

  // 处理Google登录回调
  useEffect(() => {
    const handleGoogleCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.has('token')) {
        const token = urlParams.get('token');
        if (token) {
          localStorage.setItem('access_token', token);
          await refreshUser();
          // 清除URL中的token参数
          window.history.replaceState({}, document.title, window.location.pathname);
        }
      }
    };

    handleGoogleCallback();
  }, []);

  const refreshUser = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) return;

      const response = await fetch('/api/v1/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      }
    } catch (error) {
      console.error('Refresh user failed:', error);
    }
  };

  const value = {
    user,
    isLoading,
    login,
    register,
    googleAuth,
    logout,
    refreshUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}