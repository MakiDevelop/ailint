from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import re

from ailint.rules import Diagnostic


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
COLORS = {
    "error": "\x1b[31m",
    "warning": "\x1b[33m",
    "info": "\x1b[36m",
}
RESET = "\x1b[0m"


def format_diagnostics(
    diagnostics: list[Diagnostic],
    path: str | Path,
    output_format: str = "text",
    no_color: bool = False,
) -> str:
    path_text = str(path)

    if output_format == "json":
        return json.dumps([asdict(diagnostic) for diagnostic in diagnostics], ensure_ascii=False, indent=2)

    if output_format == "github":
        return _format_github(diagnostics, path_text)

    output = _format_text(diagnostics, path_text, no_color=no_color)
    if no_color:
        output = strip_ansi(output)
    return output


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def _format_text(diagnostics: list[Diagnostic], path: str, no_color: bool) -> str:
    lines = []
    for diagnostic in diagnostics:
        severity = diagnostic.severity
        if no_color:
            severity_text = severity
        else:
            severity_text = f"{COLORS.get(severity, '')}{severity}{RESET}"
        lines.append(
            (
                f"{path}:{diagnostic.line}:{diagnostic.column} "
                f"{severity_text} [{diagnostic.rule_id}] {diagnostic.message}"
            )
        )
        if diagnostic.suggestion:
            lines.append(f"  suggestion: {diagnostic.suggestion}")

    lines.append(_summary(diagnostics, no_color=no_color))
    return "\n".join(lines)


def _format_github(diagnostics: list[Diagnostic], path: str) -> str:
    lines = []
    for diagnostic in diagnostics:
        level = "error" if diagnostic.severity == "error" else "warning"
        message = f"[{diagnostic.rule_id}] {diagnostic.message}"
        lines.append(f"::{level} file={path},line={diagnostic.line},col={diagnostic.column}::{message}")
    lines.append(_summary(diagnostics, no_color=True))
    return "\n".join(lines)


def _summary(diagnostics: list[Diagnostic], no_color: bool) -> str:
    if len(diagnostics) == 0:
        return "✔ No problems found"
    errors = sum(1 for diagnostic in diagnostics if diagnostic.severity == "error")
    warnings = sum(1 for diagnostic in diagnostics if diagnostic.severity == "warning")
    def _pl(n: int, word: str) -> str:
        return f"{n} {word}" if n == 1 else f"{n} {word}s"
    total = len(diagnostics)
    text = f"✖ {_pl(total, 'problem')} ({_pl(errors, 'error')}, {_pl(warnings, 'warning')})"
    if no_color or errors == 0:
        return text
    return f"{COLORS['error']}{text}{RESET}"
