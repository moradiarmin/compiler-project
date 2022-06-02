from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from enums.token_type import TokenType


@dataclass
class Token:
    line: int
    lexeme: str
    type: 'TokenType'

    @property
    def all_in_one(self):
        return f"({self.type}, {self.lexeme})"