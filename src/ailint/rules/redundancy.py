from __future__ import annotations

from collections import Counter
from math import log, sqrt
import re

from ailint.parser import flatten_sections, Section
from ailint.rules import Diagnostic, Rule


TOKEN_RE = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]{2,}")
THRESHOLD = 0.7


class RedundancyRule(Rule):
    id = "R003"
    name = "redundancy"
    description = "Detect highly similar sections using TF-IDF cosine similarity."

    def check(self, sections: list[Section], raw_text: str) -> list[Diagnostic]:
        all_sections = [
            section for section in flatten_sections(sections) if _tokenize(section.content)
        ]
        if len(all_sections) < 2:
            return []

        token_counts = [Counter(_tokenize(section.content)) for section in all_sections]
        document_frequency: Counter[str] = Counter()
        for counts in token_counts:
            document_frequency.update(counts.keys())

        total_docs = len(token_counts)
        vectors = [
            {
                token: count * (log((1 + total_docs) / (1 + document_frequency[token])) + 1)
                for token, count in counts.items()
            }
            for counts in token_counts
        ]

        diagnostics: list[Diagnostic] = []
        for left_index in range(len(all_sections)):
            for right_index in range(left_index + 1, len(all_sections)):
                similarity = _cosine(vectors[left_index], vectors[right_index])
                if similarity > THRESHOLD:
                    left = all_sections[left_index]
                    right = all_sections[right_index]
                    diagnostics.append(
                        Diagnostic(
                            self.id,
                            self.default_severity,
                            right.line_start,
                            1,
                            (
                                f"Section '{right.heading}' overlaps with '{left.heading}' "
                                f"({similarity:.2f} similarity)."
                            ),
                            "Merge duplicate guidance or make each section cover a distinct responsibility.",
                        )
                    )

        return diagnostics


def _tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in TOKEN_RE.finditer(text)]


def _cosine(left: dict[str, float], right: dict[str, float]) -> float:
    shared = left.keys() & right.keys()
    numerator = sum(left[token] * right[token] for token in shared)
    left_norm = sqrt(sum(value * value for value in left.values()))
    right_norm = sqrt(sum(value * value for value in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)
