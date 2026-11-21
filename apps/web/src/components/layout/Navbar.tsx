import { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { LogOut, Menu, Radar, X } from "lucide-react";
import { displayName, useAuth } from "@/hooks/useAuth";
import { cn } from "@/lib/utils";

const links = [
  { to: "/jobs", label: "Explore jobs" },
  { to: "/saved", label: "Saved" },
  { to: "/about", label: "About" },
];

export function Navbar() {
  const [open, setOpen] = useState(false);
  const { user, signOut } = useAuth();
  const name = displayName(user);

  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-navy-950/95 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link to="/" className="flex items-center gap-2 text-white">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-accent-600">
            <Radar size={19} />
          </span>
          <span className="text-base font-bold tracking-tight">FreshersJob Radar</span>
        </Link>

        <nav className="hidden items-center gap-7 md:flex">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                cn(
                  "text-sm font-medium transition-colors",
                  isActive ? "text-white" : "text-slate-300 hover:text-white",
                )
              }
            >
              {link.label}
            </NavLink>
          ))}
          {user?.role === "admin" && (
            <NavLink
              to="/admin"
              className="text-sm font-medium text-slate-300 transition-colors hover:text-white"
            >
              Admin
            </NavLink>
          )}
          {name ? (
            <div className="flex items-center gap-3">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-brand-500 to-accent-600 text-xs font-bold text-white">
                {name.slice(0, 1).toUpperCase()}
              </span>
              <span className="text-sm font-semibold text-white">Hi, {name}</span>
              <button
                type="button"
                onClick={() => void signOut()}
                title="Sign out"
                className="rounded-lg p-2 text-slate-300 transition hover:bg-white/10 hover:text-white"
              >
                <LogOut size={17} />
              </button>
            </div>
          ) : (
            <Link
              to="/login"
              className="rounded-xl bg-white px-4 py-2 text-sm font-semibold text-navy-900 transition hover:bg-slate-100"
            >
              Sign in
            </Link>
          )}
        </nav>

        <button
          aria-label="Toggle navigation"
          className="rounded-lg p-2 text-white md:hidden"
          onClick={() => setOpen((value) => !value)}
        >
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {open && (
        <div className="border-t border-white/10 bg-navy-950 px-4 py-3 md:hidden">
          {[...links, ...(user?.role === "admin" ? [{ to: "/admin", label: "Admin" }] : [])].map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className="block py-2.5 text-sm text-slate-200"
              onClick={() => setOpen(false)}
            >
              {link.label}
            </Link>
          ))}
          {name ? (
            <>
              <div className="py-2.5 text-sm font-semibold text-white">Hi, {name}</div>
              <button
                type="button"
                onClick={() => { void signOut(); setOpen(false); }}
                className="flex items-center gap-2 py-2.5 text-sm text-slate-200"
              >
                <LogOut size={16} /> Sign out
              </button>
            </>
          ) : (
            <Link
              to="/login"
              className="block py-2.5 text-sm text-slate-200"
              onClick={() => setOpen(false)}
            >
              Sign in
            </Link>
          )}
        </div>
      )}
    </header>
  );
}
