import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type Tone = "brand" | "green" | "amber" | "slate" | "purple" | "rose";

const tones: Record<Tone, string> = {
  brand: "bg-brand-50 text-brand-700 ring-brand-100",
  green: "bg-emerald-50 text-emerald-700 ring-emerald-100",
  amber: "bg-amber-50 text-amber-700 ring-amber-100",
  slate: "bg-slate-100 text-slate-600 ring-slate-200",
  purple: "bg-violet-50 text-violet-700 ring-violet-100",
  rose: "bg-rose-50 text-rose-700 ring-rose-100",
};

export function Badge({
  tone = "slate",
  className,
  ...props
}: HTMLAttributes<HTMLSpanElement> & { tone?: Tone }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-1 text-[11px] font-semibold ring-1 ring-inset",
        tones[tone],
        className,
      )}
      {...props}
    />
  );
}
