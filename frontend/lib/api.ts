const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "";

export const getStreamUrl = (runId: string): string =>
  `${API_BASE}/runs/${runId}/stream${API_KEY ? `?api_key=${API_KEY}` : ""}`;

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
      ...options.headers,
    },
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  health: () => apiFetch("/health"),

  createRun: (topic?: string, userId?: string) =>
    apiFetch("/runs", {
      method: "POST",
      body: JSON.stringify({ topic, user_id: userId }),
    }),

  getRun: (runId: string) => apiFetch(`/runs/${runId}`),

  listRuns: () => apiFetch("/runs"),

  cancelRun: (runId: string) =>
    apiFetch(`/runs/${runId}/cancel`, { method: "POST" }),

  retryRun: (runId: string) =>
    apiFetch(`/runs/${runId}/retry`, { method: "POST" }),

  approveTopic: (runId: string, approved: boolean, approvedTopic?: string) =>
    apiFetch(`/runs/${runId}/approve-topic`, {
      method: "POST",
      body: JSON.stringify({ approved, approved_topic: approvedTopic }),
    }),

  approveReport: (runId: string, approved: boolean, revisionNotes?: string) =>
    apiFetch(`/runs/${runId}/approve-report`, {
      method: "POST",
      body: JSON.stringify({ approved, revision_notes: revisionNotes || "" }),
    }),

  approvePOC: (runId: string, approved: boolean) =>
    apiFetch(`/runs/${runId}/approve-poc`, {
      method: "POST",
      body: JSON.stringify({ approved }),
    }),

  approveImprovements: (runId: string, apply: boolean) =>
    apiFetch(`/runs/${runId}/approve-improvements`, {
      method: "POST",
      body: JSON.stringify({ apply }),
    }),

  approveGithubPush: (runId: string, approved: boolean) =>
    apiFetch(`/runs/${runId}/approve-github-push`, {
      method: "POST",
      body: JSON.stringify({ approved }),
    }),

  listReports: () => apiFetch("/reports"),

  getReport: (topicSlug: string) => apiFetch(`/reports/${topicSlug}`),

  getReportMarkdown: (topicSlug: string) => apiFetch(`/reports/${topicSlug}/markdown`),

  getReportFiles: (topicSlug: string) => apiFetch(`/reports/${topicSlug}/files`),

  testGithubConnection: () =>
    apiFetch("/github/test-connection", { method: "POST" }),

  publishToGithub: (runId: string) =>
    apiFetch(`/github/publish/${runId}`, { method: "POST" }),

  getGithubSettings: () => apiFetch("/settings/github"),

  saveGithubSettings: (data: {
    github_token?: string;
    github_repo_owner?: string;
    github_repo_name?: string;
    github_default_branch?: string;
  }) => apiFetch("/settings/github", { method: "POST", body: JSON.stringify(data) }),

  getSupabaseSettings: () => apiFetch("/settings/supabase"),

  saveSupabaseSettings: (data: {
    supabase_url?: string;
    supabase_anon_key?: string;
    supabase_service_role_key?: string;
  }) => apiFetch("/settings/supabase", { method: "POST", body: JSON.stringify(data) }),

  testSupabaseConnection: () =>
    apiFetch("/settings/supabase/test", { method: "POST" }),
};
