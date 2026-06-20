from __future__ import annotations

from dataclasses import dataclass, field
import re


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


@dataclass
class Section:
    heading: str
    level: int
    line_start: int
    line_end: int
    content: str
    children: list["Section"] = field(default_factory=list)


def parse(markdown: str) -> list[Section]:
    """Parse markdown headings into a nested section tree."""
    lines = markdown.splitlines()
    roots: list[Section] = []
    stack: list[Section] = []

    for index, line in enumerate(lines, start=1):
        match = HEADING_RE.match(line)
        if not match:
            continue

        level = len(match.group(1))
        heading = match.group(2).strip()

        while stack and stack[-1].level >= level:
            stack[-1].line_end = index - 1
            stack.pop()

        section = Section(
            heading=heading,
            level=level,
            line_start=index,
            line_end=len(lines),
            content="",
        )

        if stack:
            stack[-1].children.append(section)
        else:
            roots.append(section)

        stack.append(section)

    for section in stack:
        section.line_end = len(lines)

    for section in _walk_sections(roots):
        section.content = "\n".join(lines[section.line_start - 1 : section.line_end])

    return roots


def flatten_sections(sections: list[Section]) -> list[Section]:
    return list(_walk_sections(sections))


def _walk_sections(sections: list[Section]):
    for section in sections:
        yield section
        yield from _walk_sections(section.children)
