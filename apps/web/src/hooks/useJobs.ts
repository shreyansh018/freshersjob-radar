import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { JobFilters } from "@/types";

export function useJobs(filters: JobFilters) {
  return useQuery({
    queryKey: ["jobs", filters],
    queryFn: () => api.jobs(filters),
    placeholderData: keepPreviousData,
    staleTime: 60_000,
  });
}

export function useJob(id: string | undefined) {
  return useQuery({
    queryKey: ["job", id],
    queryFn: () => api.job(id!),
    enabled: Boolean(id),
  });
}

export function useStats() {
  return useQuery({ queryKey: ["stats"], queryFn: api.stats, staleTime: 5 * 60_000 });
}
