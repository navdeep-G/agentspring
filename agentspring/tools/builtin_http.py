from . import tool
import httpx, bs4
from urllib.parse import urlparse
from agentspring.config import settings
def _allowed(url:str)->bool:
    if not settings.ALLOWLIST_DOMAINS: return True
    host=urlparse(url).hostname or ""
    allowed=[h.strip() for h in settings.ALLOWLIST_DOMAINS.split(",") if h.strip()]
    return any(host.endswith(a) for a in allowed)
@tool("http_get","Fetch a URL and return cleaned text (allowlist-enforced)",parameters={"type":"object","properties":{"url":{"type":"string","format":"uri"}},"required":["url"]})
async def http_get(url: str) -> str:
    if not _allowed(url): return "Domain not allowed."
    async with httpx.AsyncClient(timeout=30) as client:
        r=await client.get(url, follow_redirects=True); r.raise_for_status()
        soup=bs4.BeautifulSoup(r.text,"html.parser"); return soup.get_text(" ", strip=True)[:20000]
