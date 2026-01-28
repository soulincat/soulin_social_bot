# Soulin Social Bot - Complete System Architecture & Workflow

> **📸 Visual Diagram**: A visual architecture diagram has been generated and saved alongside this document.

## 🏗️ System Overview

A comprehensive **multi-platform content creation and metrics tracking system** combining:
- **Telegram Bot** for automated reporting and content commands
- **Flask Web Dashboard** for visual management and analytics
- **AI-Powered Content System** for multi-platform content generation
- **Funnel Analytics** for marketing performance tracking
- **Brand Persona Engine** for personalized content generation

---

## 📊 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACES                                   │
├──────────────────────────────────────┬──────────────────────────────────────┤
│  📱 Telegram Bot                     │  🌐 Flask Web Application           │
│  (bot_interactive.py)                │  (app.py)                            │
│  - /metrics command                   │  - Dashboard (/workspace)           │
│  - /content commands                  │  - Content Hub (/content)           │
│  - Weekly auto-reports                │  - Brand Onboarding (/onboarding)   │
│  - Error alerts                       │  - Settings (/settings)             │
└──────────────┬────────────────────────┴──────────────┬───────────────────────┘
               │                                       │
               │                                       │
┌──────────────▼───────────────────────────────────────▼───────────────────────┐
│                        FLASK BACKEND (app.py)                                │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │  Authentication  │  │   API Routes     │  │   Template Rendering     │  │
│  │  - Supabase Auth │  │   /api/*         │  │   Jinja2 Templates      │  │
│  │  - JWT Tokens    │  │   - /auth/*      │  │   - workspace.html       │  │
│  │  - Session Mgmt  │  │   - /content/*   │  │   - content_*.html       │  │
│  └──────────────────┘  │   - /workspace/*  │  │   - brand_*.html         │  │
│                        │   - /dashboard/* │  └──────────────────────────┘  │
│                        └──────────────────┘                                 │
└──────────────────────────────────────────────────────────────────────────────┘
               │                                       │
               │                                       │
┌──────────────▼───────────────────────────────────────▼───────────────────────┐
│                        CORE BUSINESS LOGIC                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  CONTENT SYSTEM (content/)                                           │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  • ai_client.py          - Claude API wrapper                        │  │
│  │  • center_post.py        - Center post creation                      │  │
│  │  • branch_generator.py   - Archive/blog versions                     │  │
│  │  • derivative_generator.py - Multi-platform derivatives              │  │
│  │  • publisher.py          - Publishing & scheduling                   │  │
│  │  • pillar_tracker.py     - Content pillar analytics                  │  │
│  │  • persona_interview.py  - Brand persona onboarding                 │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  METRICS SYSTEM                                                      │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  • metrics_collector.py  - Funnel metrics collection                 │  │
│  │  • report_formatter*.py  - Report formatting & visualization        │  │
│  │  • bot.py               - Telegram bot logic                         │  │
│  │  • bot_scheduled.py     - Scheduled reporting                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
               │                                       │
               │                                       │
┌──────────────▼───────────────────────────────────────▼───────────────────────┐
│                        STORAGE LAYER                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  PRIMARY: Supabase (PostgreSQL)                                     │  │
│  │  • clients table          - Client configurations                    │  │
│  │  • posts table            - Center posts & versions                  │  │
│  │  • derivatives table      - Generated content queue                  │  │
│  │  • pillars table          - Content pillars                          │  │
│  │  • user_clients table     - User-client associations                │  │
│  │  • brand_personas table   - Brand persona documents                 │  │
│  │  • metrics_history table  - Historical metrics                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  FALLBACK CHAIN (content/supabase_storage.py)                        │  │
│  │  1. Supabase (primary)                                              │  │
│  │  2. Vercel KV (if Supabase unavailable)                            │  │
│  │  3. JSON files (local dev: content_*.json)                          │  │
│  │  4. In-memory cache (session)                                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
               │                                       │
               │                                       │
┌──────────────▼───────────────────────────────────────▼───────────────────────┐
│                        EXTERNAL INTEGRATIONS                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Claude AI   │  │   Beehiiv    │  │  Instagram   │  │   Vercel     │  │
│  │  (Anthropic) │  │   Newsletter │  │  Graph API   │  │   Analytics  │  │
│  │              │  │              │  │              │  │              │  │
│  │ • Content    │  │ • Subscribers│  │ • Impressions│  │ • Page Views │  │
│  │   Generation │  │ • Open Rate  │  │ • Reach      │  │ • Visitors   │  │
│  │ • Persona    │  │ • Click Rate │  │ • Followers  │  │              │  │
│  │   Interview  │  │              │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐                                       │
│  │  Telegram    │  │  Supabase    │                                       │
│  │  Bot API     │  │  Auth API    │                                       │
│  │              │  │              │                                       │
│  │ • Send       │  │ • JWT Auth   │                                       │
│  │   Reports    │  │ • User Mgmt  │                                       │
│  │ • Commands   │  │              │                                       │
│  └──────────────┘  └──────────────┘                                       │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Workflow

### 1. **User Onboarding & Authentication Flow**

```
New User
   │
   ├─→ Web: /signup → Supabase Auth → JWT Token → Session Storage
   │
   └─→ Web: /login → Supabase Auth → JWT Token → Session Storage
           │
           └─→ Redirect to /workspace
```

### 2. **Brand Persona Onboarding Flow**

```
User → /onboarding
   │
   ├─→ Select Client/Project
   │
   ├─→ Start Interview (100 questions via Claude)
   │   ├─→ Beliefs & Contrarian Takes (15)
   │   ├─→ Writing Mechanics (20)
   │   ├─→ Aesthetic Crimes (15)
   │   ├─→ Voice & Personality (15)
   │   ├─→ Structural Preferences (15)
   │   ├─→ Hard Nos (10)
   │   └─→ Red Flags (10)
   │
   ├─→ Generate Persona Document (Markdown)
   │
   └─→ Save to Supabase → Used for all future content generation
```

### 3. **Content Creation Workflow**

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Create Center Post                                     │
├─────────────────────────────────────────────────────────────────┤
│  Input: Raw idea ("How to build a content system")              │
│  Process: AI expands to 800-1200 word center post              │
│  Output: Center post saved to database                          │
└─────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Generate Branches (Optional)                           │
├─────────────────────────────────────────────────────────────────┤
│  • Archive Version: Narrative, personal voice                   │
│  • Blog Version: AI-optimized, definitive guide                  │
│  Output: Both versions saved                                    │
└─────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Generate Derivatives                                    │
├─────────────────────────────────────────────────────────────────┤
│  • Newsletter Version (Beehiiv format)                          │
│  • Telegram Announcement (short)                                │
│  • Social Posts (X, LinkedIn, Instagram)                         │
│  Output: All derivatives queued for review                      │
└─────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Review & Schedule                                       │
├─────────────────────────────────────────────────────────────────┤
│  • Review generated content                                     │
│  • Edit if needed                                               │
│  • Set publish date/time                                        │
│  Output: Scheduled derivatives                                  │
└─────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: Auto-Publish (Cron Job)                                 │
├─────────────────────────────────────────────────────────────────┤
│  • content_scheduler.py runs every 5 minutes                    │
│  • Checks for scheduled derivatives                              │
│  • Publishes to platforms (Beehiiv, Telegram, Social)           │
│  • Updates status in database                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 4. **Metrics Collection & Reporting Flow**

```
┌─────────────────────────────────────────────────────────────────┐
│  TRIGGER: Weekly Schedule / /metrics command                    │
├─────────────────────────────────────────────────────────────────┤
│  • bot_scheduled.py (Monday 9 AM)                               │
│  • bot_interactive.py (/metrics command)                        │
└─────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  COLLECT METRICS (Parallelized)                                  │
├─────────────────────────────────────────────────────────────────┤
│  For each client:                                                │
│  ├─→ Beehiiv API: Subscribers, Open Rate, Click Rate            │
│  ├─→ Instagram API: Impressions, Reach, Followers               │
│  ├─→ Vercel Analytics: Page Views, Visitors                    │
│  ├─→ Manual Metrics: Inquiries, Calls, Clients                  │
│  └─→ Calculate: Week-over-week comparisons                       │
└─────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  FORMAT REPORT                                                   │
├─────────────────────────────────────────────────────────────────┤
│  • Funnel visualization (Awareness → Capture → Nurture → Convert)│
│  • Channel performance (Blog, Instagram, LinkedIn, etc.)        │
│  • Product revenue tracking                                     │
│  • Content performance (top pillars, recent posts)              │
│  • Week-over-week growth indicators                             │
└─────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  SEND TO TELEGRAM                                                │
├─────────────────────────────────────────────────────────────────┤
│  • Split long messages (>4000 chars)                            │
│  • Format with Markdown                                         │
│  • Include error alerts if APIs fail                            │
│  • Save metrics to history for next week's comparison           │
└─────────────────────────────────────────────────────────────────┘
```

### 5. **Dashboard Access Flow**

```
User → /workspace
   │
   ├─→ Load Projects (from Supabase)
   │   ├─→ Fetch client configurations
   │   ├─→ Parallel fetch metrics (cached 5 min)
   │   └─→ Render project cards
   │
   ├─→ Click Project → /dashboard?client_id=xxx
   │   ├─→ Growth Dashboard (funnel visualization)
   │   ├─→ Socials Dashboard (channel performance)
   │   └─→ Products Dashboard (revenue tracking)
   │
   └─→ Content Hub → /content
       ├─→ List all posts
       ├─→ Create new post
       ├─→ View post details
       └─→ Manage derivatives
```

---

## 🗂️ Key Components Breakdown

### **Backend (Flask)**
- **File**: `app.py` (~2000+ lines)
- **Routes**: 50+ API endpoints
- **Features**:
  - Authentication middleware (`@require_auth`)
  - Session management
  - Template rendering (Jinja2)
  - RESTful API endpoints
  - Error handling

### **Content System**
- **AI Client** (`content/ai_client.py`): Claude API integration
- **Center Posts** (`content/center_post.py`): Core content management
- **Branches** (`content/branch_generator.py`): Archive/blog versions
- **Derivatives** (`content/derivative_generator.py`): Multi-platform content
- **Publisher** (`content/publisher.py`): Scheduling & publishing
- **Pillars** (`content/pillar_tracker.py`): Content strategy tracking
- **Persona** (`content/persona_interview.py`): Brand voice onboarding

### **Metrics System**
- **Collector** (`metrics_collector.py`): Funnel metrics aggregation
- **Formatter** (`report_formatter*.py`): Report generation
- **Bot** (`bot.py`, `bot_scheduled.py`, `bot_interactive.py`): Telegram integration

### **Storage**
- **Primary**: Supabase PostgreSQL
- **Abstraction**: `content/supabase_storage.py` (with fallback chain)
- **Schema**: `supabase_schema.sql`

### **Frontend**
- **Templates**: `web/templates/*.html` (server-rendered)
- **Styles**: `web/styles/dashboard.css`
- **Assets**: `web/assets/*`
- **JavaScript**: Vanilla JS (inline in templates)

---

## 🔌 API Endpoints Summary

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

### Content Management
- `GET /api/content/posts` - List posts
- `POST /api/content/posts` - Create post
- `GET /api/content/posts/<id>` - Get post
- `PUT /api/content/posts/<id>` - Update post
- `POST /api/content/posts/<id>/expand` - AI expand idea
- `POST /api/content/posts/<id>/branch` - Generate branches
- `POST /api/content/posts/<id>/generate` - Generate derivatives
- `POST /api/content/posts/<id>/schedule` - Schedule publishing
- `GET /api/content/derivatives` - List derivatives
- `POST /api/content/derivatives/<id>/publish` - Publish derivative
- `GET /api/content/pillars` - List pillars
- `POST /api/content/pillars` - Create pillar

### Workspace & Dashboard
- `GET /api/workspace/projects` - List projects (cached, parallelized)
- `GET /api/dashboard/growth` - Funnel metrics
- `GET /api/dashboard/socials` - Social channel metrics
- `GET /api/dashboard/products` - Product revenue metrics

---

## 🚀 Deployment & Automation

### **Local Development**
```bash
python3 app.py              # Flask web server (port 3000)
python3 bot_interactive.py  # Telegram bot (interactive mode)
python3 content_scheduler.py  # Publishing scheduler (every 5 min)
```

### **Production Automation**
- **GitHub Actions**: `.github/workflows/weekly-report.yml` (weekly metrics)
- **Cron Jobs**: Scheduled content publishing
- **Vercel**: Web app deployment (optional)

### **Environment Variables**
```
# Core
SUPABASE_URL=xxx
SUPABASE_KEY=xxx
TELEGRAM_BOT_TOKEN=xxx

# AI
ANTHROPIC_API_KEY=xxx

# Integrations
BEEHIIV_API_KEY=xxx
INSTAGRAM_ACCESS_TOKEN=xxx
VERCEL_TOKEN=xxx
```

---

## 📈 Data Flow Summary

1. **User Input** → Web UI or Telegram Bot
2. **Authentication** → Supabase Auth (JWT)
3. **Business Logic** → Content/Metrics modules
4. **Storage** → Supabase (with fallbacks)
5. **External APIs** → Claude, Beehiiv, Instagram, Vercel
6. **Output** → Web Dashboard or Telegram Reports

---

## 🎯 System Capabilities

✅ **Multi-Client Support**: Manage multiple brands/projects
✅ **AI Content Generation**: Claude-powered content creation
✅ **Multi-Platform Publishing**: Newsletter, Social, Telegram
✅ **Funnel Analytics**: Complete marketing funnel tracking
✅ **Brand Persona**: Personalized content generation
✅ **Automated Reporting**: Weekly Telegram reports
✅ **Content Strategy**: Pillar-based content tracking
✅ **Real-time Metrics**: Parallel API fetching with caching
✅ **Error Handling**: Graceful degradation & alerts

---

## 📝 Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Database**: Supabase (PostgreSQL)
- **Auth**: Supabase Auth (JWT)
- **AI**: Anthropic Claude API
- **Bot**: python-telegram-bot
- **APIs**: Beehiiv, Instagram Graph API, Vercel Analytics
- **Storage**: Supabase + Vercel KV (fallback) + JSON (dev)

---

*Last Updated: January 2026*
