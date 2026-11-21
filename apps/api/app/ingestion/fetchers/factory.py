from app.ingestion.fetchers.ashby import AshbyFetcher
from app.ingestion.fetchers.base import BaseFetcher
from app.ingestion.fetchers.greenhouse import GreenhouseFetcher
from app.ingestion.fetchers.lever import LeverFetcher
from app.ingestion.fetchers.smartrecruiters import SmartRecruitersFetcher
from app.ingestion.fetchers.workable import WorkableFetcher

REGISTRY: dict[str, type[BaseFetcher]] = {
    "greenhouse": GreenhouseFetcher,
    "lever": LeverFetcher,
    "ashby": AshbyFetcher,
    "workable": WorkableFetcher,
    "smartrecruiters": SmartRecruitersFetcher,
}


def get_fetcher(platform: str, source) -> BaseFetcher:
    fetcher_cls = REGISTRY.get(platform)
    if not fetcher_cls:
        raise ValueError(f"Unsupported ATS platform: {platform}")
    return fetcher_cls(source)
