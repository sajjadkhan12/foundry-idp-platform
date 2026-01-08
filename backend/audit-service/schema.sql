-- Audit Service Database Schema
-- This database stores all audit logs for the platform

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,  -- References user in auth-service (no FK for loose coupling)
    user_email VARCHAR(255),  -- Denormalized for easy display
    user_name VARCHAR(255),  -- Denormalized for easy display
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),  -- Can be UUID or other identifier
    resource_name VARCHAR(255),  -- Denormalized name for display
    details JSONB DEFAULT '{}',
    ip_address VARCHAR(45),  -- IPv6 compatible
    user_agent TEXT,
    status VARCHAR(20) DEFAULT 'success' CHECK (status IN ('success', 'failure', 'pending')),
    error_message TEXT,
    business_unit_id UUID,  -- For filtering by business unit
    organization_id UUID,  -- For multi-tenancy
    service_name VARCHAR(100),  -- Which microservice generated the log
    correlation_id UUID,  -- For tracking related actions
    duration_ms INTEGER,  -- How long the action took
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_id ON audit_logs(resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_status ON audit_logs(status);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_business_unit_id ON audit_logs(business_unit_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_organization_id ON audit_logs(organization_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_service_name ON audit_logs(service_name);
CREATE INDEX IF NOT EXISTS idx_audit_logs_correlation_id ON audit_logs(correlation_id);

-- Composite index for common filter combinations
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_created ON audit_logs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs(resource_type, resource_id);

-- Full text search index on action and details
CREATE INDEX IF NOT EXISTS idx_audit_logs_action_text ON audit_logs USING gin(to_tsvector('english', action));

-- Comment on table
COMMENT ON TABLE audit_logs IS 'Stores all audit trail events for the platform';
COMMENT ON COLUMN audit_logs.user_email IS 'Denormalized email for display without joining to auth service';
COMMENT ON COLUMN audit_logs.service_name IS 'Name of the microservice that generated this log entry';
COMMENT ON COLUMN audit_logs.correlation_id IS 'Used to track related actions across services';
