"""llms.txt discovery isolated from concrete networking."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LlmsTxtResult:
    exists: bool
    status: Optional[int]
    content: str = ""


def check_llms_txt(url: str, fetcher) -> LlmsTxtResult:
    """Use HEAD first; fall back to GET for unsupported/ambiguous servers."""
    try:
        response = fetcher.head(url)
        if 200 <= response.status < 300:
            return LlmsTxtResult(True, response.status)
        if response.status not in (405, 501):
            return LlmsTxtResult(False, response.status)
        response = fetcher.get(url)
        return LlmsTxtResult(200 <= response.status < 300, response.status, response.text)
    except (AttributeError, NotImplementedError):
        response = fetcher.get(url)
        return LlmsTxtResult(200 <= response.status < 300, response.status, response.text)
