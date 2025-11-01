/**
 * Login page
 */
'use client';

import Link from 'next/link';
import { LoginForm } from '@/components/auth/LoginForm';

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-surface px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-center text-primary mb-2">
          Welcome Back
        </h1>
        <p className="text-center text-text-secondary mb-6">
          Login to continue your journey
        </p>

        <LoginForm />

        <p className="mt-6 text-center text-text-secondary">
          Don't have an account?{' '}
          <Link href="/register" className="text-primary hover:underline font-medium">
            Register here
          </Link>
        </p>
      </div>
    </div>
  );
}
