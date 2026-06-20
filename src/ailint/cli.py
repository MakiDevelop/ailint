from __future__ import annotations

import argparse
from pathlib import Path
import sys

from ailint import __version__
from ailint.deep import run_deep_analysis
from ailint.formatter import format_diagnostics
from ailint.parser import parse
from ailint.rules import ALL_RULES, Diagnostic


KNOWN_FILENAMES = ["CLAUDE.md", "AGENTS.md", "GEMINI.md", ".cursorrules", ".windsurfrules"]
SEVERITY_RANK = {"info": 0, "warning": 1, "error": 2}


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    path = _resolve_path(args.path)
    if path is None or not path.exists():
        target = args.path or " / ".join(KNOWN_FILENAMES)
        print(f"ailint: file not found: {target}", file=sys.stderr)
        return 2

    raw_text = path.read_text(encoding="utf-8")
    sections = parse(raw_text)

    diagnostics: list[Diagnostic] = []
    for rule in ALL_RULES:
        setter = getattr(rule, "set_context_path", None)
        if callable(setter):
            setter(path)
        diagnostics.extend(rule.check(sections, raw_text))

    if args.deep:
        try:
            diagnostics.extend(run_deep_analysis(path, raw_text))
        except RuntimeError as exc:
            print(f"ailint: {exc}", file=sys.stderr)
            return 2

    diagnostics = _filter_by_severity(diagnostics, args.severity)
    diagnostics.sort(key=lambda diagnostic: (diagnostic.line, diagnostic.column, diagnostic.rule_id))

    output = format_diagnostics(diagnostics, path, args.format, no_color=args.no_color)
    if output:
        print(output)

    return 1 if any(diagnostic.severity == "error" for diagnostic in diagnostics) else 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ailint",
        description="Lint AI agent config markdown files for structural problems.",
    )
    parser.add_argument("path", nargs="?", help="Path to CLAUDE.md, AGENTS.md, GEMINI.md, .cursorrules, or .windsurfrules.")
    parser.add_argument("--deep", action="store_true", help="Use claude CLI for semantic contradiction analysis.")
    parser.add_argument(
        "--format",
        choices=["text", "json", "github"],
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--severity",
        choices=["info", "warning", "error"],
        default="info",
        help="Minimum severity to report.",
    )
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors in text output.")
    parser.add_argument("--version", action="version", version=f"ailint {__version__}")
    return parser


def _resolve_path(path_arg: str | None) -> Path | None:
    if path_arg:
        return Path(path_arg)

    cwd = Path.cwd()
    for filename in KNOWN_FILENAMES:
        candidate = cwd / filename
        if candidate.exists():
            return candidate
    return None


def _filter_by_severity(diagnostics: list[Diagnostic], minimum: str) -> list[Diagnostic]:
    threshold = SEVERITY_RANK[minimum]
    return [
        diagnostic
        for diagnostic in diagnostics
        if SEVERITY_RANK.get(diagnostic.severity, 0) >= threshold
    ]


if __name__ == "__main__":
    raise SystemExit(main())
