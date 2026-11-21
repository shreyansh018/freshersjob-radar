from app.ingestion.fetchers.base import BaseFetcher


class SmartRecruitersFetcher(BaseFetcher):
    platform = "smartrecruiters"

    def build_url(self) -> str:
        return f"https://api.smartrecruiters.com/v1/companies/{self.board}/postings"

    def parse(self, payload):
        if isinstance(payload, dict):
            return payload.get("content", [])
        return []
