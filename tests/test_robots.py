import pytest

from mona_ai_crawler_check.robots import bot_allowed, parse_robots


def test_mixed_fixture_blocks_gptbot(fixture_text):
    rules = parse_robots(fixture_text("robots-mixed.txt"))
    assert not bot_allowed(rules, "GPTBot", "/")


def test_mixed_fixture_allows_claudebot(fixture_text):
    rules = parse_robots(fixture_text("robots-mixed.txt"))
    assert bot_allowed(rules, "ClaudeBot", "/")


def test_wildcard_blocks_private():
    rules = parse_robots("User-agent: *\nDisallow: /private")
    assert not bot_allowed(rules, "PerplexityBot", "/private/file")


def test_wildcard_allows_root():
    rules = parse_robots("User-agent: *\nDisallow: /private")
    assert bot_allowed(rules, "PerplexityBot", "/")


def test_specific_group_wins_over_wildcard():
    rules = parse_robots("User-agent: *\nDisallow: /\nUser-agent: GPTBot\nAllow: /")
    assert bot_allowed(rules, "GPTBot", "/article")


def test_longest_rule_wins():
    rules = parse_robots("User-agent: *\nDisallow: /docs\nAllow: /docs/public")
    assert bot_allowed(rules, "CCBot", "/docs/public/a")


def test_allow_wins_equal_length_tie():
    rules = parse_robots("User-agent: *\nDisallow: /a\nAllow: /a")
    assert bot_allowed(rules, "CCBot", "/a")


def test_dollar_anchors_end():
    rules = parse_robots("User-agent: *\nDisallow: /private$")
    assert not bot_allowed(rules, "CCBot", "/private")
    assert bot_allowed(rules, "CCBot", "/private/page")


def test_star_wildcard_matches():
    rules = parse_robots("User-agent: *\nDisallow: /*.pdf$")
    assert not bot_allowed(rules, "Amazonbot", "/files/a.pdf")


def test_empty_disallow_allows():
    assert bot_allowed(parse_robots("User-agent: *\nDisallow:"), "GPTBot", "/anything")


def test_comments_and_case_are_supported():
    rules = parse_robots("USER-AGENT: gptbot # bot\nDISALLOW: /secret # no")
    assert not bot_allowed(rules, "GPTBot", "/secret")


def test_consecutive_agents_share_rules():
    rules = parse_robots("User-agent: GPTBot\nUser-agent: CCBot\nDisallow: /x")
    assert not bot_allowed(rules, "GPTBot", "/x")
    assert not bot_allowed(rules, "CCBot", "/x")


def test_equal_specific_groups_are_combined():
    text = "User-agent: GPTBot\nDisallow: /x\nUser-agent: GPTBot\nDisallow: /y"
    rules = parse_robots(text)
    assert not bot_allowed(rules, "GPTBot", "/y")


def test_full_url_path_supported():
    rules = parse_robots("User-agent: *\nDisallow: /private")
    assert not bot_allowed(rules, "GPTBot", "https://example.test/private?a=1")


def test_no_matching_group_defaults_allow():
    rules = parse_robots("User-agent: OrdinaryBot\nDisallow: /")
    assert bot_allowed(rules, "GPTBot", "/")

