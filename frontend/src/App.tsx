import { useEffect, useState } from "react";
import "./style.css";

type Job = {
  source: string;
  source_id: string;
  title: string;
  company: string;
  location: string;
  description: string;
  url: string;
  posted_at?: string | null;
  workplace_type?: string | null;
  role_category?: string | null;
  city?: string | null;
  experience_level?: string | null;
  job_type?: string | null;
  is_fresher_friendly?: boolean | null;
  classification_confidence?: number | null;
};

const API = "http://127.0.0.1:8000/api";

function cleanDescription(raw: string = ""): string {
  const entities: Record<string, string> = {
    "&nbsp;": " ",
    "&amp;": "&",
    "&lt;": "<",
    "&gt;": ">",
    "&quot;": '"',
    "&#39;": "'",
    "&apos;": "'",
    "&ndash;": "–",
    "&mdash;": "—",
    "&bull;": "•",
  };

  let text = raw;

  for (let i = 0; i < 3; i++) {
    text = text.replace(
      /&(?:nbsp|amp|lt|gt|quot|apos|ndash|mdash|bull);|&#39;/gi,
      (entity) => entities[entity.toLowerCase()] ?? entity,
    );
  }

  text = text.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, " ");
  text = text.replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi, " ");

  text = text.replace(
    /<\/?(?:p|div|h[1-6]|li|ul|ol|br|section|article|tr|td|th)[^>]*>/gi,
    " ",
  );

  text = text.replace(/<[^>]*>/g, " ");
  text = text.replace(/&lt;[^&]*&gt;/gi, " ");

  return text.replace(/\s+/g, " ").trim();
}

function App() {
  const [jobs, setJobs] = useState<Job[]>([]);

  // Input values: what the user is currently typing.
  const [keyword, setKeyword] = useState("");
  const [city, setCity] = useState("");

  // Applied filters: what the API is actually using.
  const [appliedKeyword, setAppliedKeyword] = useState("");
  const [appliedCity, setAppliedCity] = useState("");
  const [role, setRole] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadJobs() {
      setLoading(true);
      setError("");

      try {
        const params = new URLSearchParams({
          fresher_only: "true",
        });

        if (appliedKeyword.trim()) {
          params.set("keyword", appliedKeyword.trim());
        }

        if (appliedCity.trim()) {
          params.set("city", appliedCity.trim());
        }

        if (role.trim()) {
          params.set("role", role.trim());
        }

        const response = await fetch(`${API}/jobs?${params.toString()}`, {
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error("Unable to fetch jobs.");
        }

        const data = await response.json();
        setJobs(data.jobs ?? []);
      } catch (err) {
        if (err instanceof Error && err.name === "AbortError") {
          return;
        }

        setError(
          "Couldn't connect to the job database. Make sure the backend is running.",
        );
        setJobs([]);
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    loadJobs();

    return () => controller.abort();
  }, [appliedKeyword, appliedCity, role]);

  function handleSearch(event: React.FormEvent) {
    event.preventDefault();
    setAppliedKeyword(keyword);
    setAppliedCity(city);
  }

  function resetFilters() {
    setKeyword("");
    setCity("");
    setAppliedKeyword("");
    setAppliedCity("");
    setRole("");
  }

  const roles = [
    "",
    "Software Engineering",
    "Operations",
    "Marketing",
    "HR",
    "Customer Support",
  ];

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#">
          <span className="brand-mark">✳</span>
          <span>
            FreshersJob<span className="brand-light">Radar</span>
          </span>
        </a>

        <nav>
          <a href="#jobs">Explore jobs</a>
          <a href="#about">About</a>
        </nav>

        <a className="top-cta" href="#jobs">
          Find your first job <span>↗</span>
        </a>
      </header>

      <main>
        <section className="hero">
          <div className="hero-content">
            <div className="eyebrow">
              <span className="pulse-dot" /> YOUR CAREER STARTS HERE
            </div>

            <h1>
              Your first job.
              <br />
              Your <span className="gradient-text">next big thing.</span>
            </h1>

            <p className="hero-description">
              A curated radar for internships and entry-level jobs. Less noise,
              more opportunities to get started.
            </p>

            <form className="search-panel" onSubmit={handleSearch}>
              <div className="search-field keyword-field">
                <span className="field-icon">⌕</span>

                <div className="field-content">
                  <label htmlFor="keyword">WHAT ARE YOU LOOKING FOR?</label>

                  <input
                    id="keyword"
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                    placeholder="Job title, skill or company"
                  />
                </div>
              </div>

              <div className="search-divider" />

              <div className="search-field location-field">
                <span className="field-icon">⌖</span>

                <div className="field-content">
                  <label htmlFor="city">LOCATION</label>

                  <input
                    id="city"
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    placeholder="City or anywhere"
                  />
                </div>
              </div>

              <button className="search-button" type="submit">
                Search jobs <span>→</span>
              </button>
            </form>

            <div className="hero-meta">
              <span>✦ Built for freshers</span>
              <span>◈ AI-powered job tagging</span>
              <span>↗ Direct application links</span>
            </div>
          </div>

          <div className="hero-decoration" aria-hidden="true">
            <div className="orbit orbit-outer" />
            <div className="orbit orbit-inner" />

            <div className="radar-center">
              <span>✳</span>
            </div>

            <div className="radar-point point-one" />
            <div className="radar-point point-two" />
            <div className="radar-point point-three" />
            <div className="radar-point point-four" />

            <div className="radar-label label-one">OPPORTUNITY DETECTED</div>

            <div className="radar-label label-two">01 / 05</div>
          </div>
        </section>

        <section className="jobs-section" id="jobs">
          <div className="section-heading">
            <div>
              <div className="eyebrow section-eyebrow">THE RADAR IS ON</div>

              <h2>
                Explore opportunities<span className="heading-dot">.</span>
              </h2>

              <p className="section-subtitle">
                Real openings. Fresh beginnings.
              </p>
            </div>

            <div className="job-count">
              <span className="count-number">{jobs.length}</span>
              <span className="count-label">OPPORTUNITIES</span>
            </div>
          </div>

          <div className="filter-row">
            <div className="filter-label">FILTER BY ROLE</div>

            <div className="role-filters">
              {roles.map((item) => (
                <button
                  key={item || "all"}
                  type="button"
                  className={`filter-chip ${role === item ? "active" : ""}`}
                  onClick={() => setRole(item)}
                >
                  {item || "All roles"}
                </button>
              ))}
            </div>

            <button
              type="button"
              className="clear-filters"
              onClick={resetFilters}
            >
              Reset ↺
            </button>
          </div>

          {loading ? (
            <div className="state-panel">
              <div className="loader" />
              <p>Scanning for opportunities...</p>
            </div>
          ) : error ? (
            <div className="state-panel error-panel">
              <p>{error}</p>
              <button type="button" onClick={resetFilters}>
                Reset ↻
              </button>
            </div>
          ) : jobs.length === 0 ? (
            <div className="state-panel empty-panel">
              <div className="empty-icon">⌕</div>
              <h3>No jobs found on this scan.</h3>
              <p>Try changing your search or filters.</p>
              <button type="button" onClick={resetFilters}>
                Clear filters
              </button>
            </div>
          ) : (
            <div className="job-grid">
              {jobs.map((job) => {
                const description = cleanDescription(job.description);

                return (
                  <article
                    className="job-card"
                    key={`${job.source}-${job.source_id}`}
                  >
                    <div className="card-top">
                      <div className="company-avatar">
                        {job.company.slice(0, 1).toUpperCase()}
                      </div>

                      <div className="company-info">
                        <span className="company-name">{job.company}</span>

                        <span className="job-location">
                          ⌖ {job.city || job.location || "India"}
                        </span>
                      </div>

                      <span className="fresh-badge">
                        <span>✳</span> FRESHER
                      </span>
                    </div>

                    <h3 className="job-title">{job.title}</h3>

                    <div className="job-tags">
                      {job.role_category && (
                        <span className="tag role-tag">
                          {job.role_category}
                        </span>
                      )}

                      {job.job_type && (
                        <span className="tag">{job.job_type}</span>
                      )}

                      {job.workplace_type && (
                        <span className="tag">{job.workplace_type}</span>
                      )}
                    </div>

                    <p className="job-description">
                      {description.slice(0, 190)}
                      {description.length > 190 ? "..." : ""}
                    </p>

                    <div className="card-footer">
                      <div className="verified-label">
                        <span>✓</span> AI screened
                      </div>

                      <a
                        className="apply-link"
                        href={job.url}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Apply now <span>↗</span>
                      </a>
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </section>

        <section className="about-strip" id="about">
          <div className="about-symbol">✳</div>

          <div>
            <h3>Built to make the beginning easier.</h3>

            <p>
              We scan public job boards, filter entry-level opportunities and
              organize them so you can focus on what matters: getting started.
            </p>
          </div>

          <span className="about-side">
            THE RADAR
            <br />
            FOR YOUR FUTURE
          </span>
        </section>
      </main>

      <footer>
        <a className="brand footer-brand" href="#">
          <span className="brand-mark">✳</span>

          <span>
            FreshersJob<span className="brand-light">Radar</span>
          </span>
        </a>

        <span>Made for the next generation of builders. © 2026</span>

        <span className="footer-status">
          <span className="pulse-dot" /> RADAR ACTIVE
        </span>
      </footer>
    </div>
  );
}

export default App;
