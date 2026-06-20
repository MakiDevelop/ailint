from __future__ import annotations

from pathlib import Path
import re

from ailint.parser import Section
from ailint.rules import Diagnostic, Rule


PATH_RE = re.compile(
    r"(?<![\w:/.-])("
    r"~/(?:[^\s`'\"<>),]+)|"
    r"\./(?:[^\s`'\"<>),]+)|"
    r"(?:[A-Za-z0-9_.-]+/)+(?:[A-Za-z0-9_.-]+\.[A-Za-z0-9]+)"
    r")"
)
URL_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://")


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
        seen: set[tuple[str, int]] = set()

        for line_no, line in enumerate(raw_text.splitlines(), start=1):
            for match in PATH_RE.finditer(line):
                raw_path = match.group(1).rstrip(".,;:")
                if URL_RE.match(raw_path) or raw_path.startswith(("http://", "https://")):
                    continue
                key = (raw_path, line_no)
                if key in seen:
                    continue
                seen.add(key)

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
