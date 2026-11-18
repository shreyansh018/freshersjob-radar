from dataclasses import dataclass


@dataclass(frozen=True)
class GreenhouseSource:
    company: str
    board_token: str


GREENHOUSE_SOURCES = [
    GreenhouseSource(
        company="Example Company",
        board_token="example",
    ),
]