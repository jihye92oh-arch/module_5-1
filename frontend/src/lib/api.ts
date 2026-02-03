// API Client Utility for authentication

import {
  User,
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  ApiError,
} from '@/types/auth';

// API base configuration - uses Next.js proxy (see next.config.js)
const API_BASE = '/api';

// Custom error class for API errors
export class ApiRequestError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = 'ApiRequestError';
    this.status = status;
    this.detail = detail;
  }
}

// Generic fetch wrapper with error handling
async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;

  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };

  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  const response = await fetch(url, config);

  if (!response.ok) {
    let errorDetail = 'An unexpected error occurred';
    try {
      const errorData: ApiError = await response.json();
      errorDetail = errorData.detail || errorDetail;
    } catch {
      errorDetail = `HTTP error ${response.status}`;
    }
    throw new ApiRequestError(response.status, errorDetail);
  }

  return response.json();
}

// Auth API functions

/**
 * Register a new user
 */
export async function register(
  username: string,
  email: string,
  password: string
): Promise<User> {
  const data: RegisterRequest = { username, email, password };
  return fetchApi<User>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Login and get JWT token
 */
export async function login(
  username: string,
  password: string
): Promise<TokenResponse> {
  const data: LoginRequest = { username, password };
  return fetchApi<TokenResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Get current authenticated user
 */
export async function getCurrentUser(token: string): Promise<User> {
  return fetchApi<User>('/auth/me', {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

/**
 * Check if an error is an ApiRequestError
 */
export function isApiError(error: unknown): error is ApiRequestError {
  return error instanceof ApiRequestError;
}

/**
 * Get error message from any error type
 */
export function getErrorMessage(error: unknown): string {
  if (isApiError(error)) {
    return error.detail;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unexpected error occurred';
}
