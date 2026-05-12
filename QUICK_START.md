# Auth API Integration - Troubleshooting Guide

## Issue: "Failed to fetch" on Login Page

### Root Cause

The frontend is trying to communicate with the backend API at `http://localhost:8000`, but the backend is **not running** or **not responding**.

## Solution: Start the Backend

### Step 1: Open a new terminal

```powershell
cd c:\Users\Nabil ramadhan\refactory_hackathon_bpjs\backend
```

### Step 2: Create/activate Python environment (if needed)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Run database migrations

```powershell
alembic upgrade head
```

### Step 5: (Optional) Seed test data

```powershell
python -m app.scripts.seed_db
```

### Step 6: Start the backend server

```powershell
uvicorn app.main:app --reload --port 8000
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

## Verify Backend is Running

### Option 1: Check in browser

Navigate to: `http://localhost:8000/docs`

You should see the FastAPI Swagger UI documentation.

### Option 2: Check in PowerShell

```powershell
curl http://localhost:8000/docs
# Should return HTML content
```

## Environment Configuration

Make sure frontend has `.env.local` in `frontend/` folder:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AUTH_STORAGE_KEY=access_token
```

If not, create it:

```powershell
@"
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AUTH_STORAGE_KEY=access_token
"@ | Out-File frontend/.env.local -Encoding UTF8
```

## Test the Integration

### 1. Backend Running

- ✅ Check: `http://localhost:8000/docs` loads

### 2. Frontend Running

- ✅ Check: `http://localhost:3000/login` loads

### 3. Attempt Login

- Use test credentials from database
- Should see success or proper error message
- No "Failed to fetch" errors

## Common Issues & Fixes

### Issue: Backend won't start

**Error**: `ModuleNotFoundError: No module named 'app'`
**Fix**:

```powershell
cd backend
pip install -r requirements.txt
```

### Issue: Port 8000 already in use

**Fix**:

```powershell
# Find process using port 8000
netstat -ano | findstr :8000
# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Issue: Database connection error

**Error**: `asyncpg.exceptions.PostgresError`
**Fix**:

```powershell
# Check if PostgreSQL is running
# Or update DATABASE_URL in backend/.env
alembic upgrade head
```

### Issue: CORS errors

**Error**: `Access to XMLHttpRequest at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked`
**Fix**: Backend CORS is already configured - just ensure backend is running

## Architecture

```
┌─────────────────┐
│  Frontend       │
│  localhost:3000 │
└────────┬────────┘
         │ HTTP
         │ localhost:8000/auth/login
         │
┌────────▼────────┐
│  Backend        │
│  localhost:8000 │
└─────────────────┘
     │
     ▼
  PostgreSQL
```

## Next Steps After Backend is Running

1. ✅ Backend running on port 8000
2. ✅ Login with valid credentials
3. ✅ Token stored in localStorage
4. ✅ Redirect to dashboard
5. ✅ Check other API endpoints working
6. ✅ Test AI workflows

## Quick Start Command

Run all in PowerShell (new session):

```powershell
# Terminal 1: Backend
cd c:\Users\Nabil ramadhan\refactory_hackathon_bpjs\backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd c:\Users\Nabil ramadhan\refactory_hackathon_bpjs\frontend
npm run dev
```

Then visit: `http://localhost:3000/login`
