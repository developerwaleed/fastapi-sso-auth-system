"""Application-wide constants"""

# OAuth Providers
OAUTH_PROVIDER_GOOGLE = "google"
OAUTH_PROVIDER_GITHUB = "github"
OAUTH_PROVIDER_AZURE = "azure"

SUPPORTED_OAUTH_PROVIDERS = [
    OAUTH_PROVIDER_GOOGLE,
    OAUTH_PROVIDER_GITHUB,
]

# Default Roles
ROLE_ADMIN = "admin"
ROLE_USER = "user"
ROLE_VIEWER = "viewer"

DEFAULT_ROLES = [ROLE_ADMIN, ROLE_USER, ROLE_VIEWER]

# Permission Actions
ACTION_READ = "read"
ACTION_WRITE = "write"
ACTION_DELETE = "delete"
ACTION_UPDATE = "update"

# Permission Resources
RESOURCE_USERS = "users"
RESOURCE_POSTS = "posts"
RESOURCE_ANALYTICS = "analytics"
RESOURCE_API_KEYS = "api_keys"

# Default Permissions
DEFAULT_PERMISSIONS = [
    {"name": "users:read", "resource": RESOURCE_USERS, "action": ACTION_READ},
    {"name": "users:write", "resource": RESOURCE_USERS, "action": ACTION_WRITE},
    {"name": "users:delete", "resource": RESOURCE_USERS, "action": ACTION_DELETE},
    {"name": "posts:read", "resource": RESOURCE_POSTS, "action": ACTION_READ},
    {"name": "posts:write", "resource": RESOURCE_POSTS, "action": ACTION_WRITE},
    {"name": "posts:delete", "resource": RESOURCE_POSTS, "action": ACTION_DELETE},
    {"name": "analytics:read", "resource": RESOURCE_ANALYTICS, "action": ACTION_READ},
]

# HTTP Headers
HEADER_API_KEY = "X-API-Key"
HEADER_AUTHORIZATION = "Authorization"

# Token Types
TOKEN_TYPE_BEARER = "bearer"

