from __future__ import annotations

import argparse
import json
from pathlib import Path

from .adapters import get_adapter
from .runner import run_suite
from .schema import load_suite


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="continuitybench")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="Run a ContinuityBench suite")
    run.add_argument("--suite", required=True, help="Path to a JSON benchmark suite")
    run.add_argument("--adapter", default="mock", help="Model adapter name")
    run.add_argument("--out", help="Optional output JSON path")
    run.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        suite = load_suite(Path(args.suite))
        adapter = get_adapter(args.adapter)
        report = run_suite(suite, adapter)
        indent = 2 if args.pretty or not args.out else None
        payload = json.dumps(report.to_dict(), indent=indent)

        if args.out:
            out_path = Path(args.out)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(payload + "\n", encoding="utf-8")
        else:
            print(payload)

    return 0
