from __future__ import annotations

import re

from ailint.parser import Section
from ailint.rules import Diagnostic, Rule


VAGUE_RE = re.compile(
    r"盡量|適當|儘可能|大概|酌情|視情況|原則上|基本上"
    r"|try to|should try|as appropriate|when possible|if feasible|ideally"
    r"|feel free to|use your judgm?ent|at your discretion",
    re.IGNORECASE,
)

_DEFINITION_CONTEXT_RE = re.compile(
    r"禁止|不要|不得|不可|forbidden|avoid|do not|don't|never use|never say",
    re.IGNORECASE,
)


class VagueLanguageRule(Rule):
    id = "R002"
    name = "vague-language"
    description = "Detect vague or unenforceable language."

    def check(self, sections: list[Section], raw_text: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        in_code_block = False

        for line_no, line in enumerate(raw_text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            if _DEFINITION_CONTEXT_RE.search(line):
                continue

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
