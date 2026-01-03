-- Supabase Database Schema for Content System
-- Run this in your Supabase SQL Editor

-- ==================== CLIENTS TABLE ====================
-- Stores all projects/clients
CREATE TABLE IF NOT EXISTS clients (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    client_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    brand JSONB DEFAULT '{}',
    funnel_structure JSONB DEFAULT '{}',
    connected_accounts JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_clients_client_id ON clients(client_id);
CREATE INDEX IF NOT EXISTS idx_clients_status ON clients(status);

-- ==================== USER-CLIENT RELATIONSHIPS ====================
-- Who can access which projects
CREATE TABLE IF NOT EXISTS user_clients (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id TEXT NOT NULL, -- Supabase Auth user ID (UUID)
    client_id TEXT NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
    role TEXT DEFAULT 'viewer', -- owner, editor, viewer
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, client_id)
);

CREATE INDEX IF NOT EXISTS idx_user_clients_user_id ON user_clients(user_id);
CREATE INDEX IF NOT EXISTS idx_user_clients_client_id ON user_clients(client_id);

-- ==================== USER SETTINGS ====================
CREATE TABLE IF NOT EXISTS user_settings (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id TEXT NOT NULL UNIQUE, -- Supabase Auth user ID
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_settings_user_id ON user_settings(user_id);

-- ==================== API CREDENTIALS ====================
-- Stores API credentials for Beehiiv, Buffer, etc.
CREATE TABLE IF NOT EXISTS api_credentials (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    client_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    pub_id TEXT,
    api_key TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(client_id, platform)
);

CREATE INDEX IF NOT EXISTS idx_api_credentials_client_platform ON api_credentials(client_id, platform);

-- ==================== POSTS TABLE ====================
-- Posts table
CREATE TABLE IF NOT EXISTS posts (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    client_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'idea',
    raw_idea TEXT NOT NULL,
    pillar_id TEXT,
    include_cta BOOLEAN DEFAULT FALSE,
    time_invested_minutes INTEGER DEFAULT 0,
    center_post JSONB,
    archive_version JSONB,
    blog_version JSONB,
    error TEXT
);

-- Derivatives table
CREATE TABLE IF NOT EXISTS derivatives (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    post_id TEXT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    scheduled_for TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    published_url TEXT,
    engagement_metrics JSONB DEFAULT '{}',
    status TEXT GENERATED ALWAYS AS (metadata->>'status') STORED
);

-- Pillars table
CREATE TABLE IF NOT EXISTS pillars (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    client_id TEXT NOT NULL,
    name TEXT NOT NULL,
    color TEXT DEFAULT '#3b82f6',
    channels JSONB DEFAULT '[]',
    target_audience TEXT
);

-- Content metrics table
CREATE TABLE IF NOT EXISTS content_metrics (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    post_id TEXT REFERENCES posts(id) ON DELETE CASCADE,
    derivative_id TEXT REFERENCES derivatives(id) ON DELETE CASCADE,
    pillar_id TEXT REFERENCES pillars(id) ON DELETE SET NULL,
    metric_type TEXT NOT NULL,
    metric_value NUMERIC,
    metric_data JSONB DEFAULT '{}',
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_posts_client_id ON posts(client_id);
CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);
CREATE INDEX IF NOT EXISTS idx_posts_pillar_id ON posts(pillar_id);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_derivatives_post_id ON derivatives(post_id);
CREATE INDEX IF NOT EXISTS idx_derivatives_type ON derivatives(type);
CREATE INDEX IF NOT EXISTS idx_derivatives_status ON derivatives(status);
CREATE INDEX IF NOT EXISTS idx_derivatives_scheduled_for ON derivatives(scheduled_for);

CREATE INDEX IF NOT EXISTS idx_pillars_client_id ON pillars(client_id);

CREATE INDEX IF NOT EXISTS idx_metrics_post_id ON content_metrics(post_id);
CREATE INDEX IF NOT EXISTS idx_metrics_pillar_id ON content_metrics(pillar_id);
CREATE INDEX IF NOT EXISTS idx_metrics_recorded_at ON content_metrics(recorded_at DESC);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to auto-update updated_at
CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_posts_updated_at BEFORE UPDATE ON posts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_derivatives_updated_at BEFORE UPDATE ON derivatives
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pillars_updated_at BEFORE UPDATE ON pillars
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_settings_updated_at BEFORE UPDATE ON user_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_api_credentials_updated_at BEFORE UPDATE ON api_credentials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

