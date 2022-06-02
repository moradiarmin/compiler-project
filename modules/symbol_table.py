from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

from core.scanner import TokenType
from modules.token import Token
from utils.patterns.singleton import Singleton

    
@dataclass
class Attribute:
    scope_no: int

@dataclass
class FuncAttribute(Attribute):
    args_addr: Optional[List[int]]
    jp_addr: int

@dataclass
class Row:
    lexeme: Token
    type: TokenType  
    attribute: Union[Attribute, FuncAttribute]      

class SymbolTable(metaclass=Singleton):
    
    def __init__(self, keywords: List[str]) -> None:
        self.keywords = keywords
        self.table: List[Row] = list()
        self._scope_no: int = None
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
        self._scope_no = None

    def set_scope_no(self, scope_no: int) -> None:
        self._scope_no = scope_no