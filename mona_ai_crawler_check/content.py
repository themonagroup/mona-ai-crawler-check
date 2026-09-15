"""HTML crawlability analysis using only the standard library."""

from dataclasses import dataclass
from html.parser import HTMLParser
import re
from typing import List


@dataclass(frozen=True)
class ContentAnalysis:
    visible_text: str
    text_length: int
    script_text_length: int
    script_ratio: float
    is_js_shell: bool
    has_json_ld: bool
    has_title: bool
    has_meta_description: bool
    has_h1: bool


class _PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hidden_depth = 0
        self.script_depth = 0
        self.h1_depth = 0
        self.text: List[str] = []
        self.script_text: List[str] = []
        self.has_json_ld = False
        self.has_title = False
        self.has_description = False
        self.has_h1 = False

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        values = {str(k).lower(): (v or "") for k, v in attrs}
        if tag in ("script", "style", "noscript", "template"):
            self.hidden_depth += 1
        if tag == "script":
            self.script_depth += 1
            if values.get("type", "").lower().split(";", 1)[0].strip() == "application/ld+json":
                self.has_json_ld = True
        elif tag == "title":
            self.has_title = True
        elif tag == "meta" and values.get("name", "").lower() == "description" and values.get("content", "").strip():
            self.has_description = True
        elif tag == "h1":
            self.h1_depth += 1

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "h1" and self.h1_depth:
            self.h1_depth -= 1
        if tag == "script" and self.script_depth:
            self.script_depth -= 1
        if tag in ("script", "style", "noscript", "template") and self.hidden_depth:
            self.hidden_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.script_depth:
            self.script_text.append(data)
        elif not self.hidden_depth:
            cleaned = " ".join(data.split())
            if cleaned:
                self.text.append(cleaned)
                if self.h1_depth:
                    self.has_h1 = True


def analyze_content(html: str) -> ContentAnalysis:
    parser = _PageParser()
    try:
        parser.feed(html or "")
        parser.close()
    except (AssertionError, ValueError):
        # HTML lỗi vẫn nên cho ra báo cáo thay vì làm cả lượt kiểm tra thất bại.
        pass
    visible = " ".join(parser.text)
    visible = re.sub(r"\s+", " ", visible).strip()
    script_length = len("".join(parser.script_text).strip())
    total = len(visible) + script_length
    ratio = script_length / total if total else 0.0
    # Dưới 80 ký tự thường chỉ là tên app/loading shell, chưa đủ nội dung trích dẫn.
    is_shell = len(visible) < 80 and (script_length > 0 or not visible)
    return ContentAnalysis(
        visible, len(visible), script_length, ratio, is_shell,
        parser.has_json_ld, parser.has_title, parser.has_description, parser.has_h1,
    )

