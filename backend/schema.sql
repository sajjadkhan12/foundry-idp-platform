-- DevPlatform IDP Database Schema
-- This schema creates all required tables for the application
-- Note: For Docker, the database is created automatically via POSTGRES_DB
-- For manual setup, connect to the database first: psql -U postgres -d devplatform_idp
--
-- ORGANIZATION ISOLATION:
-- This schema includes organization_id columns for multi-tenant isolation.
-- All resources (roles, groups, deployments, jobs, plugins, credentials, etc.) are
-- isolated by organization to ensure complete data separation between tenants.
-- System roles (platform-admin, super-admin) have organization_id = NULL.
-- Organization-specific resources have organization_id set to their organization.

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Casbin Rule Table
-- ============================================================================
-- NOTE: The casbin-sqlalchemy-adapter creates this table automatically, but we define it
-- here to ensure correct column defaults. The adapter reads v0-v5, but v4 and v5 should
-- be NULL (not empty strings) to avoid "invalid policy size" errors in Casbin.
-- 
-- Policy format: p = sub, dom, obj, act (4 fields: v0, v1, v2, v3)
-- Grouping format: g = user, role, domain (3 fields: v0, v1, v2)
-- v4 and v5 must remain NULL (not empty strings) for proper Casbin operation.

CREATE TABLE IF NOT EXISTS casbin_rule (
    id SERIAL PRIMARY KEY,
    ptype VARCHAR(255) NOT NULL DEFAULT '',
    v0 VARCHAR(255) NOT NULL DEFAULT '',
    v1 VARCHAR(255) NOT NULL DEFAULT '',
    v2 VARCHAR(255) NOT NULL DEFAULT '',
    v3 VARCHAR(255) DEFAULT NULL,  -- NULL by default, not empty string
    v4 VARCHAR(255) DEFAULT NULL,  -- NULL by default, not empty string
    v5 VARCHAR(255) DEFAULT NULL   -- NULL by default, not empty string
);

-- Index for faster policy lookups
CREATE INDEX IF NOT EXISTS idx_casbin_rule_ptype ON casbin_rule(ptype);
CREATE INDEX IF NOT EXISTS idx_casbin_rule_v0 ON casbin_rule(v0);
CREATE INDEX IF NOT EXISTS idx_casbin_rule_v1 ON casbin_rule(v1);

-- ============================================================================
-- RBAC Tables
-- ============================================================================

-- Organizations table
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description VARCHAR(1000),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    avatar_url VARCHAR(500),
    is_active BOOLEAN NOT NULL,
    -- Organization
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE NOT NULL,
    -- Active Business Unit (user preference) - constraint added after business_units table
    active_business_unit_id UUID,
    -- Cloud Identity Bindings
    aws_role_arn VARCHAR(255),
    gcp_service_account VARCHAR(255),
    azure_client_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Refresh tokens table
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Roles table
-- Organization isolation: NULL for system roles (platform-admin, super-admin), set for org-specific roles
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    is_platform_role BOOLEAN DEFAULT false NOT NULL,
    -- Organization isolation: NULL for system roles, set for org-specific roles
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Unique constraint for org-specific roles: same role name can exist in different organizations
CREATE UNIQUE INDEX roles_name_organization_unique 
ON roles(name, organization_id) 
WHERE organization_id IS NOT NULL;

-- Unique constraint for system roles: name must be unique when organization_id IS NULL
CREATE UNIQUE INDEX roles_name_unique_system 
ON roles(name) 
WHERE organization_id IS NULL;

-- Groups table
-- Organization isolation: Groups must belong to an organization
CREATE TABLE groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    -- Organization isolation: Groups must belong to an organization
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- Org-scoped unique constraint: same group name can exist in different organizations
    UNIQUE(name, organization_id)
);

-- Permissions metadata table
-- Stores human-readable metadata for permissions (names, descriptions, categories, icons)
-- This is for UI clarity only - Casbin remains the source of truth for permissions
CREATE TABLE permissions_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    resource VARCHAR(100),
    action VARCHAR(100),
    environment VARCHAR(50),
    icon VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Plugin System Tables
-- ============================================================================

-- Plugins table
-- Organization isolation: Each organization manages its own plugins
CREATE TABLE plugins (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    author VARCHAR,
    is_locked BOOLEAN DEFAULT FALSE NOT NULL,
    deployment_type VARCHAR(50) DEFAULT 'infrastructure' NOT NULL,
    -- Organization isolation: Each organization manages its own plugins
    -- Note: No foreign key constraint to avoid cross-service dependencies
    -- The organization_id is validated at the application level
    organization_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Plugin versions table
CREATE TABLE plugin_versions (
    id SERIAL PRIMARY KEY,
    plugin_id VARCHAR REFERENCES plugins(id) ON DELETE CASCADE NOT NULL,
    version VARCHAR NOT NULL,
    manifest JSONB NOT NULL,
    storage_path VARCHAR,
    git_repo_url VARCHAR(255),
    -- Template Git branch for this plugin version (e.g., 'plugin-gcp-bucket')
    -- All deployment branches are created from this template.
    git_branch VARCHAR(255),
    template_repo_url VARCHAR(500),
    template_path VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(plugin_id, version)
);

-- Cloud credentials table
CREATE TYPE cloud_provider_enum AS ENUM ('aws', 'gcp', 'azure', 'kubernetes');

CREATE TABLE cloud_credentials (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    provider cloud_provider_enum NOT NULL,
    encrypted_data TEXT NOT NULL,
    -- Organization isolation: Each organization manages its own credentials
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- Org-scoped unique constraint: same credential name can exist in different organizations
    UNIQUE(organization_id, name)
);

-- Plugin access control tables
-- Table to track which users have been granted access to locked plugins
-- Note: business_unit_id foreign key constraint added after business_units table is created
CREATE TABLE plugin_access (
    id SERIAL PRIMARY KEY,
    plugin_id VARCHAR NOT NULL REFERENCES plugins(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    business_unit_id UUID,  -- Foreign key constraint added later
    granted_by UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    granted_at TIMESTAMP WITH TIME ZONE NOT NULL,
    UNIQUE(plugin_id, user_id, business_unit_id)
);

-- Table to track access requests for locked plugins
-- Note: status is stored as VARCHAR(20), valid values: 'pending', 'approved', 'rejected'
-- Note: business_unit_id foreign key constraint added after business_units table is created
CREATE TABLE plugin_access_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plugin_id VARCHAR NOT NULL REFERENCES plugins(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    business_unit_id UUID,  -- Foreign key constraint added later
    status VARCHAR(20) NOT NULL,
    requested_at TIMESTAMP WITH TIME ZONE NOT NULL,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    note TEXT
);

-- ============================================================================
-- Business Units Tables
-- ============================================================================

-- Business units table
CREATE TABLE business_units (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    description VARCHAR(1000),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(slug, organization_id)
);

-- Add foreign key constraints for business_units references
-- (These columns were created without constraints since business_units table didn't exist yet)

-- Add foreign key constraints for business_units references
-- (These columns were created without constraints since business_units table didn't exist yet)
-- Constraint names match the pattern used by SQLAlchemy: {table}_{column}_fkey

-- Add foreign key constraint for active_business_unit_id in users table
ALTER TABLE users 
ADD CONSTRAINT users_active_business_unit_id_fkey 
FOREIGN KEY (active_business_unit_id) 
REFERENCES business_units(id) 
ON DELETE SET NULL;

-- Add foreign key constraint for business_unit_id in plugin_access table
ALTER TABLE plugin_access 
ADD CONSTRAINT plugin_access_business_unit_id_fkey 
FOREIGN KEY (business_unit_id) 
REFERENCES business_units(id) 
ON DELETE SET NULL;

-- Add foreign key constraint for business_unit_id in plugin_access_requests table
ALTER TABLE plugin_access_requests 
ADD CONSTRAINT plugin_access_requests_business_unit_id_fkey 
FOREIGN KEY (business_unit_id) 
REFERENCES business_units(id) 
ON DELETE SET NULL;

-- Business unit members table (many-to-many relationship)
-- Note: Uses role_id foreign key to roles table instead of enum
-- role_id is nullable to allow adding members without roles initially
-- Multiple roles per user per BU are allowed (unique constraint on business_unit_id, user_id, role_id)
CREATE TABLE business_unit_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_unit_id UUID REFERENCES business_units(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    role_id UUID REFERENCES roles(id) ON DELETE RESTRICT,  -- NULLABLE: allows members without roles
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Unique constraint for non-NULL role_id: allows multiple roles per user per BU
-- A user can have multiple specific roles in the same BU
CREATE UNIQUE INDEX uix_business_unit_member_role_not_null
ON business_unit_members (business_unit_id, user_id, role_id)
WHERE role_id IS NOT NULL;

-- Unique constraint for NULL role_id: one entry per user per BU without a role
-- A user can only be added once to a BU without a specific role
CREATE UNIQUE INDEX uix_business_unit_member_no_role
ON business_unit_members (business_unit_id, user_id)
WHERE role_id IS NULL;

-- Business unit groups table (for managing groups within a business unit)
CREATE TABLE business_unit_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_unit_id UUID REFERENCES business_units(id) ON DELETE CASCADE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    role_id UUID REFERENCES roles(id) ON DELETE RESTRICT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(business_unit_id, name)
);

-- Business unit group members table (many-to-many relationship)
CREATE TABLE business_unit_group_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id UUID REFERENCES business_unit_groups(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(group_id, user_id)
);

-- ============================================================================
-- Deployment Tables
-- ============================================================================

-- Deployments table
-- Note: status is stored as VARCHAR, valid values: 'active', 'provisioning', 'deleting', 'failed', 'deleted'
-- Note: deployment_type is 'infrastructure' or 'microservice'
-- Note: environment is 'development', 'staging', or 'production'
CREATE TABLE deployments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'provisioning',
    deployment_type VARCHAR(50) NOT NULL DEFAULT 'infrastructure',
    -- Environment separation and cost tracking
    environment VARCHAR(50) NOT NULL DEFAULT 'development',
    cost_center VARCHAR(100),
    project_code VARCHAR(100),
    -- Plugin reference
    plugin_id VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    -- Infrastructure details
    stack_name VARCHAR(255),
    cloud_provider VARCHAR(50),
    region VARCHAR(100),
    -- Per‑deployment Git branch cloned from the plugin version template branch
    git_branch VARCHAR(255),
    -- Microservice repository details
    github_repo_url VARCHAR(500),
    github_repo_name VARCHAR(255),
    -- CI/CD status tracking
    ci_cd_status VARCHAR(50),
    ci_cd_run_id BIGINT,
    ci_cd_run_url VARCHAR(500),
    ci_cd_updated_at TIMESTAMP WITH TIME ZONE,
    -- Update tracking (for updating existing deployments)
    update_status VARCHAR(50),
    last_update_job_id VARCHAR(255),
    last_update_error TEXT,
    last_update_attempted_at TIMESTAMP WITH TIME ZONE,
    -- Infrastructure linking
    pulumi_stack_name VARCHAR(255),
    infrastructure_deployment_id UUID REFERENCES deployments(id) ON DELETE SET NULL,
    -- Data
    inputs JSONB,
    outputs JSONB,
    -- Ownership
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    -- Business Unit
    business_unit_id UUID REFERENCES business_units(id) ON DELETE SET NULL,
    -- Organization isolation: Direct organization filtering for better performance
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE NOT NULL,
    -- Cost estimation fields
    estimated_monthly_cost DECIMAL(10, 2),
    actual_monthly_cost DECIMAL(10, 2),
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Deployment tags table for flexible key-value tagging
CREATE TABLE deployment_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deployment_id UUID NOT NULL REFERENCES deployments(id) ON DELETE CASCADE,
    key VARCHAR(100) NOT NULL,
    value VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uix_deployment_tag_key UNIQUE (deployment_id, key)
);

-- Deployment history table for tracking all versions/changes (for rollback capability)
CREATE TABLE deployment_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deployment_id UUID NOT NULL REFERENCES deployments(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    inputs JSONB NOT NULL,
    outputs JSONB,
    status VARCHAR(50) NOT NULL,
    job_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),  -- User email who created this version
    description TEXT,  -- Optional description of what changed
    CONSTRAINT uix_deployment_version UNIQUE (deployment_id, version_number)
);

-- Deployment costs table for historical monthly cost tracking
CREATE TABLE deployment_costs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deployment_id UUID NOT NULL REFERENCES deployments(id) ON DELETE CASCADE,
    billing_month VARCHAR(7) NOT NULL,  -- Format: YYYY-MM
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    breakdown JSONB,  -- Detailed cost breakdown by resource type
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uix_deployment_billing_month UNIQUE (deployment_id, billing_month)
);

-- ============================================================================
-- Job Management Tables
-- ============================================================================

-- Job status enum
CREATE TYPE job_status_enum AS ENUM ('pending', 'running', 'success', 'failed', 'cancelled', 'dead_letter');

-- Jobs table
CREATE TABLE jobs (
    id VARCHAR PRIMARY KEY,
    plugin_version_id INTEGER REFERENCES plugin_versions(id) NOT NULL,
    deployment_id UUID REFERENCES deployments(id),
    status job_status_enum DEFAULT 'pending',
    triggered_by VARCHAR NOT NULL,
    inputs JSONB DEFAULT '{}',
    outputs JSONB,
    retry_count INTEGER DEFAULT 0 NOT NULL,
    error_state VARCHAR(255),
    error_message TEXT,
    -- Organization isolation: Populated from associated deployment
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP WITH TIME ZONE
);

-- Job logs table
CREATE TABLE job_logs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR REFERENCES jobs(id) ON DELETE CASCADE NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR DEFAULT 'INFO',
    message TEXT NOT NULL
);

-- ============================================================================
-- Notification Tables
-- ============================================================================

-- Notifications table
CREATE TABLE notifications (
    id VARCHAR PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    title VARCHAR NOT NULL,
    message VARCHAR NOT NULL,
    type VARCHAR DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    link VARCHAR,
    -- Organization isolation: Populated from user who receives the notification
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Audit Tables
-- ============================================================================

-- Audit logs table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    details JSONB,
    ip_address VARCHAR(45),
    -- Organization isolation: Populated from user who performed the action
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

-- Organizations indexes
CREATE INDEX idx_organizations_name ON organizations(name);
CREATE INDEX idx_organizations_slug ON organizations(slug);

-- Users indexes
CREATE UNIQUE INDEX ix_users_email ON users(email);
CREATE UNIQUE INDEX ix_users_username ON users(username);
CREATE INDEX ix_users_organization_id ON users(organization_id);
CREATE INDEX ix_users_active_business_unit_id ON users(active_business_unit_id);

-- Refresh tokens indexes
CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);

-- Roles indexes
CREATE INDEX idx_roles_name ON roles(name);
CREATE INDEX idx_roles_is_platform_role ON roles(is_platform_role);
CREATE INDEX idx_roles_organization_id ON roles(organization_id);

-- Groups indexes
CREATE INDEX idx_groups_name ON groups(name);
CREATE INDEX idx_groups_organization_id ON groups(organization_id);

-- Permissions metadata indexes
CREATE INDEX idx_permissions_metadata_category ON permissions_metadata(category);
CREATE INDEX idx_permissions_metadata_resource ON permissions_metadata(resource);
CREATE INDEX idx_permissions_metadata_slug ON permissions_metadata(slug);

-- Cloud credentials indexes
CREATE INDEX idx_cloud_credentials_organization_id ON cloud_credentials(organization_id);

-- Plugin indexes
CREATE INDEX idx_plugin_versions_plugin_id ON plugin_versions(plugin_id);
CREATE INDEX idx_plugins_organization_id ON plugins(organization_id);
CREATE INDEX idx_plugin_access_plugin_id ON plugin_access(plugin_id);
CREATE INDEX idx_plugin_access_user_id ON plugin_access(user_id);
CREATE INDEX ix_plugin_access_business_unit_id ON plugin_access(business_unit_id);
CREATE INDEX idx_plugin_access_requests_plugin_id ON plugin_access_requests(plugin_id);
CREATE INDEX idx_plugin_access_requests_user_id ON plugin_access_requests(user_id);
CREATE INDEX idx_plugin_access_requests_status ON plugin_access_requests(status);
CREATE INDEX ix_plugin_access_requests_business_unit_id ON plugin_access_requests(business_unit_id);

-- Job indexes
CREATE INDEX idx_jobs_plugin_version_id ON jobs(plugin_version_id);
CREATE INDEX idx_jobs_deployment_id ON jobs(deployment_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_triggered_by ON jobs(triggered_by);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
CREATE INDEX idx_jobs_organization_id ON jobs(organization_id);
-- Composite index for status-based queries with time ordering
CREATE INDEX idx_jobs_status_created ON jobs(status, created_at DESC);

-- Job logs indexes
CREATE INDEX idx_job_logs_job_id ON job_logs(job_id);
CREATE INDEX idx_job_logs_timestamp ON job_logs(timestamp);

-- Business units indexes
CREATE INDEX idx_business_units_name ON business_units(name);
CREATE INDEX idx_business_units_slug ON business_units(slug);
CREATE INDEX idx_business_units_organization_id ON business_units(organization_id);

-- Business unit members indexes
CREATE INDEX idx_business_unit_members_business_unit_id ON business_unit_members(business_unit_id);
CREATE INDEX idx_business_unit_members_user_id ON business_unit_members(user_id);
CREATE INDEX idx_business_unit_members_role_id ON business_unit_members(role_id);

-- Business unit groups indexes
CREATE INDEX idx_business_unit_groups_business_unit_id ON business_unit_groups(business_unit_id);
CREATE INDEX idx_business_unit_groups_name ON business_unit_groups(name);
CREATE INDEX idx_business_unit_groups_role_id ON business_unit_groups(role_id);

-- Business unit group members indexes
CREATE INDEX idx_business_unit_group_members_group_id ON business_unit_group_members(group_id);
CREATE INDEX idx_business_unit_group_members_user_id ON business_unit_group_members(user_id);

-- Deployment indexes
CREATE INDEX idx_deployments_user_id ON deployments(user_id);
CREATE INDEX idx_deployments_status ON deployments(status);
CREATE INDEX idx_deployments_plugin_id ON deployments(plugin_id);
CREATE INDEX idx_deployments_created_at ON deployments(created_at);
CREATE INDEX idx_deployments_environment ON deployments(environment);
CREATE INDEX idx_deployments_business_unit_id ON deployments(business_unit_id);
CREATE INDEX idx_deployments_organization_id ON deployments(organization_id);
-- Composite index for user's deployment list queries (user_id + status + created_at)
CREATE INDEX idx_deployments_user_status_created ON deployments(user_id, status, created_at DESC);
-- Index for update status queries (for filtering deployments by update status)
CREATE INDEX idx_deployments_update_status ON deployments(update_status) WHERE update_status IS NOT NULL;
-- Composite index for organization filtering with environment and status
CREATE INDEX idx_deployments_org_env_status ON deployments(organization_id, environment, status) WHERE organization_id IS NOT NULL;

-- Deployment tags indexes
CREATE INDEX idx_deployment_tags_deployment_id ON deployment_tags(deployment_id);
CREATE INDEX idx_deployment_tags_key ON deployment_tags(key);
CREATE INDEX idx_deployment_tags_value ON deployment_tags(value);
-- Composite index for efficient tag filtering
CREATE INDEX idx_deployment_tags_composite ON deployment_tags(deployment_id, key, value);

-- Deployment history indexes
CREATE INDEX idx_deployment_history_deployment_id ON deployment_history(deployment_id);
CREATE INDEX idx_deployment_history_version ON deployment_history(deployment_id, version_number DESC);
CREATE INDEX idx_deployment_history_created_at ON deployment_history(created_at DESC);

-- Deployment costs indexes
CREATE INDEX idx_deployment_costs_deployment_id ON deployment_costs(deployment_id);
CREATE INDEX idx_deployment_costs_billing_month ON deployment_costs(billing_month DESC);
CREATE INDEX idx_deployment_costs_amount ON deployment_costs(amount DESC);

-- Notification indexes
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);
CREATE INDEX idx_notifications_organization_id ON notifications(organization_id);

-- Audit log indexes
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_organization_id ON audit_logs(organization_id);
-- Composite index for user audit history queries
CREATE INDEX idx_audit_logs_user_created ON audit_logs(user_id, created_at DESC) WHERE user_id IS NOT NULL;

-- ============================================================================
-- Initial Data (Optional - can be created via db_init.py)
-- ============================================================================

-- Note: Default admin user is created via app/core/db_init.py using environment variables
-- The following is for reference only and should match your .env ADMIN_* variables

-- Example admin user (password: admin123)
-- INSERT INTO users (email, username, hashed_password, full_name, is_active)
-- VALUES (
--     'admin@devplatform.com',
--     'admin',
--     '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS6ZhHZUu',
--     'System Admin',
--     TRUE
-- );

-- ============================================================================
-- Notes
-- ============================================================================

-- Business Unit-Scoped RBAC:
-- The business_unit_members table uses role_id (UUID foreign key to roles table) instead of
-- an enum. This allows for global roles that can be reused across business units.
-- Default roles are created during database initialization:
--   Platform roles: platform-admin, security-admin, admin
--   BU roles: bu-owner, bu-admin, developer, viewer
-- Migration from enum to role_id is handled automatically by migrations/add_bu_scoped_rbac.sql
-- which is executed during application startup via app/core/db_init.py

-- Casbin RBAC tables (casbin_rule) are defined at the top of this schema.
-- IMPORTANT: v4, v5, and v3 (for grouping policies) must be NULL, not empty strings.
-- The casbin-sqlalchemy-adapter includes all non-NULL columns when loading policies.
-- If v4/v5 are empty strings, Casbin will see 6-field policies instead of 4-field,
-- causing "invalid policy size" errors.

-- Environment-based permissions are automatically created during database initialization
-- (see app/core/db_init.py). The permission model is:
--   - Development: engineer, admin (create, update, delete)
--   - Staging: senior-engineer, admin (create, update, delete)
--   - Production: admin only (create, update, delete)
-- Permission format: deployments:create:development, deployments:create:staging, etc.
-- (New format: resource:action:environment)
--
-- Permissions metadata is populated from app/core/permission_registry.py via
-- scripts/populate_permission_metadata.py. This metadata is for UI clarity only;
-- Casbin remains the source of truth for permission enforcement.

-- The application uses SQLAlchemy ORM which will create tables automatically
-- if they don't exist when using Base.metadata.create_all()
-- This schema.sql is provided for reference and manual database setup if needed.

-- ============================================================================
-- Organization Configurations Table
-- ============================================================================

-- Organization configurations table (for per-org settings like Pulumi tokens, GitHub tokens, etc.)
CREATE TABLE IF NOT EXISTS organization_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE NOT NULL,
    business_unit_id UUID REFERENCES business_units(id) ON DELETE CASCADE,
    config_key VARCHAR(255) NOT NULL,
    config_value_encrypted TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(organization_id, business_unit_id, config_key)
);

CREATE INDEX IF NOT EXISTS idx_org_config_org ON organization_configurations(organization_id);
CREATE INDEX IF NOT EXISTS idx_org_config_bu ON organization_configurations(business_unit_id);
CREATE INDEX IF NOT EXISTS idx_org_config_key ON organization_configurations(config_key);
CREATE INDEX IF NOT EXISTS idx_org_config_active ON organization_configurations(is_active) WHERE is_active = TRUE;

-- ============================================================================
-- Performance Indexes
-- ============================================================================

-- Performance Indexes:
-- This schema includes all performance indexes for optimal query performance.
-- Composite indexes are included for common query patterns:
--   - idx_deployments_user_status_created: User deployment lists with status filtering
--   - idx_jobs_status_created: Job status queries with time ordering
--   - idx_deployment_tags_composite: Efficient tag-based filtering
--   - idx_audit_logs_user_created: User audit history queries
--   - idx_refresh_tokens_expires_at: Token cleanup operations
--
-- Note: If the deployments table has an organization_id column (for multi-tenant deployments),
-- the index idx_deployments_org_env_status will be created automatically by the application
-- during startup (see app/core/db_init.py). This conditional index is not included in
-- this schema.sql as it depends on the table structure.
--
-- All indexes use IF NOT EXISTS in the migration file (migrations/add_composite_indexes.sql)
-- to ensure idempotent execution. The application automatically creates these indexes
-- on startup for fresh installations.