from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
import importlib
import pkgutil
from pathlib import Path
from typing import ClassVar

from ailint.parser import Section


@dataclass
class Diagnostic:
    rule_id: str
    severity: str
    line: int
    column: int
    message: str
    suggestion: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class Rule(ABC):
    id: ClassVar[str]
    name: ClassVar[str]
    description: ClassVar[str]
    default_severity: ClassVar[str] = "warning"

    @abstractmethod
    def check(self, sections: list[Section], raw_text: str) -> list[Diagnostic]:
        raise NotImplementedError


def _discover_rules() -> list[Rule]:
    package_path = Path(__file__).parent
    package_name = __name__

    for module_info in pkgutil.iter_modules([str(package_path)]):
        if module_info.name.startswith("_"):
            continue
        importlib.import_module(f"{package_name}.{module_info.name}")

    subclasses = sorted(Rule.__subclasses__(), key=lambda cls: cls.id)
    return [rule_class() for rule_class in subclasses]


ALL_RULES = _discover_rules()
