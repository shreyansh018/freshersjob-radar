import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import { loginSchema, type LoginValues } from "@/lib/schemas";

export function Login() {
  const navigate = useNavigate();
  const { setUser } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [error, setError] = useState("");
  const form = useForm<LoginValues>({ resolver: zodResolver(loginSchema) });

  async function submit(values: LoginValues) {
    setError("");
    try {
      if (mode === "login") {
        const result = await api.login(values.email, values.password);
        setUser(result.user);
      } else {
        await api.register(values.email, values.password);
        // Registration does not set a session cookie, so sign in immediately.
        const result = await api.login(values.email, values.password);
        setUser(result.user);
      }
      navigate("/saved");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    }
  }

  return (
    <div className="flex min-h-[70vh] items-center justify-center bg-slate-50 px-4 py-12">
      <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-7 shadow-card">
        <h1 className="text-2xl font-bold text-navy-900">{mode === "login" ? "Welcome back" : "Create an account"}</h1>
        <p className="mt-2 text-sm text-slate-500">
          {mode === "login" ? "Sign in to save jobs and set preferences." : "Saved jobs and preferences are free."}
        </p>
        <form className="mt-6 space-y-4" onSubmit={form.handleSubmit(submit)}>
          <label className="block text-sm font-semibold text-slate-700">
            Email
            <div className="mt-2"><Input type="email" {...form.register("email")} placeholder="you@example.com" /></div>
            {form.formState.errors.email && <span className="text-xs text-rose-600">{form.formState.errors.email.message}</span>}
          </label>
          <label className="block text-sm font-semibold text-slate-700">
            Password
            <div className="mt-2"><Input type="password" {...form.register("password")} placeholder="At least 8 characters" /></div>
            {form.formState.errors.password && <span className="text-xs text-rose-600">{form.formState.errors.password.message}</span>}
          </label>
          {error && <p className="text-sm text-rose-600">{error}</p>}
          <Button type="submit" className="w-full">{mode === "login" ? "Sign in" : "Create account"}</Button>
        </form>
        <button
          className="mt-5 w-full text-center text-sm font-semibold text-brand-600"
          onClick={() => setMode(mode === "login" ? "register" : "login")}
        >
          {mode === "login" ? "Need an account? Register" : "Already have an account? Sign in"}
        </button>
      </div>
    </div>
  );
}
