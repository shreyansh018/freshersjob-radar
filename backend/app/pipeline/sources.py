from dataclasses import dataclass


@dataclass(frozen=True)
class GreenhouseSource:
    company: str
    board_token: str


@dataclass(frozen=True)
class LeverSource:
    company: str
    site: str


GREENHOUSE_SOURCES = [
    GreenhouseSource("Stripe", "stripe"),
    GreenhouseSource("Figma", "figma"),
    GreenhouseSource("Databricks", "databricks"),
    GreenhouseSource("Cloudflare", "cloudflare"),
    GreenhouseSource("Anthropic", "anthropic"),
    GreenhouseSource("MongoDB", "mongodb"),
    GreenhouseSource("Coinbase", "coinbase"),
    GreenhouseSource("Brex", "brex"),
    GreenhouseSource("Ramp", "ramp"),
    GreenhouseSource("Scale AI", "scaleai"),
    GreenhouseSource("Groww", "groww"),
    GreenhouseSource("HackerRank", "hackerrank"),
    GreenhouseSource("Instacart", "instacart"),
    GreenhouseSource("Vercel", "vercel"),
    GreenhouseSource("Gusto", "gusto"),
    GreenhouseSource("Discord", "discord"),
    GreenhouseSource("Glance", "glance"),
    GreenhouseSource("Duolingo", "duolingo"),
    GreenhouseSource("Turing", "turing"),
    GreenhouseSource("Rubrik", "rubrik"),
    GreenhouseSource("Airbnb", "airbnb"),
    GreenhouseSource("Samsara", "samsara"),
]

LEVER_SOURCES = [
    LeverSource("Employ", "employ"),
]