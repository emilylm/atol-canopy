# Authentication with Refresh Tokens

This document explains how the authentication system works in the ATOL Canopy application with the new refresh token implementation.

## Overview

The authentication system uses a stateful refresh token approach with JWT (JSON Web Tokens):

1. **Access Tokens**: Short-lived JWTs (15 minutes) used for API authorization
2. **Refresh Tokens**: Longer-lived tokens (7 days) stored in the database and used to obtain new access tokens

## Authentication Flow

### 1. Login

When a user logs in with valid credentials, the system:

- Creates a short-lived access token (JWT)
- Generates a refresh token and stores it in the database
- Returns both tokens to the client

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=your_username&password=your_password
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "random_secure_string",
  "token_type": "bearer"
}
```

### 2. Using Access Tokens

Include the access token in the `Authorization` header for protected API requests:

```http
GET /api/v1/protected-endpoint
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3. Refreshing Tokens

When the access token expires, use the refresh token to get a new pair of tokens:

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "your_refresh_token"
}
```

Response:

```json
{
  "access_token": "new_access_token",
  "refresh_token": "new_refresh_token",
  "token_type": "bearer"
}
```

**Note**: The system implements token rotation - each time you refresh, you get a new refresh token and the old one is invalidated.

### 4. Logout

To securely logout, revoke all refresh tokens:

```http
POST /api/v1/auth/logout
Authorization: Bearer your_access_token
```

Response:

```json
{
  "message": "Successfully logged out"
}
```

## Security Features

1. **Token Rotation**: Each refresh operation invalidates the used refresh token and issues a new one
2. **Database Storage**: Refresh tokens are stored as secure hashes, not plaintext
3. **Automatic Expiration**: Both access and refresh tokens have expiration times
4. **Revocation**: Refresh tokens can be revoked by the user or the system
5. **Cascading Deletion**: When a user is deleted, all their refresh tokens are automatically removed

## Implementation Details

- Access tokens are stateless JWTs signed with a secret key
- Refresh tokens are securely generated random strings
- Refresh tokens are stored in the `refresh_tokens` table with a hash of the actual token
- Token validation includes checking expiration and revocation status

## Best Practices for Client Applications

1. Store the refresh token securely (e.g., in an HTTP-only cookie or secure storage)
2. Store the access token in memory (not localStorage) to prevent XSS attacks
3. Implement automatic token refresh when access tokens expire
4. Always call the logout endpoint when the user logs out
