import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { Search } from "lucide-react";
import { JobCard } from "@/components/jobs/JobCard";
import { JobFiltersPanel } from "@/components/jobs/JobFilters";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { useDebounce } from "@/hooks/useDebounce";
import { useJobs } from "@/hooks/useJobs";
import { api } from "@/lib/api";
import type { JobFilters } from "@/types";

export function Jobs() {
  const [params, setParams] = useSearchParams();
  const [search, setSearch] = useState(params.get("q") ?? "");
  const debouncedSearch = useDebounce(search, 300);

  const filters: JobFilters = useMemo(() => {
    const values: JobFilters = {
      q: debouncedSearch || undefined,
      city: params.get("city") || undefined,
      role_category: params.get("role_category") || undefined,
      experience_level: params.get("experience_level") || undefined,
      employment_type: params.get("employment_type") || undefined,
      workplace_type: params.get("workplace_type") || undefined,
      company: params.get("company") || undefined,
      sort: (params.get("sort") as JobFilters["sort"]) || "relevance",
      page: Number(params.get("page") || 1),
      limit: 20,
    };
    return values;
  }, [debouncedSearch, params]);

  const jobsQuery = useJobs(filters);
  const categories = useQuery({ queryKey: ["categories"], queryFn: api.categories });
  const locations = useQuery({ queryKey: ["locations"], queryFn: api.locations });

  useEffect(() => {
    setParams((previous) => {
      const next = new URLSearchParams(previous);
      if (debouncedSearch) next.set("q", debouncedSearch);
      else next.delete("q");
      return next;
    });
  }, [debouncedSearch, setParams]);

  function onChange(patch: Partial<JobFilters>) {
    setParams((previous) => {
      const next = new URLSearchParams(previous);
      Object.entries(patch).forEach(([key, value]) => {
        if (value) next.set(key, String(value));
        else next.delete(key);
      });
      next.delete("page");
      return next;
    });
  }

  function goToPage(page: number) {
    setParams((previous) => {
      const next = new URLSearchParams(previous);
      next.set("page", String(page));
      return next;
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function handleSave(id: string) {
    try {
      await api.saveJob(id);
    } catch {
      window.location.href = "/login";
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <h1 className="text-2xl font-bold text-navy-900 sm:text-3xl">Discover opportunities</h1>
          <p className="mt-1 text-sm text-slate-500">Real postings from public company career pages across India — filter by role, city, company and experience.</p>
          <div className="mt-5 flex flex-col gap-3 sm:flex-row">
            <div className="flex flex-1 items-center gap-2 rounded-xl border border-slate-200 bg-white px-3">
              <Search size={18} className="text-slate-400" />
              <Input
                aria-label="Search jobs"
                className="border-0 px-0 shadow-none focus:ring-0"
                placeholder="Try 'frontend', 'Python' or a company name"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
            </div>
            <Select
              aria-label="Sort results"
              className="h-11 sm:w-48"
              value={filters.sort}
              onChange={(event) => onChange({ sort: event.target.value as JobFilters["sort"] })}
            >
              <option value="relevance">Most relevant</option>
              <option value="newest">Newest first</option>
              <option value="oldest">Oldest first</option>
            </Select>
          </div>
        </div>
      </div>

      <div className="mx-auto grid max-w-7xl gap-6 px-4 py-8 sm:px-6 lg:grid-cols-[280px_1fr] lg:px-8">
        <JobFiltersPanel
          filters={filters}
          onChange={onChange}
          onReset={() => setParams(new URLSearchParams())}
          categories={categories.data ?? []}
          locations={locations.data ?? []}
        />

        <div>
          <div className="mb-4 flex items-center justify-between">
            <p className="text-sm text-slate-600">
              {jobsQuery.isLoading ? "Searching…" : `${jobsQuery.data?.total ?? 0} jobs found`}
            </p>
          </div>

          {jobsQuery.isLoading && (
            <div className="space-y-4">
              {[1, 2, 3].map((item) => <Skeleton key={item} className="h-44 w-full" />)}
            </div>
          )}
          {jobsQuery.isError && (
            <div className="rounded-xl border border-rose-200 bg-rose-50 p-5 text-sm text-rose-700">
              Search is unavailable right now. Check that the API container is running.
            </div>
          )}
          {jobsQuery.data && jobsQuery.data.items.length === 0 && (
            <div className="rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center">
              <p className="font-semibold text-navy-900">No jobs match these filters.</p>
              <p className="mt-2 text-sm text-slate-500">Try removing a filter, or run an ingestion cycle to collect fresh postings.</p>
            </div>
          )}

          <div className="space-y-4">
            {jobsQuery.data?.items.map((job) => (
              <JobCard key={job.id} job={job} onSave={(item) => handleSave(item.id)} />
            ))}
          </div>

          {jobsQuery.data && jobsQuery.data.total > filters.limit! && (
            <div className="mt-8 flex items-center justify-center gap-3">
              <Button
                variant="outline"
                disabled={filters.page === 1}
                onClick={() => goToPage(filters.page! - 1)}
              >
                Previous
              </Button>
              <span className="text-sm text-slate-600">Page {filters.page}</span>
              <Button
                variant="outline"
                disabled={!jobsQuery.data.has_more}
                onClick={() => goToPage(filters.page! + 1)}
              >
                Next
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
