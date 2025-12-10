# FastAPI SSO & Authorization System

A production-ready FastAPI backend featuring SSO authentication (Google & GitHub) with comprehensive JWT and API Key authorization system supporting role-based and permission-based access control.

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────┐
│   Client    │
│  (Postman)  │
└──────┬──────┘
       │
       │ HTTP/HTTPS
       │
┌──────▼──────────────────────────────────┐
│         FastAPI Application              │
│  ┌────────────────────────────────────┐ │
│  │     Authentication Layer           │ │
│  │  - JWT Token Validation            │ │
│  │  - API Key Validation              │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │     Authorization Layer            │ │
│  │  - Role-Based Access Control       │ │
│  │  - Permission-Based Access Control │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │         API Routes                 │ │
│  │  - /auth (OAuth callbacks)         │ │
│  │  - /users                          │ │
│  │  - /api-keys                       │ │
│  │  - /roles                          │ │
│  │  - /demo                           │ │
│  └────────────────────────────────────┘ │
└──────┬──────────────────────────────────┘
       │
       │ SQLAlchemy ORM
       │
┌──────▼──────────┐     ┌──────────────┐
│   PostgreSQL    │────▶│  OAuth APIs  │
│    Database     │     │  - Google    │
└─────────────────┘     │  - GitHub    │
                        └──────────────┘
```

### Authentication Flow

#### OAuth SSO Flow
1. Client requests login URL from `/auth/{provider}/login`
2. Server returns OAuth authorization URL
3. User authenticates with OAuth provider (Google/GitHub)
4. Provider redirects to callback endpoint with authorization code
5. Server exchanges code for access token
6. Server fetches user info from provider
7. Server creates/links user account
8. Server generates JWT token with roles & permissions
9. JWT token returned to client

#### JWT Authentication
```
Authorization: Bearer <jwt-token>
```

#### API Key Authentication
```
X-API-Key: <api-key>
```

## 📊 Database Schema

### Entity Relationship Diagram

```
┌──────────────┐
│    users     │
├──────────────┤
│ id (PK)      │
│ email        │───┐
│ full_name    │   │
│ avatar_url   │   │
│ is_active    │   │
│ is_superuser │   │
│ created_at   │   │
│ updated_at   │   │
└──────────────┘   │
       │           │
       │ 1:N       │ 1:N
       │           │
┌──────▼──────────┐│   ┌──────────────┐
│ oauth_accounts  ││   │   api_keys   │
├─────────────────┤│   ├──────────────┤
│ id (PK)         ││   │ id (PK)      │
│ user_id (FK)    ││   │ user_id (FK) │◀───┘
│ provider        ││   │ key (UNIQUE) │
│ provider_user_id││   │ name         │
│ access_token    ││   │ description  │
│ refresh_token   ││   │ is_active    │
│ token_expires_at││   │ expires_at   │
│ provider_data   ││   │ last_used_at │
│ created_at      ││   │ created_at   │
└─────────────────┘│   └──────────────┘
                   │          │
                   │          │ M:N
                   │          │
       ┌───────────┴──────────▼────────┐
       │                               │
┌──────▼──────┐              ┌─────────▼──────┐
│    roles    │◀────M:N─────▶│  permissions   │
├─────────────┤              ├────────────────┤
│ id (PK)     │              │ id (PK)        │
│ name        │              │ name           │
│ description │              │ description    │
│ created_at  │              │ resource       │
└─────────────┘              │ action         │
       ▲                     │ created_at     │
       │                     └────────────────┘
       │ M:N                          ▲
       │                              │
       └──────────────────────────────┘
              M:N
```

### Tables Description

#### users
Stores user account information from SSO providers.
- Primary user identity table
- Links to multiple OAuth providers
- Can have multiple roles
- Can own multiple API keys

#### oauth_accounts
Links users to their OAuth provider accounts.
- Supports multiple providers per user (Google, GitHub, Azure)
- Stores provider-specific tokens
- Enables account linking

#### api_keys
Programmatic access tokens for users.
- Can have independent roles and permissions
- Support expiration dates
- Track usage (last_used_at)

#### roles
Groups of permissions for easier management.
- Can be assigned to users and API keys
- Contain multiple permissions
- Examples: admin, user, viewer

#### permissions
Fine-grained access control.
- Resource-action based (e.g., users:read, posts:write)
- Can be assigned directly to API keys
- Assigned to users through roles

### Association Tables (Many-to-Many)

- `user_roles`: Links users to roles
- `role_permissions`: Links roles to permissions
- `apikey_roles`: Links API keys to roles
- `apikey_permissions`: Links API keys to permissions

## 🚀 Setup Instructions

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Google OAuth credentials (optional)
- GitHub OAuth credentials (optional)

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd fastapi-sso-auth
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Create PostgreSQL Database

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE fastapi_sso_db;

# Exit
\q
```

#### Update Database Connection

Copy `.env.example` to `.env` and update:

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/fastapi_sso_db
SECRET_KEY=your-super-secret-key-generate-with-openssl-rand-hex-32
```

### 5. OAuth Configuration (Optional)

#### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URI: `   http://localhost:8000/api/v1/auth/google/callback`
6. Update `.env`:

```env
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=   http://localhost:8000/api/v1/auth/google/callback
```

#### GitHub OAuth Setup

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Set Authorization callback URL: `http://localhost:8000/api/v1/auth/github/callback`
4. Update `.env`:

```env
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_REDIRECT_URI=http://localhost:8000/api/v1/auth/github/callback
```

### 6. Generate Secret Key

```bash
# Generate a secure secret key
openssl rand -hex 32
```

Update `SECRET_KEY` in `.env` with the generated key.

### 7. Run Database Migrations

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 8. Seed Database (Optional)

```bash
export PYTHONPATH=.
python scripts/seed_db.py
```

This creates:
- Default permissions (users:read, users:write, etc.)
- Default roles (admin, user, viewer)
- Test users
- Test API keys

### 9. Run Application

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- API: `http://localhost:8000`
- Interactive Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📚 API Endpoints Documentation

### Authentication Endpoints

#### `GET /auth/google/login`
Initiate Google OAuth login flow.

**Response:**
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
  "state": "random-state-token"
}
```

#### `GET /auth/google/callback`
Google OAuth callback endpoint.

**Query Parameters:**
- `code`: Authorization code from Google
- `state`: State token for CSRF protection

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "avatar_url": "https://...",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2024-01-01T00:00:00Z",
    "roles": [...]
  }
}
```

#### `GET /auth/github/login`
Initiate GitHub OAuth login flow.

#### `GET /auth/github/callback`
GitHub OAuth callback endpoint.

### User Endpoints (JWT Required)

#### `GET /users/me`
Get current user profile.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "avatar_url": "https://...",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-01T00:00:00Z",
  "roles": [
    {
      "id": 1,
      "name": "user",
      "description": "Regular user",
      "created_at": "2024-01-01T00:00:00Z",
      "permissions": [...]
    }
  ]
}
```

#### `GET /users/`
List all users (Admin only).

#### `POST /users/{user_id}/roles/{role_id}`
Assign role to user.

#### `DELETE /users/{user_id}/roles/{role_id}`
Remove role from user.

### API Key Endpoints (JWT Required)

#### `POST /api-keys/`
Create new API key.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Request Body:**
```json
{
  "name": "My API Key",
  "description": "API key for automation",
  "expires_at": "2024-12-31T23:59:59Z",
  "role_ids": [1, 2],
  "permission_ids": [3, 4]
}
```

**Response:**
```json
{
  "id": 1,
  "name": "My API Key",
  "description": "API key for automation",
  "key": "long-random-api-key-string",
  "is_active": true,
  "expires_at": "2024-12-31T23:59:59Z",
  "created_at": "2024-01-01T00:00:00Z",
  "roles": [...],
  "permissions": [...]
}
```

**⚠️ Important:** Save the API key immediately - it won't be shown again!

#### `GET /api-keys/`
List all API keys for current user.

#### `GET /api-keys/{api_key_id}`
Get specific API key details.

#### `DELETE /api-keys/{api_key_id}`
Delete an API key.

#### `PATCH /api-keys/{api_key_id}/deactivate`
Deactivate an API key.

#### `PATCH /api-keys/{api_key_id}/activate`
Activate an API key.

### Role & Permission Endpoints (JWT Required)

#### `POST /roles/permissions/`
Create new permission.

**Request Body:**
```json
{
  "name": "posts:write",
  "description": "Write blog posts",
  "resource": "posts",
  "action": "write"
}
```

#### `GET /roles/permissions/`
List all permissions.

#### `POST /roles/`
Create new role.

**Request Body:**
```json
{
  "name": "editor",
  "description": "Content editor role",
  "permission_ids": [1, 2, 3]
}
```

#### `GET /roles/`
List all roles.

#### `GET /roles/{role_id}`
Get role details.

#### `POST /roles/{role_id}/permissions/{permission_id}`
Add permission to role.

### Example Endpoints

#### `GET /examples/public`
Public endpoint - no authentication required.

**Response:**
```json
{
  "message": "This is a public endpoint - no authentication required",
  "status": "public"
}
```

#### `GET /examples/jwt-only`
Requires JWT authentication only.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "message": "Success! You accessed this endpoint with JWT token",
  "user_id": 1,
  "email": "user@example.com",
  "auth_type": "JWT"
}
```

#### `GET /examples/apikey-only`
Requires API Key authentication only.

**Headers:**
```
X-API-Key: <api-key>
```

**Response:**
```json
{
  "message": "Success! You accessed this endpoint with API Key",
  "user_id": 1,
  "email": "user@example.com",
  "auth_type": "API_KEY"
}
```

#### `GET /examples/either-auth`
Accepts either JWT or API Key.

**Headers (choose one):**
```
Authorization: Bearer <jwt-token>
OR
X-API-Key: <api-key>
```

#### `GET /examples/admin-only`
Requires 'admin' role.

**Headers:**
```
Authorization: Bearer <jwt-token>
OR
X-API-Key: <api-key>
```

#### `GET /examples/read-users-permission`
Requires 'users:read' permission.

#### `GET /examples/write-users-permission`
Requires 'users:write' permission.

## 🧪 Testing with Postman

### Importing Postman Collection

1. Open Postman
2. Click "Import" button
3. Select `FastAPI_SSO_Auth.postman_collection.json`
4. Collection will be imported with all endpoints

### Environment Setup

Create a new environment in Postman with these variables:

```
base_url: http://localhost:8000
jwt_token: (will be set after login)
api_key: (will be set after creating API key)
```

### Testing Flow

#### 1. OAuth Login (Manual Browser Flow)

Since OAuth requires browser interaction, follow these steps:

1. Run the request: `GET /auth/google/login` (or GitHub)
2. Copy the `authorization_url` from response
3. Open the URL in a browser
4. Complete OAuth authentication
5. After redirect, copy the `access_token` from the response
6. Set `jwt_token` environment variable in Postman

#### 2. Get Current User

1. Request: `GET /users/me`
2. Headers will automatically use `{{jwt_token}}`
3. Verify user details are returned

#### 3. Create Roles and Permissions

1. Create permissions: `POST /roles/permissions/`
2. Create roles: `POST /roles/`
3. Assign roles to your user: `POST /users/{user_id}/roles/{role_id}`

#### 4. Create API Key

1. Request: `POST /api-keys/`
2. Save the returned `key` value
3. Set `api_key` environment variable

#### 5. Test Different Auth Requirements

Test all example endpoints:
- `/examples/public` - No auth
- `/examples/jwt-only` - JWT only
- `/examples/apikey-only` - API Key only
- `/examples/either-auth` - JWT or API Key
- `/examples/admin-only` - Admin role required
- `/examples/read-users-permission` - Specific permission

### Expected Test Results

✅ **JWT-only endpoint** with JWT token → Success  
❌ **JWT-only endpoint** with API key → 401 Unauthorized  
✅ **API Key-only endpoint** with API key → Success  
❌ **API Key-only endpoint** with JWT → 401 Unauthorized  
✅ **Either auth endpoint** with JWT → Success  
✅ **Either auth endpoint** with API key → Success  
✅ **Admin endpoint** with admin role → Success  
❌ **Admin endpoint** without admin role → 403 Forbidden  

*Note: Example endpoints are provided specifically to demonstrate different authentication and authorization requirements.*  

## 🔐 JWT Payload Structure

JWT tokens contain the following claims:

```json
{
  "sub": 1,                    // User ID
  "email": "user@example.com", // User email
  "roles": [                   // User roles
    "admin",
    "user"
  ],
  "permissions": [             // Aggregated permissions from all roles
    "users:read",
    "users:write",
    "users:delete",
    "posts:read",
    "posts:write",
    "analytics:read"
  ],
  "exp": 1672531200            // Expiration timestamp
}
```

### Decoding JWT (for debugging)

You can decode JWT tokens at [jwt.io](https://jwt.io) to inspect the payload.

**Example decoded token:**
```json
{
  "sub": 1,
  "email": "admin@example.com",
  "roles": ["admin"],
  "permissions": [
    "users:read",
    "users:write",
    "users:delete",
    "posts:read",
    "posts:write",
    "posts:delete",
    "analytics:read"
  ],
  "exp": 1704067200
}
```

## 🔒 Authorization Examples

### Role-Based Authorization

```python
@router.get("/admin-only")
async def admin_endpoint(
    current_user: User = Depends(get_current_user_either),
    _: bool = Depends(require_roles(["admin"]))
):
    return {"message": "Admin access granted"}
```

### Permission-Based Authorization

```python
@router.get("/users")
async def list_users(
    current_user: User = Depends(get_current_user_either),
    _: bool = Depends(require_permissions(["users:read"]))
):
    return {"users": [...]}
```

### Multiple Auth Methods

```python
# JWT only
@router.get("/jwt-only")
async def jwt_only(user: User = Depends(get_current_user_jwt_only)):
    pass

# API Key only
@router.get("/apikey-only")
async def apikey_only(user: User = Depends(get_current_user_apikey_only)):
    pass

# Either JWT or API Key
@router.get("/either")
async def either(user: User = Depends(get_current_user_either)):
    pass
```

## 🏆 Features Implemented

### Core Requirements

✅ SSO login with Google and GitHub  
✅ Link multiple provider accounts to same user  
✅ JWT token generation with roles and permissions  
✅ API Keys with roles and permissions  
✅ Routes requiring JWT only  
✅ Routes requiring API key only  
✅ Routes allowing either authentication method  
✅ Role-based authorization  
✅ Permission-based authorization  
✅ Comprehensive README  
✅ Database migrations  
✅ Postman collection  

### Additional Features

✅ SQLAlchemy models with proper relationships  
✅ Alembic migrations  
✅ Database seeding script  
✅ API key expiration  
✅ API key usage tracking  
✅ Comprehensive API documentation (Swagger/ReDoc)  
✅ CORS configuration  
✅ Health check endpoints  
✅ Token expiration handling  
✅ Proper error handling and HTTP status codes  

## 🛠️ Technology Stack

- **Framework:** FastAPI 0.109.0
- **Database:** PostgreSQL with SQLAlchemy 2.0
- **Authentication:** Authlib (OAuth2), python-jose (JWT)
- **Migrations:** Alembic
- **Validation:** Pydantic v2
- **Server:** Uvicorn

## 📝 Design Decisions & Assumptions

### Authentication
- **OAuth Providers:** Implemented Google and GitHub (most commonly used)
- **Account Linking:** Users can link multiple OAuth providers to one account via email matching
- **Token Expiration:** JWT tokens expire in 30 minutes (configurable)

### Authorization
- **Role-Based:** Roles group related permissions for easier management
- **Permission-Based:** Fine-grained control with resource:action format (e.g., users:read)
- **API Keys:** Can have roles and/or permissions independent of user's roles

### Security
- **API Key Generation:** Uses `secrets.token_urlsafe(48)` for cryptographically secure keys
- **JWT Secret:** Must be changed in production (generate with `openssl rand -hex 32`)
- **Password Hashing:** Not needed as we use OAuth (no password storage)

### Database
- **PostgreSQL:** Chosen for production-readiness, ACID compliance, and JSON support
- **Soft Deletes:** Not implemented (can be added via `is_deleted` flag)
- **Audit Trail:** Timestamps (created_at, updated_at) on all entities

## 🚨 Production Considerations

Before deploying to production:

1. **Change SECRET_KEY** to a strong, random value
2. **Use HTTPS** for all endpoints
3. **Configure OAuth redirect URIs** for production domain
4. **Set up database backups**
5. **Implement rate limiting** (e.g., with slowapi)
6. **Add logging** (e.g., with loguru)
7. **Set up monitoring** (e.g., Sentry)
8. **Use environment-specific configs**
9. **Mask API keys** in responses (show first/last chars only)
10. **Implement API key rotation**

## 📞 Support & Contact

For questions or issues:
- Review the Postman collection examples
- Check FastAPI documentation: https://fastapi.tiangolo.com
- SQLAlchemy docs: https://docs.sqlalchemy.org

## 📄 License

This project is created as a technical assessment and is free to use for evaluation purposes.

---

**Built with ❤️ using FastAPI and SQLAlchemy**

**Author:** Waleed Amjad  
**GitHub:** [github.com/developerwaleed](https://github.com/developerwaleed)

