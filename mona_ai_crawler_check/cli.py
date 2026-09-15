"""Command-line entry point."""

import argparse
import sys

from . import check_site
from .fetch import FetchError
from .report import Status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check whether AI crawlers can read a website")
    parser.add_argument("url", help="Website page URL")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = check_site(args.url)
    except (FetchError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(report.to_json() if args.json else report.render_text())
    return 1 if report.status == Status.FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())

