from app.ingestion.fetchers.base import BaseFetcher


class WorkableFetcher(BaseFetcher):
    """Public Workable careers widget feed (per-account, where permitted)."""

    platform = "workable"

    def build_url(self) -> str:
        return f"https://apply.workable.com/api/v3/accounts/{self.board}/jobs"

    def parse(self, payload):
        if isinstance(payload, dict):
            return payload.get("results", [])
        return []
