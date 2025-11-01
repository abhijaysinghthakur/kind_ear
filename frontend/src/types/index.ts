/**
 * TypeScript types for the application
 */

export interface User {
  id: string;
  email: string;
  pseudonym: string;
  real_name?: string;
  bio?: string;
  profile_picture_url?: string;
  roles: ('sharer' | 'listener')[];
  interests: string[];
  languages: string[];
  listener_availability?: 'available' | 'unavailable' | 'in_chat';
  listener_rating?: number;
  listener_total_chats?: number;
  listener_topics?: string[];
  privacy_settings?: {
    show_profile_picture: boolean;
    allow_feedback: boolean;
  };
  created_at?: string;
  is_active?: boolean;
  is_admin?: boolean;
}

export interface ChatSession {
  session_id: string;
  sharer_id?: string;
  listener_id?: string;
  started_at: string;
  ended_at?: string | null;
  status: 'active' | 'ended' | 'abandoned';
  topic?: string;
  language?: string;
}

export interface Message {
  id: string;
  sender_pseudonym: string;
  content: string;
  sent_at: string;
  is_own_message: boolean;
}

export interface MatchedListener {
  id: string;
  pseudonym: string;
  bio: string;
  profile_picture_url?: string;
  languages: string[];
  listener_topics: string[];
  listener_rating: number;
  listener_total_chats: number;
  match_score: number;
}

export interface Feedback {
  chat_session_id: string;
  rating: number;
  helpfulness: number;
  empathy: number;
  safety: number;
  comment?: string;
}

export interface Report {
  id?: string;
  reported_user_id: string;
  chat_session_id?: string;
  message_id?: string;
  reason: 'harassment' | 'inappropriate' | 'spam' | 'safety_concern' | 'other';
  description: string;
  status?: string;
  created_at?: string;
}

export interface AdminStats {
  total_users: number;
  total_sharers: number;
  total_listeners: number;
  active_chats: number;
  available_listeners: number;
  total_chats_today: number;
  total_chats_all_time: number;
  pending_reports: number;
  average_rating: number;
}
