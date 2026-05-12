# Backend Integration Guide

## Overview

The frontend is now integrated with the FastAPI backend. All data is fetched in real-time from the backend APIs.

## Configuration

### 1. Environment Setup

Create `.env.local` in the `frontend/` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AUTH_STORAGE_KEY=access_token
```

### 2. Starting the Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
alembic upgrade head
python -m app.scripts.seed_db
uvicorn app.main:app --reload --port 8000
```

### 3. Starting the Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on `http://localhost:3001`.

## API Integration

### API Client

The API client is located in `lib/api/client.ts` and provides methods for:

- Projects: `projectsAPI.list()`, `projectsAPI.get()`, `projectsAPI.create()`, etc.
- Tasks: `tasksAPI.list()`, `tasksAPI.create()`, `tasksAPI.updateStatus()`, etc.
- Teams: `teamsAPI.list()`, `teamsAPI.getMembers()`, etc.
- Workers: `workersAPI.list()`, `workersAPI.getKPI()`, etc.
- AI Assistant: `aiAssistantAPI.planning()`, `aiAssistantAPI.sprintSummary()`, etc.

### Hooks

Use React hooks for data fetching:

```typescript
import { useProjects, useProject } from "@/lib/api/projects";
import { useTasks, useTask } from "@/lib/api/tasks";
import { useTeams, useTeamMembers } from "@/lib/api/teams";
import { useAIPlanning, useAIJobStatus } from "@/lib/api/ai";

// Fetch list of projects
const { data: projects, loading, error, refetch } = useProjects();

// Fetch specific project
const { data: project } = useProject(projectId);

// Launch AI planning (lazy)
const { launch } = useLazyAIPlanning();
const response = await launch({ prompt: "Plan Q3 2024" });

// Poll job status
const { data: jobStatus } = useAIJobStatus(jobId);
```

## Data Transformation

Mock data has been replaced with real API calls. The response formats are:

### ProjectResponse

```typescript
{
  project_id: number;
  name: string;
  description?: string;
  status: string;
  created_by: number;
  start_date?: string;
  end_date?: string;
  repository_url?: string;
  repository_type?: string;
  version: number;
}
```

### ProjectTaskResponse

```typescript
{
  task_id: number;
  project_id: number;
  title: string;
  description?: string;
  status: string;
  priority: string;
  story_points?: number;
  assigned_to?: number;
  deadline?: string;
  version: number;
}
```

### TeamResponse

```typescript
{
  team_id: number;
  name: string;
  category_id: number;
  description?: string;
  status: string;
  capacity_hours: number;
}
```

### WorkerResponse

```typescript
{
  worker_id: number;
  full_name: string;
  email: string;
  division_id: number;
  employment_status: string;
}
```

## AI Assistant Integration

The AI assistant has been integrated with proper wrapping for async workflows:

### Workflows

1. **Planning** - `/ai-assistant/planning`
   - Generate project plans
   - Requires: prompt, context (project_id, team_size)

2. **Sprint Summary** - `/ai-assistant/sprint-summary`
   - Summarize sprint progress
   - Requires: prompt, context (sprint_id, project_id)

3. **Task Recommendation** - `/ai-assistant/task-recommendation`
   - Get task recommendations
   - Requires: prompt, context (project_id, sprint_id)

4. **Standup Recap** - `/ai-assistant/standup-recap`
   - Generate standup summaries
   - Requires: prompt, context (team_id, date)

### Async Mode

All workflows support async mode:

```typescript
const response = await aiAssistantAPI.planning({
  prompt: "Create Q3 plan",
  context: { project_id: 1 },
  async_mode: true, // Returns job_id for polling
});

if (response.job_id) {
  // Poll job status
  const { data: status } = useAIJobStatus(response.job_id);
  // Wait for completion...
}
```

## Testing AI Wrapping

Run AI tests in the browser console:

```javascript
import { runAllAITests } from "@/lib/tests/ai-wrapping.test";

const results = await runAllAITests();
console.log(results);
```

Or create a test page and import:

```typescript
'use client';

import { runAllAITests, exportTestResults } from '@/lib/tests/ai-wrapping.test';
import { useState } from 'react';

export function AITestPage() {
  const [results, setResults] = useState(null);

  const runTests = async () => {
    const testResults = await runAllAITests();
    setResults(testResults);
  };

  return (
    <div>
      <button onClick={runTests}>Run AI Tests</button>
      {results && <pre>{exportTestResults(results)}</pre>}
    </div>
  );
}
```

## UI/UX Updates

Pages have been updated to use real API data:

- **Projects Page** - Fetches from `/projects` endpoint
- **Tasks Page** - Fetches from `/projects/{id}/tasks` endpoint
- **Team Page** - Fetches from `/teams` endpoint
- **Analytics Page** - Will fetch from worker KPI endpoints

## Error Handling

All hooks include error handling:

```typescript
const { data, error, loading, refetch } = useProjects();

if (error) {
  return <ErrorComponent error={error} onRetry={refetch} />;
}

if (loading) {
  return <LoadingComponent />;
}

return <ProjectsList projects={data} />;
```

## Authentication

### Auth Flow

The authentication flow is implemented in `lib/auth/api.ts` and integrated into the API layer via `lib/api/auth.ts`:

```typescript
import { login, logout, isAuthenticated } from "@/lib/auth/api";

// Login
const response = await login({
  email: "user@example.com",
  password: "password",
});
// Token is automatically stored to localStorage

// Check if authenticated
if (isAuthenticated()) {
  // User is logged in
}

// Logout
logout(); // Clears localStorage
```

### Auth Hooks

Use React hooks for authentication:

```typescript
import { useAuth, useLazyLogin } from "@/lib/api/auth";

// Get current user and auth state
const { user, loading, error, isAuthenticated, getCurrentUser, logout } =
  useAuth();

// Lazy login for forms
const { data, loading, error, launch } = useLazyLogin();
const response = await launch({ email, password });
```

### Token Storage

- Tokens are stored in `localStorage` with key `access_token`
- Automatically included in all API requests via `Authorization: Bearer <token>` header
- Token is cleared on logout

## Caching & Polling

- Use `refetch()` to manually update data
- Use `refetchInterval` in `useFetch()` for periodic updates
- AI job status uses 5-second polling by default

## Next Steps

1. Migrate remaining mock data pages to use APIs
2. Implement real-time updates with WebSocket
3. Add request cancellation for in-flight requests
4. Implement proper error boundaries
5. Add loading states and optimistic updates
