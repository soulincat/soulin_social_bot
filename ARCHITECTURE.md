# Architecture Overview

## System Type: Flask Backend + Vanilla JavaScript Frontend

This is **NOT** a React app. It's a traditional server-rendered Flask application with vanilla JavaScript for interactivity.

## Architecture Pattern

```
┌─────────────────────────────────────────────────────────┐
│                    Flask Backend                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Routes     │  │   Auth       │  │   API        │ │
│  │  /workspace  │  │  Middleware  │  │  Endpoints   │ │
│  │  /dashboard  │  │  Decorators  │  │  /api/*      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Supabase Storage Layer                   │   │
│  │  (content/supabase_storage.py)                   │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Supabase Database                      │
│  - PostgreSQL (clients, posts, derivatives, etc.)       │
│  - Supabase Auth (user authentication)                 │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              HTML Templates (Server-Rendered)           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ workspace.html│  │ login.html   │  │ dashboard    │ │
│  │              │  │              │  │ (via Flask)   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │      Vanilla JavaScript (Client-Side)             │   │
│  │  - fetch() API calls                             │   │
│  │  - DOM manipulation                               │   │
│  │  - No framework dependencies                      │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Backend (Flask)
- **File**: `app.py`
- **Purpose**: Main server application
- **Responsibilities**:
  - Serve HTML templates
  - Handle API endpoints (`/api/*`)
  - Authentication middleware
  - Session management
  - Route protection

### 2. Frontend (Vanilla JavaScript)
- **Location**: `web/templates/*.html` (inline `<script>` tags)
- **Purpose**: Client-side interactivity
- **No Framework**: Pure JavaScript, no React/Vue/Angular
- **API Communication**: Uses `fetch()` API
- **State Management**: Local variables, no global state library

### 3. Storage Layer
- **File**: `content/supabase_storage.py`
- **Purpose**: Abstraction over Supabase
- **Fallback Chain**:
  1. Supabase (primary)
  2. Vercel KV (if Supabase unavailable)
  3. JSON files (local dev)
  4. In-memory cache (session)

### 4. Database (Supabase)
- **Type**: PostgreSQL via Supabase
- **Tables**: `clients`, `posts`, `derivatives`, `user_clients`, etc.
- **Auth**: Supabase Auth (JWT tokens)

## Request Flow

### Example: Loading Workspace Projects

```
1. User visits /workspace
   ↓
2. Flask serves workspace.html template
   ↓
3. Browser loads HTML + CSS + inline JavaScript
   ↓
4. JavaScript calls: fetch('/api/workspace/projects')
   ↓
5. Flask route handler:
   - Checks authentication (@require_auth)
   - Loads clients from Supabase
   - Fetches metrics (parallelized, cached)
   - Returns JSON
   ↓
6. JavaScript receives JSON
   ↓
7. JavaScript renders project cards via DOM manipulation
```

## Is This a Separate System?

**No, it's all one integrated Flask application.**

- **Backend and Frontend**: Same codebase, same server
- **Templates**: Served directly by Flask
- **API**: Same Flask app, different routes
- **No Build Step**: No webpack, no bundler, no npm build
- **Static Files**: Served from `web/` directory

## Why Not React?

This architecture was chosen for:
- ✅ **Simplicity**: No build pipeline, no npm dependencies
- ✅ **Fast Development**: Direct HTML/JS editing
- ✅ **Server-Side Rendering**: Templates rendered by Flask
- ✅ **Small Footprint**: No framework overhead
- ✅ **Easy Deployment**: Single Flask app, no separate frontend build

## Can We Add React Later?

**Yes, but it would require restructuring:**

1. **Option A: Keep Flask as API-only**
   - Move templates to React app
   - Flask becomes pure REST API
   - React app calls Flask API
   - Requires separate deployment/build

2. **Option B: Hybrid Approach**
   - Keep some pages as Flask templates
   - Add React for specific components
   - Use React via CDN (no build step)
   - More complex, not recommended

3. **Option C: Current Architecture (Recommended)**
   - Keep vanilla JS
   - Add more structure if needed (modules, components)
   - No framework overhead
   - Works well for this use case

## Performance Optimizations

### Workspace API (`/api/workspace/projects`)
- ✅ **Parallel Requests**: Uses `ThreadPoolExecutor` to fetch metrics concurrently
- ✅ **Caching**: 5-minute in-memory cache per user
- ✅ **Error Handling**: Graceful degradation if metrics fail

### Caching Strategy
```python
# Cache key: workspace_projects_{user_id}
# TTL: 5 minutes
# Storage: In-memory dict (thread-safe with Lock)
```

## File Structure

```
soulin_social_bot/
├── app.py                    # Flask server (routes, API, auth)
├── content/
│   └── supabase_storage.py   # Database abstraction layer
├── web/
│   ├── templates/            # HTML templates (server-rendered)
│   │   ├── workspace.html
│   │   ├── login.html
│   │   └── ...
│   ├── styles/              # CSS files
│   └── assets/              # Images, fonts
└── supabase_schema.sql       # Database schema
```

## Authentication Flow

```
1. User submits login form (login.html)
   ↓
2. JavaScript: fetch('/api/auth/login', { email, password })
   ↓
3. Flask: Calls Supabase Auth API
   ↓
4. Supabase: Validates credentials, returns JWT token
   ↓
5. Flask: Stores token in session
   ↓
6. JavaScript: Stores token in sessionStorage
   ↓
7. Redirect to /workspace
   ↓
8. Subsequent requests: Include token in Authorization header
   ↓
9. Flask middleware: Verifies token with Supabase
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Sign up
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

### Workspace
- `GET /api/workspace/projects` - List projects (cached, parallelized)
- `POST /api/workspace/cache/clear` - Clear cache

### Dashboard
- `GET /api/dashboard/growth?client_id=xxx`
- `GET /api/dashboard/socials?client_id=xxx`
- `GET /api/dashboard/products?client_id=xxx`

## Development Workflow

1. **Edit Templates**: Modify `web/templates/*.html`
2. **Edit Backend**: Modify `app.py`
3. **Restart Server**: `python app.py`
4. **No Build Step**: Changes are immediate

## Deployment

- **Single Deployment**: Just deploy Flask app
- **No Frontend Build**: Templates are served directly
- **Static Files**: Served by Flask from `web/` directory
- **Environment Variables**: Set `SUPABASE_URL`, `SUPABASE_KEY`

## Summary

- ✅ **Flask Backend**: Server-rendered templates + API
- ✅ **Vanilla JavaScript**: No React, no framework
- ✅ **Integrated System**: Backend and frontend in same codebase
- ✅ **Supabase**: Database + Auth
- ✅ **Simple & Fast**: No build pipeline, direct development

This is a **traditional web application** architecture, not a modern SPA (Single Page Application). It's simpler, faster to develop, and perfectly suited for this use case.


