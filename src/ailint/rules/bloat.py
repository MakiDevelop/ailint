from __future__ import annotations

from ailint.parser import flatten_sections, Section
from ailint.rules import Diagnostic, Rule


class BloatRule(Rule):
    id = "R001"
    name = "bloat"
    description = "Detect oversized config files and sections."

    def check(self, sections: list[Section], raw_text: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        total_lines = len(raw_text.splitlines())

        if total_lines > 1000:
            diagnostics.append(
                Diagnostic(
                    self.id,
                    "error",
                    1,
                    1,
                    f"File has {total_lines} lines; split or consolidate it below 1000 lines.",
                    "Move stable reference material into linked docs and keep agent instructions concise.",
                )
            )
        elif total_lines > 500:
            diagnostics.append(
                Diagnostic(
                    self.id,
                    self.default_severity,
                    1,
                    1,
                    f"File has {total_lines} lines; configs above 500 lines are hard for agents to follow.",
                    "Split long background material into separate referenced files.",
                )
            )

        for section in flatten_sections(sections):
            section_lines = section.line_end - section.line_start + 1
            if section_lines > 100:
                diagnostics.append(
                    Diagnostic(
                        self.id,
                        self.default_severity,
                        section.line_start,
                        1,
                        f"Section '{section.heading}' has {section_lines} lines; sections above 100 lines are hard to scan.",
                        "Break the section into focused subsections or remove repeated guidance.",
                    )
                )

        return diagnostics
