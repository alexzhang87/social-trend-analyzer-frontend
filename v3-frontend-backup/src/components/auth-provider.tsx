"use client"

import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { authApiClient, authStorage, type User } from '@/lib/auth-api';

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string, fullName?: string) => Promise<void>;
  logout: () => Promise<void>;
  loading: boolean;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check authentication status during initialization
    const initAuth = async () => {
      try {
        const token = authStorage.getToken();
        const savedUser = authStorage.getUser();
        
        if (token && savedUser) {
          // Verify if token is still valid
          try {
            const currentUser = await authApiClient.getCurrentUser();
            // Fetch credits balance and merge
            try {
              const credits = await authApiClient.getCreditsBalance();
              setUser({ ...currentUser, ...credits });
            } catch (e) {
              setUser(currentUser);
            }
            setIsAuthenticated(true);
          } catch (error) {
            // Token invalid, clear local storage
            authStorage.clearAuth();
            setUser(null);
            setIsAuthenticated(false);
          }
        }
      } catch (error) {
        console.error('Auth initialization failed:', error);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const authResponse = await authApiClient.login({ 
        username: email, // FastAPI expects username field
        password 
      });
      
      authStorage.setAuth(authResponse);
      // Get user and credits information
      const currentUser = await authApiClient.getCurrentUser();
      try {
        const credits = await authApiClient.getCreditsBalance();
        setUser({ ...currentUser, ...credits });
      } catch (e) {
        setUser(currentUser);
      }
      setIsAuthenticated(true);
    } catch (error) {
      throw error;
    }
  };

  const register = async (email: string, username: string, password: string, fullName?: string) => {
    try {
      await authApiClient.register({
        email,
        username,
        password,
        full_name: fullName
      });
      
      // Auto login after successful registration
      await login(email, password);
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authApiClient.logout();
    } catch (error) {
      console.error('Logout API call failed:', error);
    } finally {
      authStorage.clearAuth();
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const refreshUser = async () => {
    try {
      const currentUser = await authApiClient.getCurrentUser();
      try {
        const credits = await authApiClient.getCreditsBalance();
        setUser({ ...currentUser, ...credits });
      } catch (e) {
        setUser(currentUser);
      }
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Failed to refresh user:', error);
    }
  };

  const value: AuthContextType = {
    isAuthenticated,
    user,
    login,
    register,
    logout,
    loading,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}