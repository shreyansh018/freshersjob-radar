import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { JobCard } from "@/components/jobs/JobCard";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

export function Saved() {
  const queryClient = useQueryClient();
  const saved = useQuery({ queryKey: ["saved"], queryFn: api.savedJobs, retry: false });
  const remove = useMutation({
    mutationFn: api.unsaveJob,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["saved"] }),
  });

  if (saved.isError) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-20 text-center">
        <h1 className="text-2xl font-bold text-navy-900">Sign in to see saved jobs</h1>
        <p className="mt-2 text-sm text-slate-500">Your saved list is private to your account.</p>
        <Link to="/login" className="mt-5 inline-block"><Button>Sign in</Button></Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
        <h1 className="text-2xl font-bold text-navy-900">Saved jobs</h1>
        <p className="mt-1 text-sm text-slate-500">Keep track of the opportunities you want to revisit.</p>
        <div className="mt-8 space-y-4">
          {saved.data?.map(({ job }) => (
            <JobCard key={job.id} job={job} saved onSave={(item) => remove.mutate(item.id)} />
          ))}
          {saved.data && saved.data.length === 0 && (
            <div className="rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center text-sm text-slate-500">
              You haven't saved any jobs yet. <Link to="/jobs" className="font-semibold text-brand-600">Explore jobs</Link>.
            </div>
          )}
          {saved.isLoading && <p className="text-sm text-slate-500">Loading saved jobs…</p>}
        </div>
      </div>
    </div>
  );
}
