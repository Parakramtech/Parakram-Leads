const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface RequestOptions {
  method?: string;
  body?: unknown;
  token?: string;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, token } = options;
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const orgId = getOrgId();
  if (orgId) {
    headers['X-Organization-ID'] = orgId;
  }
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Request failed');
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export function getToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('parakram_token');
  }
  return null;
}

export function setToken(token: string) {
  localStorage.setItem('parakram_token', token);
}

export function clearToken() {
  localStorage.removeItem('parakram_token');
}

export function getOrgId(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('parakram_org_id');
  }
  return null;
}

export function setOrgId(orgId: string) {
  localStorage.setItem('parakram_org_id', orgId);
}

export function clearOrgId() {
  localStorage.removeItem('parakram_org_id');
}

export const api = {
  auth: {
    login: (data: { email: string; password: string }) =>
      request<{ access_token: string; token_type: string; user: any }>('/auth/login', { method: 'POST', body: data }),
    register: (data: { email: string; password: string; full_name?: string }) =>
      request<{ access_token: string; token_type: string; user: any }>('/auth/register', { method: 'POST', body: data }),
    google: (credential: string) =>
      request<{ access_token: string; token_type: string; user: any }>('/auth/google', { method: 'POST', body: { credential } }),
    me: () =>
      request<any>('/auth/me', { token: getToken() || undefined }),
  },
  leads: {
    list: (params?: Record<string, string | number>) => {
      const qs = params ? '?' + new URLSearchParams(
        Object.entries(params).map(([k, v]) => [k, String(v)])
      ).toString() : '';
      return request<any>(`/leads${qs}`, { token: getToken() || undefined });
    },
    get: (id: string) =>
      request<any>(`/leads/${id}`, { token: getToken() || undefined }),
    create: (data: any) =>
      request<any>('/leads', { method: 'POST', body: data, token: getToken() || undefined }),
    update: (id: string, data: any) =>
      request<any>(`/leads/${id}`, { method: 'PATCH', body: data, token: getToken() || undefined }),
    delete: (id: string) =>
      request<void>(`/leads/${id}`, { method: 'DELETE', token: getToken() || undefined }),
    approveOutreach: (id: string, data: any) =>
      request<any>(`/leads/${id}/approve-outreach`, { method: 'POST', body: data, token: getToken() || undefined }),
    bulk: (data: { lead_ids: string[]; action: string }) =>
      request<any>('/leads/bulk', { method: 'POST', body: data, token: getToken() || undefined }),
  },
  messages: {
    list: (leadId?: string) => {
      const qs = leadId ? `?lead_id=${leadId}` : '';
      return request<any[]>(`/messages${qs}`, { token: getToken() || undefined });
    },
    filter: (params?: Record<string, string>) => {
      const query = params ? '?' + new URLSearchParams(params).toString() : '';
      return request<any[]>(`/messages${query}`, { token: getToken() || undefined });
    },
  },
  organizations: {
    list: () =>
      request<any[]>('/organizations', { token: getToken() || undefined }),
    get: (orgId: string) =>
      request<any>(`/organizations/${orgId}`, { token: getToken() || undefined }),
    create: (data: { name: string; slug: string }) =>
      request<any>('/organizations', { method: 'POST', body: data, token: getToken() || undefined }),
    update: (orgId: string, data: any) =>
      request<any>(`/organizations/${orgId}`, { method: 'PATCH', body: data, token: getToken() || undefined }),
    getSettings: (orgId: string) =>
      request<any>(`/organizations/${orgId}`, { token: getToken() || undefined }),
    updateSettings: (orgId: string, data: any) =>
      request<any>(`/organizations/${orgId}`, { method: 'PATCH', body: data, token: getToken() || undefined }),
    switch: (orgId: string) =>
      request<any>(`/organizations/switch/${orgId}`, { method: 'POST', token: getToken() || undefined }),
    listMembers: (orgId: string) =>
      request<any[]>(`/organizations/${orgId}/members`, { token: getToken() || undefined }),
    inviteMember: (orgId: string, data: { email: string; role: string }) =>
      request<any>(`/organizations/${orgId}/members`, { method: 'POST', body: data, token: getToken() || undefined }),
    updateMemberRole: (orgId: string, userId: string, role: string) =>
      request<any>(`/organizations/${orgId}/members/${userId}/role?role=${role}`, { method: 'PATCH', token: getToken() || undefined }),
    removeMember: (orgId: string, userId: string) =>
      request<void>(`/organizations/${orgId}/members/${userId}`, { method: 'DELETE', token: getToken() || undefined }),
    listTeams: (orgId: string) =>
      request<any[]>(`/organizations/${orgId}/teams`, { token: getToken() || undefined }),
    createTeam: (orgId: string, data: { name: string; description?: string }) =>
      request<any>(`/organizations/${orgId}/teams`, { method: 'POST', body: data, token: getToken() || undefined }),
  },
  scraper: {
    importCsv: (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      const orgId = getOrgId();
      const headers: Record<string, string> = {};
      const token = getToken();
      if (token) headers['Authorization'] = `Bearer ${token}`;
      if (orgId) headers['X-Organization-ID'] = orgId;
      return fetch(`${API_BASE}/scraper/import-csv`, {
        method: 'POST',
        headers,
        body: formData,
      }).then(async (res) => {
        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: res.statusText }));
          throw new Error(err.detail || 'Import failed');
        }
        return res.json();
      });
    },
    exportCsv: () => {
      const token = getToken();
      const orgId = getOrgId();
      const headers: Record<string, string> = {};
      if (token) headers['Authorization'] = `Bearer ${token}`;
      if (orgId) headers['X-Organization-ID'] = orgId;
      return fetch(`${API_BASE}/scraper/export-csv`, { headers }).then(async (res) => {
        if (!res.ok) throw new Error('Export failed');
        return res.blob();
      });
    },
    run: (data: any) =>
      request<any>('/scraper/run', { method: 'POST', body: data, token: getToken() || undefined }),
    categories: () =>
      request<any[]>('/scraper/categories', { token: getToken() || undefined }),
    locations: () =>
      request<any[]>('/scraper/locations', { token: getToken() || undefined }),
  },
  dashboard: {
    get: () =>
      request<any>('/messages/dashboard', { token: getToken() || undefined }),
  },
  intelligence: {
    predict: (leadId: string) =>
      request<any>(`/intelligence/predict/${leadId}`, { token: getToken() || undefined }),
    sequence: (leadId: string) =>
      request<any>(`/intelligence/sequence/${leadId}`, { token: getToken() || undefined }),
    enrich: (leadId: string) =>
      request<any>(`/intelligence/enrich/${leadId}`, { token: getToken() || undefined }),
    full: (leadId: string) =>
      request<any>(`/intelligence/full/${leadId}`, { token: getToken() || undefined }),
    analyzeResponse: (data: { reply_text: string; lead_name?: string }) =>
      request<any>('/intelligence/analyze-response', { method: 'POST', body: data, token: getToken() || undefined }),
    prioritizeBatch: (leadIds: string[]) =>
      request<any>('/intelligence/prioritize-batch', { method: 'POST', body: { lead_ids: leadIds }, token: getToken() || undefined }),
    triggerAnalysis: (leadId: string) =>
      request<any>(`/intelligence/analyze/${leadId}`, { method: 'POST', token: getToken() || undefined }),
    alerts: (limit?: number) =>
      request<any>(`/intelligence/alerts${limit ? `?limit=${limit}` : ''}`, { token: getToken() || undefined }),
    sendLinkedin: (leadId: string) =>
      request<any>(`/intelligence/send-linkedin/${leadId}`, { method: 'POST', token: getToken() || undefined }),
  },
  audit: {
    list: (params?: Record<string, string | number>) => {
      const qs = params ? '?' + new URLSearchParams(
        Object.entries(params).map(([k, v]) => [k, String(v)])
      ).toString() : '';
      return request<any>(`/audit${qs}`, { token: getToken() || undefined });
    },
  },
};
