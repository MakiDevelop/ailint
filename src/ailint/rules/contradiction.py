from __future__ import annotations

import re

from ailint.parser import flatten_sections, Section
from ailint.rules import Diagnostic, Rule


CONTRADICTION_PAIRS = [
    (("直接做", "直接執行"), ("先問", "先確認", "等確認")),
    (("always",), ("never",)),
    (("must",), ("must not", "禁止")),
    (("自由", "自動"), ("需要確認", "需要批准")),
]
WORD_RE = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]+")


class ContradictionRule(Rule):
    id = "R005"
    name = "contradiction"
    description = "Detect likely contradictory instructions using keyword proximity."

    def check(self, sections: list[Section], raw_text: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        line_lookup = raw_text.splitlines()

        for section in flatten_sections(sections):
            for left_terms, right_terms in CONTRADICTION_PAIRS:
                left_hits = _find_terms(section.content, left_terms, section.line_start)
                right_hits = _find_terms(section.content, right_terms, section.line_start)
                if not left_hits or not right_hits:
                    continue

                for left_hit in left_hits:
                    for right_hit in right_hits:
                        if abs(left_hit.line - right_hit.line) > 20:
                            continue
                        if _same_topic(line_lookup, left_hit.line, right_hit.line):
                            diagnostics.append(
                                Diagnostic(
                                    self.id,
                                    self.default_severity,
                                    min(left_hit.line, right_hit.line),
                                    1,
                                    (
                                        f"Possible contradiction in section '{section.heading}': "
                                        f"'{left_hit.term}' at line {left_hit.line} conflicts with "
                                        f"'{right_hit.term}' at line {right_hit.line}."
                                    ),
                                    "Clarify the condition that decides whether action is automatic or requires confirmation.",
                                )
                            )
                            break
                    else:
                        continue
                    break

        return diagnostics


class _Hit:
    def __init__(self, term: str, line: int) -> None:
        self.term = term
        self.line = line


def _find_terms(text: str, terms: tuple[str, ...], base_line: int) -> list[_Hit]:
    hits: list[_Hit] = []
    for offset, line in enumerate(text.splitlines()):
        lowered = line.lower()
        for term in terms:
            if term.lower() in lowered:
                hits.append(_Hit(term, base_line + offset))
    return hits


def _same_topic(lines: list[str], left_line: int, right_line: int) -> bool:
    if left_line == right_line:
        return True

    left_tokens = _topic_tokens(lines[left_line - 1])
    right_tokens = _topic_tokens(lines[right_line - 1])
    if not left_tokens or not right_tokens:
        return abs(left_line - right_line) <= 3

    return bool(left_tokens & right_tokens) or abs(left_line - right_line) <= 3


def _topic_tokens(line: str) -> set[str]:
    stopwords = {
        "always",
        "never",
        "must",
        "not",
        "the",
        "and",
        "or",
        "to",
        "a",
        "an",
        "直接做",
        "直接執行",
        "先問",
        "先確認",
        "等確認",
        "禁止",
        "自由",
        "自動",
        "需要確認",
        "需要批准",
    }
    return {
        token.lower()
        for token in WORD_RE.findall(line)
        if len(token) > 1 and token.lower() not in stopwords
    }
