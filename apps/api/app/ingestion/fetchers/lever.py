from app.ingestion.fetchers.base import BaseFetcher


class LeverFetcher(BaseFetcher):
    platform = "lever"

    def build_url(self) -> str:
        return f"https://api.lever.co/v0/postings/{self.board}?mode=json"
