import type {
  AdminOverview,
  AdminSource,
  CategoryCount,
  IngestionRun,
  JobDetail,
  JobFilters,
  JobSummary,
  Paginated,
  Preferences,
  Stats,
  User,
} from "@/types";
import { buildQuery } from "./utils";

const BASE = "/api/v1";

function cookieValue(name: string): string | null {
  const match = document.cookie.split("; ").find((item) => item.startsWith(`${name}=`));
  return match ? decodeURIComponent(match.split("=")[1]) : null;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const method = (init.method || "GET").toUpperCase();
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    const csrf = cookieValue("csrf_token");
    if (csrf) headers.set("X-CSRF-Token", csrf);
  }
  const response = await fetch(`${BASE}${path}`, {
    ...init,
    headers,
    credentials: "include",
  });
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      detail = body.detail || body.error?.message || detail;
    } catch {
      // keep generic message
    }
    throw new Error(detail);
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export const api = {
  health: () => request<{ status: string }>("/health"),
  jobs: (filters: JobFilters) => request<Paginated<JobSummary>>(`/jobs?${buildQuery({ ...filters })}`),
  job: (id: string) => request<JobDetail>(`/jobs/${id}`),
  related: (id: string) => request<JobSummary[]>(`/jobs/${id}/related`),
  stats: () => request<Stats>("/stats"),
  categories: () => request<CategoryCount[]>("/categories"),
  locations: () => request<CategoryCount[]>("/locations"),

  login: (email: string, password: string) =>
    request<{ access_token: string; user: User }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  register: (email: string, password: string) =>
    request<User>("/auth/register", { method: "POST", body: JSON.stringify({ email, password }) }),
  logout: () => request<{ ok: boolean }>("/auth/logout", { method: "POST" }),
  me: () => request<User | null>("/auth/me"),

  savedJobs: () => request<Array<{ saved_at: string; job: JobSummary }>>("/users/me/saved-jobs"),
  saveJob: (id: string) => request<{ saved: boolean }>(`/users/me/saved-jobs/${id}`, { method: "POST" }),
  unsaveJob: (id: string) => request<{ saved: boolean }>(`/users/me/saved-jobs/${id}`, { method: "DELETE" }),
  preferences: () => request<Preferences>("/users/me/preferences"),
  updatePreferences: (payload: Preferences) =>
    request<Preferences>("/users/me/preferences", { method: "PUT", body: JSON.stringify(payload) }),

  adminOverview: () => request<AdminOverview>("/admin/overview"),
  adminSources: () => request<AdminSource[]>("/admin/sources"),
  adminRuns: () => request<IngestionRun[]>("/admin/ingestion-runs"),
  triggerIngestion: () => request<{ task_id: string }>("/admin/ingestion/run", { method: "POST" }),
  toggleSource: (id: string) => request<{ enabled: boolean }>(`/admin/sources/${id}/toggle`, { method: "POST" }),
};
