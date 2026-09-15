from mona_ai_crawler_check.content import analyze_content


def test_js_shell_fails_detection(fixture_text):
    assert analyze_content(fixture_text("js-shell.html")).is_js_shell


def test_rich_html_is_not_shell(fixture_text):
    assert not analyze_content(fixture_text("rich.html")).is_js_shell


def test_json_ld_detected(fixture_text):
    assert analyze_content(fixture_text("rich.html")).has_json_ld


def test_json_ld_type_is_case_insensitive():
    assert analyze_content('<script type="Application/LD+JSON">{}</script>').has_json_ld


def test_title_detected(fixture_text):
    assert analyze_content(fixture_text("rich.html")).has_title


def test_description_requires_content():
    assert not analyze_content('<meta name="description" content="">').has_meta_description


def test_description_detected(fixture_text):
    assert analyze_content(fixture_text("rich.html")).has_meta_description


def test_h1_requires_text():
    assert not analyze_content("<h1></h1>").has_h1


def test_h1_detected(fixture_text):
    assert analyze_content(fixture_text("rich.html")).has_h1


def test_script_not_counted_as_visible_text():
    result = analyze_content("<body>Hello<script>very long javascript source</script></body>")
    assert result.visible_text == "Hello"
    assert result.script_text_length > 0


def test_style_and_noscript_are_not_visible():
    result = analyze_content("<style>abc</style><noscript>fallback</noscript><p>Shown</p>")
    assert result.visible_text == "Shown"


def test_empty_html_is_shell():
    assert analyze_content("").is_js_shell

