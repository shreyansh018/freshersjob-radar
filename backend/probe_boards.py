import asyncio
import httpx

candidates = [
    "rubrik", "hackerrank", "glance", "turing", "samsara",
    "instacart", "gusto", "notion", "duolingo", "ginkgo",
    "nvidia", "airbnb", "discord", "stripe", "figma",
    "databricks", "cloudflare", "anthropic", "mongodb",
    "coinbase", "groww", "palantir", "spotify",
    "sentry", "vercel", "grammarly", "doordash",
]

async def probe(client, token):
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    try:
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            count = len(data.get("jobs", []))
            if count:
                print(f"VALID | {token} | {count} jobs")
                return
        print(f"MISS  | {token} | {response.status_code}")
    except Exception as e:
        print(f"ERROR | {token} | {e}")

async def main():
    async with httpx.AsyncClient(timeout=15) as client:
        await asyncio.gather(*(probe(client, t) for t in candidates))

asyncio.run(main())