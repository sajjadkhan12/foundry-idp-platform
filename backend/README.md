# DevPlatform IDP Backend

FastAPI backend with JWT authentication and RBAC for the Internal Developer Platform.

## Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup PostgreSQL Database

Make sure PostgreSQL is running locally. Then create the database and tables:

```bash
psql -U postgres -f schema.sql
```

Or manually:
```bash
psql -U postgres
CREATE DATABASE devplatform_idp;
\c devplatform_idp
# Then run the SQL from schema.sql
```

### 4. Configure Environment

Copy `.env.example` to `.env` and update if needed:

```bash
cp .env.example .env
```

### 5. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Default Users

Two default users are created:

**Admin User:**
- Email: `admin@devplatform.com`
- Password: `admin123`
- Role: `admin`

**Engineer User:**
- Email: `engineer@devplatform.com`
- Password: `engineer123`
- Role: `engineer`

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update current user profile
- `POST /api/v1/users/me/password` - Change password
- `POST /api/v1/users/me/avatar` - Upload avatar
- `GET /api/v1/users` - List all users (admin only, supports search & role filters)
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user (admin only, supports role & password reset)
- `PUT /api/v1/users/{user_id}/role` - Update user role (admin only)

### Deployments
- `GET /api/v1/deployments` - List deployments (filtered by role)
- `GET /api/v1/deployments/{id}` - Get deployment by ID
- `POST /api/v1/deployments` - Create deployment
- `PUT /api/v1/deployments/{id}` - Update deployment
- `DELETE /api/v1/deployments/{id}` - Delete deployment

## RBAC Permissions

### Admin Role
- Full access to all resources
- Can manage users and roles
- Can view all deployments
- Can manage plugins and settings

### Engineer Role
- Can create deployments
- Can only view/edit/delete own deployments
- Cannot manage users or roles
- Cannot manage plugins or settings

## Pulumi ESC Configuration

The platform uses **Pulumi ESC (Environments, Secrets, and Configuration)** for automatic cloud credential management. ESC eliminates the need for manual credential injection by automatically handling OIDC token exchange for AWS, GCP, and Azure.

### Quick Setup

1. **Install Pulumi ESC CLI:**
   ```bash
   brew install pulumi/tap/esc
   # Or: curl -fsSL https://get.pulumi.com/esc/install.sh | sh
   ```

2. **Login to ESC:**
   ```bash
   esc login
   ```

3. **Create ESC environments** for each cloud provider (see detailed guides below)

4. **Configure in your application:**
   ```bash
   # In .env or Kubernetes secrets
   PULUMI_ACCESS_TOKEN=your-pulumi-access-token
   PULUMI_ORG=your-org-name
   PULUMI_ESC_ENVIRONMENT_GCP=your-org/gcp-production
   PULUMI_ESC_ENVIRONMENT_AWS=your-org/aws-production
   PULUMI_ESC_ENVIRONMENT_AZURE=your-org/azure-production
   PULUMI_USE_ESC=true
   ```

### Detailed Setup Guides

For detailed setup instructions, see the main [README.md](../README.md#configuration) in the project root.

**Quick Reference:**

1. **GCP ESC Setup:**
   - Create GCP Workload Identity Pool and Provider in Pulumi Cloud
   - Create ESC environment: `esc env init your-org/gcp-production`
   - Configure with `pulumi-cloud-pool` and `pulumi-oidc-provider`
   - Set `PULUMI_ESC_ENVIRONMENT_GCP=your-org/gcp-production`

2. **AWS ESC Setup:**
   - Create AWS IAM OIDC provider: `aws iam create-open-id-connect-provider --url https://api.pulumi.com/oidc --client-id-list your-org`
   - Create IAM role with trust policy for Pulumi ESC
   - Create ESC environment: `esc env init your-org/aws-production`
   - Configure with role ARN
   - Set `PULUMI_ESC_ENVIRONMENT_AWS=your-org/aws-production`

### How It Works

1. When deploying infrastructure, the system detects the cloud provider from the plugin manifest
2. It automatically selects the appropriate ESC environment (GCP, AWS, or Azure)
3. ESC handles OIDC token exchange and provides credentials as environment variables
4. Pulumi programs run with cloud credentials automatically - no manual injection needed

### Benefits

- ✅ **No Static Keys**: Credentials are generated on-demand via OIDC
- ✅ **Automatic Rotation**: Credentials expire and refresh automatically
- ✅ **Centralized Management**: All credentials managed in Pulumi Cloud
- ✅ **Multi-Provider Support**: Same pattern works for AWS, GCP, and Azure
- ✅ **Reduced Complexity**: Eliminates ~150 lines of credential injection code

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PULUMI_ACCESS_TOKEN` | Pulumi Cloud access token | `pul-xxxxx` |
| `PULUMI_ORG` | Pulumi organization name | `your-org` |
| `PULUMI_ESC_ENVIRONMENT_GCP` | ESC environment for GCP | `your-org/gcp-production` |
| `PULUMI_ESC_ENVIRONMENT_AWS` | ESC environment for AWS | `your-org/aws-production` |
| `PULUMI_ESC_ENVIRONMENT_AZURE` | ESC environment for Azure | `your-org/azure-production` |
| `PULUMI_USE_ESC` | Enable ESC (default: `true`) | `true` |

### Testing ESC

```bash
# Test GCP ESC environment
esc env run your-org/gcp-production -- env | grep GOOGLE

# Test AWS ESC environment
esc env run your-org/aws-production -- env | grep AWS
```

## Testing

Test the API using the Swagger UI at `http://localhost:8000/docs` or use curl:

```bash
# Register a new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123",
    "full_name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@devplatform.com",
    "password": "admin123"
  }'

# Use the access token in subsequent requests
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
