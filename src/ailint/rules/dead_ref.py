from __future__ import annotations

from pathlib import Path
import re

from ailint.parser import Section
from ailint.rules import Diagnostic, Rule


PATH_RE = re.compile(
    r"(?<![\w:/.-])("
    r"~/(?:[^\s`'\"<>),）」】]+)|"
    r"\./(?:[^\s`'\"<>),）」】]+)|"
    r"(?:[A-Za-z0-9_.-]+/)+(?:[A-Za-z0-9_.-]+\.[A-Za-z0-9]+)"
    r")"
)
URL_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://")

_VERSION_RE = re.compile(r"^[\d.]+/[\d.]+$")

_SKIP_PREFIXES = (
    "http://", "https://",
    "roles/",
    "schemas/",
)

_SKIP_PATTERNS = [
    re.compile(r"^[A-Za-z]+/[\d.]+"),  # Chrome/91.0, axios/0.21.4
    re.compile(r"^\d+\.\d+/\d+"),       # 1.1/1.2, 3.12/3.13
    re.compile(r".*\*"),                 # wildcard paths
]


class DeadReferenceRule(Rule):
    id = "R004"
    name = "dead-reference"
    description = "Detect references to missing local paths."
    default_severity = "error"

    def __init__(self) -> None:
        self.base_path = Path.cwd()

    def set_context_path(self, file_path: Path) -> None:
        self.base_path = file_path.expanduser().resolve().parent

    def check(self, sections: list[Section], raw_text: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        seen: set[str] = set()
        in_code_block = False

        for line_no, line in enumerate(raw_text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            for match in PATH_RE.finditer(line):
                raw_path = match.group(1).rstrip(".,;:）」】")
                if raw_path in seen:
                    continue

                if any(raw_path.startswith(p) for p in _SKIP_PREFIXES):
                    continue
                if URL_RE.match(raw_path):
                    continue
                if _VERSION_RE.match(raw_path):
                    continue
                if any(p.match(raw_path) for p in _SKIP_PATTERNS):
                    continue

                seen.add(raw_path)

                candidate = Path(raw_path).expanduser()
                if not candidate.is_absolute():
                    candidate = self.base_path / candidate

                if not candidate.exists():
                    diagnostics.append(
                        Diagnostic(
                            self.id,
                            self.default_severity,
                            line_no,
                            match.start(1) + 1,
                            f"Referenced path does not exist: {raw_path}",
                            "Fix the path, create the referenced file, or remove the stale reference.",
                        )
                    )

        return diagnostics
