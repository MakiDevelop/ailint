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
    error_msg = None
    if path is None:
        names = ", ".join(KNOWN_FILENAMES)
        error_msg = f"no config file found in current directory (looked for {names})"
    elif not path.exists():
        error_msg = f"file not found: {args.path}"
    elif not path.is_file():
        error_msg = f"not a file: {path}"

    if error_msg is None:
        try:
            raw_text = path.read_text(encoding="utf-8")  # type: ignore[union-attr]
        except (UnicodeDecodeError, OSError) as exc:
            error_msg = f"cannot read file: {exc}"

    if error_msg is not None:
        _print_error(error_msg, args.format)
        return 2
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


def _print_error(message: str, fmt: str) -> None:
    import json as _json
    if fmt == "json":
        print(_json.dumps({"error": message}, ensure_ascii=False))
    elif fmt == "github":
        print(f"::error ::{message}")
    else:
        print(f"ailint: {message}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
