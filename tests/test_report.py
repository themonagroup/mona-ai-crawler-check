import json

from mona_ai_crawler_check import check_site
from mona_ai_crawler_check.fetch import FetchResponse
from mona_ai_crawler_check.report import Check, Report, Status


class SiteFetcher:
    def __init__(self, robots, html, llms_status=404):
        self.robots = robots
        self.html = html
        self.llms_status = llms_status

    def get(self, url):
        if url.endswith("/robots.txt"):
            return FetchResponse(200, self.robots)
        if url.endswith("/llms.txt"):
            return FetchResponse(self.llms_status, "# Site")
        return FetchResponse(200, self.html)

    def head(self, url):
        return FetchResponse(self.llms_status)


def test_locked_robot_results(fixture_text):
    report = check_site("https://example.test", fetcher=SiteFetcher(
        fixture_text("robots-mixed.txt"), fixture_text("rich.html"), 200))
    assert report.robots["GPTBot"].status == Status.FAIL
    assert report.robots["ClaudeBot"].status == Status.PASS


def test_shell_content_is_fail(fixture_text):
    report = check_site("https://example.test", fetcher=SiteFetcher("", fixture_text("js-shell.html")))
    assert report.content.status == Status.FAIL


def test_rich_content_and_json_ld_pass(fixture_text):
    report = check_site("https://example.test", fetcher=SiteFetcher("", fixture_text("rich.html"), 200))
    assert report.content.status == report.json_ld.status == Status.PASS


def test_missing_llms_is_warn_with_mona_suggestion(fixture_text):
    report = check_site("https://example.test", fetcher=SiteFetcher("", fixture_text("rich.html")))
    assert report.llms_txt.status == Status.WARN
    assert "mona-llms-txt" in report.llms_txt.fix


def test_json_output_is_valid(fixture_text):
    report = check_site("example.test", fetcher=SiteFetcher("", fixture_text("rich.html"), 200))
    assert json.loads(report.to_json())["status"] == "PASS"


def test_text_output_contains_table_and_fixes(fixture_text):
    report = check_site("https://example.test", fetcher=SiteFetcher("", fixture_text("js-shell.html")))
    output = report.render_text()
    assert "CHECK" in output and "Fixes:" in output and "Server content" in output


def test_issues_excludes_passes():
    good = Check("good", Status.PASS, "ok")
    warn = Check("warn", Status.WARN, "hmm", "fix")
    report = Report("https://x", {}, good, warn, good, {})
    assert report.issues == [warn]


def test_missing_robots_means_allowed(fixture_text):
    class MissingRobots(SiteFetcher):
        def get(self, url):
            if url.endswith("robots.txt"):
                return FetchResponse(404)
            return super().get(url)
    report = check_site("https://example.test", fetcher=MissingRobots("", fixture_text("rich.html"), 200))
    assert all(check.status == Status.PASS for check in report.robots.values())


def test_metadata_is_exposed(fixture_text):
    report = check_site("https://example.test", fetcher=SiteFetcher("", fixture_text("rich.html"), 200))
    assert report.metadata == {"title": True, "meta_description": True, "h1": True}


def test_query_path_used_for_robots(fixture_text):
    report = check_site("https://example.test/private?q=x", fetcher=SiteFetcher(
        "User-agent: *\nDisallow: /private", fixture_text("rich.html"), 200))
    assert report.robots["PerplexityBot"].status == Status.FAIL


def test_invalid_url_rejected():
    try:
        check_site("ftp://example.test", fetcher=SiteFetcher("", ""))
    except ValueError:
        pass
    else:
        raise AssertionError("ValueError expected")
