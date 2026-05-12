# Auth API Testing Guide

## Quick Test in Browser Console

### 1. Test Auth Configuration

```javascript
import { runAllAuthTests } from "@/lib/tests/auth-integration.test";

const results = await runAllAuthTests();
console.table(results);
```

### 2. Test Login Flow (Manual)

```javascript
import { login, getStoredToken } from "@/lib/auth/api";

// Attempt login
try {
  const response = await login({
    email: "test@example.com",
    password: "TestPassword123",
  });
  console.log("✅ Login successful:", response);
  console.log("Token stored:", getStoredToken());
} catch (error) {
  console.error("❌ Login failed:", error);
}
```

### 3. Test Auth Hooks

```javascript
import { useAuth, useLazyLogin } from "@/lib/api/auth";
import { useState, useEffect } from "react";

// In a component:
export function TestAuth() {
  const auth = useAuth();
  const { launch: tryLogin } = useLazyLogin();

  useEffect(() => {
    auth.getCurrentUser();
  }, []);

  return (
    <div>
      <p>Authenticated: {auth.isAuthenticated ? "Yes" : "No"}</p>
      <p>User: {auth.user?.email}</p>
      <button
        onClick={() =>
          tryLogin({ email: "test@example.com", password: "test" })
        }
      >
        Login
      </button>
      <button onClick={() => auth.logout()}>Logout</button>
    </div>
  );
}
```

## Expected Behavior

### Login Success

```
POST http://localhost:8000/auth/login
↓
200 OK
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "user_id": 1,
    "email": "user@example.com",
    "full_name": "User Name",
    "is_active": true,
    "last_login": "2026-05-12T10:30:00"
  }
}
↓
Token stored in localStorage["access_token"]
```

### Login Failure

```
POST http://localhost:8000/auth/login
↓
401 Unauthorized / 422 Validation Error
{
  "detail": "Invalid credentials"
}
↓
Error thrown: "Invalid credentials"
localStorage remains empty
```

## Testing Checklist

- [ ] Backend `/auth/login` endpoint is running
- [ ] Valid test credentials exist in database
- [ ] Frontend API URL is configured (`NEXT_PUBLIC_API_URL`)
- [ ] localStorage is not disabled in browser
- [ ] Token is stored after successful login
- [ ] Token is included in subsequent requests
- [ ] Login form redirects to dashboard on success
- [ ] Error message displayed on login failure
- [ ] Logout clears localStorage

## Common Issues

### Issue: 404 Not Found

**Cause**: Backend auth endpoint not running
**Solution**: Start backend: `uvicorn app.main:app --reload --port 8000`

### Issue: 422 Validation Error

**Cause**: Invalid request format
**Solution**: Ensure email and password fields are correct

### Issue: 401 Unauthorized

**Cause**: Invalid credentials
**Solution**: Use valid test credentials from database

### Issue: CORS Error

**Cause**: Backend CORS not configured for frontend origin
**Solution**: Check backend `cors_origins` config includes `http://localhost:3000`

### Issue: Token not stored

**Cause**: localStorage disabled or window context issue
**Solution**: Check browser DevTools > Application > Storage > localStorage

## Files Modified

- `lib/auth/api.ts` - Updated to store tokens to localStorage
- `lib/api/auth.ts` - NEW: React hooks for auth operations
- `lib/tests/auth-integration.test.ts` - NEW: Auth integration tests
- `BACKEND_INTEGRATION.md` - Updated with auth section
