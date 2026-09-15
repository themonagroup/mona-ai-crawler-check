from mona_ai_crawler_check.fetch import FetchResponse
from mona_ai_crawler_check.llmstxt import check_llms_txt


class FakeFetcher:
    def __init__(self, head_status=200, get_status=200):
        self.head_status = head_status
        self.get_status = get_status
        self.calls = []

    def head(self, url):
        self.calls.append(("HEAD", url))
        return FetchResponse(self.head_status)

    def get(self, url):
        self.calls.append(("GET", url))
        return FetchResponse(self.get_status, "# Site")


def test_head_200_exists():
    fetcher = FakeFetcher(200)
    assert check_llms_txt("https://x/llms.txt", fetcher).exists


def test_head_404_missing():
    assert not check_llms_txt("https://x/llms.txt", FakeFetcher(404)).exists


def test_head_405_falls_back_to_get():
    fetcher = FakeFetcher(405, 200)
    result = check_llms_txt("https://x/llms.txt", fetcher)
    assert result.exists and len(fetcher.calls) == 2


def test_head_501_failed_get_is_missing():
    assert not check_llms_txt("https://x/llms.txt", FakeFetcher(501, 404)).exists


def test_fetcher_without_head_uses_get():
    class GetOnly:
        def get(self, url):
            return FetchResponse(200, "ok")
    assert check_llms_txt("https://x/llms.txt", GetOnly()).exists

