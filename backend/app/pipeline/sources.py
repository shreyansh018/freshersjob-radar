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
]

LEVER_SOURCES = [
    LeverSource("Employ", "employ"),
]