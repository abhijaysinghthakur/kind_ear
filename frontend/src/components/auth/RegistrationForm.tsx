/**
 * Registration form component
 */
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/shared/Button';
import { Input } from '@/components/shared/Input';
import { api } from '@/lib/api';
import { useNotificationStore } from '@/store/notificationStore';

export const RegisterForm = () => {
  const router = useRouter();
  const addNotification = useNotificationStore(state => state.addNotification);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [pseudonym, setPseudonym] = useState('');
  const [selectedRoles, setSelectedRoles] = useState<string[]>(['sharer']);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleRoleToggle = (role: string) => {
    setSelectedRoles(prev =>
      prev.includes(role)
        ? prev.filter(r => r !== role)
        : [...prev, role]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (selectedRoles.length === 0) {
      setError('Please select at least one role');
      return;
    }

    setIsLoading(true);

    try {
      await api.register(email, password, pseudonym, selectedRoles);
      addNotification('success', 'Registration successful! Please login.');
      router.push('/login');
    } catch (err: any) {
      setError(err.message || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        type="email"
        label="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
        placeholder="you@example.com"
      />

      <Input
        type="text"
        label="Pseudonym"
        value={pseudonym}
        onChange={(e) => setPseudonym(e.target.value)}
        required
        placeholder="YourNickname"
        helperText="3-20 characters, letters, numbers, and underscores only"
      />

      <Input
        type="password"
        label="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
        placeholder="••••••••"
        helperText="Minimum 8 characters, include uppercase, lowercase, and number"
      />

      <div>
        <label className="block text-sm font-medium text-text-primary mb-2">
          I want to be a:
        </label>
        <div className="space-y-2">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={selectedRoles.includes('sharer')}
              onChange={() => handleRoleToggle('sharer')}
              className="rounded border-gray-300 text-primary focus:ring-primary"
            />
            <span>Sharer (I need someone to listen)</span>
          </label>
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={selectedRoles.includes('listener')}
              onChange={() => handleRoleToggle('listener')}
              className="rounded border-gray-300 text-primary focus:ring-primary"
            />
            <span>Listener (I want to help others)</span>
          </label>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-error text-error px-4 py-2 rounded">
          {error}
        </div>
      )}

      <Button
        type="submit"
        className="w-full"
        isLoading={isLoading}
      >
        Register
      </Button>
    </form>
  );
};
