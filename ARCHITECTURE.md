# System Architecture

## Overview

This FastAPI application follows a **layered architecture** pattern with clear separation of concerns, making it scalable, maintainable, and testable. The architecture is designed for enterprise-grade applications with complex business logic and authorization requirements.

## Project Structure

```
app/
├── api/                      # API Layer
│   ├── deps.py              # Dependency injection & auth dependencies
│   └── v1/                  # API version 1
│       ├── __init__.py      # API router aggregation
│       └── endpoints/       # API endpoint handlers
│           ├── auth.py      # OAuth & authentication
│           ├── users.py     # User management
│           ├── api_keys.py  # API key management
│           ├── roles.py     # Roles & permissions
│           └── examples.py  # Example endpoints
│
├── core/                    # Core Layer (Infrastructure)
│   ├── config.py           # Application configuration
│   ├── security.py         # Security utilities (JWT, hashing)
│   └── constants.py        # Application-wide constants
│
├── db/                      # Database Layer
│   ├── base.py             # SQLAlchemy base & model imports
│   ├── session.py          # Database session & connection
│   └── init_db.py          # Database initialization
│
├── models/                  # Data Models Layer
│   ├── user.py             # User model
│   ├── oauth.py            # OAuth account model
│   ├── api_key.py          # API key model
│   ├── role.py             # Role model
│   ├── permission.py       # Permission model
│   └── associations.py     # Many-to-many association tables
│
├── schemas/                 # Pydantic Schemas Layer
│   ├── user.py             # User schemas
│   ├── oauth.py            # OAuth schemas
│   ├── api_key.py          # API key schemas
│   ├── role.py             # Role schemas
│   ├── permission.py       # Permission schemas
│   └── auth.py             # Auth schemas (tokens, etc.)
│
├── crud/                    # Repository Layer (Data Access)
│   ├── base.py             # Base CRUD operations
│   ├── user.py             # User repository
│   ├── api_key.py          # API key repository
│   ├── role.py             # Role repository
│   └── permission.py       # Permission repository
│
├── services/                # Business Logic Layer
│   ├── auth_service.py     # Authentication business logic
│   ├── user_service.py     # User business logic
│   └── api_key_service.py  # API key business logic
│
├── utils/                   # Utilities
│   └── oauth_providers.py  # OAuth provider integrations
│
└── main.py                  # Application entry point
```

## Architectural Layers

### 1. API Layer (`api/`)

**Responsibility:** HTTP request/response handling, routing, and API versioning.

- **Endpoints:** Define API routes and handle HTTP-specific logic
- **Dependencies:** Authentication and authorization dependencies via `deps.py`
- **Versioning:** API versioned under `/api/v1/` for backward compatibility

**Key Files:**
- `api/deps.py`: Reusable FastAPI dependencies (auth, permissions, roles)
- `api/v1/endpoints/`: Individual endpoint modules

**Benefits:**
- Easy to version APIs (v1, v2, etc.)
- Clean separation of HTTP concerns
- Testable endpoint logic

### 2. Core Layer (`core/`)

**Responsibility:** Application configuration and cross-cutting concerns.

- **Config:** Environment-based settings using Pydantic
- **Security:** JWT creation/validation, API key generation
- **Constants:** Shared constants (roles, permissions, OAuth providers)

**Benefits:**
- Centralized configuration
- Type-safe settings
- Reusable security utilities

### 3. Database Layer (`db/`)

**Responsibility:** Database connection and initialization.

- **Session:** SQLAlchemy engine and session management
- **Base:** Declarative base for all models
- **Init DB:** Database seeding and initialization

**Benefits:**
- Connection pooling configured
- Easy database switching
- Clean session management via dependency injection

### 4. Models Layer (`models/`)

**Responsibility:** Database schema definition using SQLAlchemy ORM.

- Each model in separate file for clarity
- Relationships defined with lazy loading strategies
- Business logic properties (e.g., `user.permissions`)

**Benefits:**
- Single responsibility per file
- Easy to maintain and test
- Clear relationships

### 5. Schemas Layer (`schemas/`)

**Responsibility:** Data validation and serialization using Pydantic.

- **Request schemas:** Validate incoming data
- **Response schemas:** Control outgoing data
- **Type safety:** Full type hints and validation

**Benefits:**
- Automatic API documentation
- Runtime data validation
- Separation from database models

### 6. CRUD/Repository Layer (`crud/`)

**Responsibility:** Data access operations abstracted from business logic.

- **Base CRUD:** Generic operations (get, create, update, delete)
- **Specialized repos:** Model-specific operations
- No business logic - pure data access

**Benefits:**
- Reusable data access patterns
- Easy to mock for testing
- Database operations isolated

### 7. Services Layer (`services/`)

**Responsibility:** Business logic and orchestration.

- Complex operations spanning multiple models
- Business rules enforcement
- Orchestrates CRUD operations

**Examples:**
- `AuthService.create_user_token()`: Generates JWT with roles/permissions
- `UserService.assign_role_to_user()`: Business logic for role assignment
- `APIKeyService.validate_api_key()`: Key validation and expiration logic

**Benefits:**
- Business logic centralized
- Reusable across different API endpoints
- Easy to test in isolation

### 8. Utils Layer (`utils/`)

**Responsibility:** Utility functions and third-party integrations.

- OAuth provider integrations (Google, GitHub)
- Helper functions
- External API interactions

## Design Patterns

### 1. Repository Pattern (CRUD Layer)

Abstracts data access logic from business logic.

```python
# Usage in service
user = user_crud.get_by_email(db, email="user@example.com")
user_crud.add_role(db, user=user, role=admin_role)
```

### 2. Service Pattern (Services Layer)

Encapsulates business logic and orchestrates operations.

```python
# Usage in endpoint
token = AuthService.create_user_token(user)
APIKeyService.validate_api_key(db, key=api_key)
```

### 3. Dependency Injection

FastAPI dependencies for clean, testable code.

```python
# Authentication dependencies
async def get_current_user_jwt_required(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    ...
```

### 4. Strategy Pattern

Different authentication strategies (JWT, API Key, Either).

```python
@router.get("/jwt-only")
async def endpoint(user: User = Depends(get_current_user_jwt_required)):
    ...

@router.get("/either-auth")
async def endpoint(user: User = Depends(get_current_user_either)):
    ...
```

## Data Flow

### Authentication Flow

```
Client Request
    ↓
API Endpoint (api/v1/endpoints/auth.py)
    ↓
OAuth Provider (utils/oauth_providers.py)
    ↓
AuthService (services/auth_service.py)
    ↓
UserCRUD (crud/user.py)
    ↓
Database (models/user.py)
```

### Authorization Flow

```
Client Request with Token/API Key
    ↓
Dependency (api/deps.py)
    ├→ JWT: decode_access_token() → get_current_user_from_jwt()
    └→ API Key: APIKeyService.validate_api_key() → get_current_user_from_apikey()
    ↓
Check Roles/Permissions (require_roles() or require_permissions())
    ↓
API Endpoint
    ↓
Service Layer (business logic)
    ↓
CRUD Layer (data access)
    ↓
Database
```

## Key Design Decisions

### 1. API Versioning

**Decision:** Version API under `/api/v1/`

**Rationale:**
- Backward compatibility
- Gradual migration to new versions
- Industry standard

### 2. Separate Models and Schemas

**Decision:** SQLAlchemy models separate from Pydantic schemas

**Rationale:**
- Different concerns (persistence vs validation)
- More control over API responses
- Prevent accidental data exposure

### 3. Service Layer

**Decision:** Business logic in dedicated service layer

**Rationale:**
- Reusable across endpoints
- Easier to test
- Single source of truth for business rules

### 4. Repository Pattern

**Decision:** CRUD layer abstracts data access

**Rationale:**
- Database-agnostic business logic
- Easy to mock for testing
- Consistent data access patterns

### 5. Dependency Injection for Auth

**Decision:** Auth logic in reusable dependencies

**Rationale:**
- DRY (Don't Repeat Yourself)
- Declarative auth requirements
- Easy to add new auth strategies

## Security Architecture

### Authentication Strategies

1. **JWT Tokens**
   - User-centric authentication
   - Contains roles and permissions in payload
   - Short-lived (30 min default)

2. **API Keys**
   - System-to-system authentication
   - Long-lived tokens
   - Can have independent roles/permissions
   - Usage tracking (last_used_at)

3. **Flexible Requirements**
   - JWT only endpoints
   - API key only endpoints
   - Either auth method endpoints

### Authorization Model

**RBAC (Role-Based Access Control):**
- Users have roles
- Roles contain permissions
- Permissions define resource:action pairs

**Permission-Based:**
- Fine-grained control
- Format: `resource:action` (e.g., `users:read`)
- Can be assigned directly to API keys

## Scalability Considerations

### Current Architecture Supports:

1. **Horizontal Scaling**
   - Stateless JWT authentication
   - Database connection pooling
   - No in-memory session storage

2. **Caching Layer** (easy to add)
   - Service layer ready for caching
   - Repository pattern supports cache-aside pattern

3. **Async Operations**
   - FastAPI fully async
   - Async OAuth calls
   - Ready for async database drivers

4. **Microservices** (if needed)
   - Clear layer separation
   - Services can become separate services
   - API versioning supports gradual migration

## Testing Strategy

### Unit Tests
- Service layer (business logic)
- CRUD layer (data access)
- Utility functions

### Integration Tests
- API endpoints
- Database operations
- OAuth flow

### Test Structure
```
tests/
├── unit/
│   ├── test_services/
│   ├── test_crud/
│   └── test_utils/
└── integration/
    ├── test_api/
    └── test_auth/
```

## Future Enhancements

1. **Caching Layer**
   - Redis for JWT token blacklist
   - Cache user permissions

2. **Event System**
   - Event-driven architecture
   - Audit logging

3. **Background Tasks**
   - Celery for async tasks
   - Email notifications

4. **Rate Limiting**
   - Per-user rate limits
   - API key rate limits

5. **Monitoring**
   - APM integration (Sentry, DataDog)
   - Performance metrics

## Conclusion

This architecture provides:
- ✅ Clear separation of concerns
- ✅ Scalability and maintainability
- ✅ Testability at all layers
- ✅ Industry best practices
- ✅ Production-ready design

Perfect for a **Senior Python Developer** role demonstrating expertise in clean architecture, design patterns, and scalable system design.

