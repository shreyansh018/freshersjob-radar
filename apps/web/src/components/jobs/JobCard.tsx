import { Link } from "react-router-dom";
import { ArrowUpRight, Bookmark, Building2, MapPin, ShieldCheck } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import type { JobSummary } from "@/types";
import { cn, formatDate, safeExternalUrl } from "@/lib/utils";

interface JobCardProps {
  job: JobSummary;
  saved?: boolean;
  onSave?: (job: JobSummary) => void;
  saving?: boolean;
}

export function JobCard({ job, saved = false, onSave, saving = false }: JobCardProps) {
  const applyUrl = safeExternalUrl(job.application_url);
  return (
    <Card className="group transition-all duration-200 hover:-translate-y-0.5 hover:border-brand-200 hover:shadow-lg">
      <CardContent className="flex h-full flex-col gap-4 p-5">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <Link to={`/jobs/${job.id}`} className="text-lg font-bold leading-snug text-navy-900 hover:text-brand-600">
              {job.title}
            </Link>
            <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-slate-500">
              <span className="inline-flex items-center gap-1.5">
                <Building2 size={14} /> {job.company?.name ?? "Company not listed"}
              </span>
              <span className="inline-flex items-center gap-1.5">
                <MapPin size={14} /> {job.normalized_location || job.city || "Location not listed"}
              </span>
            </div>
          </div>
          {onSave && (
            <button
              type="button"
              aria-label={saved ? "Remove from saved jobs" : "Save job"}
              onClick={() => onSave(job)}
              disabled={saving}
              className={cn(
                "flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border transition",
                saved
                  ? "border-brand-200 bg-brand-50 text-brand-600"
                  : "border-slate-200 text-slate-400 hover:border-brand-300 hover:text-brand-600",
              )}
            >
              <Bookmark size={17} fill={saved ? "currentColor" : "none"} />
            </button>
          )}
        </div>

        <div className="flex flex-wrap gap-1.5">
          {job.is_new && <Badge tone="green" title="First discovered recently">New</Badge>}
          {job.fresher_friendly && <Badge tone="brand">Fresher-friendly</Badge>}
          {job.employment_type === "Internship" && <Badge tone="purple">Internship</Badge>}
          {job.experience_level && <Badge tone="slate">{job.experience_level}</Badge>}
          {job.workplace_type === "Remote" && <Badge tone="amber">Remote</Badge>}
          {job.workplace_type === "Hybrid" && <Badge tone="amber">Hybrid</Badge>}
          {job.recently_verified && (
            <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-600">
              <ShieldCheck size={13} /> Recently verified
            </span>
          )}
        </div>

        {job.skills.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {job.skills.slice(0, 5).map((skill) => (
              <span key={skill} className="rounded-md bg-slate-50 px-2 py-1 text-[11px] font-medium text-slate-600">
                {skill}
              </span>
            ))}
          </div>
        )}

        <div className="mt-auto flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-4">
          <div className="text-xs text-slate-400">
            {job.posted_at ? `Posted ${formatDate(job.posted_at)}` : `Discovered ${formatDate(job.first_seen_at)}`}
            {" · "}
            {job.source?.platform ?? "Public source"}
          </div>
          <div className="flex items-center gap-2">
            <Link
              to={`/jobs/${job.id}`}
              className="rounded-lg px-2.5 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-50"
            >
              View details
            </Link>
            {applyUrl && (
              <a
                href={applyUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 rounded-lg bg-brand-50 px-3 py-1.5 text-xs font-semibold text-brand-700 hover:bg-brand-100"
              >
                Apply <ArrowUpRight size={13} />
              </a>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
