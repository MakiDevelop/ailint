from __future__ import annotations

import re

from ailint.parser import Section
from ailint.rules import Diagnostic, Rule


VAGUE_RE = re.compile(
    r"盡量|適當|儘可能|大概|try to|should try|as appropriate|when possible|if feasible|ideally",
    re.IGNORECASE,
)


class VagueLanguageRule(Rule):
    id = "R002"
    name = "vague-language"
    description = "Detect vague or unenforceable language."

    def check(self, sections: list[Section], raw_text: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        for line_no, line in enumerate(raw_text.splitlines(), start=1):
            for match in VAGUE_RE.finditer(line):
                text = match.group(0)
                diagnostics.append(
                    Diagnostic(
                        self.id,
                        self.default_severity,
                        line_no,
                        match.start() + 1,
                        f"Vague phrase '{text}' is hard to enforce.",
                        "Replace it with a concrete condition, threshold, or required action.",
                    )
                )

        return diagnostics
