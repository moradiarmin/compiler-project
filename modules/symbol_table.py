from typing import List, Optional, Tuple

from core.scanner import TokenType
from data_class.symbol_table import Attribute, Row
from data_class.token import Token
from utils.patterns.singleton import Singleton

    
class SymbolTable(metaclass=Singleton):
    
    def __init__(self, keywords: List[str]) -> None:
        self.keywords = keywords
        self.table: List[Row] = list()
        self.scope_no: int = 0
        self.scope_boundary: List[Tuple[int, int]] = list()

    def __enter__(self) -> 'SymbolTable':
        self._put_keywords_in_table()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._reset()

    def _put_keywords_in_table(self) -> None:
        self.table = [Row(lexeme, TokenType.KEYWORD, Attribute(None)) 
                for lexeme in self.keywords]

    def _reset(self) -> None:
        self.table.clear()
        self.scope_boundary.clear()
        self.scope_no = None

    def set_scope_no(self, scope_no: int) -> None:
        self.scope_no = scope_no

    def find_row(self, lexeme: str) -> Row:
        start, end = self.scope_boundary[self.scope_no]

        for i in range(start, end + 1):
            if self.table[i].lexeme == lexeme:
                return self.table[i]
        