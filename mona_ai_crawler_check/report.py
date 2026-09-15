"""Report value objects and renderers."""

from dataclasses import asdict, dataclass
from enum import Enum
import json
from typing import Any, Dict, List, Mapping


class Status(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


@dataclass(frozen=True)
class Check:
    name: str
    status: Status
    detail: str
    fix: str = ""


@dataclass
class Report:
    url: str
    robots: Mapping[str, Check]
    content: Check
    llms_txt: Check
    json_ld: Check
    metadata: Mapping[str, bool]

    @property
    def checks(self) -> List[Check]:
        return list(self.robots.values()) + [self.content, self.llms_txt, self.json_ld]

    @property
    def issues(self) -> List[Check]:
        return [check for check in self.checks if check.status != Status.PASS]

    @property
    def status(self) -> Status:
        statuses = {check.status for check in self.checks}
        return Status.FAIL if Status.FAIL in statuses else Status.WARN if Status.WARN in statuses else Status.PASS

    def to_dict(self) -> Dict[str, Any]:
        def item(check: Check) -> Dict[str, str]:
            data = asdict(check)
            data["status"] = check.status.value
            return data
        return {
            "url": self.url,
            "status": self.status.value,
            "robots": {bot: item(check) for bot, check in self.robots.items()},
            "content": item(self.content),
            "llms_txt": item(self.llms_txt),
            "json_ld": item(self.json_ld),
            "metadata": dict(self.metadata),
            "issues": [item(check) for check in self.issues],
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def render_text(self) -> str:
        rows = [("Overall", self.status.value, self.url)]
        rows += [(f"robots: {bot}", check.status.value, check.detail) for bot, check in self.robots.items()]
        rows += [("Server content", self.content.status.value, self.content.detail),
                 ("llms.txt", self.llms_txt.status.value, self.llms_txt.detail),
                 ("JSON-LD", self.json_ld.status.value, self.json_ld.detail)]
        widths = [max(len(row[i]) for row in rows + [("CHECK", "STATUS", "DETAIL")]) for i in range(3)]
        line = "+" + "+".join("-" * (width + 2) for width in widths) + "+"
        output = [line, f"| {'CHECK':<{widths[0]}} | {'STATUS':<{widths[1]}} | {'DETAIL':<{widths[2]}} |", line]
        output.extend(f"| {a:<{widths[0]}} | {b:<{widths[1]}} | {c:<{widths[2]}} |" for a, b, c in rows)
        output.append(line)
        if self.issues:
            output.append("Fixes:")
            output.extend(f"- {check.name}: {check.fix}" for check in self.issues if check.fix)
        return "\n".join(output)

