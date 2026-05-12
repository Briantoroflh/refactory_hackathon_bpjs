const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const apiClient = {
  async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    // Merge existing headers
    if (options?.headers) {
      const existingHeaders = options.headers;
      if (existingHeaders instanceof Headers) {
        existingHeaders.forEach((value, key) => {
          headers[key] = value;
        });
      } else if (Array.isArray(existingHeaders)) {
        existingHeaders.forEach(([key, value]) => {
          headers[key] = value;
        });
      } else {
        Object.assign(headers, existingHeaders);
      }
    }

    // Add auth token if available
    const token =
      typeof window !== "undefined"
        ? localStorage.getItem("access_token")
        : null;
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    // Always include cookies (httpOnly tokens) when communicating with backend
    const response = await fetch(url, {
      ...options,
      headers,
      credentials: "include",
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `API error: ${response.status}`);
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return undefined as T;
    }

    return response.json();
  },

  get<T>(endpoint: string, options?: RequestInit) {
    return this.request<T>(endpoint, { ...options, method: "GET" });
  },

  post<T>(endpoint: string, data?: unknown, options?: RequestInit) {
    return this.request<T>(endpoint, {
      ...options,
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  put<T>(endpoint: string, data?: unknown, options?: RequestInit) {
    return this.request<T>(endpoint, {
      ...options,
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  patch<T>(endpoint: string, data?: unknown, options?: RequestInit) {
    return this.request<T>(endpoint, {
      ...options,
      method: "PATCH",
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  delete<T>(endpoint: string, options?: RequestInit) {
    return this.request<T>(endpoint, { ...options, method: "DELETE" });
  },
};

// Projects API
export const projectsAPI = {
  list: () => apiClient.get("/projects"),
  get: (id: number) => apiClient.get(`/projects/${id}`),
  create: (data: any) => apiClient.post("/projects", data),
  update: (id: number, data: any) => apiClient.put(`/projects/${id}`, data),
  updateStatus: (id: number, status: string) =>
    apiClient.patch(`/projects/${id}/status`, { status }),
};

// Tasks API
export const tasksAPI = {
  list: (projectId: number, skip = 0, limit = 20) =>
    apiClient.get(`/projects/${projectId}/tasks?skip=${skip}&limit=${limit}`),
  get: (taskId: number) => apiClient.get(`/tasks/${taskId}`),
  create: (projectId: number, data: any) =>
    apiClient.post(`/projects/${projectId}/tasks`, data),
  update: (taskId: number, data: any) =>
    apiClient.put(`/tasks/${taskId}`, data),
  updateStatus: (taskId: number, status: string, version: number) =>
    apiClient.patch(`/tasks/${taskId}/status`, { status, version }),
  addComment: (taskId: number, content: string) =>
    apiClient.post(`/tasks/${taskId}/comments`, { content }),
  getComments: (taskId: number) => apiClient.get(`/tasks/${taskId}/comments`),
  logWorkload: (taskId: number, data: any) =>
    apiClient.post(`/tasks/${taskId}/worklog`, data),
  getHistory: (taskId: number) => apiClient.get(`/tasks/${taskId}/history`),
};

// Teams API
export const teamsAPI = {
  list: (skip = 0, limit = 20) =>
    apiClient.get(`/teams?skip=${skip}&limit=${limit}`),
  get: (id: number) => apiClient.get(`/teams/${id}`),
  create: (data: any) => apiClient.post("/teams", data),
  update: (id: number, data: any) => apiClient.put(`/teams/${id}`, data),
  getMembers: (id: number) => apiClient.get(`/teams/${id}/members`),
  addMember: (id: number, workerId: number, role = "member") =>
    apiClient.post(`/teams/${id}/members`, { worker_id: workerId, role }),
  removeMember: (id: number, memberId: number) =>
    apiClient.delete(`/teams/${id}/members/${memberId}`),
};

// AI Assistant API
export const aiAssistantAPI = {
  planning: (data: any) => apiClient.post("/ai-assistant/planning", data),
  sprintSummary: (data: any) =>
    apiClient.post("/ai-assistant/sprint-summary", data),
  standupRecap: (data: any) =>
    apiClient.post("/ai-assistant/standup-recap", data),
  taskRecommendation: (data: any) =>
    apiClient.post("/ai-assistant/task-recommendation", data),
  jobStatus: (jobId: string) => apiClient.get(`/ai-assistant/job/${jobId}`),
};

// Workers API
export const workersAPI = {
  list: (skip = 0, limit = 20) =>
    apiClient.get(`/workers?skip=${skip}&limit=${limit}`),
  get: (id: number) => apiClient.get(`/workers/${id}`),
  getKPI: (id: number) => apiClient.get(`/workers/${id}/kpi`),
};

// Auth API
export const authAPI = {
  register: (data: any) => apiClient.post("/auth/register", data),
  login: (data: any) => apiClient.post("/auth/login", data),
  refresh: (refreshToken: string) =>
    apiClient.post("/auth/refresh", { refresh_token: refreshToken }),
  me: () => apiClient.get("/auth/me"),
};
