/**
 * Dashboard - role selection page
 */
'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/shared/Button';
import { useAuthStore } from '@/store/authStore';
import { useEffect } from 'react';

export default function DashboardPage() {
  const router = useRouter();
  const user = useAuthStore(state => state.user);

  useEffect(() => {
    // Redirect to login if not authenticated
    if (!user) {
      router.push('/login');
    }
  }, [user, router]);

  if (!user) {
    return <div>Loading...</div>;
  }

  const isSharer = user.roles.includes('sharer');
  const isListener = user.roles.includes('listener');

  return (
    <div className="min-h-screen bg-surface">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold text-primary">Dashboard</h1>
          <div className="flex items-center gap-4">
            <span className="text-text-secondary">Hello, {user.pseudonym}</span>
            <Button variant="outline" onClick={() => router.push('/profile')}>
              Profile
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 py-12">
        <h2 className="text-3xl font-bold text-text-primary mb-8 text-center">
          What would you like to do today?
        </h2>

        <div className="grid md:grid-cols-2 gap-6">
          {isSharer && (
            <div className="bg-white rounded-lg shadow-md p-8 flex flex-col items-center text-center">
              <h3 className="text-2xl font-semibold text-primary mb-4">
                Talk to Someone
              </h3>
              <p className="text-text-secondary mb-6">
                Find an empathetic listener to share your thoughts and feelings with.
              </p>
              <Button onClick={() => router.push('/sharer/find-listener')}>
                Find a Listener
              </Button>
            </div>
          )}

          {isListener && (
            <div className="bg-white rounded-lg shadow-md p-8 flex flex-col items-center text-center">
              <h3 className="text-2xl font-semibold text-secondary mb-4">
                Listen to Others
              </h3>
              <p className="text-text-secondary mb-6">
                Make yourself available to help someone who needs to talk.
              </p>
              <Button
                variant="secondary"
                onClick={() => router.push('/listener/queue')}
              >
                Start Listening
              </Button>
            </div>
          )}
        </div>

        {/* Admin access */}
        {user.is_admin && (
          <div className="mt-8 text-center">
            <Button
              variant="outline"
              onClick={() => router.push('/admin')}
            >
              Admin Panel
            </Button>
          </div>
        )}
      </main>
    </div>
  );
}
