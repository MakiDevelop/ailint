from __future__ import annotations

from pathlib import Path
import re
import shutil
import subprocess

from ailint.rules import Diagnostic


PROMPT_TEMPLATE = """You are a strict config file auditor. Analyze this AI agent configuration for semantic contradictions — rules that conflict with each other in meaning.

RULES:
1. Only report genuine logical contradictions, not stylistic differences.
2. Each contradiction must reference specific line numbers from the file.
3. Output ONLY in this exact format, one per line:

CONTRADICTION:<line_a>:<line_b>:<one-sentence description>

4. If no contradictions exist, output exactly: NONE
5. Do NOT output any other text, explanation, or preamble.

File content (with line numbers):
---
{content}
---"""


def run_deep_analysis(path: str | Path, raw_text: str) -> list[Diagnostic]:
    claude = shutil.which("claude")
    if claude is None:
        raise RuntimeError(
            "claude CLI not found. Install Claude Code or remove --deep to run stdlib-only checks."
        )

    numbered = "\n".join(f"{i}: {line}" for i, line in enumerate(raw_text.splitlines(), 1))
    prompt = PROMPT_TEMPLATE.format(content=numbered)

    result = subprocess.run(
        [claude, "-p", prompt],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=120,
    )

    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown error"
        raise RuntimeError(f"claude CLI failed: {detail}")

    return _parse_response(result.stdout)


_CONTRA_RE = re.compile(r"^CONTRADICTION:(\d+):(\d+):(.+)$")


def _parse_response(response: str) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []

    for line in response.strip().splitlines():
        line = line.strip()
        if line == "NONE" or not line:
            continue

        m = _CONTRA_RE.match(line)
        if not m:
            continue

        line_a = int(m.group(1))
        line_b = int(m.group(2))
        desc = m.group(3).strip()

        diagnostics.append(
            Diagnostic(
                "R005-deep",
                "warning",
                min(line_a, line_b),
                1,
                f"Semantic contradiction (lines {line_a} vs {line_b}): {desc}",
                "Resolve the conflict or document the exact precedence rule.",
            )
        )

    return diagnostics
