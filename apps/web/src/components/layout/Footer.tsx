import { Link } from "react-router-dom";
import { Radar } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="mx-auto grid max-w-7xl gap-8 px-4 py-12 sm:px-6 md:grid-cols-4 lg:px-8">
        <div className="md:col-span-2">
          <div className="flex items-center gap-2 text-navy-900">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-white">
              <Radar size={17} />
            </span>
            <span className="font-bold">FreshersJob Radar</span>
          </div>
          <p className="mt-3 max-w-md text-sm leading-6 text-slate-500">
            Real jobs in India — from internships to experienced roles — collected from public
            company sources, classified, deduplicated and refreshed daily. Applications always
            happen on the employer's own website.
          </p>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-navy-900">Product</h3>
          <ul className="mt-3 space-y-2 text-sm text-slate-500">
            <li><Link to="/jobs" className="hover:text-brand-600">Explore jobs</Link></li>
            <li><Link to="/saved" className="hover:text-brand-600">Saved jobs</Link></li>
            <li><Link to="/preferences" className="hover:text-brand-600">Preferences</Link></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-navy-900">Company</h3>
          <ul className="mt-3 space-y-2 text-sm text-slate-500">
            <li><Link to="/about" className="hover:text-brand-600">About &amp; methodology</Link></li>
            <li><a href="/api/v1/health" className="hover:text-brand-600">System health</a></li>
            <li><Link to="/admin" className="hover:text-brand-600">Admin monitoring</Link></li>
          </ul>
        </div>
      </div>
      <div className="border-t border-slate-100 py-5 text-center text-xs text-slate-400">
        Built for job seekers in India, at every career stage. No fabricated listings.
      </div>
    </footer>
  );
}
