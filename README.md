# Foundry Platform - Internal Developer Platform (IDP)

A production-ready, enterprise-grade Internal Developer Platform for streamlined infrastructure provisioning, microservice management, and multi-cloud deployment orchestration.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://react.dev/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue.svg)](https://www.typescriptlang.org/)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Screenshots](#-screenshots)
- [Architecture](#-architecture)
- [Core Features](#-core-features)
- [API Endpoints](#-api-endpoints)
- [Database Models](#-database-models)
- [Frontend Pages](#-frontend-pages)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Security](#-security)
- [Development](#-development)
- [Production Deployment](#-production-deployment)

---

## 🎯 Overview

**Foundry Platform** is a comprehensive Internal Developer Platform that enables organizations to:

- **Provision Infrastructure**: Deploy cloud resources across AWS, GCP, and Azure using Pulumi-based plugins
- **Manage Microservices**: Create, deploy, and manage microservices with GitOps workflows
- **Multi-Tenant Support**: Organization-based isolation with Casbin RBAC
- **Plugin System**: Extensible architecture with custom infrastructure templates
- **CI/CD Integration**: Native GitHub Actions integration with webhook support
- **Pulumi ESC Integration**: Automatic cloud credential management via Pulumi Environments, Secrets, and Configuration
- **Audit Logging**: Complete activity tracking and compliance monitoring

---

## 📸 Screenshots

### Login
![Login](screenshots/login.png)
*User authentication interface with email and password login*

### Dashboard
![Dashboard](screenshots/dashboard.png)
*Main dashboard showing deployments, plugins, and notifications overview*

### Service Catalog
![Service Catalog](screenshots/service-catalog.png)
*Service catalog displaying available plugins and infrastructure templates*

### Jobs
![Jobs](screenshots/jobs.png)
*Job management interface showing provisioning job status, logs, and history*

### Plugin Upload
![Plugin Upload](screenshots/plugin-upload.png)
*Plugin upload interface for uploading Pulumi-based infrastructure plugins*

### User Management
![User Management](screenshots/user-management.png)
*User management interface for creating, updating, and managing users*

### Group Management
![Group Management](screenshots/group-management.png)
*Group management interface with role assignment and member management*

### Role Management
![Role Management](screenshots/role-management.png)
*Role management interface with permission assignment and metadata*

### Audit Logs
![Audit Logs](screenshots/audit-logs.png)
*Audit logs interface showing complete activity tracking and compliance monitoring*

### Profile
![Profile](screenshots/profile.png)
*User profile management interface with avatar upload and personal information*

---

## 🏗️ Architecture

### Backend Stack

```
FastAPI (Python 3.11+)
├── Database: PostgreSQL + SQLAlchemy ORM (Async)
├── Authorization: Casbin (RBAC with domain isolation)
├── Task Queue: Celery + Redis
├── IaC Engine: Pulumi
├── Git Operations: GitPython
├── Cloud Credentials: Pulumi ESC (automatic OIDC-based credential management)
├── Encryption: Cryptography (Fernet)
└── Authentication: JWT (Access + Refresh tokens)
```

### Frontend Stack

```
React 18 + TypeScript
├── Build Tool: Vite
├── Routing: React Router v6
├── State: React Context + Hooks
├── Styling: Tailwind CSS
├── Icons: Lucide React
└── API Client: Axios
```

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  Dashboard | Provision | Users | Roles | Groups | Plugins   │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTPS/JWT
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Auth API   │  │  Plugin API  │  │  Deploy API  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Casbin RBAC  │  │    Celery    │  │  Pulumi Svc  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
         ↓                    ↓                    ↓
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │    │    Redis     │    │    GitHub    │
└──────────────┘    └──────────────┘    └──────────────┘
         ↓                                        ↓
┌──────────────────────────────────────────────────────────────┐
│         Cloud Providers (via Pulumi ESC)                      │
│         AWS          │        GCP       │       Azure        │
└──────────────────────────────────────────────────────────────┘
```

---

## ✨ Core Features

### 🔐 Advanced RBAC & Multi-Tenancy

- **Organization Isolation**: Each organization operates in its own domain with complete data isolation
- **Business Unit Separation**: Multi-tenant data isolation with business unit-scoped permissions and resources
- **Casbin Integration**: Policy-based access control with high performance (10K+ rules)
- **Hierarchical Permissions**: `User → Groups → Roles → Permissions`
- **Multiple Group Membership**: Users inherit permissions from all groups
- **Domain-Aware Enforcement**: Automatic organization context in all authorization checks
- **Business Unit-Scoped RBAC**: Permissions evaluated within business unit context for complete data isolation
- **Platform vs BU Roles**: Platform-level roles (admin) vs business unit-scoped roles (developer, engineer, viewer)
- **Granular Permissions**: Fine-grained control over resources and actions
- **Environment-Based Permissions**: Separate permissions for development, staging, and production environments
- **Permission Debugging**: Debug endpoints to inspect user permissions and roles

### 👥 User & Access Management

- **User Management**: Create, update, delete users with profile support
- **Business Unit Management**: Create and manage business units with owners and members
- **Business Unit Owners**: Owners can manage members and approve plugin access requests
- **Group Management**: Organize users by teams, departments, or functions (scoped to business units)
- **Role Management**: Custom roles with specific permission sets (global roles, reusable across BUs)
- **Business Unit Membership**: Users can belong to multiple business units with different roles in each
- **Active Business Unit Selection**: Users select an active business unit for their session
- **Avatar Support**: Upload and manage user avatars
- **Profile Management**: Users can update their own profiles
- **Password Management**: Secure password change with verification

### 🔧 Plugin System

- **Upload Infrastructure Plugins**: Pulumi-based ZIP file uploads with validation
- **Microservice Templates**: GitOps-based microservice scaffolding
- **Version Management**: Multiple versions per plugin with automatic latest selection
- **Multi-Cloud Support**: AWS, GCP, Azure, Kubernetes
- **Dynamic Forms**: Auto-generated input forms from plugin schemas
- **Plugin Locking**: Restrict plugin access with approval workflows
- **Access Requests**: Users can request access to locked plugins
- **GitOps Integration**: Automatic Git branch creation for each plugin
- **Environment-Aware Provisioning**: Deploy to specific environments with permission checks
- **Tag Validation**: Enforce required tags (team, owner, purpose) during provisioning

### 🚀 Infrastructure Provisioning

- **Pulumi Integration**: Full Infrastructure as Code support
- **Async Processing**: Background job processing with Celery
- **Job Management**: Complete history, logs, and status tracking
- **Retry Logic**: Automatic retries with dead-letter queue for failed jobs
- **Pulumi ESC**: Automatic cloud credential management for AWS, GCP, and Azure via OIDC
- **Multi-Cloud Deployment**: Deploy to AWS, GCP, Azure from single interface
- **Deployment Tracking**: Real-time status updates and output capture
- **Environment Separation**: Deploy to development, staging, or production with strict access control
- **Tagging System**: Flexible key-value tags for cost tracking and resource organization
- **Cost Tracking**: Built-in cost center and project code fields for financial management

### 🏭 Microservice Management

- **Template-Based Generation**: Create microservices from Git templates
- **GitHub Integration**: Automatic repository creation and initialization
- **CI/CD Setup**: GitHub Actions workflows with webhook integration
- **Real-Time Status**: Live CI/CD pipeline status updates
- **Branch Management**: Automatic deployment branch creation
- **Repository Webhooks**: Receive build status updates automatically

### 🔔 Notifications & Audit

- **Real-Time Notifications**: Job status, access approvals, system events
- **Unread Tracking**: Mark notifications as read/unread
- **Action Links**: Direct links to related resources
- **Audit Logging**: Complete activity tracking with middleware
- **Search & Filter**: Advanced filtering by user, action, resource, date
- **Compliance Ready**: Full audit trail for security compliance

### 🔒 Security Features

- **JWT Authentication**: Access tokens (15min) + Refresh tokens (7 days)
- **HTTP-Only Cookies**: Secure refresh token storage
- **Password Hashing**: Bcrypt with secure password policies
- **Pulumi ESC**: Centralized credential management with automatic OIDC token exchange
- **Encrypted Credentials**: Fernet encryption for sensitive data
- **CORS Configuration**: Secure cross-origin resource sharing
- **Rate Limiting Ready**: Infrastructure for rate limiting
- **Environment-Based Access Control**: Strict permissions for development/staging/production
- **Tag Validation**: Required tags for all deployments with format validation

---

## 🚀 Quick Start

### Prerequisites

- **PostgreSQL** (v14+)
- **Node.js** (v18+)
- **Python** (v3.11+)
- **UV** package manager
- **Redis** (v6+)

### Option 1: Automated Start (Recommended)
**1. Backend Setup:**
```bash
cd backend

# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Create .env file (see Configuration section)
cp .env.example .env
# Edit .env with your values

# Setup PostgreSQL database
createdb Foundry_platform

# Start backend server
uv run uvicorn app.main:app --reload --port 8000
```

**2. Celery Worker (separate terminal):**
```bash
cd backend
uv run celery -A app.worker worker --loglevel=info
```

**3. Frontend Setup:**
```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env

# Start dev server
npm run dev
```

### Access Points

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc

### Default Admin Credentials

The system creates a default admin user on first startup. Check the backend logs for credentials, or use the values from your `.env` file:

```
Email: [ADMIN_EMAIL from .env]
Password: [ADMIN_PASSWORD from .env]
```

---

## ⚙️ Configuration

### Backend Environment Variables (`.env`)


#### Pulumi ESC Configuration

The platform uses Pulumi ESC for automatic cloud credential management. Configure ESC environments in Pulumi Cloud and reference them in your application:

```bash
# Pulumi Cloud Configuration
PULUMI_ACCESS_TOKEN=your-pulumi-access-token
PULUMI_ORG=your-org-name

# Pulumi ESC Environments (format: "org/environment-name")
PULUMI_ESC_ENVIRONMENT_GCP=your-org/gcp-production
PULUMI_ESC_ENVIRONMENT_AWS=your-org/aws-production
PULUMI_ESC_ENVIRONMENT_AZURE=your-org/azure-production
PULUMI_USE_ESC=true
```

**Note:** Detailed setup instructions for ESC environments are in the [Backend README](backend/README.md#pulumi-esc-configuration).

#### Plugin Storage
```bash
PLUGINS_STORAGE_PATH=./storage/plugins
```

### Frontend Environment Variables

Create `frontend/.env`:
```bash
VITE_API_URL=http://localhost:8000
```

---

## 🔒 Security

### Authentication Flow

1. **Login**: User submits email/password
2. **Token Generation**: Backend generates:
   - Access token (JWT, 15 min expiry)
   - Refresh token (UUID, 7 days expiry, stored in DB)
3. **Cookie Storage**: Refresh token stored in HTTP-only cookie
4. **API Requests**: Access token sent in Authorization header
5. **Token Refresh**: When access token expires, use refresh token to get new access token
6. **Logout**: Delete refresh token from DB and clear cookie

### Authorization Flow

1. **Request**: User makes API request with access token
2. **User Extraction**: Decode JWT to get user ID
3. **Organization Context**: Load user's organization
4. **Permission Check**: Casbin enforcer checks:
   - User's direct roles
   - Roles inherited from groups
   - Organization domain isolation
5. **Resource Access**: Grant or deny based on policies

### RBAC Model (Casbin)

**Business Unit-Scoped RBAC:**
```conf
[request_definition]
r = sub, dom, obj, act, bu

[policy_definition]
p = sub, dom, obj, act

[role_definition]
g = _, _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
# Platform-level permissions (no BU required)
m = g(r.sub, p.sub, r.dom) && r.dom == p.dom && r.obj == p.obj && r.act == p.act && p.sub == "platform-admin"

# Business unit-scoped permissions (BU required)
m = g(r.sub, p.sub, r.dom) && r.dom == p.dom && r.obj == p.obj && r.act == p.act && r.bu == p.bu
```

**Example Policies:**
```
# Platform-level permissions (global)
p, platform-admin, org123, users, create
p, platform-admin, org123, business_units, create

# Business unit-scoped permissions
p, developer, org123, bu:bu-123:plugins, provision
p, engineer, org123, bu:bu-123:deployments, create:development
p, bu-owner, org123, bu:bu-123:business_units, manage_members

# Role assignments
g, user456, platform-admin, org123
g, user789, developer, org123
g, user789, bu-123, org123  # User is member of BU bu-123 with developer role
```

**Permission Scopes:**
- **Platform-level**: Actions that don't require a business unit (e.g., `users:create`, `business_units:create`)
- **Business Unit-scoped**: Actions that require an active business unit (e.g., `plugins:provision`, `deployments:create`)
- **User-specific**: Actions on user-owned resources (e.g., `deployments:list:own`)

**Current Schema:**
- All tables are automatically created on application startup via `Base.metadata.create_all()`
- `permissions_metadata` table stores permission metadata (name, description, category, icon) for UI display
- `deployments` table includes `environment`, `cost_center`, and `project_code` columns
- `deployment_tags` table provides flexible key-value tagging with unique constraint on (deployment_id, key)

### Adding a New API Endpoint

### Testing

#### Quick Test Flow
1. Login with admin credentials
2. Create a business unit (e.g., "Engineering", code: "ENG")
3. Assign yourself or another user as the business unit owner
4. Add members to the business unit with roles (developer, engineer, viewer)
5. As a member, select the business unit as your active business unit
6. Upload a plugin and provision infrastructure
7. All deployments will be tagged with the business unit code

#### Business Unit Test Flow
1. **As Admin:**
   - Create a business unit (e.g., "IT Operations", code: "IT-OPS")
   - Assign a user as the business unit owner
2. **As Business Unit Owner:**
   - Add members to the business unit
   - Assign roles (developer, engineer, viewer)
   - Approve plugin access requests from members
3. **As Member:**
   - Select the business unit as your active business unit
   - Request access to locked plugins
   - Provision infrastructure (if you have the right role)
   - View only deployments from your active business unit

#### Upload Plugin Test
1. Navigate to `/admin/plugins/upload`
2. Upload a Pulumi plugin ZIP file
3. Plugin is validated and extracted
4. If GitOps enabled, pushed to GitHub branch
5. Plugin appears in `/provision` page

#### Provision Infrastructure Test
1. Navigate to `/provision`
2. Select a plugin
3. Fill in required inputs
4. Submit provisioning job
5. Monitor job status in real-time
6. View logs and outputs

### Permission System Redesign

**New Features:**
- ✅ **Permission Metadata System**: Centralized permission registry with name, description, category, and icon
- ✅ **User-Specific Permissions**: New category for user-owned resources (`deployments:list:own`, `deployments:update:own`, `deployments:delete:own`)
- ✅ **Permission Categories**: Permissions organized by category (User Specific, User Management, Deployment Management, etc.)
- ✅ **Enhanced UI**: Permissions displayed with metadata in role management interface
- ✅ **Automatic Table Creation**: All database tables created automatically on startup
- ✅ **Permission Registry**: Single source of truth for all permissions with metadata

**Permission Categories:**
- **User Specific**: Profile and own deployment management
- **User Management**: Organization-wide user administration
- **Group Management**: Team and group administration
- **Role Management**: Role and permission assignment
- **Permission Management**: Permission viewing and listing
- **Deployment Management**: General deployment operations
- **Deployment - Development/Staging/Production**: Environment-specific permissions
- **Plugin Management**: Plugin upload, deletion, and provisioning
- **Audit**: Audit log access