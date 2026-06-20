from __future__ import annotations

from pathlib import Path
import re
import shutil
import subprocess

from ailint.rules import Diagnostic


LINE_RE = re.compile(r"(?:line|行)\s*(\d+)", re.IGNORECASE)


def run_deep_analysis(path: str | Path, raw_text: str) -> list[Diagnostic]:
    claude = shutil.which("claude")
    if claude is None:
        raise RuntimeError(
            "claude CLI not found. Install Claude Code or remove --deep to run stdlib-only checks."
        )

    prompt = (
        "Analyze this AI agent config for semantic contradictions. "
        "Return one issue per line in this format: line: message. "
        "Only report likely contradictions.\n\n"
        f"File: {path}\n\n{raw_text}"
    )
    result = subprocess.run(
        [claude, "-p", prompt],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown error"
        raise RuntimeError(f"claude CLI failed: {detail}")

    return _parse_claude_response(result.stdout)


def _parse_claude_response(response: str) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for raw_line in response.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        line_no = 1
        message = line
        prefix = re.match(r"^(\d+)\s*:\s*(.+)$", line)
        if prefix:
            line_no = int(prefix.group(1))
            message = prefix.group(2).strip()
        else:
            match = LINE_RE.search(line)
            if match:
                line_no = int(match.group(1))

        diagnostics.append(
            Diagnostic(
                "R005-deep",
                "warning",
                line_no,
                1,
                message,
                "Resolve the semantic conflict or document the exact precedence rule.",
            )
        )

    return diagnostics
