import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import type { Preferences } from "@/types";

interface FormValues {
  roles: string;
  locations: string;
  skills: string;
  experience: string;
  remote_preference: string;
}

const asList = (value: string) => value.split(",").map((item) => item.trim()).filter(Boolean);

export function Preferences() {
  const queryClient = useQueryClient();
  const prefs = useQuery({ queryKey: ["preferences"], queryFn: api.preferences, retry: false });
  const form = useForm<FormValues>({
    defaultValues: { roles: "", locations: "", skills: "", experience: "", remote_preference: "" },
  });

  useEffect(() => {
    if (prefs.data) {
      form.reset({
        roles: prefs.data.roles.join(", "),
        locations: prefs.data.locations.join(", "),
        skills: prefs.data.skills.join(", "),
        experience: prefs.data.experience ?? "",
        remote_preference: prefs.data.remote_preference ?? "",
      });
    }
  }, [prefs.data, form]);

  const save = useMutation({
    mutationFn: (values: FormValues): Promise<Preferences> =>
      api.updatePreferences({
        roles: asList(values.roles),
        locations: asList(values.locations),
        skills: asList(values.skills),
        experience: values.experience || null,
        remote_preference: values.remote_preference || null,
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["preferences"] }),
  });

  if (prefs.isError) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-20 text-center">
        <h1 className="text-2xl font-bold text-navy-900">Sign in to manage preferences</h1>
        <Link to="/login" className="mt-5 inline-block"><Button>Sign in</Button></Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
        <h1 className="text-2xl font-bold text-navy-900">Your preferences</h1>
        <p className="mt-1 text-sm text-slate-500">Used to prioritise recommendations — other opportunities stay visible.</p>
        <form
          className="mt-8 space-y-5 rounded-2xl border border-slate-200 bg-white p-6"
          onSubmit={form.handleSubmit((values) => save.mutate(values))}
        >
          <Field label="Preferred roles" hint="Comma separated">
            <Input {...form.register("roles")} placeholder="Frontend Development, Data Analytics" />
          </Field>
          <Field label="Preferred locations" hint="Comma separated">
            <Input {...form.register("locations")} placeholder="Bengaluru, Pune" />
          </Field>
          <Field label="Skills" hint="Comma separated">
            <Input {...form.register("skills")} placeholder="React, Python, SQL" />
          </Field>
          <Field label="Experience">
            <Input {...form.register("experience")} placeholder="Fresher" />
          </Field>
          <Field label="Remote preference">
            <Input {...form.register("remote_preference")} placeholder="Remote or Hybrid" />
          </Field>
          <Button type="submit" disabled={save.isPending}>{save.isPending ? "Saving…" : "Save preferences"}</Button>
          {save.isSuccess && <p className="text-sm text-emerald-600">Preferences saved.</p>}
          {save.isError && <p className="text-sm text-rose-600">Could not save preferences. Please sign in again.</p>}
        </form>
      </div>
    </div>
  );
}

function Field({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="flex items-center justify-between text-sm font-semibold text-slate-700">
        {label} {hint && <span className="text-xs font-normal text-slate-400">{hint}</span>}
      </span>
      <div className="mt-2">{children}</div>
    </label>
  );
}
