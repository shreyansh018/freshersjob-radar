# Source coverage

`scripts/seed_sources.py` seeds **candidate** public ATS boards. It does not seed jobs.

Validate the registry with:

```powershell
docker compose run --rm -v "${PWD}:/repo" -w /repo api python scripts/check_sources.py
```

Boards that return 404 or zero postings are disabled with:

```powershell
docker compose run --rm -v "${PWD}:/repo" -w /repo api python scripts/disable_dead_sources.py
```

Only sources with reachable public endpoints and genuine India postings stay enabled.
No authentication, paywall or anti-bot protection is bypassed. Terms of service and
robots.txt must be re-checked before enabling any new source.

## Validated high-yield boards

Measured on 2026-11-20 with `check_sources.py` (raw postings / India-eligible postings):

| Source | Platform | Raw | India posts | Notes |
|---|---|---:|---:|---|
| Okta | greenhouse | 365 | 103 | Highest yield |
| Zscaler | greenhouse | 377 | 89 | Added after first validation |
| Databricks | greenhouse | 901 | 79 | Capped by `MAX_JOBS_PER_SOURCE` |
| MongoDB | greenhouse | 413 | 70 | |
| Sarvam | ashby | 44 | 44 | India-only board; interns/final-year grads |
| Stripe | greenhouse | 773 | 45 | Bengaluru interns |
| Rubrik | greenhouse | 204 | 41 | Bengaluru interns |
| GitLab | greenhouse | 246 | 32 | Added after second validation |
| Airbound | ashby | 25 | 25 | India-only board; fresher internship program |
| Kandou AI | ashby | 42 | 21 | Hyderabad/Bengaluru internships |
| CloudSEK | greenhouse | 19 | 19 | India-only board; SDE interns |
| Meraki Labs | ashby | 19 | 17 | Bengaluru AI internships |
| Karya | greenhouse | 16 | 16 | India-only board; research interns |
| Twilio | greenhouse | 107 | 15 | |
| Elastic | greenhouse | 370 | 14 | |
| Airbnb | greenhouse | 203 | 13 | Added after second validation |
| AiPrise | ashby | 19 | 10 | Bengaluru SDE I roles |
| Datadog | greenhouse | 382 | 9 | |
| Groww | greenhouse | 9 | 9 | Small board, entirely India |
| Cloudflare | greenhouse | 497 | 8 | |
| Composio | ashby | 30 | 4 | Bengaluru product-ops intern |
| New Relic | greenhouse | 42 | 4 | Added after second validation |
| Figma | greenhouse | 145 | 2 | |
| Duolingo | greenhouse | 55 | 1 | |

Third validation batch (fresher/intern-heavy boards): 9 added, all reachable.
Registry total: `TOTAL raw=6011 india_eligible=688 sources=34`.

Valid boards that currently have **no** India postings (kept enabled for future refreshes):
Airtable, Robinhood, Pinterest, Linear, Perplexity, Webflow, Dropbox, Discord, Calendly, Vanta.

Disabled after validation: 41 boards returning 404 or zero postings, including Atlassian,
Notion, Canva, Quora, Reddit, Asana, Ramp, Anthropic, Razorpay, Snowflake, Postman,
BrowserStack, Chargebee, Freshworks, Zoho, Meesho, Cred, Zepto, Pulsus, PayPal, eBay,
HashiCorp, Splunk, ServiceNow, Workday, Adobe, Intuit, Uber, Zoom, Miro, Retool, Coursera,
and the SmartRecruiters boards that returned empty feeds.

## Observed funnel (last full ingestion)

```
raw=6011  ->  normalized=6011  ->  candidates=688
new=197  updated=19  unchanged=472  duplicates=0
failed_sources=0
resulting active jobs: 689
```

Every India-eligible posting is now kept and tagged by seniority — internship through
experienced. Earlier runs dropped explicitly senior titles; that filter was removed so
the portal reflects real market coverage. No jobs, salaries, dates or links are invented.
