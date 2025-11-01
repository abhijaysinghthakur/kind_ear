/**
 * API client for backend communication
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api/v1';

class APIClient {
  private async request(endpoint: string, options: RequestInit = {}) {
    const url = `${API_URL}${endpoint}`;

    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      credentials: 'include', // Important for cookies
    };

    const response = await fetch(url, config);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Request failed' }));
      throw new Error(error.error || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Auth endpoints
  async register(email: string, password: string, pseudonym: string, roles: string[]) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, pseudonym, roles }),
    });
  }

  async login(email: string, password: string) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async googleLogin(credential: string) {
    return this.request('/auth/google', {
      method: 'POST',
      body: JSON.stringify({ credential }),
    });
  }

  async logout() {
    return this.request('/auth/logout', { method: 'POST' });
  }

  async refresh() {
    return this.request('/auth/refresh', { method: 'POST' });
  }

  // User endpoints
  async getCurrentUser() {
    return this.request('/users/me');
  }

  async updateProfile(data: any) {
    return this.request('/users/me', {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async uploadAvatar(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    return fetch(`${API_URL}/users/me/avatar`, {
      method: 'POST',
      body: formData,
      credentials: 'include',
    }).then(res => res.json());
  }

  async updateAvailability(availability: string) {
    return this.request('/users/me/availability', {
      method: 'PATCH',
      body: JSON.stringify({ availability }),
    });
  }

  // Matching endpoints
  async findListeners(preferences: any) {
    return this.request('/match/find-listeners', {
      method: 'POST',
      body: JSON.stringify(preferences),
    });
  }

  async requestChat(listenerId: string, topic?: string) {
    return this.request('/match/request-chat', {
      method: 'POST',
      body: JSON.stringify({ listener_id: listenerId, topic }),
    });
  }

  // Chat endpoints
  async getActiveSession() {
    return this.request('/chat/sessions/active');
  }

  async getMessages(sessionId: string, limit?: number, before?: string) {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit.toString());
    if (before) params.append('before', before);

    return this.request(`/chat/sessions/${sessionId}/messages?${params}`);
  }

  async endChat(sessionId: string) {
    return this.request(`/chat/sessions/${sessionId}/end`, { method: 'POST' });
  }

  // Feedback endpoints
  async submitFeedback(feedback: any) {
    return this.request('/feedback', {
      method: 'POST',
      body: JSON.stringify(feedback),
    });
  }

  // Report endpoints
  async submitReport(report: any) {
    return this.request('/reports', {
      method: 'POST',
      body: JSON.stringify(report),
    });
  }

  // Admin endpoints
  async getAdminStats() {
    return this.request('/admin/stats');
  }

  async getAdminUsers(params?: any) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/admin/users?${query}`);
  }

  async banUser(userId: string, isActive: boolean, reason: string) {
    return this.request(`/admin/users/${userId}/ban`, {
      method: 'PATCH',
      body: JSON.stringify({ is_active: isActive, reason }),
    });
  }

  async getAdminReports(params?: any) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/admin/reports?${query}`);
  }

  async updateReport(reportId: string, status: string, resolution?: string) {
    return this.request(`/admin/reports/${reportId}`, {
      method: 'PATCH',
      body: JSON.stringify({ status, resolution }),
    });
  }
}

export const api = new APIClient();
