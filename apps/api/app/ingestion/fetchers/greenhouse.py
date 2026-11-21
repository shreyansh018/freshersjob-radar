from app.ingestion.fetchers.base import BaseFetcher


class GreenhouseFetcher(BaseFetcher):
    platform = "greenhouse"

    def build_url(self) -> str:
        return f"https://boards-api.greenhouse.io/v1/boards/{self.board}/jobs?content=true"
