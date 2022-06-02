from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from enums.error import ScannerErrorType

@dataclass
class ScannerError:
    line: int
    lexeme: str
    type: 'ScannerErrorType'

    @property
    def all_in_one(self):
        return f"({self.lexeme}, {self.type})"
