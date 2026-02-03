'use client';

import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';

/**
 * Header component - shows navigation with auth state
 */
export default function Header() {
  const { user, isAuthenticated, isLoading, logout } = useAuth();

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Logo / Home link */}
          <Link
            href="/"
            className="text-xl font-bold text-indigo-600 hover:text-indigo-700 transition-colors"
          >
            Module 5
          </Link>

          {/* Navigation items */}
          <div className="flex items-center gap-4">
            {isLoading ? (
              // Loading state
              <div className="h-8 w-24 bg-gray-200 animate-pulse rounded"></div>
            ) : isAuthenticated ? (
              // Authenticated state
              <div className="flex items-center gap-4">
                <Link
                  href="/dashboard"
                  className="text-gray-600 hover:text-gray-900 transition-colors"
                >
                  Dashboard
                </Link>
                <span className="text-sm text-gray-600 hidden sm:block">
                  Welcome,{' '}
                  <span className="font-medium text-gray-900">
                    {user?.username}
                  </span>
                </span>
                <button
                  onClick={logout}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-500 rounded-lg hover:bg-red-600 transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                >
                  Logout
                </button>
              </div>
            ) : (
              // Unauthenticated state
              <div className="flex items-center gap-3">
                <Link
                  href="/login"
                  className="px-4 py-2 text-sm font-medium text-indigo-600 hover:text-indigo-700 transition-colors"
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                >
                  Register
                </Link>
              </div>
            )}
          </div>
        </div>
      </nav>
    </header>
  );
}
