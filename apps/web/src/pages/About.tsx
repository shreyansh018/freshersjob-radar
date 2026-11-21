import { Link } from "react-router-dom";
import { Database, Filter, RefreshCw, ShieldCheck, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

export function About() {
  return (
    <div className="min-h-screen bg-white">
      <div className="mx-auto max-w-4xl px-4 py-14 sm:px-6">
        <h1 className="text-3xl font-extrabold text-navy-900">About FreshersJob Radar</h1>
        <p className="mt-4 text-lg leading-8 text-slate-600">
          FreshersJob Radar helps job seekers in India — from students and freshers to experienced
          professionals — find genuine openings without checking dozens of career pages every day.
        </p>

        <section className="mt-12">
          <h2 className="text-xl font-bold text-navy-900">How jobs are sourced</h2>
          <p className="mt-3 text-sm leading-7 text-slate-600">
            We read public, unauthenticated job-board endpoints provided by ATS platforms such as
            Greenhouse, Lever, Ashby, Workable and SmartRecruiters. Each source is stored in a
            registry and can be enabled or disabled independently. We respect robots.txt, rate
            limits and terms of service, and never bypass authentication or anti-bot controls.
          </p>
        </section>

        <div className="mt-10 grid gap-4 sm:grid-cols-2">
          {[
            { icon: RefreshCw, title: "Daily refresh", body: "A scheduler fetches every enabled source each day, with retries, exponential backoff and per-source error isolation." },
            { icon: Filter, title: "Honest filtering", body: "India eligibility and seniority are deterministic and auditable. Every genuine posting is kept and tagged by level." },
            { icon: Sparkles, title: "AI-assisted tags", body: "Gemini classifies role, level, skills and ambiguous cities with structured output, validation and content-hash caching." },
            { icon: Database, title: "Source transparency", body: "Every job keeps its original link, source platform, discovery date and last verification time." },
          ].map((item) => (
            <div key={item.title} className="rounded-2xl border border-slate-200 p-5">
              <item.icon size={19} className="text-brand-600" />
              <h3 className="mt-3 font-bold text-navy-900">{item.title}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-500">{item.body}</p>
            </div>
          ))}
        </div>

        <section className="mt-12">
          <h2 className="text-xl font-bold text-navy-900">Limitations</h2>
          <ul className="mt-3 list-disc space-y-2 pl-5 text-sm leading-7 text-slate-600">
            <li>Coverage depends on public endpoints; some companies do not publish machine-readable feeds.</li>
            <li>Posting dates are shown only when the source provides them. Discovery date is shown separately.</li>
            <li>AI confidence is a triage signal, not a calibrated probability, and tags can be wrong.</li>
            <li>Salary data is shown only when explicitly present in the source posting.</li>
            <li>Always verify role details on the employer's website before applying.</li>
          </ul>
        </section>

        <div className="mt-12 flex items-start gap-3 rounded-2xl bg-emerald-50 p-5 text-sm text-emerald-800">
          <ShieldCheck size={19} className="mt-0.5 shrink-0" />
          <p>
            We never fabricate listings, salaries, companies or application links. Applications
            always happen on the employer's own website.
          </p>
        </div>

        <Link to="/jobs" className="mt-8 inline-block"><Button>Explore jobs</Button></Link>
      </div>
    </div>
  );
}
