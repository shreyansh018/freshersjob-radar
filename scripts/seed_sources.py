"""Seed the source registry with candidate public ATS boards.

This seeds only source configuration — never job data. Run `check_sources.py`
afterwards to validate which boards are reachable and yield India postings.
"""

import asyncio
import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1] / "apps" / "api"
if (API_DIR / "app").exists():
    sys.path.insert(0, str(API_DIR))

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models import Company, Source

CANDIDATES: list[tuple[str, str, str]] = [
    ("Stripe", "greenhouse", "stripe"),
    ("Datadog", "greenhouse", "datadog"),
    ("Airtable", "greenhouse", "airtable"),
    ("Duolingo", "greenhouse", "duolingo"),
    ("Robinhood", "greenhouse", "robinhood"),
    ("Figma", "greenhouse", "figma"),
    ("Notion", "greenhouse", "notion"),
    ("Canva", "greenhouse", "canva"),
    ("Atlassian", "greenhouse", "atlassian"),
    ("MongoDB", "greenhouse", "mongodb"),
    ("Elastic", "greenhouse", "elastic"),
    ("Cloudflare", "greenhouse", "cloudflare"),
    ("Twilio", "greenhouse", "twilio"),
    ("Okta", "greenhouse", "okta"),
    ("Pinterest", "greenhouse", "pinterest"),
    ("Reddit", "lever", "reddit"),
    ("Quora", "lever", "quora"),
    ("Asana", "lever", "asana"),
    ("Ramp", "lever", "ramp"),
    ("Linear", "ashby", "linear"),
    ("Vercel", "ashby", "vercel"),
    ("Perplexity", "ashby", "perplexity"),
    ("Anthropic", "ashby", "anthropic"),
    ("Webflow", "ashby", "webflow"),
    ("Razorpay", "ashby", "razorpay"),
    ("SAP", "smartrecruiters", "sap"),
    # Additional candidate boards with public APIs. check_sources.py validates
    # which are reachable and actually carry India postings; dead boards are
    # disabled afterwards.
    ("Databricks", "greenhouse", "databricks"),
    ("Snowflake", "greenhouse", "snowflake"),
    ("Postman", "greenhouse", "postman"),
    ("BrowserStack", "greenhouse", "browserstack"),
    ("Chargebee", "greenhouse", "chargebee"),
    ("Zscaler", "greenhouse", "zscaler"),
    ("Freshworks", "greenhouse", "freshworks"),
    ("Zoho", "greenhouse", "zoho"),
    ("Meesho", "greenhouse", "meesho"),
    ("Cred", "greenhouse", "cred"),
    ("Groww", "greenhouse", "groww"),
    ("Cognizant", "smartrecruiters", "Cognizant"),
    ("Infosys", "smartrecruiters", "Infosys"),
    ("Wipro", "smartrecruiters", "Wipro"),
    ("HCLTechnologies", "smartrecruiters", "HCLTechnologies"),
    ("TechMahindra", "smartrecruiters", "TechMahindra"),
    ("Accenture", "smartrecruiters", "Accenture"),
    ("IBM", "smartrecruiters", "IBM"),
    ("Zepto", "ashby", "zepto"),
    ("Pulsus", "ashby", "pulsus"),
    # Second validation batch of public ATS boards.
    ("Dropbox", "greenhouse", "dropbox"),
    ("PayPal", "greenhouse", "paypal"),
    ("eBay", "greenhouse", "ebay"),
    ("GitLab", "greenhouse", "gitlab"),
    ("HashiCorp", "greenhouse", "hashicorp"),
    ("New Relic", "greenhouse", "newrelic"),
    ("Splunk", "greenhouse", "splunk"),
    ("ServiceNow", "greenhouse", "servicenow"),
    ("Workday", "greenhouse", "workday"),
    ("Adobe", "greenhouse", "adobe"),
    ("Intuit", "greenhouse", "intuit"),
    ("Uber", "greenhouse", "uber"),
    ("Airbnb", "greenhouse", "airbnb"),
    ("Discord", "greenhouse", "discord"),
    ("Zoom", "greenhouse", "zoom"),
    ("Miro", "greenhouse", "miro"),
    ("Calendly", "greenhouse", "calendly"),
    ("Retool", "ashby", "retool"),
    ("Vanta", "ashby", "vanta"),
    ("Coursera", "lever", "coursera"),
    # Third batch: boards that actually carry India intern/fresher postings.
    ("Rubrik", "greenhouse", "rubrik"),
    ("CloudSEK", "greenhouse", "cloudsek"),
    ("Karya", "greenhouse", "karya"),
    ("Airbound", "ashby", "airbound"),
    ("Composio", "ashby", "composio"),
    ("Meraki Labs", "ashby", "meraki-labs"),
    ("Sarvam", "ashby", "sarvam"),
    ("AiPrise", "ashby", "aiprise"),
    ("Kandou AI", "ashby", "kandou-ai"),
]


async def main() -> None:
    inserted = 0
    async with AsyncSessionLocal() as db:
        for name, platform, board in CANDIDATES:
            exists = (
                await db.execute(
                    select(Source).where(Source.platform == platform, Source.board_identifier == board)
                )
            ).scalar_one_or_none()
            if exists:
                continue
            company = (await db.execute(select(Company).where(Company.name == name))).scalar_one_or_none()
            if not company:
                company = Company(name=name)
                db.add(company)
                await db.flush()
            db.add(
                Source(
                    name=name,
                    company_id=company.id,
                    platform=platform,
                    board_identifier=board,
                    config={},
                    enabled=True,
                    fetch_interval_minutes=1440,
                )
            )
            inserted += 1
        await db.commit()
    print(f"Seeded {inserted} candidate sources. Total configured: {len(CANDIDATES)}")


if __name__ == "__main__":
    asyncio.run(main())
