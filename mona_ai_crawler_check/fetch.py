"""Network boundary. Tests inject a fetcher and never call this module's client."""

from dataclasses import dataclass
from typing import Mapping, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


@dataclass(frozen=True)
class FetchResponse:
    status: int
    text: str = ""
    headers: Optional[Mapping[str, str]] = None


class FetchError(RuntimeError):
    pass


class UrlFetcher:
    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout

    def request(self, url: str, method: str = "GET") -> FetchResponse:
        request = Request(url, method=method, headers={"User-Agent": "mona-ai-crawler-check/0.1"})
        try:
            with urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode(response.headers.get_content_charset() or "utf-8", "replace")
                return FetchResponse(response.status, body, dict(response.headers.items()))
        except HTTPError as exc:
            body = exc.read().decode("utf-8", "replace") if method != "HEAD" else ""
            return FetchResponse(exc.code, body, dict(exc.headers.items()))
        except (URLError, OSError) as exc:
            raise FetchError(str(exc)) from exc

    def get(self, url: str) -> FetchResponse:
        return self.request(url, "GET")

    def head(self, url: str) -> FetchResponse:
        return self.request(url, "HEAD")
