"""Public API for mona-ai-crawler-check."""

from urllib.parse import urlsplit, urlunsplit

from .bots import AI_BOTS
from .content import analyze_content
from .fetch import UrlFetcher
from .llmstxt import check_llms_txt
from .report import Check, Report, Status
from .robots import bot_allowed, parse_robots

__version__ = "0.1.0"


def _site_urls(url: str):
    if "://" not in url:
        url = "https://" + url
    parsed = urlsplit(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("url must be an HTTP(S) website URL")
    origin = urlunsplit((parsed.scheme, parsed.netloc, "", "", "")).rstrip("/")
    page_path = parsed.path or "/"
    if parsed.query:
        page_path += "?" + parsed.query
    return url, origin, page_path


def check_site(url: str, *, fetcher=None) -> Report:
    """Check one page. Pass a fetcher with get/head methods for deterministic tests."""
    page_url, origin, page_path = _site_urls(url)
    fetcher = fetcher or UrlFetcher()

    robots_response = fetcher.get(origin + "/robots.txt")
    # Missing robots.txt means crawlers are allowed by default.
    robots_rules = parse_robots(robots_response.text if robots_response.status == 200 else "")
    robot_checks = {}
    for bot in AI_BOTS:
        allowed = bot_allowed(robots_rules, bot, page_path)
        robot_checks[bot] = Check(
            f"robots.txt / {bot}", Status.PASS if allowed else Status.FAIL,
            "Allowed for requested path" if allowed else f"Blocked on {page_path}",
            "Remove or narrow the matching Disallow rule in robots.txt." if not allowed else "",
        )

    page_response = fetcher.get(page_url)
    analysis = analyze_content(page_response.text if 200 <= page_response.status < 300 else "")
    content_ok = 200 <= page_response.status < 300 and not analysis.is_js_shell
    content_check = Check(
        "Server-rendered content", Status.PASS if content_ok else Status.FAIL,
        f"{analysis.text_length} visible characters" if content_ok else "AI receives an empty or very thin JS-only shell",
        "Render meaningful page content in the initial HTML response (SSR or static HTML)." if not content_ok else "",
    )

    llms = check_llms_txt(origin + "/llms.txt", fetcher)
    llms_check = Check(
        "llms.txt", Status.PASS if llms.exists else Status.WARN,
        "Found /llms.txt" if llms.exists else "/llms.txt was not found",
        "Generate and publish /llms.txt; you can use mona-llms-txt." if not llms.exists else "",
    )
    json_check = Check(
        "JSON-LD", Status.PASS if analysis.has_json_ld else Status.WARN,
        "Structured data found" if analysis.has_json_ld else "No JSON-LD structured data found",
        "Add relevant schema.org JSON-LD to the server-rendered HTML." if not analysis.has_json_ld else "",
    )
    return Report(page_url, robot_checks, content_check, llms_check, json_check, {
        "title": analysis.has_title,
        "meta_description": analysis.has_meta_description,
        "h1": analysis.has_h1,
    })


__all__ = ["check_site", "Report"]

