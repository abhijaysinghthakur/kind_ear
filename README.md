# Empathetic Listening Platform - Implementation Plan

## Overview

Building a responsive web application that connects people who need someone to listen ("Sharers") with empathetic volunteer listeners ("Listeners"). The platform provides a safe, welcoming environment for peer support through real-time text-based conversations, with emphasis on privacy, accessibility, and ease of use.

## Project Context

- **Greenfield project**: Starting from empty repository (ai\_agent\_to\_test)
- **Purpose**: Peer support platform (not professional counseling)
- **Target users**: People feeling isolated/anxious + volunteer listeners
- **Core value**: Safe, anonymous emotional support at any time

## Tech Stack Decisions

### Frontend

- **Framework**: Next.js 14 (App Router)
- **Styling**: TailwindCSS
- **Real-time**: Socket.IO client
- **State Management**: React Context + hooks (or Zustand for complex state)
- **Form Handling**: React Hook Form
- **HTTP Client**: Fetch API (native)

### Backend

- **Framework**: Python Flask
- **Real-time**: Flask-SocketIO
- **ORM**: PyMongo (MongoDB driver)
- **Auth**: Flask-JWT-Extended
- **OAuth**: Authlib (for Google OAuth)
- **Validation**: Marshmallow
- **CORS**: Flask-CORS

### Database

- **Primary DB**: MongoDB
- **Session Store**: Redis (for Socket.IO sessions and online status)

### Authentication

- **JWT**: Access tokens (15min) + Refresh tokens (7 days)
- **OAuth**: Google Sign-In integration
- **Storage**: JWT in httpOnly cookies

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                    │
│  - Pages: Home, Login, Register, Dashboard, Chat, Admin │
│  - Components: ProfileCard, ChatWindow, MatchList       │
│  - State: React Context + Zustand                       │
└──────────────┬────────────────────────┬─────────────────┘
               │                        │
         REST API                  WebSocket (Socket.IO)
               │                        │
┌──────────────┴────────────────────────┴─────────────────┐
│              Backend (Python Flask)                      │
│  - API Routes: /auth, /users, /match, /chat, /admin    │
│  - Socket.IO: Real-time messaging & status              │
│  - Middleware: JWT auth, CORS, rate limiting            │
└──────────────┬────────────────────────┬─────────────────┘
               │                        │
            MongoDB                   Redis
        (User data, chats,        (Sessions, online
         profiles, feedback)       status, queue)
```

### Key Design Decisions

- **Always anonymous**: Users see pseudonyms only, never real names
- **Hybrid matching**: Algorithm suggests top 3 matches, user picks
- **24-hour chat deletion**: Messages auto-delete after 24hrs for privacy
- **Dual role support**: Users can be both Sharer and Listener
- **OAuth + JWT**: Google Sign-In plus email/password option

## Feature Scope

**Full feature implementation including:**

- User authentication (email/password + Google OAuth)
- Profile management (Sharer and Listener roles)
- Matching algorithm with preferences
- Real-time text chat with Socket.IO
- Queue/availability system for listeners
- Feedback and ratings system
- Privacy controls and anonymous mode
- Text moderation and abuse reporting
- Admin panel for platform management
- Responsive UI with accessibility features

---

## Database Schema (MongoDB Collections)

### users Collection

```
{
  _id: ObjectId,
  email: string (unique, required),
  password_hash: string (required for email/password users),
  oauth_provider: string (null or "google"),
  oauth_id: string (unique for OAuth users),
  pseudonym: string (unique, required - displayed name),
  real_name: string (optional, never displayed in chats),
  bio: string (max 500 chars),
  profile_picture_url: string (optional),
  roles: array ["sharer", "listener"] (user can have both),
  interests: array of strings (for matching),
  languages: array of strings (for matching),
  created_at: datetime,
  updated_at: datetime,
  is_active: boolean (for soft delete/ban),
  is_admin: boolean,

  // Listener-specific fields
  listener_availability: string ("available", "unavailable", "in_chat"),
  listener_rating: float (average rating),
  listener_total_chats: int,
  listener_topics: array of strings (what they're comfortable discussing),

  // Privacy settings
  privacy_settings: {
    show_profile_picture: boolean,
    allow_feedback: boolean
  }
}
```

### chat\_sessions Collection

```
{
  _id: ObjectId,
  sharer_id: ObjectId (ref: users),
  listener_id: ObjectId (ref: users),
  started_at: datetime,
  ended_at: datetime (null if ongoing),
  status: string ("active", "ended", "abandoned"),
  initiated_by: ObjectId (who requested the chat),
  expires_at: datetime (started_at + 24 hours for auto-deletion),

  // Metadata
  topic: string (optional - what Sharer wants to discuss),
  language: string (language of conversation)
}
```

### messages Collection

```
{
  _id: ObjectId,
  chat_session_id: ObjectId (ref: chat_sessions),
  sender_id: ObjectId (ref: users),
  sender_role: string ("sharer" or "listener"),
  content: string (required, max 2000 chars),
  sent_at: datetime,
  expires_at: datetime (sent_at + 24 hours),
  is_flagged: boolean (for moderation),

  // For moderation
  moderation_status: string ("pending", "approved", "flagged", "removed"),
  flagged_reason: string (optional)
}
```

### feedback Collection

```
{
  _id: ObjectId,
  chat_session_id: ObjectId (ref: chat_sessions),
  reviewer_id: ObjectId (who gave feedback),
  reviewee_id: ObjectId (who received feedback),
  rating: int (1-5 stars),
  comment: string (optional, max 500 chars),
  is_anonymous: boolean (always true for this platform),
  created_at: datetime,

  // Feedback categories
  helpfulness: int (1-5),
  empathy: int (1-5),
  safety: int (1-5)
}
```

### reports Collection

```
{
  _id: ObjectId,
  reporter_id: ObjectId (ref: users),
  reported_user_id: ObjectId (ref: users),
  chat_session_id: ObjectId (optional, ref: chat_sessions),
  message_id: ObjectId (optional, ref: messages),
  reason: string ("harassment", "inappropriate", "spam", "safety_concern", "other"),
  description: string (max 1000 chars),
  status: string ("pending", "under_review", "resolved", "dismissed"),
  created_at: datetime,
  reviewed_at: datetime (optional),
  reviewed_by: ObjectId (optional, ref: users - admin),
  resolution: string (optional, admin notes)
}
```

### match\_preferences Collection

```
{
  _id: ObjectId,
  user_id: ObjectId (ref: users),
  role: string ("sharer" - preferences when looking for listener),
  preferred_languages: array of strings,
  preferred_topics: array of strings,
  preferred_listener_min_rating: float (optional, e.g., 4.0),
  avoid_previous_matches: boolean (don't match with recent listeners),
  updated_at: datetime
}
```

### admin\_logs Collection

```
{
  _id: ObjectId,
  admin_id: ObjectId (ref: users),
  action: string ("ban_user", "resolve_report", "delete_message", etc.),
  target_id: ObjectId (user/message/chat affected),
  details: object (additional context),
  timestamp: datetime
}
```

---

## Project Structure

### Repository: ai\_agent\_to\_test

```
ai_agent_to_test/
├── frontend/                          # Next.js application
│   ├── src/
│   │   ├── app/                      # Next.js 14 App Router
│   │   │   ├── layout.tsx            # Root layout with providers
│   │   │   ├── page.tsx              # Landing page
│   │   │   ├── login/
│   │   │   │   └── page.tsx          # Login page
│   │   │   ├── register/
│   │   │   │   └── page.tsx          # Registration page
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx          # Main dashboard (role selection)
│   │   │   ├── sharer/
│   │   │   │   ├── find-listener/
│   │   │   │   │   └── page.tsx      # Find and match with listener
│   │   │   │   └── chat/[sessionId]/
│   │   │   │       └── page.tsx      # Active chat as Sharer
│   │   │   ├── listener/
│   │   │   │   ├── queue/
│   │   │   │   │   └── page.tsx      # Listener availability & queue
│   │   │   │   └── chat/[sessionId]/
│   │   │   │       └── page.tsx      # Active chat as Listener
│   │   │   ├── profile/
│   │   │   │   └── page.tsx          # Edit profile & preferences
│   │   │   └── admin/
│   │   │       ├── page.tsx          # Admin dashboard
│   │   │       ├── users/
│   │   │       │   └── page.tsx      # User management
│   │   │       └── reports/
│   │   │           └── page.tsx      # Report moderation
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   ├── RegisterForm.tsx
│   │   │   │   └── GoogleAuthButton.tsx
│   │   │   ├── chat/
│   │   │   │   ├── ChatWindow.tsx    # Main chat interface
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── MessageInput.tsx
│   │   │   │   └── ChatHeader.tsx
│   │   │   ├── matching/
│   │   │   │   ├── MatchCard.tsx     # Display suggested listener
│   │   │   │   ├── MatchList.tsx     # List of top 3 suggestions
│   │   │   │   └── TopicSelector.tsx
│   │   │   ├── profile/
│   │   │   │   ├── ProfileForm.tsx
│   │   │   │   ├── AvatarUpload.tsx
│   │   │   │   └── PreferencesForm.tsx
│   │   │   ├── feedback/
│   │   │   │   └── FeedbackModal.tsx # Post-chat feedback
│   │   │   ├── admin/
│   │   │   │   ├── UserTable.tsx
│   │   │   │   ├── ReportTable.tsx
│   │   │   │   └── StatsCard.tsx
│   │   │   └── shared/
│   │   │       ├── Button.tsx
│   │   │       ├── Input.tsx
│   │   │       ├── Modal.tsx
│   │   │       └── LoadingSpinner.tsx
│   │   ├── lib/
│   │   │   ├── api.ts                # API client functions
│   │   │   ├── socket.ts             # Socket.IO client setup
│   │   │   ├── auth.ts               # Auth helpers
│   │   │   └── utils.ts              # Utility functions
│   │   ├── store/
│   │   │   ├── authStore.ts          # Zustand auth state
│   │   │   ├── chatStore.ts          # Zustand chat state
│   │   │   └── notificationStore.ts  # Toast notifications
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useSocket.ts
│   │   │   └── useChat.ts
│   │   └── types/
│   │       └── index.ts              # TypeScript types
│   ├── public/
│   │   ├── images/
│   │   └── icons/
│   ├── tailwind.config.js
│   ├── next.config.js
│   ├── package.json
│   └── tsconfig.json
│
├── backend/                           # Python Flask application
│   ├── app/
│   │   ├── __init__.py               # Flask app factory
│   │   ├── config.py                 # Configuration classes
│   │   ├── extensions.py             # Initialize extensions (PyMongo, JWT, etc.)
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py               # User model & methods
│   │   │   ├── chat.py               # Chat session model
│   │   │   ├── message.py            # Message model
│   │   │   ├── feedback.py           # Feedback model
│   │   │   └── report.py             # Report model
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # /auth endpoints (login, register, OAuth)
│   │   │   ├── users.py              # /users endpoints (profile CRUD)
│   │   │   ├── match.py              # /match endpoints (find matches)
│   │   │   ├── chat.py               # /chat endpoints (chat history, sessions)
│   │   │   ├── feedback.py           # /feedback endpoints
│   │   │   ├── reports.py            # /reports endpoints
│   │   │   └── admin.py              # /admin endpoints
│   │   ├── sockets/
│   │   │   ├── __init__.py
│   │   │   ├── chat_events.py        # Socket.IO chat events
│   │   │   └── status_events.py      # Socket.IO status events
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py       # Auth logic (JWT, OAuth)
│   │   │   ├── matching_service.py   # Matching algorithm
│   │   │   ├── chat_service.py       # Chat business logic
│   │   │   ├── moderation_service.py # Text moderation (basic keyword filter)
│   │   │   └── cleanup_service.py    # Background job for 24hr deletion
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # JWT validation decorator
│   │   │   ├── rate_limit.py         # Rate limiting
│   │   │   └── admin.py              # Admin role check
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user_schema.py        # Marshmallow schemas
│   │   │   ├── chat_schema.py
│   │   │   └── feedback_schema.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── validators.py         # Custom validators
│   │       └── helpers.py            # Utility functions
│   ├── migrations/                    # Database migration scripts (optional)
│   ├── tests/
│   │   ├── test_auth.py
│   │   ├── test_matching.py
│   │   └── test_chat.py
│   ├── requirements.txt
│   ├── run.py                        # Application entry point
│   └── .env.example
│
├── docker/
│   ├── frontend.Dockerfile
│   ├── backend.Dockerfile
│   └── docker-compose.yml
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml                 # GitHub Actions workflow
│
├── docs/
│   ├── API.md                        # API documentation
│   ├── SETUP.md                      # Setup instructions
│   ├── ARCHITECTURE.md               # System architecture
│   └── DEPLOYMENT.md                 # Deployment guide
│
├── scripts/
│   ├── seed_db.py                    # Create test users
│   └── cleanup_old_chats.py          # Manual cleanup script
│
├── .gitignore
└── README.md
```

---

## API Endpoints Specification

### Base URL

- **Backend API**: `http://localhost:5000/api/v1`
- **Socket.IO**: `http://localhost:5000`

### Authentication Endpoints (backend/app/routes/auth.py)

#### POST /api/v1/auth/register

**Purpose**: Register new user with email/password
**Auth**: None (public)
**Request Body**:

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "pseudonym": "KindListener",
  "roles": ["listener"]
}
```

**Validation**:

- Email: Valid email format, unique in database
- Password: Minimum 8 characters, must contain uppercase, lowercase, number
- Pseudonym: 3-20 characters, alphanumeric + underscores, unique
- Roles: Array containing "sharer" and/or "listener", at least one required

**Response (201)**:

```json
{
  "message": "User registered successfully",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "pseudonym": "KindListener",
    "roles": ["listener"]
  }
}
```

**Error Responses**:

- 400: Invalid input (validation errors listed)
- 409: Email or pseudonym already exists

---

#### POST /api/v1/auth/login

**Purpose**: Login with email/password, receive JWT tokens
**Auth**: None (public)
**Request Body**:

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200)**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "pseudonym": "KindListener",
    "roles": ["listener"],
    "profile_picture_url": "https://..."
  }
}
```

**Token Storage**: Set httpOnly cookies for both tokens

- `access_token` cookie: expires in 15 minutes
- `refresh_token` cookie: expires in 7 days

**Error Responses**:

- 401: Invalid credentials
- 403: Account banned/inactive

---

#### POST /api/v1/auth/google

**Purpose**: OAuth login/register with Google
**Auth**: None (public)
**Request Body**:

```json
{
  "credential": "google_oauth_token_here"
}
```

**Implementation**:

- Verify Google token using Authlib
- Extract email, name, profile picture from Google
- If user exists (by email): Log them in
- If user doesn't exist: Create new user with `oauth_provider: "google"`, `oauth_id: google_user_id`
- Generate pseudonym from name if new user (ensure uniqueness)
- Return JWT tokens same as login endpoint

**Response (200)**: Same as /auth/login

---

#### POST /api/v1/auth/refresh

**Purpose**: Refresh expired access token using refresh token
**Auth**: Refresh token (from cookie)
**Request Body**: None (token from cookie)

**Response (200)**:

```json
{
  "access_token": "new_access_token_here"
}
```

**Sets new access\_token cookie**

**Error Responses**:

- 401: Invalid or expired refresh token

---

#### POST /api/v1/auth/logout

**Purpose**: Logout user, invalidate tokens
**Auth**: Access token required
**Request Body**: None

**Response (200)**:

```json
{
  "message": "Logged out successfully"
}
```

**Action**: Clear both httpOnly cookies, add refresh token to Redis blacklist

---

### User Profile Endpoints (backend/app/routes/users.py)

#### GET /api/v1/users/me

**Purpose**: Get current user's profile
**Auth**: Access token required
**Response (200)**:

```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "pseudonym": "KindListener",
  "real_name": "John Doe",
  "bio": "Here to listen and support",
  "profile_picture_url": "https://...",
  "roles": ["listener", "sharer"],
  "interests": ["mental health", "anxiety", "relationships"],
  "languages": ["English", "Spanish"],
  "listener_availability": "available",
  "listener_rating": 4.7,
  "listener_total_chats": 23,
  "listener_topics": ["anxiety", "loneliness", "stress"],
  "privacy_settings": {
    "show_profile_picture": true,
    "allow_feedback": true
  },
  "created_at": "2025-01-15T10:30:00Z"
}
```

---

#### PATCH /api/v1/users/me

**Purpose**: Update current user's profile
**Auth**: Access token required
**Request Body** (all fields optional):

```json
{
  "pseudonym": "NewPseudonym",
  "real_name": "Jane Doe",
  "bio": "Updated bio",
  "interests": ["anxiety", "depression"],
  "languages": ["English"],
  "listener_topics": ["grief", "stress"],
  "privacy_settings": {
    "show_profile_picture": false
  }
}
```

**Validation**:

- Pseudonym: If provided, must be unique
- Bio: Max 500 characters
- Interests/languages/topics: Arrays of strings

**Response (200)**: Updated user object (same format as GET /users/me)

**Error Responses**:

- 400: Validation error
- 409: Pseudonym already taken

---

#### POST /api/v1/users/me/avatar

**Purpose**: Upload profile picture
**Auth**: Access token required
**Request**: multipart/form-data with file field
**File Requirements**:

- Max size: 5MB
- Allowed formats: JPG, PNG, GIF
- Uploaded to cloud storage (implementation can use local storage initially)

**Response (200)**:

```json
{
  "profile_picture_url": "https://storage.example.com/avatars/507f1f77bcf86cd799439011.jpg"
}
```

**Error Responses**:

- 400: File too large or invalid format
- 413: Payload too large

---

#### PATCH /api/v1/users/me/availability

**Purpose**: Update listener availability status
**Auth**: Access token required
**Validation**: User must have "listener" role

**Request Body**:

```json
{
  "availability": "available"
}
```

**Allowed values**: "available", "unavailable", "in\_chat"

**Response (200)**:

```json
{
  "listener_availability": "available"
}
```

**Additional Action**: Broadcast status change via Socket.IO to all connected clients in matching queue

**Error Responses**:

- 403: User is not a listener

---

### Matching Endpoints (backend/app/routes/match.py)

#### POST /api/v1/match/find-listeners

**Purpose**: Get top 3 suggested listeners based on preferences (hybrid matching)
**Auth**: Access token required
**Validation**: User must have "sharer" role

**Request Body**:

```json
{
  "topic": "anxiety",
  "language": "English",
  "preferred_min_rating": 4.0
}
```

**All fields optional, used to refine matching**

**Matching Algorithm Implementation**:

1. Query users collection for listeners where:

- `listener_availability: "available"`
- `is_active: true`
- `"listener" in roles`

2. Filter by preferences:

- If language specified: `language in listeners.languages`
- If topic specified: `topic in listeners.listener_topics` OR `topic in listeners.interests`
- If min\_rating specified: `listeners.listener_rating >= preferred_min_rating`
- Exclude listeners user chatted with in last 24 hours (check chat\_sessions collection)

3. Score each listener:

- Base score: 100
- Topic match (exact): +50
- Topic match (in interests): +25
- Language match: +30
- Rating bonus: `(listener_rating - 3.0) * 10` (e.g., 4.5 rating = +15)
- Experience bonus: `min(listener_total_chats / 10, 20)` (max +20)
- Random factor: +/- 10 (for variety)

4. Sort by score descending, return top 3

**Response (200)**:

```json
{
  "matches": [
    {
      "id": "507f1f77bcf86cd799439011",
      "pseudonym": "CaringListener",
      "bio": "Here to help with anxiety and stress",
      "profile_picture_url": "https://...",
      "languages": ["English"],
      "listener_topics": ["anxiety", "stress"],
      "listener_rating": 4.8,
      "listener_total_chats": 45,
      "match_score": 185
    },
    {
      "id": "507f1f77bcf86cd799439012",
      "pseudonym": "EmpathyFirst",
      "bio": "Experienced with mental health topics",
      "profile_picture_url": null,
      "languages": ["English", "Spanish"],
      "listener_topics": ["anxiety", "depression"],
      "listener_rating": 4.5,
      "listener_total_chats": 32,
      "match_score": 170
    },
    {
      "id": "507f1f77bcf86cd799439013",
      "pseudonym": "PatientEar",
      "bio": "Always ready to listen",
      "profile_picture_url": "https://...",
      "languages": ["English"],
      "listener_topics": ["loneliness", "anxiety"],
      "listener_rating": 4.6,
      "listener_total_chats": 28,
      "match_score": 165
    }
  ]
}
```

**Edge Cases**:

- If no matches found: Return 200 with empty array and message: "No available listeners match your preferences right now. Please try again later."
- If fewer than 3 matches: Return however many are available
- If user doesn't have "sharer" role: Return 403

**Error Responses**:

- 403: User is not a sharer

---

#### POST /api/v1/match/request-chat

**Purpose**: Sharer requests chat with specific listener
**Auth**: Access token required
**Validation**: User must have "sharer" role

**Request Body**:

```json
{
  "listener_id": "507f1f77bcf86cd799439011",
  "topic": "anxiety"
}
```

**Implementation Steps**:

1. Verify listener exists and is available (`listener_availability: "available"`)
2. Check listener isn't in another active chat session
3. Create new chat\_session document:

- `sharer_id`: current user
- `listener_id`: from request
- `status: "active"`
- `started_at`: current timestamp
- `expires_at`: current timestamp + 24 hours
- `topic`: from request

4. Update listener availability to "in\_chat"
5. Send Socket.IO notification to listener: `chat_request` event with session details
6. Return chat session details

**Response (201)**:

```json
{
  "session_id": "507f1f77bcf86cd799439020",
  "listener": {
    "id": "507f1f77bcf86cd799439011",
    "pseudonym": "CaringListener",
    "profile_picture_url": "https://..."
  },
  "topic": "anxiety",
  "started_at": "2025-01-28T15:30:00Z",
  "status": "active"
}
```

**Socket.IO Event to Listener**:

```json
Event: "chat_request"
Data: {
  "session_id": "507f1f77bcf86cd799439020",
  "sharer": {
    "id": "507f1f77bcf86cd799439015",
    "pseudonym": "AnonymousSharer"
  },
  "topic": "anxiety"
}
```

**Error Responses**:

- 400: Listener not available or doesn't exist
- 403: User is not a sharer
- 409: Sharer already in active chat

---

### Chat Endpoints (backend/app/routes/chat.py)

#### GET /api/v1/chat/sessions/active

**Purpose**: Get user's current active chat session
**Auth**: Access token required

**Response (200)** if active session exists:

```json
{
  "session_id": "507f1f77bcf86cd799439020",
  "partner": {
    "id": "507f1f77bcf86cd799439011",
    "pseudonym": "CaringListener",
    "profile_picture_url": "https://...",
    "role": "listener"
  },
  "topic": "anxiety",
  "started_at": "2025-01-28T15:30:00Z",
  "user_role": "sharer"
}
```

**Response (200)** if no active session:

```json
{
  "session_id": null
}
```

---

#### GET /api/v1/chat/sessions/:sessionId/messages

**Purpose**: Get messages for specific chat session
**Auth**: Access token required
**Validation**: User must be participant in this session

**Query Parameters**:

- `limit`: (optional) Default 50, max 200
- `before`: (optional) Message ID for pagination

**Response (200)**:

```json
{
  "messages": [
    {
      "id": "507f1f77bcf86cd799439030",
      "sender_pseudonym": "CaringListener",
      "content": "Hi, I'm here to listen. How are you feeling?",
      "sent_at": "2025-01-28T15:31:00Z",
      "is_own_message": false
    },
    {
      "id": "507f1f77bcf86cd799439031",
      "sender_pseudonym": "AnonymousSharer",
      "content": "I've been feeling really anxious lately.",
      "sent_at": "2025-01-28T15:31:30Z",
      "is_own_message": true
    }
  ],
  "has_more": false
}
```

**Error Responses**:

- 403: User is not a participant in this session
- 404: Session not found

---

#### POST /api/v1/chat/sessions/:sessionId/end

**Purpose**: End active chat session
**Auth**: Access token required
**Validation**: User must be participant, session must be active

**Request Body**: None

**Implementation**:

1. Update chat\_sessions document:

- `status: "ended"`
- `ended_at`: current timestamp

2. Update both users' availability if they're listeners
3. Send Socket.IO `chat_ended` event to both participants
4. Return success

**Response (200)**:

```json
{
  "message": "Chat ended successfully",
  "session_id": "507f1f77bcf86cd799439020",
  "duration_minutes": 23
}
```

**Socket.IO Event to Both Users**:

```json
Event: "chat_ended"
Data: {
  "session_id": "507f1f77bcf86cd799439020",
  "ended_by": "507f1f77bcf86cd799439015",
  "feedback_required": true
}
```

**Error Responses**:

- 403: User not participant
- 404: Session not found
- 400: Session already ended

---

### Feedback Endpoints (backend/app/routes/feedback.py)

#### POST /api/v1/feedback

**Purpose**: Submit feedback for chat partner after session ends
**Auth**: Access token required

**Request Body**:

```json
{
  "chat_session_id": "507f1f77bcf86cd799439020",
  "rating": 5,
  "helpfulness": 5,
  "empathy": 5,
  "safety": 5,
  "comment": "Very helpful and understanding"
}
```

**Validation**:

- User must be participant in session
- Session must be ended (status: "ended")
- Ratings: 1-5 (integers)
- Comment: Max 500 characters, optional
- User can only submit feedback once per session

**Implementation**:

1. Create feedback document
2. Update reviewee's listener\_rating (recalculate average from all feedback)
3. Return success

**Response (201)**:

```json
{
  "message": "Feedback submitted successfully",
  "feedback_id": "507f1f77bcf86cd799439040"
}
```

**Error Responses**:

- 400: Invalid ratings or already submitted
- 403: User not participant
- 404: Session not found

---

### Reports Endpoints (backend/app/routes/reports.py)

#### POST /api/v1/reports

**Purpose**: Report user or message for abuse
**Auth**: Access token required

**Request Body**:

```json
{
  "reported_user_id": "507f1f77bcf86cd799439011",
  "chat_session_id": "507f1f77bcf86cd799439020",
  "message_id": "507f1f77bcf86cd799439031",
  "reason": "harassment",
  "description": "User sent inappropriate messages"
}
```

**Allowed reasons**: "harassment", "inappropriate", "spam", "safety\_concern", "other"

**Validation**:

- reported\_user\_id: Required
- chat\_session\_id: Optional (if report is about specific chat)
- message\_id: Optional (if report is about specific message)
- reason: Required, must be one of allowed values
- description: Required, max 1000 characters

**Response (201)**:

```json
{
  "message": "Report submitted successfully",
  "report_id": "507f1f77bcf86cd799439050"
}
```

---

### Admin Endpoints (backend/app/routes/admin.py)

**All admin endpoints require**:

- Access token with `is_admin: true`
- 403 error if user is not admin

---

#### GET /api/v1/admin/stats

**Purpose**: Get platform statistics
**Auth**: Admin access token required

**Response (200)**:

```json
{
  "total_users": 1523,
  "total_sharers": 985,
  "total_listeners": 632,
  "active_chats": 12,
  "available_listeners": 8,
  "total_chats_today": 45,
  "total_chats_all_time": 3421,
  "pending_reports": 3,
  "average_rating": 4.6
}
```

---

#### GET /api/v1/admin/users

**Purpose**: Get all users with filtering and pagination
**Auth**: Admin access token required

**Query Parameters**:

- `page`: Default 1
- `limit`: Default 20, max 100
- `role`: Filter by role ("sharer", "listener")
- `is_active`: Filter by active status (true/false)
- `search`: Search by pseudonym or email

**Response (200)**:

```json
{
  "users": [
    {
      "id": "507f1f77bcf86cd799439011",
      "email": "user@example.com",
      "pseudonym": "KindListener",
      "roles": ["listener"],
      "is_active": true,
      "is_admin": false,
      "listener_rating": 4.7,
      "listener_total_chats": 23,
      "created_at": "2025-01-15T10:30:00Z"
    }
  ],
  "total": 1523,
  "page": 1,
  "pages": 77
}
```

---

#### PATCH /api/v1/admin/users/:userId/ban

**Purpose**: Ban/unban user
**Auth**: Admin access token required

**Request Body**:

```json
{
  "is_active": false,
  "reason": "Multiple harassment reports"
}
```

**Implementation**:

1. Update user `is_active` field
2. If banning: End any active chat sessions
3. Create admin\_log entry
4. If user is online: Disconnect their Socket.IO connection

**Response (200)**:

```json
{
  "message": "User banned successfully",
  "user_id": "507f1f77bcf86cd799439011"
}
```

---

#### GET /api/v1/admin/reports

**Purpose**: Get all reports with filtering
**Auth**: Admin access token required

**Query Parameters**:

- `status`: Filter by status ("pending", "under\_review", "resolved", "dismissed")
- `page`: Default 1
- `limit`: Default 20

**Response (200)**:

```json
{
  "reports": [
    {
      "id": "507f1f77bcf86cd799439050",
      "reporter": {
        "id": "507f1f77bcf86cd799439015",
        "pseudonym": "AnonymousSharer"
      },
      "reported_user": {
        "id": "507f1f77bcf86cd799439011",
        "pseudonym": "BadListener"
      },
      "reason": "harassment",
      "description": "User sent inappropriate messages",
      "status": "pending",
      "created_at": "2025-01-28T16:00:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "pages": 1
}
```

---

#### PATCH /api/v1/admin/reports/:reportId

**Purpose**: Update report status and add resolution
**Auth**: Admin access token required

**Request Body**:

```json
{
  "status": "resolved",
  "resolution": "User has been warned and monitored"
}
```

**Implementation**:

1. Update report status, reviewed\_at, reviewed\_by
2. Create admin\_log entry

**Response (200)**:

```json
{
  "message": "Report updated successfully",
  "report_id": "507f1f77bcf86cd799439050"
}
```

---

## Socket.IO Real-Time Events (backend/app/sockets/)

### Connection Setup

**Client Connection** (frontend/src/lib/socket.ts):

```typescript
import io from 'socket.io-client';

const socket = io('http://localhost:5000', {
  auth: {
    token: accessToken // JWT from cookie/storage
  },
  transports: ['websocket']
});
```

**Server Authentication** (backend/app/sockets/**init**.py):

- On connection: Verify JWT token from `auth.token`
- If invalid: Disconnect with error
- If valid: Store user\_id in session, add socket to user's room

---

### Socket Events Specification

#### Event: "join\_chat"

**Direction**: Client → Server
**When**: User enters chat page
**Payload**:

```json
{
  "session_id": "507f1f77bcf86cd799439020"
}
```

**Server Action**:

1. Verify user is participant in session
2. Join socket to room `chat_${session_id}`
3. Emit `user_joined` to other participant

---

#### Event: "send\_message"

**Direction**: Client → Server
**When**: User sends chat message
**Payload**:

```json
{
  "session_id": "507f1f77bcf86cd799439020",
  "content": "Hello, how can I help?"
}
```

**Server Action**:

1. Validate user is participant in session
2. Validate content (max 2000 chars, not empty)
3. Run basic moderation check (keyword filter in moderation\_service.py)
4. Create message document in messages collection
5. Emit `new_message` to room `chat_${session_id}`

**Moderation Keywords (Flagged)**:

- Explicit sexual content keywords
- Contact information (phone numbers, email addresses)
- External meeting requests
- Self-harm keywords (flag for admin review, don't block)

If flagged: Set `moderation_status: "flagged"`, still deliver message but log for admin review

---

#### Event: "new\_message"

**Direction**: Server → Client
**When**: New message received in chat
**Payload**:

```json
{
  "message_id": "507f1f77bcf86cd799439031",
  "sender_id": "507f1f77bcf86cd799439011",
  "sender_pseudonym": "CaringListener",
  "content": "Hello, how can I help?",
  "sent_at": "2025-01-28T15:31:00Z",
  "is_own_message": false
}
```

**Client Action**: Append message to chat window, scroll to bottom

---

#### Event: "typing"

**Direction**: Client → Server
**When**: User is typing in message input
**Payload**:

```json
{
  "session_id": "507f1f77bcf86cd799439020"
}
```

**Server Action**: Emit `user_typing` to other participant only

---

#### Event: "user\_typing"

**Direction**: Server → Client
**Payload**:

```json
{
  "pseudonym": "CaringListener"
}
```

**Client Action**: Show "CaringListener is typing..." indicator for 3 seconds

---

#### Event: "leave\_chat"

**Direction**: Client → Server
**When**: User leaves chat page
**Payload**:

```json
{
  "session_id": "507f1f77bcf86cd799439020"
}
```

**Server Action**: Remove socket from room `chat_${session_id}`

---

#### Event: "chat\_ended"

**Direction**: Server → Client (broadcast)
**When**: Chat session is ended by either participant
**Payload**:

```json
{
  "session_id": "507f1f77bcf86cd799439020",
  "ended_by": "507f1f77bcf86cd799439015",
  "feedback_required": true
}
```

**Client Action**: Show feedback modal, redirect to dashboard after feedback

---

#### Event: "status\_change"

**Direction**: Client → Server
**When**: Listener changes availability status
**Payload**:

```json
{
  "availability": "available"
}
```

**Server Action**:

1. Update user's `listener_availability` in database
2. Broadcast availability to all clients in matching queue

---

#### Event: "listener\_status\_update"

**Direction**: Server → Clients (broadcast to matching queue)
**When**: Listener changes availability
**Payload**:

```json
{
  "listener_id": "507f1f77bcf86cd799439011",
  "availability": "available"
}
```

**Client Action**: Update listener's status in match list if displayed

---

## Frontend Implementation Details

### Authentication Flow (frontend/src/lib/auth.ts)

**Login Process**:

1. User submits LoginForm (frontend/src/components/auth/LoginForm.tsx)
2. Form validates locally (email format, password not empty)
3. POST to /api/v1/auth/login
4. On success:

- Tokens stored in httpOnly cookies (automatic)
- User object stored in Zustand authStore
- Redirect to /dashboard

5. On error:

- Show error message below form
- Highlight invalid fields

**Google OAuth Flow**:

1. User clicks GoogleAuthButton (frontend/src/components/auth/GoogleAuthButton.tsx)
2. Open Google OAuth popup using Google Identity Services
3. User authorizes
4. Receive credential (JWT from Google)
5. POST credential to /api/v1/auth/google
6. On success: Same as login
7. On error: Show error toast

**Protected Routes** (frontend/src/app/layout.tsx):

- Middleware checks for access\_token cookie
- If missing or expired: Attempt refresh using /api/v1/auth/refresh
- If refresh succeeds: Continue
- If refresh fails: Redirect to /login
- Store attempted URL for post-login redirect

**Token Refresh Strategy**:

- On 401 response from any API call: Attempt token refresh
- Use refresh token from cookie
- If success: Retry original request
- If fail: Logout and redirect to login

---

### Matching Flow (frontend/src/app/sharer/find-listener/page.tsx)

**UI Layout**:

```
┌─────────────────────────────────────────┐
│  Find a Listener                        │
├─────────────────────────────────────────┤
│                                         │
│  What would you like to talk about?    │
│  ┌─────────────────────────────────┐   │
│  │ anxiety                         │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Language preference:                  │
│  [ ] English  [ ] Spanish  [ ] French  │
│                                         │
│  [Find Listeners Button]               │
│                                         │
├─────────────────────────────────────────┤
│  Suggested Listeners:                   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ 👤 CaringListener      ⭐ 4.8   │   │
│  │ "Here to help with anxiety..."  │   │
│  │ Topics: anxiety, stress         │   │
│  │ 45 chats                        │   │
│  │                                 │   │
│  │        [Connect]                │   │
│  └─────────────────────────────────┘   │
│                                         │
│  [2 more similar cards]                │
│                                         │
└─────────────────────────────────────────┘
```

**Flow Steps**:

1. Page loads, show topic input and preference selectors
2. User selects topic (optional, free text or dropdown of common topics)
3. User selects language preference (checkboxes for multiple)
4. Click "Find Listeners" button
5. Show loading spinner
6. POST to /api/v1/match/find-listeners with preferences
7. Display top 3 matches as MatchCard components (frontend/src/components/matching/MatchCard.tsx)
8. User reviews cards and clicks "Connect" on one
9. POST to /api/v1/match/request-chat with listener\_id
10. On success: Redirect to /sharer/chat/[sessionId]
11. On error (listener unavailable): Show toast, refresh match list

**Match Card Component** (MatchCard.tsx):

- Display pseudonym, profile picture (if show\_profile\_picture: true), rating
- Show bio (truncated to 100 chars with "read more")
- Show listener topics as tags
- Show total chats count
- "Connect" button

**Edge Cases**:

- No matches found: Show message "No listeners available right now. Try different preferences or check back soon."
- Only 1-2 matches: Show only those, with message "Limited availability"
- All matches become unavailable while browsing: Show toast "These listeners are no longer available" and refresh list

---

### Chat Interface (frontend/src/app/sharer/chat/[sessionId]/page.tsx)

**UI Layout**:

```
┌─────────────────────────────────────────┐
│ 👤 CaringListener          [End Chat]  │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ CaringListener: Hi, I'm here to │   │
│  │ listen. How are you feeling?    │   │
│  │                     15:31        │   │
│  └─────────────────────────────────┘   │
│                                         │
│     ┌─────────────────────────────┐    │
│     │ You: I've been feeling      │    │
│     │ really anxious lately.      │    │
│     │                 15:31        │    │
│     └─────────────────────────────┘    │
│                                         │
│  [CaringListener is typing...]         │
│                                         │
├─────────────────────────────────────────┤
│ Type your message...        [Send]     │
└─────────────────────────────────────────┘
```

**Implementation** (ChatWindow component):

**On Page Load**:

1. Extract sessionId from URL params
2. Verify user has access: GET /api/v1/chat/sessions/active
3. If no active session or sessionId mismatch: Redirect to dashboard
4. GET /api/v1/chat/sessions/:sessionId/messages to load history
5. Initialize Socket.IO connection
6. Emit "join\_chat" event with sessionId
7. Listen for "new\_message", "user\_typing", "chat\_ended" events

**Message Display** (MessageList.tsx):

- Messages displayed in scrollable container
- Own messages aligned right with blue background (#3b82f6)
- Partner messages aligned left with gray background (#e5e7eb)
- Show pseudonym above each message
- Timestamp below message (format: HH:MM)
- Auto-scroll to bottom on new message
- "Load more" button at top for pagination

**Message Input** (MessageInput.tsx):

- Textarea with max 2000 characters
- Character counter: "1850/2000"
- "Send" button disabled if empty or over limit
- On typing: Emit "typing" event (throttled to once per 2 seconds)
- On Enter key (without Shift): Send message
- On Shift+Enter: New line
- On send: Emit "send\_message" event, clear input, disable until delivered

**Typing Indicator**:

- Listen for "user\_typing" event
- Show "[Partner] is typing..." for 3 seconds
- Position above message input

**End Chat**:

- "End Chat" button in header
- On click: Show confirmation modal
- "Are you sure you want to end this chat?"
- [Cancel] [End Chat]
- If confirmed: POST to /api/v1/chat/sessions/:sessionId/end
- On success: Listen for "chat\_ended" event, show FeedbackModal

**Feedback Modal** (frontend/src/components/feedback/FeedbackModal.tsx):

```
┌─────────────────────────────────────────┐
│  How was your experience?               │
├─────────────────────────────────────────┤
│                                         │
│  Overall Rating:                        │
│  ⭐⭐⭐⭐⭐                                │
│                                         │
│  Helpfulness: ⭐⭐⭐⭐⭐                   │
│  Empathy: ⭐⭐⭐⭐⭐                       │
│  Safety: ⭐⭐⭐⭐⭐                        │
│                                         │
│  Additional Comments (optional):        │
│  ┌─────────────────────────────────┐   │
│  │                                 │   │
│  └─────────────────────────────────┘   │
│                                         │
│  [Skip]              [Submit Feedback] │
└─────────────────────────────────────────┘
```

**Feedback Submission**:

- Star ratings: Click to select 1-5 stars, highlight selected
- Comment: Optional textarea, max 500 chars
- "Skip" button: Close modal, redirect to dashboard
- "Submit" button: POST to /api/v1/feedback, then redirect
- After 30 seconds: Auto-show "Skip" prominently (user may have left)

---

### Listener Queue (frontend/src/app/listener/queue/page.tsx)

**UI Layout**:

```
┌─────────────────────────────────────────┐
│  Listener Dashboard                     │
├─────────────────────────────────────────┤
│                                         │
│  Your Status:                           │
│  ○ Available  ○ Unavailable            │
│                                         │
│  Your Stats:                           │
│  Rating: ⭐ 4.7                        │
│  Total Chats: 23                       │
│                                         │
├─────────────────────────────────────────┤
│  Waiting for Sharers...                │
│                                         │
│  You'll be notified when someone       │
│  wants to talk.                        │
│                                         │
└─────────────────────────────────────────┘
```

**Implementation**:

**On Page Load**:

1. GET /api/v1/users/me to get current availability and stats
2. Display current status and stats
3. Initialize Socket.IO connection
4. Listen for "chat\_request" event

**Status Toggle**:

- Radio buttons for "Available" / "Unavailable"
- On change: PATCH /api/v1/users/me/availability
- Emit "status\_change" Socket.IO event
- Update UI to reflect new status
- If switching to "Available": Show "Waiting for Sharers..." message
- If switching to "Unavailable": Show "You are not visible to Sharers"

**Chat Request Notification**:

- Listen for "chat\_request" Socket.IO event
- Show toast notification: "New chat request from [Pseudonym]"
- Auto-redirect to /listener/chat/[sessionId] after 2 seconds
- Play notification sound (optional)

**Edge Case - Already in Chat**:

- If listener has active session: Show "Currently in Chat" with link to session
- Disable "Available" status toggle

---

### Profile Page (frontend/src/app/profile/page.tsx)

**UI Sections**:

1. **Basic Information**:

- Pseudonym (editable, shows availability indicator)
- Real name (editable, with note: "Never shown to other users")
- Email (display only, not editable)
- Bio (textarea, 500 char limit)
- Profile picture upload (AvatarUpload component)

2. **Roles & Interests**:

- Roles: Checkboxes for "Sharer" and "Listener" (at least one required)
- Interests: Tag input (e.g., "anxiety", "relationships", "stress")
- Languages: Multi-select dropdown

3. **Listener Settings** (only if "Listener" role checked):

- Topics: Tag input for topics comfortable discussing
- Current stats (display only): Rating, Total Chats

4. **Privacy Settings**:

- Toggle: "Show profile picture to chat partners"
- Toggle: "Allow feedback after chats"

**Form Behavior**:

- All changes save on "Save Profile" button click
- PATCH to /api/v1/users/me with all fields
- Show success toast on save
- Show validation errors inline
- Unsaved changes warning if user navigates away

**Avatar Upload** (AvatarUpload component):

- Current avatar displayed (or placeholder if none)
- "Change Picture" button opens file picker
- Preview image before upload
- POST to /api/v1/users/me/avatar
- Show upload progress bar
- Update profile picture URL on success

---

### Admin Panel (frontend/src/app/admin/page.tsx)

**Dashboard View**:

```
┌─────────────────────────────────────────┐
│  Platform Statistics                    │
├─────────────────────────────────────────┤
│  ┌────────┐ ┌────────┐ ┌────────┐      │
│  │ 1,523  │ │   12   │ │  4.6   │      │
│  │ Users  │ │ Active │ │ Rating │      │
│  └────────┘ └────────┘ └────────┘      │
│                                         │
│  ┌────────┐ ┌────────┐ ┌────────┐      │
│  │  632   │ │    8   │ │   3    │      │
│  │Listens │ │Availbl │ │Reports │      │
│  └────────┘ └────────┘ └────────┘      │
└─────────────────────────────────────────┘
```

**Navigation**:

- Tabs: Dashboard | Users | Reports
- GET /api/v1/admin/stats for dashboard stats
- Render StatsCard components for each metric

**Users Tab** (admin/users/page.tsx):

- Table showing all users (UserTable component)
- Columns: Pseudonym, Email, Roles, Rating, Chats, Status, Actions
- Search bar filters by pseudonym or email
- Role filter dropdown
- Status filter: Active / Banned
- Pagination controls
- Actions per row:
- "Ban" button (if active) → Shows confirmation modal
- "Unban" button (if banned)
- "View Details" → Expand row to show full profile

**Ban User Action**:

- Confirmation modal: "Are you sure? This will end any active chats."
- Reason textarea (required)
- PATCH /api/v1/admin/users/:userId/ban
- Refresh table on success

**Reports Tab** (admin/reports/page.tsx):

- Table showing all reports (ReportTable component)
- Columns: Date, Reporter, Reported User, Reason, Status, Actions
- Status filter: Pending / Under Review / Resolved / Dismissed
- Click row to expand and show:
- Full description
- Related chat session (if any)
- Related message (if any)
- Admin resolution section (textarea + status dropdown)
- Save resolution: PATCH /api/v1/admin/reports/:reportId

---

## Background Jobs & Cleanup (backend/app/services/cleanup\_service.py)

**24-Hour Message Deletion Job**:

**Purpose**: Auto-delete messages and chat sessions after 24 hours for privacy

**Implementation**:

- Use APScheduler (or similar) to run every hour
- Query messages collection: `expires_at < current_time`
- Delete matching messages
- Query chat\_sessions collection: `expires_at < current_time AND status != "active"`
- Delete matching sessions

**Alternative Implementation** (MongoDB TTL Index):

- Create TTL index on messages collection: `db.messages.createIndex({ "expires_at": 1 }, { expireAfterSeconds: 0 })`
- Create TTL index on chat\_sessions collection: `db.chat_sessions.createIndex({ "expires_at": 1 }, { expireAfterSeconds: 0 })`
- MongoDB automatically deletes expired documents

**Recommended**: Use MongoDB TTL indexes for automatic cleanup

---

## Environment Variables

### Frontend (.env.local)

```
NEXT_PUBLIC_API_URL=http://localhost:5000/api/v1
NEXT_PUBLIC_SOCKET_URL=http://localhost:5000
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id_here
```

### Backend (.env)

```
# Flask
FLASK_ENV=development
SECRET_KEY=your_secret_key_here_generate_random_string
FLASK_APP=run.py

# MongoDB
MONGODB_URI=mongodb://localhost:27017/empathy_platform

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your_jwt_secret_here_different_from_flask_secret
JWT_ACCESS_TOKEN_EXPIRES=900  # 15 minutes in seconds
JWT_REFRESH_TOKEN_EXPIRES=604800  # 7 days in seconds

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:5000/api/v1/auth/google/callback

# File Upload (optional, use local storage for initial implementation)
UPLOAD_FOLDER=uploads/avatars
MAX_UPLOAD_SIZE=5242880  # 5MB in bytes

# CORS
CORS_ORIGINS=http://localhost:3000

# Moderation
MODERATION_ENABLED=true
```

---

## Initialization & Setup Files

### Frontend package.json Dependencies

```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "socket.io-client": "^4.6.0",
    "zustand": "^4.4.0",
    "react-hook-form": "^7.48.0",
    "@tanstack/react-query": "^5.0.0",
    "tailwindcss": "^3.3.0",
    "lucide-react": "^0.294.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "typescript": "^5.2.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.31"
  }
}
```

### Backend requirements.txt

```
Flask==3.0.0
Flask-CORS==4.0.0
Flask-JWT-Extended==4.6.0
Flask-SocketIO==5.3.5
pymongo==4.6.0
redis==5.0.1
python-socketio==5.10.0
python-engineio==4.8.0
eventlet==0.33.3
Authlib==1.3.0
marshmallow==3.20.1
python-dotenv==1.0.0
bcrypt==4.1.2
APScheduler==3.10.4
```

---

## Data Seeding Script (scripts/seed\_db.py)

**Purpose**: Create test users for development

**Implementation**:

```python
# Script creates following test users:
# 1. Admin user
#    - email: admin@example.com
#    - password: Admin123!
#    - pseudonym: AdminUser
#    - is_admin: true

# 2. Test Sharer
#    - email: sharer@example.com
#    - password: Sharer123!
#    - pseudonym: TestSharer
#    - roles: ["sharer"]

# 3. Test Listener 1
#    - email: listener1@example.com
#    - password: Listener123!
#    - pseudonym: CaringListener
#    - roles: ["listener"]
#    - listener_topics: ["anxiety", "stress", "depression"]
#    - listener_availability: "available"
#    - listener_rating: 4.8

# 4. Test Listener 2
#    - email: listener2@example.com
#    - password: Listener123!
#    - pseudonym: EmpathyFirst
#    - roles: ["listener"]
#    - listener_topics: ["relationships", "loneliness"]
#    - listener_availability: "available"
#    - listener_rating: 4.5

# 5. Test Dual Role User
#    - email: both@example.com
#    - password: Both123!
#    - pseudonym: FlexibleHelper
#    - roles: ["sharer", "listener"]
```

**Run with**: `python scripts/seed_db.py`

---

## Docker Configuration

### docker/frontend.Dockerfile

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

### docker/backend.Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./

EXPOSE 5000

CMD ["python", "run.py"]
```

### docker/docker-compose.yml

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: ../
      dockerfile: docker/backend.Dockerfile
    ports:
      - "5000:5000"
    environment:
      - MONGODB_URI=mongodb://mongodb:27017/empathy_platform
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - ../backend/.env
    depends_on:
      - mongodb
      - redis

  frontend:
    build:
      context: ../
      dockerfile: docker/frontend.Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:5000/api/v1
      - NEXT_PUBLIC_SOCKET_URL=http://localhost:5000
    depends_on:
      - backend

volumes:
  mongo_data:
```

---

## CI/CD Pipeline (.github/workflows/ci-cd.yml)

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run tests
        run: |
          cd backend
          python -m pytest tests/

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Node
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        run: |
          cd frontend
          npm install

      - name: Run linter
        run: |
          cd frontend
          npm run lint

      - name: Build
        run: |
          cd frontend
          npm run build

  docker-build:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker images
        run: |
          docker-compose -f docker/docker-compose.yml build
```

---

## Additional Implementation Details

### Text Moderation (backend/app/services/moderation\_service.py)

**Basic Keyword Filter**:

**Blocked Keywords** (prevent message from sending):

- Contact sharing: Phone number patterns (regex: `\b\d{3}[-.]?\d{3}[-.]?\d{4}\b`)
- Email patterns (regex: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b`)
- Social media: "whatsapp", "telegram", "snapchat", "instagram" + username patterns
- Meeting requests: "meet me", "my address", "come to"

**Flagged Keywords** (allowed but logged for admin review):

- Self-harm indicators: "kill myself", "end it all", "suicide"
- Severe distress: "hurt myself", "can't go on"

**Function**:

```python
def moderate_message(content: str) -> dict:
    """
    Returns: {
        "status": "approved" | "blocked" | "flagged",
        "reason": str | None
    }
    """
    # Check blocked patterns
    # Check flagged patterns
    # Return result
```

**Usage**: Called in Socket.IO "send\_message" handler before saving message

---

### Rate Limiting (backend/app/middleware/rate\_limit.py)

**Limits**:

- Authentication endpoints: 5 requests per minute per IP
- Message sending: 30 messages per minute per user
- API endpoints: 100 requests per minute per user
- Admin endpoints: 200 requests per minute

**Implementation**: Use Flask-Limiter with Redis backend

**Decorator Usage**:

```python
from flask_limiter import Limiter

@limiter.limit("5 per minute")
def login():
    ...
```

---

## Testing Strategy

### Backend Tests (backend/tests/)

**test\_auth.py**:

- Test registration with valid data
- Test registration with duplicate email
- Test login with correct credentials
- Test login with wrong password
- Test JWT token validation
- Test Google OAuth flow

**test\_matching.py**:

- Test matching algorithm scoring
- Test matching with no available listeners
- Test matching with language filter
- Test matching with topic filter
- Test exclusion of recent matches

**test\_chat.py**:

- Test chat session creation
- Test message sending
- Test message retrieval
- Test chat ending
- Test 24-hour expiration

**test\_moderation.py**:

- Test blocked keyword detection
- Test flagged keyword detection
- Test pattern matching (phone, email)

**test\_admin.py**:

- Test ban user functionality
- Test report resolution
- Test stats retrieval

---

## UI/UX Design Specifications

### Color Palette (Calming & Accessible)

- **Primary**: #3b82f6 (Blue) - Trust, calm
- **Secondary**: #10b981 (Green) - Growth, safety
- **Background**: #ffffff (White)
- **Surface**: #f9fafb (Light gray)
- **Text Primary**: #1f2937 (Dark gray)
- **Text Secondary**: #6b7280 (Medium gray)
- **Error**: #ef4444 (Red)
- **Warning**: #f59e0b (Amber)
- **Success**: #10b981 (Green)

### Typography

- **Font Family**: Inter (sans-serif) or system default
- **Headings**: 24px - 32px, font-weight 700
- **Body**: 16px, font-weight 400, line-height 1.6
- **Small**: 14px

### Spacing

- Use 4px base unit (4, 8, 12, 16, 24, 32, 48, 64)
- Consistent padding: 16px for cards, 24px for pages
- Consistent margins between sections: 24px

### Accessibility Requirements

- **WCAG 2.1 Level AA** compliance
- Color contrast ratio minimum 4.5:1 for text
- Focus indicators on all interactive elements (2px blue outline)
- Keyboard navigation support (Tab, Enter, Escape)
- Screen reader support:
- Semantic HTML (nav, main, article, section)
- ARIA labels on icons and interactive elements
- Alt text on images
- Font size: Minimum 16px, user can zoom to 200%
- Touch targets: Minimum 44x44px on mobile

### Responsive Breakpoints

- **Mobile**: 320px - 640px
- **Tablet**: 641px - 1024px
- **Desktop**: 1025px+

**Mobile-first approach**: Design for mobile, enhance for desktop

---

## Future Enhancements (Post-MVP)

**Documented for future development**:

1. **Audio/Video Calls**:

- Integration with WebRTC
- Toggle between text and voice
- Requires additional consent and moderation

2. **Group Support Sessions**:

- Multiple Sharers with one or more Listeners
- Scheduled sessions
- Topic-based rooms

3. **AI-Powered Features**:

- Sentiment analysis on messages (detect distress)
- Automated chat summaries
- Smart matching improvements (ML-based)
- Crisis detection and auto-escalation

4. **Multi-language Support**:

- i18n implementation (next-i18next)
- Translation service integration
- Language-specific content moderation

5. **Mobile Apps**:

- React Native for iOS/Android
- Push notifications for chat requests
- Offline message queuing

6. **Advanced Moderation**:

- AI-powered content moderation (e.g., Perspective API)
- Automated pattern detection
- User reputation system

7. **Analytics Dashboard**:

- Platform usage metrics
- User engagement tracking
- Outcome measurements

8. **Listener Training**:

- Built-in training modules
- Certification system
- Best practices library

---

## Documentation Files to Create

### README.md (Root)

```markdown
# Empathetic Listening Platform

A peer support platform connecting people who need someone to listen with volunteer listeners.

## Quick Start

### Prerequisites
- Node.js 20+
- Python 3.11+
- MongoDB 7.0+
- Redis 7+

### Development Setup

1. Clone repository
2. Install dependencies:
   ```bash
   cd frontend && npm install
   cd ../backend && pip install -r requirements.txt
```

3. Copy environment files:

```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.local.example frontend/.env.local
```

4. Start MongoDB and Redis
5. Seed database:

```bash
   python scripts/seed_db.py
```

6. Start backend:

```bash
   cd backend && python run.py
```

7. Start frontend:

```bash
   cd frontend && npm run dev
```

8. Open http://localhost:3000

### Test Users

- Admin: admin@example.com / Admin123!
- Sharer: sharer@example.com / Sharer123!
- Listener: listener1@example.com / Listener123!

## Documentation

- [Setup Guide](docs/SETUP.md)
- [API Documentation](docs/API.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Deployment](docs/DEPLOYMENT.md)

## Technology Stack

- Frontend: Next.js 14, TailwindCSS, Socket.IO
- Backend: Python Flask, Flask-SocketIO
- Database: MongoDB, Redis
- Auth: JWT, Google OAuth

## License

MIT

```
### docs/SETUP.md
Detailed setup instructions including:
- System requirements
- Installation steps for all dependencies
- Configuration guide
- Common issues and troubleshooting
- Development workflow

### docs/API.md
Complete API documentation including:
- All endpoints with examples
- Request/response formats
- Error codes and handling
- Socket.IO events
- Authentication flow

### docs/ARCHITECTURE.md
System architecture documentation including:
- Component diagram
- Data flow diagrams
- Database schema explanation
- Technology choices rationale
- Scalability considerations

### docs/DEPLOYMENT.md
Deployment guide including:
- Docker deployment
- Environment configuration for production
- Database setup and migrations
- Monitoring and logging
- Backup strategies
- Security best practices

---

## Security Considerations

### Authentication Security
- Passwords hashed with bcrypt (cost factor 12)
- JWT tokens in httpOnly cookies (prevents XSS)
- CSRF protection with SameSite cookies
- Refresh token rotation
- Token blacklist for logout

### Data Privacy
- Always anonymous: Real names never exposed in chats
- 24-hour auto-deletion of messages and sessions
- Encrypted in transit (HTTPS required in production)
- Minimal data collection
- GDPR-compliant (right to deletion, data export)

### Input Validation
- All user inputs validated on backend
- SQL injection prevention (using PyMongo parameterization)
- XSS prevention (React auto-escaping, CSP headers)
- File upload validation (type, size, sanitization)
- Rate limiting on all endpoints

### Moderation & Safety
- Keyword-based content filter
- Abuse reporting system
- Admin review queue
- User ban functionality
- Emergency resources (crisis hotline info displayed)

### Infrastructure
- Environment variables for secrets (never commit)
- Principle of least privilege for database access
- Regular security updates
- Logging of admin actions
- API request logging for audit trail

---

## Performance Optimization

### Backend
- MongoDB indexes:
  - users: `email`, `pseudonym`, `listener_availability`
  - chat_sessions: `sharer_id`, `listener_id`, `status`, `expires_at` (TTL)
  - messages: `chat_session_id`, `expires_at` (TTL)
  - feedback: `reviewee_id`, `chat_session_id`
  - reports: `status`, `reported_user_id`
- Redis for session storage and real-time status
- Connection pooling for MongoDB
- Async Socket.IO with Eventlet

### Frontend
- Next.js SSR for initial page load
- Code splitting and lazy loading
- Image optimization (Next.js Image component)
- React.memo for expensive components
- Virtual scrolling for long message lists
- Debouncing on search inputs
- Socket.IO reconnection handling

---

## Monitoring & Logging

### Backend Logging
- Request/response logging (Flask logger)
- Error tracking (exceptions logged with stack traces)
- Socket.IO connection/disconnection events
- Admin action logging (admin_logs collection)
- Moderation events (flagged messages)

**Log Levels**:
- DEBUG: Development only
- INFO: Important events (user login, chat start/end)
- WARNING: Moderation triggers, rate limit hits
- ERROR: Exceptions, failed operations

### Frontend Error Handling
- Global error boundary for React errors
- API error logging to backend
- Socket.IO error events
- User-friendly error messages (no technical details)

### Metrics to Track (Future)
- User registration rate
- Daily/monthly active users
- Average chat duration
- Listener availability rate
- Match success rate
- Average listener rating
- Report frequency

---

## Summary of Key Implementation Points

### Critical Features
1. **Always Anonymous**: Pseudonyms only, never expose real names
2. **Hybrid Matching**: Top 3 suggestions, user picks
3. **24-Hour Deletion**: Auto-delete messages/sessions for privacy
4. **Real-Time Chat**: Socket.IO for instant messaging
5. **Dual Roles**: Users can be both Sharer and Listener
6. **Safety First**: Moderation, reporting, admin controls

### Technical Highlights
- **Next.js 14 App Router**: Modern React framework
- **Flask + Socket.IO**: Python backend with real-time support
- **MongoDB + Redis**: Flexible data storage + fast caching
- **JWT + OAuth**: Secure authentication with social login
- **TailwindCSS**: Utility-first styling
- **Docker Ready**: Containerized deployment
- **CI/CD**: GitHub Actions workflow

### Development Workflow
1. Setup local environment (MongoDB, Redis)
2. Run seed script for test data
3. Start backend (Flask on :5000)
4. Start frontend (Next.js on :3000)
5. Test with provided test users
6. Iterate and develop features
7. Run tests before committing
8. Deploy with Docker Compose

### Testing Checklist
- [ ] User registration and login
- [ ] Google OAuth login
- [ ] Profile creation and editing
- [ ] Sharer finding listeners (hybrid matching)
- [ ] Real-time chat messaging
- [ ] Typing indicators
- [ ] Chat ending and feedback
- [ ] Listener availability toggle
- [ ] Report submission
- [ ] Admin user/report management
- [ ] 24-hour message deletion (verify TTL indexes)
- [ ] Mobile responsiveness
- [ ] Accessibility (keyboard navigation, screen readers)

---

## Conclusion

This implementation plan provides complete specifications for building a full-featured empathetic listening platform. Every aspect has been detailed:

✅ **Architecture**: Clear separation of frontend/backend, real-time communication
✅ **Database**: Complete schema with all collections and relationships
✅ **API**: All endpoints specified with request/response formats
✅ **Real-Time**: Socket.IO events for chat and status updates
✅ **Matching**: Hybrid algorithm with scoring system
✅ **UI/UX**: Page layouts, component structure, accessibility
✅ **Security**: Authentication, privacy, moderation, safety
✅ **Deployment**: Docker configuration, CI/CD pipeline
✅ **Documentation**: Setup, API, architecture guides
✅ **Testing**: Test strategy and checklist

The implementation agent can now build this platform exactly as specified with zero ambiguity.
```
