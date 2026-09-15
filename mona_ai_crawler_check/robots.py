"""Small, deterministic robots.txt parser implementing RFC-style matching."""

from dataclasses import dataclass
import re
from typing import Iterable, List, Optional, Tuple
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Rule:
    directive: str
    pattern: str


@dataclass(frozen=True)
class Group:
    user_agents: Tuple[str, ...]
    rules: Tuple[Rule, ...]


@dataclass(frozen=True)
class RobotsRules:
    groups: Tuple[Group, ...]


def parse_robots(txt: str) -> RobotsRules:
    """Parse relevant user-agent/allow/disallow records into immutable groups."""
    groups: List[Group] = []
    agents: List[str] = []
    rules: List[Rule] = []
    seen_rule = False

    def flush() -> None:
        nonlocal agents, rules, seen_rule
        if agents:
            groups.append(Group(tuple(agents), tuple(rules)))
        agents, rules, seen_rule = [], [], False

    for raw_line in txt.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = (part.strip() for part in line.split(":", 1))
        key = key.lower()
        if key == "user-agent":
            if seen_rule:
                flush()
            if value:
                agents.append(value.lower())
        elif key in ("allow", "disallow") and agents:
            seen_rule = True
            # Disallow rỗng có nghĩa là không chặn, nên không tạo rule.
            if value:
                rules.append(Rule(key, value))
    flush()
    return RobotsRules(tuple(groups))


def _selected_rules(parsed: RobotsRules, ua: str) -> Iterable[Rule]:
    ua_lower = ua.lower()
    matches = []
    best = -1
    for group in parsed.groups:
        lengths = [len(token) if token != "*" else 0
                   for token in group.user_agents
                   if token == "*" or token in ua_lower]
        if not lengths:
            continue
        specificity = max(lengths)
        if specificity > best:
            matches, best = [group], specificity
        elif specificity == best:
            matches.append(group)
    for group in matches:
        yield from group.rules


def _rule_regex(pattern: str) -> re.Pattern[str]:
    anchored = pattern.endswith("$")
    if anchored:
        pattern = pattern[:-1]
    expression = re.escape(pattern).replace(r"\*", ".*")
    return re.compile("^" + expression + ("$" if anchored else ""))


def bot_allowed(rules: RobotsRules, ua: str, path: str) -> bool:
    """Return access decision; longest matching rule wins and Allow wins ties."""
    if not path:
        path = "/"
    if "://" in path:
        parsed_url = urlsplit(path)
        path = parsed_url.path or "/"
        if parsed_url.query:
            path += "?" + parsed_url.query
    winning: Optional[Tuple[int, bool]] = None
    for rule in _selected_rules(rules, ua):
        if _rule_regex(rule.pattern).search(path):
            # Độ dài pattern (không tính wildcard/$) quyết định độ đặc hiệu.
            specificity = len(rule.pattern.replace("*", "").rstrip("$"))
            allowed = rule.directive == "allow"
            candidate = (specificity, allowed)
            if winning is None or candidate > winning:
                winning = candidate
    return True if winning is None else winning[1]
