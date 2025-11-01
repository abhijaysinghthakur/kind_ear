/**
 * Landing page
 */
'use client';

import Link from 'next/link';
import { Button } from '@/components/shared/Button';

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold text-primary">Empathetic Listening</h1>
          <div className="space-x-4">
            <Link href="/login">
              <Button variant="outline">Login</Button>
            </Link>
            <Link href="/register">
              <Button>Get Started</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 py-12 bg-gradient-to-b from-surface to-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-5xl font-bold text-text-primary mb-6">
            You Are Not Alone
          </h2>
          <p className="text-xl text-text-secondary mb-8 max-w-2xl mx-auto">
            Connect with empathetic listeners who care. Share your feelings in a safe, anonymous, and judgment-free space.
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/register">
              <Button size="lg">Start Talking</Button>
            </Link>
            <Link href="/register">
              <Button size="lg" variant="secondary">Become a Listener</Button>
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="max-w-6xl mx-auto grid md:grid-cols-3 gap-8 mt-16">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-3 text-primary">Anonymous & Safe</h3>
            <p className="text-text-secondary">
              Your privacy matters. All conversations are anonymous with messages auto-deleted after 24 hours.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-3 text-primary">Available 24/7</h3>
            <p className="text-text-secondary">
              Compassionate listeners are available any time you need to talk. No appointments necessary.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-3 text-primary">Peer Support</h3>
            <p className="text-text-secondary">
              Connect with trained volunteers who understand what you're going through and truly care.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-surface border-t border-gray-200 px-6 py-8">
        <div className="max-w-7xl mx-auto text-center text-text-secondary">
          <p>&copy; 2025 Empathetic Listening Platform. Not a replacement for professional counseling.</p>
        </div>
      </footer>
    </div>
  );
}
