import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, BadgeCheck, Filter, RefreshCw, Search, ShieldCheck, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { JobCard } from "@/components/jobs/JobCard";
import { useStats } from "@/hooks/useJobs";
import { api } from "@/lib/api";
import { buildQuery } from "@/lib/utils";

export function Landing() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [city, setCity] = useState("");
  const stats = useStats();
  const latest = useQuery({
    queryKey: ["landing", "latest"],
    queryFn: () => api.jobs({ sort: "newest", limit: 6 }),
  });

  function submit(event: FormEvent) {
    event.preventDefault();
    navigate(`/jobs?${buildQuery({ q: query, city })}`);
  }

  const numbers = [
    { label: "Active opportunities", value: stats.data?.total_active_jobs },
    { label: "Fresher-friendly", value: stats.data?.fresher_friendly_jobs },
    { label: "Internships", value: stats.data?.internships },
    { label: "Companies", value: stats.data?.companies },
  ];

  return (
    <div>
      <section className="relative overflow-hidden bg-navy-950 text-white">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_10%,rgba(99,102,241,0.25),transparent_45%),radial-gradient(circle_at_85%_20%,rgba(124,58,237,0.22),transparent_40%)]" />
        <div className="relative mx-auto max-w-7xl px-4 pb-20 pt-20 sm:px-6 lg:px-8 lg:pb-28 lg:pt-28">
          <div className="mx-auto max-w-3xl text-center">
            <span className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-3 py-1.5 text-xs font-semibold text-indigo-200">
              <Sparkles size={14} /> Real jobs across India — fresher to experienced
            </span>
            <h1 className="mt-6 text-4xl font-extrabold leading-[1.1] tracking-tight sm:text-6xl">
              Your first job. <span className="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">Your next big move.</span>
            </h1>
            <p className="mx-auto mt-5 max-w-2xl text-base leading-7 text-slate-300 sm:text-lg">
              Real jobs from public company career pages — internships, fresher roles and
              experienced positions, deduplicated and refreshed daily. Apply directly on the
              employer's website.
            </p>

            <form onSubmit={submit} className="mx-auto mt-9 flex max-w-2xl flex-col gap-2 rounded-2xl border border-white/10 bg-white/10 p-2 backdrop-blur sm:flex-row">
              <div className="flex flex-1 items-center gap-2 rounded-xl bg-white px-4">
                <Search size={18} className="text-slate-400" />
                <Input
                  aria-label="Job title, skill or company"
                  className="h-12 border-0 bg-transparent px-0 shadow-none focus:ring-0"
                  placeholder="Job title, skill or company"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
              </div>
              <div className="flex flex-1 items-center gap-2 rounded-xl bg-white px-4">
                <MapPinIcon />
                <Input
                  aria-label="City"
                  className="h-12 border-0 bg-transparent px-0 shadow-none focus:ring-0"
                  placeholder="City (e.g. Bengaluru)"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                />
              </div>
              <Button size="lg" type="submit" className="shrink-0">
                Search jobs <ArrowRight size={17} />
              </Button>
            </form>
            <p className="mt-3 text-xs text-slate-400">
              No sign-up required to search. Every listing links to the original employer.
            </p>
          </div>

          <div className="mx-auto mt-14 grid max-w-4xl grid-cols-2 gap-3 sm:grid-cols-4">
            {numbers.map((item) => (
              <div key={item.label} className="rounded-xl border border-white/10 bg-white/5 px-4 py-4 text-center">
                <div className="text-2xl font-bold">{stats.isLoading ? "—" : (item.value ?? 0).toLocaleString("en-IN")}</div>
                <div className="mt-1 text-xs text-slate-300">{item.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="flex items-end justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-navy-900 sm:text-3xl">Latest opportunities</h2>
            <p className="mt-1 text-sm text-slate-500">Freshly discovered from public company boards.</p>
          </div>
          <Button variant="outline" onClick={() => navigate("/jobs")}>View all</Button>
        </div>
        {latest.isLoading && <p className="mt-8 text-sm text-slate-500">Loading jobs…</p>}
        {latest.isError && <p className="mt-8 text-sm text-rose-600">Could not load jobs. Please try again.</p>}
        {latest.data && latest.data.items.length === 0 && (
          <p className="mt-8 text-sm text-slate-500">
            No postings have been ingested yet. Run the first ingestion (see README) to populate this page.
          </p>
        )}
        <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {latest.data?.items.map((job) => <JobCard key={job.id} job={job} />)}
        </div>
      </section>

      <section className="bg-slate-50 py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-bold text-navy-900 sm:text-3xl">How it works</h2>
          <div className="mt-8 grid gap-5 md:grid-cols-4">
            {[
              { icon: RefreshCw, title: "Collect daily", body: "Public ATS boards are fetched on a schedule with retries and rate limits." },
              { icon: Filter, title: "Clean & dedupe", body: "India eligibility, relevance screening and canonical URLs remove noise." },
              { icon: Sparkles, title: "AI-assisted tags", body: "Gemini classifies role, level, skills and ambiguous cities with caching." },
              { icon: ShieldCheck, title: "Apply directly", body: "Original employer links are preserved. No fake application flows." },
            ].map((step) => (
              <div key={step.title} className="rounded-2xl border border-slate-200 bg-white p-5">
                <step.icon size={20} className="text-brand-600" />
                <h3 className="mt-4 font-bold text-navy-900">{step.title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-500">{step.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="flex flex-col items-start justify-between gap-6 rounded-2xl bg-gradient-to-br from-brand-700 to-accent-600 px-8 py-10 text-white md:flex-row md:items-center">
          <div>
            <h2 className="text-2xl font-bold">Stop refreshing twenty career pages.</h2>
            <p className="mt-2 max-w-xl text-sm text-indigo-100">
              One searchable feed for genuine jobs across India — filter by role, city and
              experience level.
            </p>
          </div>
          <Button variant="secondary" onClick={() => navigate("/jobs")} className="bg-white text-brand-700 hover:bg-indigo-50">
            Explore jobs <BadgeCheck size={16} />
          </Button>
        </div>
      </section>
    </div>
  );
}

function MapPinIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0Z" />
      <circle cx="12" cy="10" r="3" />
    </svg>
  );
}
