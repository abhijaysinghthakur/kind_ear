/**
 * Registration page
 */
'use client';

import Link from 'next/link';
import { RegisterForm } from '@/components/auth/RegisterForm';

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-surface px-4 py-8">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-center text-primary mb-2">
          Join Us
        </h1>
        <p className="text-center text-text-secondary mb-6">
          Create your account to get started
        </p>

        <RegisterForm />

        <p className="mt-6 text-center text-text-secondary">
          Already have an account?{' '}
          <Link href="/login" className="text-primary hover:underline font-medium">
            Login here
          </Link>
        </p>
      </div>
    </div>
  );
}
