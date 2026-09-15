# BRIEF — build repo `mona-ai-crawler-check` (Python)

Bạn là kỹ sư. Dựng thư viện + CLI Python **chạy thật, có test pass** trong ĐÚNG thư mục hiện tại (`--cd`). KHÔNG hỏi lại. Xong in tóm tắt + kết quả `pytest`.

## Mục tiêu
`mona-ai-crawler-check` = công cụ **soi xem AI có đọc được website không**: kiểm robots.txt cho các bot AI, xem trang có nội dung server-side (không chỉ JS rỗng), có `llms.txt`, có structured data (JSON-LD) không → báo cáo cái gì đang chặn AI trích dẫn site. Công cụ GEO mở tách ra từ MONA GEO OS — hữu ích thật.

## Kiến trúc (stdlib ưu tiên; fetch tách riêng để test không cần mạng)
```
mona_ai_crawler_check/
  __init__.py       # export check_site(), Report
  robots.py         # parse robots.txt -> với mỗi AI bot: allowed/blocked path nào (logic match chuẩn robots)
  bots.py           # danh sách UA bot AI: GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-Web,
                    #  Google-Extended, PerplexityBot, CCBot, Bytespider, Amazonbot, meta-externalagent...
  content.py        # từ HTML: đếm text hiển thị vs tỉ lệ <script>, phát hiện "JS-only shell" (body rỗng text),
                    #  có JSON-LD? có <title>/<meta description>/<h1>? (html.parser stdlib)
  llmstxt.py        # có /llms.txt không (HEAD/GET)
  report.py         # gộp thành Report + render bảng text + JSON; mỗi mục có mức PASS/WARN/FAIL + gợi ý sửa
  fetch.py          # tải robots.txt / trang / llms.txt — CÔ LẬP, test dùng fixture, KHÔNG network
  cli.py            # `python -m mona_ai_crawler_check https://site.com [--json]`
tests/              # pytest >=24: robots (fixture: chặn GPTBot, mở ClaudeBot...), content (fixture html
                    #  giàu text vs shell rỗng), llmstxt có/không, report tổng hợp. KHÔNG network.
fixtures/           # robots.txt mẫu, html giàu text, html JS-shell rỗng, có/không JSON-LD
pyproject.toml      # python>=3.9; deps tối thiểu (urllib stdlib ưu tiên)
.gitignore
examples/demo.py
```

## API
- `check_site(url, *, fetcher=None) -> Report` — `fetcher` inject được để test (trả fixture). Report có: robots per-bot, content-crawlability, có llms.txt, có JSON-LD, danh sách vấn đề + fix.
- Hàm con pure test được: `parse_robots(txt)`, `bot_allowed(rules, ua, path)`, `analyze_content(html)`.

## Test khoá cứng
- robots.txt fixture chặn `User-agent: GPTBot / Disallow: /` nhưng cho ClaudeBot → report GPTBot=FAIL, ClaudeBot=PASS.
- Wildcard `User-agent: *` + `Disallow: /private` → bot AI bị chặn /private, được / .
- HTML fixture "JS-only shell" (body chỉ có `<div id=root></div>` + script) → content = FAIL (AI thấy trang rỗng).
- HTML giàu text + có JSON-LD → PASS.
- Không có llms.txt → WARN kèm gợi ý dùng mona-llms-txt.

## Ràng buộc
- ⛔️ KHÔNG lộ endpoint/key nội bộ, KHÔNG network trong test, KHÔNG dữ liệu khách thật.
- Comment tiếng Việt chỗ khó. README + LICENSE để Claude viết sau (placeholder 1 dòng).
- `pytest -q` PASS hết (>=24 test). In kết quả cuối.
