import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Activity, Play, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";

export function Admin() {
  const queryClient = useQueryClient();
  const overview = useQuery({ queryKey: ["admin", "overview"], queryFn: api.adminOverview, retry: false });
  const sources = useQuery({ queryKey: ["admin", "sources"], queryFn: api.adminSources, retry: false });
  const runs = useQuery({ queryKey: ["admin", "runs"], queryFn: api.adminRuns, retry: false });

  const trigger = useMutation({
    mutationFn: api.triggerIngestion,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin"] }),
  });
  const toggle = useMutation({
    mutationFn: api.toggleSource,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin"] }),
  });

  if (overview.isError) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-20 text-center">
        <h1 className="text-2xl font-bold text-navy-900">Admin access required</h1>
        <p className="mt-2 text-sm text-slate-500">Sign in with an admin account to view monitoring data.</p>
      </div>
    );
  }

  const metrics = [
    ["Active jobs", overview.data?.active_jobs],
    ["Stale jobs", overview.data?.stale_jobs],
    ["Sources enabled", overview.data?.sources_enabled],
    ["Failing sources", overview.data?.sources_failing],
    ["AI calls", overview.data?.ai_calls],
    ["Cache hits", overview.data?.ai_cache_hits],
    ["Est. AI spend", overview.data ? `$${overview.data.estimated_ai_cost_usd.toFixed(4)}` : null],
    ["Last ingestion", overview.data?.last_ingestion_at ? formatDate(overview.data.last_ingestion_at) : null],
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="flex items-center gap-2 text-2xl font-bold text-navy-900"><Activity size={22} className="text-brand-600" /> System monitoring</h1>
            <p className="mt-1 text-sm text-slate-500">Source health, ingestion runs and AI usage from the live database.</p>
          </div>
          <Button onClick={() => trigger.mutate()} disabled={trigger.isPending}>
            <Play size={15} /> {trigger.isPending ? "Queued…" : "Run ingestion"}
          </Button>
        </div>

        <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {metrics.map(([label, value]) => (
            <Card key={String(label)}><CardContent className="p-4">
              <div className="text-xs font-medium text-slate-500">{label}</div>
              <div className="mt-1 text-xl font-bold text-navy-900">{value ?? "—"}</div>
            </CardContent></Card>
          ))}
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          <Card>
            <CardContent className="p-5">
              <h2 className="font-bold text-navy-900">Sources</h2>
              <div className="mt-4 max-h-96 space-y-2 overflow-auto">
                {sources.data?.map((source) => (
                  <div key={source.id} className="flex items-center justify-between gap-3 rounded-lg border border-slate-100 p-3 text-sm">
                    <div className="min-w-0">
                      <div className="font-semibold text-slate-800">{source.name}</div>
                      <div className="text-xs text-slate-400">{source.platform} · {source.job_count} jobs · {source.health_status}</div>
                      {source.last_error && <div className="mt-1 truncate text-xs text-rose-600">{source.last_error}</div>}
                    </div>
                    <button
                      onClick={() => toggle.mutate(source.id)}
                      className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-2 py-1 text-xs font-semibold text-slate-600"
                    >
                      <RefreshCw size={12} /> {source.enabled ? "Disable" : "Enable"}
                    </button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-5">
              <h2 className="font-bold text-navy-900">Recent ingestion runs</h2>
              <div className="mt-4 max-h-96 space-y-2 overflow-auto">
                {runs.data?.map((run) => (
                  <div key={run.id} className="rounded-lg border border-slate-100 p-3 text-xs text-slate-600">
                    <div className="flex justify-between font-semibold text-slate-800">
                      <span>{formatDate(run.started_at)}</span><span>{run.status}</span>
                    </div>
                    <div className="mt-1">raw={run.raw_jobs} · candidates={run.candidate_jobs} · new={run.new_jobs} · updated={run.updated_jobs} · duplicates={run.duplicates} · failed={run.failed_sources}</div>
                  </div>
                ))}
                {runs.data && runs.data.length === 0 && <p className="text-sm text-slate-500">No ingestion runs yet.</p>}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
