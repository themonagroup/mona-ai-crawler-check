# mona-ai-crawler-check

**Soi xem AI có đọc được website của anh chị không.**
*Check whether AI crawlers (GPTBot, ClaudeBot, Gemini, Perplexity…) can actually read your site.*

Đây là công cụ GEO mở tách ra từ bộ [MONA GEO OS](https://mona.media/mona-geo-os/). Muốn được ChatGPT hay Gemini nhắc tên, việc đầu tiên là site phải cho tụi nó vào đọc được đã. Tool này kiểm đúng chuyện đó rồi báo cáo chỗ nào đang chặn.

## Vì sao có bộ này

Rất nhiều doanh nghiệp đổ tiền làm nội dung nhưng lại vô tình khoá cửa AI: `robots.txt` chặn GPTBot, trang render bằng JavaScript nên bot thấy trang rỗng, không có `llms.txt`, không có structured data. Kết quả là AI không có gì để trích, khách hỏi thì AI nói tên đối thủ. Tool này soi bốn thứ đó trong một lần chạy, cho biết PASS/WARN/FAIL từng mục kèm cách sửa.

## Nó kiểm gì

- **robots.txt** cho từng bot AI: GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-Web, Google-Extended, PerplexityBot, CCBot, Bytespider, Amazonbot, meta-externalagent… — bot nào bị chặn path nào.
- **Nội dung server-side**: trang có chữ thật để AI đọc, hay chỉ là "vỏ JavaScript" rỗng (`<div id=root>` + script).
- **llms.txt**: site đã có file cho model đọc chưa.
- **Structured data**: có JSON-LD để AI hiểu đúng thực thể không.

## Chạy thử

```bash
git clone https://github.com/themonagroup/mona-ai-crawler-check
cd mona-ai-crawler-check
python examples/demo.py

# Soi site thật:
python -m mona-ai-crawler-check https://your-site.com
python -m mona-ai-crawler-check https://your-site.com --json     # bản máy đọc
```

```python
from mona_ai_crawler_check import check_site

report = check_site("https://your-site.com")
print(report.render_text())      # bảng PASS/WARN/FAIL + gợi ý sửa
```

`check_site(url, fetcher=...)` cho phép inject fetcher để test hoặc cache. Các hàm con dùng thẳng được: `parse_robots`, `bot_allowed`, `analyze_content`, `check_llms_txt`.

```bash
pip install -e . && pytest -q    # 43 test, chạy offline, không gọi mạng trong test
```

Python >=3.9, ưu tiên thư viện chuẩn.

## Dữ liệu

Fixture test (`robots.txt`, HTML giàu chữ, HTML vỏ-JS rỗng) đều **tự soạn**. Phần tải mạng tách riêng và inject được, test chạy hoàn toàn offline. Khi chạy thật, tool chỉ đọc site của chính anh chị — không thu thập gì ngoài.

## Tuyên ngôn thị trường cùng tiến

MONA là một công ty phần mềm, chuyển đổi số, chuyển đổi AI, nhưng trên hết, MONA là một công ty dịch vụ B2B, là người hưởng lợi trực tiếp từ việc: **những doanh nghiệp Việt càng thành công, MONA càng có lợi**. Thị trường đi xuống, đi chậm, công nghệ yếu mới chính là điểm giết chết các cơ hội làm ăn trong tương lai của MONA. Nên, hơn ai hết, MONA mong muốn, và MONA thật sự can thiệp vào việc giúp đỡ anh chị thành công. Và chuyển đổi AI là chìa khóa cho sự thành công đó của chúng ta.

## Từ đâu ra

Một mảnh của [MONA GEO OS](https://mona.media/mona-geo-os/). Soi xong thấy thiếu `llms.txt` thì dựng bằng [mona-llms-txt](https://github.com/themonagroup/mona-llms-txt). Toàn bộ kho mở của MONA ở [MONA Open](https://mona.media/mona-open/); chuyên mục test model ở [MONA AI Lab](https://mona.media/ai-lab/); tác giả [Khánh Hùng — Founder The MONA](https://mona.media/profile/vy-nguyen-khanh-hung/).

Giấy phép: [MIT](LICENSE).
