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
    # We'll add verified Lever boards in the next step.
]