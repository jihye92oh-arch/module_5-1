'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';

interface HealthStatus {
  status: string;
  message: string;
}

export default function Home() {
  const { isAuthenticated, user, isLoading: authLoading } = useAuth();
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/health')
      .then((res) => res.json())
      .then((data) => {
        setHealth(data);
        setLoading(false);
      })
      .catch(() => {
        setHealth({ status: 'error', message: 'Backend connection failed' });
        setLoading(false);
      });
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12">
      <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full mx-4">
        <h1 className="text-3xl font-bold text-gray-800 text-center mb-2">
          Module 5
        </h1>
        <p className="text-gray-600 text-center mb-8">
          Next.js + FastAPI + SQLite
        </p>

        {/* Auth Status Section */}
        <div className="border-t pt-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-700 mb-3">
            Authentication Status
          </h2>
          {authLoading ? (
            <div className="flex items-center justify-center py-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
          ) : isAuthenticated ? (
            <div className="p-4 rounded-lg bg-green-50 text-green-700">
              <p className="font-medium">Logged in as {user?.username}</p>
              <p className="text-sm mt-1">{user?.email}</p>
              <Link
                href="/dashboard"
                className="mt-3 inline-block text-sm font-medium text-green-700 hover:text-green-800 underline"
              >
                Go to Dashboard
              </Link>
            </div>
          ) : (
            <div className="p-4 rounded-lg bg-gray-50">
              <p className="text-gray-600 mb-4">
                You are not logged in. Please sign in or create an account.
              </p>
              <div className="flex gap-3">
                <Link
                  href="/login"
                  className="flex-1 text-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  className="flex-1 text-center px-4 py-2 border border-indigo-600 text-indigo-600 rounded-lg hover:bg-indigo-50 transition-colors"
                >
                  Register
                </Link>
              </div>
            </div>
          )}
        </div>

        {/* Backend Status Section */}
        <div className="border-t pt-6">
          <h2 className="text-lg font-semibold text-gray-700 mb-3">
            Backend Status
          </h2>
          {loading ? (
            <div className="flex items-center justify-center py-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
          ) : (
            <div
              className={`p-4 rounded-lg ${
                health?.status === 'ok'
                  ? 'bg-green-50 text-green-700'
                  : 'bg-red-50 text-red-700'
              }`}
            >
              <p className="font-medium">
                {health?.status === 'ok' ? 'Connected' : 'Connection Failed'}
              </p>
              <p className="text-sm mt-1">{health?.message}</p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
