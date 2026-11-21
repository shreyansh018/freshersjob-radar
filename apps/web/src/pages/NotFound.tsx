import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

export function NotFound() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center px-4 text-center">
      <p className="text-sm font-bold text-brand-600">404</p>
      <h1 className="mt-2 text-3xl font-extrabold text-navy-900">We couldn't find that page</h1>
      <p className="mt-2 text-sm text-slate-500">The job may have expired or the link may be incorrect.</p>
      <Link to="/jobs" className="mt-6"><Button>Explore jobs</Button></Link>
    </div>
  );
}
