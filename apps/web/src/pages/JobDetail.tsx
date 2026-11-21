import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, ArrowUpRight, Building2, CalendarDays, Clock3, MapPin, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { JobCard } from "@/components/jobs/JobCard";
import { useJob } from "@/hooks/useJobs";
import { api } from "@/lib/api";
import { formatDate, relativeTime, safeExternalUrl } from "@/lib/utils";

export function JobDetail() {
  const { id } = useParams<{ id: string }>();
  const jobQuery = useJob(id);
  const related = useQuery({
    queryKey: ["related", id],
    queryFn: () => api.related(id!),
    enabled: Boolean(id),
  });

  if (jobQuery.isLoading) return <div className="mx-auto max-w-5xl px-4 py-10"><Skeleton className="h-96 w-full" /></div>;
  if (jobQuery.isError || !jobQuery.data) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-16 text-center">
        <p className="text-lg font-semibold text-navy-900">This job could not be loaded.</p>
        <Link to="/jobs" className="mt-4 inline-block text-sm font-semibold text-brand-600">Back to search</Link>
      </div>
    );
  }

  const job = jobQuery.data;
  const applyUrl = safeExternalUrl(job.application_url);

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-5xl px-4 py-6 sm:px-6">
          <Link to="/jobs" className="inline-flex items-center gap-1.5 text-sm font-semibold text-slate-500 hover:text-brand-600">
            <ArrowLeft size={15} /> Back to results
          </Link>
          <div className="mt-5 flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
            <div>
              <h1 className="text-2xl font-bold text-navy-900 sm:text-3xl">{job.title}</h1>
              <div className="mt-2 flex flex-wrap gap-x-5 gap-y-1 text-sm text-slate-500">
                <span className="inline-flex items-center gap-1.5"><Building2 size={15} /> {job.company?.name ?? "Company not listed"}</span>
                <span className="inline-flex items-center gap-1.5"><MapPin size={15} /> {job.normalized_location || "Location not listed"}</span>
                <span className="inline-flex items-center gap-1.5"><CalendarDays size={15} /> {job.posted_at ? `Posted ${formatDate(job.posted_at)}` : `Discovered ${formatDate(job.first_seen_at)}`}</span>
              </div>
              <div className="mt-4 flex flex-wrap gap-1.5">
                {job.is_new && <Badge tone="green" title="First discovered recently">New</Badge>}
                {job.fresher_friendly && <Badge tone="brand">Fresher-friendly</Badge>}
                {job.experience_level && <Badge tone="slate">{job.experience_level}</Badge>}
                {job.employment_type && <Badge tone="slate">{job.employment_type}</Badge>}
                <Badge tone="slate">{job.workplace_type}</Badge>
                {job.role_category && <Badge tone="purple">{job.role_category}</Badge>}
              </div>
            </div>
            {applyUrl && (
              <a href={applyUrl} target="_blank" rel="noopener noreferrer" className="shrink-0">
                <Button size="lg">Apply on company website <ArrowUpRight size={17} /></Button>
              </a>
            )}
          </div>
        </div>
      </div>

      <div className="mx-auto grid max-w-5xl gap-6 px-4 py-8 sm:px-6 lg:grid-cols-[1fr_300px]">
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-bold text-navy-900">About this role</h2>
            <div className="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-600">
              {job.description || "The employer did not provide a description in the public posting."}
            </div>
            {job.skills.length > 0 && (
              <>
                <h3 className="mt-8 text-sm font-bold text-navy-900">Skills mentioned</h3>
                <div className="mt-3 flex flex-wrap gap-2">
                  {job.skills.map((skill) => <Badge key={skill} tone="brand">{skill}</Badge>)}
                </div>
              </>
            )}
            {job.degree_requirements.length > 0 && (
              <>
                <h3 className="mt-8 text-sm font-bold text-navy-900">Education</h3>
                <p className="mt-2 text-sm text-slate-600">{job.degree_requirements.join(", ")}</p>
              </>
            )}
            <p className="mt-8 text-xs text-slate-400">
              Job descriptions are untrusted external content and are rendered as plain text.
            </p>
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardContent className="space-y-3 p-5 text-sm">
              <h2 className="font-bold text-navy-900">Job details</h2>
              <DetailRow label="Experience" value={job.experience_min !== null ? `${job.experience_min}${job.experience_max !== null ? `–${job.experience_max}` : "+"} years` : "Not specified"} />
              <DetailRow label="Employment" value={job.employment_type || "Not specified"} />
              <DetailRow label="Workplace" value={job.workplace_type || "Not specified"} />
              <DetailRow label="Department" value={job.department || "Not specified"} />
              <DetailRow label="Salary" value={job.salary_min !== null ? `${job.salary_currency ?? ""}${job.salary_min}–${job.salary_max ?? ""}` : "Not disclosed"} />
              <DetailRow label="First discovered" value={formatDate(job.first_seen_at)} />
              <DetailRow label="Last checked" value={formatDate(job.last_checked_at)} />
              <div className="flex items-start gap-2 border-t border-slate-100 pt-3 text-xs text-emerald-600">
                <ShieldCheck size={14} className="mt-0.5 shrink-0" />
                <span>{relativeTime(job.last_source_confirmed_at)}</span>
              </div>
              <div className="border-t border-slate-100 pt-3 text-xs text-slate-400">
                Source: {job.source?.platform ?? "public job board"}
                {job.classification_source === "gemini" && " · AI-assisted tags"}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-5 text-sm">
              <h2 className="font-bold text-navy-900">About classification</h2>
              <p className="mt-2 text-xs leading-5 text-slate-500">
                {job.classification_reasoning || "Tags were assigned from deterministic signals in the posting."}
              </p>
              <p className="mt-2 flex items-center gap-1.5 text-xs text-slate-400"><Clock3 size={13} /> Confidence is a triage signal, not a probability.</p>
            </CardContent>
          </Card>
        </div>
      </div>

      {related.data && related.data.length > 0 && (
        <div className="mx-auto max-w-5xl px-4 pb-14 sm:px-6">
          <h2 className="mb-4 text-xl font-bold text-navy-900">Related opportunities</h2>
          <div className="grid gap-4 md:grid-cols-2">
            {related.data.slice(0, 4).map((item) => <JobCard key={item.id} job={item} />)}
          </div>
        </div>
      )}
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4">
      <span className="text-slate-500">{label}</span>
      <span className="text-right font-medium text-slate-800">{value}</span>
    </div>
  );
}
