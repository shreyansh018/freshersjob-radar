
from dataclasses import dataclass


@dataclass(frozen=True)
class GreenhouseSource:
    company: str
    board_token: str


@dataclass(frozen=True)
class LeverSource:
    company: str
    site: str


# Candidate Greenhouse boards.
# These are probed by the ingestion pipeline; some may not exist
# or may have no relevant jobs at the time of fetching.
GREENHOUSE_SOURCES = [
    GreenhouseSource("Stripe", "stripe"),
    GreenhouseSource("Figma", "figma"),
    GreenhouseSource("Databricks", "databricks"),
    GreenhouseSource("Cloudflare", "cloudflare"),
    GreenhouseSource("Rippling", "rippling"),
    GreenhouseSource("Plaid", "plaid"),
    GreenhouseSource("Anthropic", "anthropic"),
    GreenhouseSource("Canva", "canva"),
    GreenhouseSource("Uber", "uber"),
    GreenhouseSource("Slack", "slack"),
    GreenhouseSource("Zapier", "zapier"),
    GreenhouseSource("MongoDB", "mongodb"),
    GreenhouseSource("Supabase", "supabase"),
    GreenhouseSource("Linear", "linear"),
    GreenhouseSource("Coinbase", "coinbase"),
    GreenhouseSource("Brex", "brex"),
    GreenhouseSource("Ramp", "ramp"),
    GreenhouseSource("Scale AI", "scaleai"),
    GreenhouseSource("Postman", "postman"),
    GreenhouseSource("BrowserStack", "browserstack"),
    GreenhouseSource("PhonePe", "phonepe"),
    GreenhouseSource("Razorpay", "razorpay"),
    GreenhouseSource("Swiggy", "swiggy"),
    GreenhouseSource("CRED", "cred"),
    GreenhouseSource("Meesho", "meesho"),
    GreenhouseSource("Zomato", "zomato"),
    GreenhouseSource("Groww", "groww"),
    GreenhouseSource("Freshworks", "freshworks"),
    GreenhouseSource("Zoho", "zoho"),
]


# Candidate Lever boards.
LEVER_SOURCES = [
    LeverSource("Employ", "employ"),
    LeverSource("Lever Demo", "leverdemo"),
]
