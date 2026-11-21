import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { JobCard } from "@/components/jobs/JobCard";
import type { JobSummary } from "@/types";

const job: JobSummary = {
  id: "1",
  title: "Frontend Engineering Intern",
  company: { id: "c1", name: "Acme" },
  source: { id: "s1", name: "Acme", platform: "greenhouse" },
  normalized_location: "Bengaluru, India",
  city: "Bengaluru",
  country: "India",
  workplace_type: "Hybrid",
  employment_type: "Internship",
  experience_level: "Internship",
  role_category: "Frontend Development",
  fresher_friendly: true,
  status: "active",
  posted_at: "2026-01-01T00:00:00Z",
  first_seen_at: "2026-01-01T00:00:00Z",
  last_checked_at: null,
  skills: ["React", "TypeScript"],
  application_url: "https://example.com/apply",
  is_new: false,
  recently_verified: false,
};

describe("JobCard", () => {
  it("shows the title, company and a safe apply link", () => {
    render(<MemoryRouter><JobCard job={job} /></MemoryRouter>);
    expect(screen.getByText("Frontend Engineering Intern")).toBeInTheDocument();
    expect(screen.getByText("Acme")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /apply/i })).toHaveAttribute("href", "https://example.com/apply");
  });

  it("does not render an apply link for an unsafe URL", () => {
    render(<MemoryRouter><JobCard job={{ ...job, application_url: "javascript:alert(1)" }} /></MemoryRouter>);
    expect(screen.queryByRole("link", { name: /apply/i })).not.toBeInTheDocument();
  });
});
