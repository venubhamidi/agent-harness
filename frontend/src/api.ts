// Typed client for the example API. Types mirror app/api.py.
export interface Item {
  id: number;
  item_key: string;
  title: string;
  owner: string | null;
  priority: "high" | "medium" | "low" | "unknown";
  status: string;
  updated_at: string;
  flags: string[];
}

export interface Page<T> { items: T[]; total: number; limit: number; offset: number }

export interface ItemSummary {
  total: number;
  without_owner: number;
  priority_unknown: number;
  data_as_of: string | null;
}

export interface Health {
  status: string;
  database: string;
  auth_provider: string;
  llm_provider: string;
  version: string;
  harness_version: string;
}

export interface AgentResponse {
  status: "succeeded" | "failed";
  output: { flags?: string[]; summary?: string; suggested_next_step?: string };
  explanation: string;
  confidence: string;
  error: string | null;
  tool_calls: number;
  llm_calls: number;
  guardrail_events: string[];
}

// Development only: a fixed token. With single sign-on the token comes from the login flow.
export function getToken(): string {
  let saved: string | null = null;
  try { saved = localStorage.getItem("app_token"); } catch { /* storage unavailable */ }
  return saved ?? import.meta.env.VITE_DEV_TOKEN ?? "dev-editor-token";
}

async function request<T>(path: string, method = "GET"): Promise<T> {
  const res = await fetch(path, { method, headers: { Authorization: `Bearer ${getToken()}` } });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(`${res.status}: ${body.detail ?? res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  items: (params: Record<string, string> = {}) => request<Page<Item>>(`/api/v1/items?${new URLSearchParams(params)}`),
  summary: () => request<ItemSummary>("/api/v1/items/summary"),
  review: (key: string) => request<AgentResponse>(`/api/v1/items/${encodeURIComponent(key)}/review`, "POST"),
  health: () => fetch("/api/v1/platform/health").then((r) => r.json() as Promise<Health>),
};
