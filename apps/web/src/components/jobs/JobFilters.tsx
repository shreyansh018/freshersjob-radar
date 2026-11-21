import { RotateCcw, SlidersHorizontal } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import type { CategoryCount, JobFilters as Filters } from "@/types";

interface Props {
  filters: Filters;
  onChange: (patch: Partial<Filters>) => void;
  onReset: () => void;
  categories: CategoryCount[];
  locations: CategoryCount[];
}

const experiences = [
  "Internship",
  "Fresher",
  "Graduate",
  "Entry Level",
  "Early Career",
  "Experienced",
];
const employment = ["Full-time", "Internship", "Part-time", "Contract", "Apprenticeship"];

export function JobFiltersPanel({ filters, onChange, onReset, categories, locations }: Props) {
  const active = Object.entries(filters).filter(
    ([key, value]) => !["page", "limit", "sort"].includes(key) && Boolean(value),
  );

  return (
    <aside className="rounded-2xl border border-slate-200 bg-white p-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="flex items-center gap-2 text-sm font-bold text-navy-900">
          <SlidersHorizontal size={16} className="text-brand-600" /> Filters
        </h2>
        {active.length > 0 && (
          <button onClick={onReset} className="inline-flex items-center gap-1 text-xs font-semibold text-brand-600">
            <RotateCcw size={13} /> Reset
          </button>
        )}
      </div>

      {active.length > 0 && (
        <div className="mb-5 flex flex-wrap gap-1.5">
          {active.map(([key, value]) => (
            <Badge key={key} tone="brand">
              {key}: {String(value)}
            </Badge>
          ))}
        </div>
      )}

      <div className="space-y-4">
        <div>
          <label className="mb-1.5 block text-xs font-semibold text-slate-600">Role category</label>
          <Select value={filters.role_category ?? ""} onChange={(e) => onChange({ role_category: e.target.value })}>
            <option value="">All roles</option>
            {categories.map((item) => (
              <option key={item.name} value={item.name}>{item.name} ({item.count})</option>
            ))}
          </Select>
        </div>

        <div>
          <label className="mb-1.5 block text-xs font-semibold text-slate-600">City</label>
          <Select value={filters.city ?? ""} onChange={(e) => onChange({ city: e.target.value })}>
            <option value="">All cities</option>
            {locations.map((item) => (
              <option key={item.name} value={item.name}>{item.name} ({item.count})</option>
            ))}
          </Select>
        </div>

        <div>
          <label className="mb-1.5 block text-xs font-semibold text-slate-600">Experience</label>
          <Select value={filters.experience_level ?? ""} onChange={(e) => onChange({ experience_level: e.target.value })}>
            <option value="">Any experience</option>
            {experiences.map((item) => <option key={item} value={item}>{item}</option>)}
          </Select>
        </div>

        <div>
          <label className="mb-1.5 block text-xs font-semibold text-slate-600">Employment type</label>
          <Select value={filters.employment_type ?? ""} onChange={(e) => onChange({ employment_type: e.target.value })}>
            <option value="">Any type</option>
            {employment.map((item) => <option key={item} value={item}>{item}</option>)}
          </Select>
        </div>

        <div>
          <label className="mb-1.5 block text-xs font-semibold text-slate-600">Workplace</label>
          <Select value={filters.workplace_type ?? ""} onChange={(e) => onChange({ workplace_type: e.target.value })}>
            <option value="">Any workplace</option>
            <option value="On-site">On-site</option>
            <option value="Hybrid">Hybrid</option>
            <option value="Remote">Remote</option>
          </Select>
        </div>

        <div>
          <label className="mb-1.5 block text-xs font-semibold text-slate-600">Company</label>
          <Input
            placeholder="e.g. Stripe"
            value={filters.company ?? ""}
            onChange={(e) => onChange({ company: e.target.value })}
          />
        </div>

        <Button variant="outline" className="w-full" onClick={onReset}>
          Clear all filters
        </Button>
      </div>
    </aside>
  );
}
