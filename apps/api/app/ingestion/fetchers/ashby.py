from app.ingestion.fetchers.base import BaseFetcher


class AshbyFetcher(BaseFetcher):
    platform = "ashby"

    def build_url(self) -> str:
        return f"https://api.ashbyhq.com/posting-api/job-board/{self.board}?includeCompensation=true"

    def parse(self, payload):
        if isinstance(payload, dict):
            return payload.get("jobs", [])
        return []
