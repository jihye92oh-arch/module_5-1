'use client';

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from 'react';
import { User, AuthContextType } from '@/types/auth';
import * as api from '@/lib/api';

// Token storage key
const TOKEN_KEY = 'auth_token';

// Create the context with undefined default
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider props interface
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * AuthProvider component - wraps the app to provide authentication state
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Computed property for authentication status
  const isAuthenticated = !!user && !!token;

  /**
   * Save token to localStorage and state
   */
  const saveToken = useCallback((newToken: string) => {
    localStorage.setItem(TOKEN_KEY, newToken);
    setToken(newToken);
  }, []);

  /**
   * Remove token from localStorage and state
   */
  const removeToken = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
  }, []);

  /**
   * Load user from stored token on app start
   */
  const loadUser = useCallback(async () => {
    const storedToken = localStorage.getItem(TOKEN_KEY);

    if (!storedToken) {
      setIsLoading(false);
      return;
    }

    try {
      const userData = await api.getCurrentUser(storedToken);
      setUser(userData);
      setToken(storedToken);
    } catch (error) {
      // Token is invalid or expired
      console.error('Failed to load user:', error);
      removeToken();
    } finally {
      setIsLoading(false);
    }
  }, [removeToken]);

  /**
   * Login function
   */
  const login = useCallback(
    async (username: string, password: string) => {
      const tokenResponse = await api.login(username, password);
      saveToken(tokenResponse.access_token);

      // Fetch user data after login
      const userData = await api.getCurrentUser(tokenResponse.access_token);
      setUser(userData);
    },
    [saveToken]
  );

  /**
   * Register function
   */
  const register = useCallback(
    async (username: string, email: string, password: string) => {
      await api.register(username, email, password);
      // After registration, automatically log in
      await login(username, password);
    },
    [login]
  );

  /**
   * Logout function
   */
  const logout = useCallback(() => {
    removeToken();
    setUser(null);
  }, [removeToken]);

  // Load user on mount
  useEffect(() => {
    loadUser();
  }, [loadUser]);

  // Context value
  const value: AuthContextType = {
    user,
    token,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * useAuth hook - use this to access auth state and functions
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
}
