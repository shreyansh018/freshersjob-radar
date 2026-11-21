export interface CompanyMini {
  id: string;
  name: string;
  logo_url?: string | null;
  website?: string | null;
}

export interface SourceMini {
  id: string;
  name: string;
  platform: string;
}

export interface JobSummary {
  id: string;
  title: string;
  company: CompanyMini | null;
  source: SourceMini | null;
  normalized_location: string | null;
  city: string | null;
  country: string | null;
  workplace_type: string;
  employment_type: string;
  experience_level: string | null;
  role_category: string | null;
  fresher_friendly: boolean;
  status: string;
  posted_at: string | null;
  first_seen_at: string;
  last_checked_at: string | null;
  skills: string[];
  application_url: string;
  is_new: boolean;
  recently_verified: boolean;
}

export interface JobDetail extends JobSummary {
  description: string | null;
  original_location: string | null;
  state: string | null;
  department: string | null;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string | null;
  experience_min: number | null;
  experience_max: number | null;
  classification_confidence: number | null;
  classification_reasoning: string | null;
  classification_source: string | null;
  degree_requirements: string[];
  last_seen_at: string | null;
  last_source_confirmed_at: string | null;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
}

export interface CategoryCount {
  name: string;
  count: number;
}

export interface Stats {
  total_active_jobs: number;
  fresher_friendly_jobs: number;
  internships: number;
  new_jobs_today: number;
  companies: number;
  cities: number;
  role_categories: CategoryCount[];
  top_cities: CategoryCount[];
}

export interface JobFilters {
  q?: string;
  city?: string;
  role_category?: string;
  experience_level?: string;
  employment_type?: string;
  workplace_type?: string;
  company?: string;
  posted_after?: string;
  sort?: "relevance" | "newest" | "oldest";
  page?: number;
  limit?: number;
}

export interface User {
  id: string;
  email: string;
  role: string;
  created_at: string;
}

export interface Preferences {
  roles: string[];
  locations: string[];
  skills: string[];
  experience: string | null;
  remote_preference: string | null;
}

export interface AdminSource {
  id: string;
  name: string;
  platform: string;
  board_identifier: string;
  enabled: boolean;
  health_status: string;
  job_count: number;
  last_fetch_at: string | null;
  last_success_at: string | null;
  last_error: string | null;
}

export interface AdminOverview {
  total_jobs: number;
  active_jobs: number;
  stale_jobs: number;
  expired_jobs: number;
  sources_enabled: number;
  sources_failing: number;
  last_ingestion_at: string | null;
  ai_calls: number;
  ai_cache_hits: number;
  ai_prompt_tokens: number;
  ai_completion_tokens: number;
  estimated_ai_cost_usd: number;
}

export interface IngestionRun {
  id: string;
  started_at: string;
  finished_at: string | null;
  duration_ms: number | null;
  status: string;
  raw_jobs: number;
  candidate_jobs: number;
  new_jobs: number;
  updated_jobs: number;
  duplicates: number;
  failed_sources: number;
  error: string | null;
}
