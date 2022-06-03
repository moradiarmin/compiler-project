from typing import List, Tuple, Dict

from core.scanner import TokenType
from data_class.node import Node
from data_class.symbol_table import Attribute, FuncAttribute, Row
from modules.semantic import Semantic
from utils.patterns.singleton import Singleton

        
class SymbolTable(metaclass=Singleton):
    
    def __init__(self, keywords: List[str]) -> None:
        self.keywords = keywords
        self.table: List[Row] = list()
        self.scope_boundary: Dict[int, Tuple[int, int]] = list()

    def __enter__(self) -> 'SymbolTable':
        self._put_keywords_in_table()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._reset()
        
    def _put_keywords_in_table(self) -> None:
        self.table = [Row(lexeme, TokenType.KEYWORD, Attribute(Semantic().scope_no, None)) 
                for lexeme in self.keywords]

    def _reset(self) -> None:
        self.table.clear()
        self.scope_boundary.clear()

    def find_row(self, lexeme: str, scope_no: int) -> Row:
        start, end = self.scope_boundary[scope_no]
        if end is None:
            end = len(self.table)

        for i in range(start, end):
            i = i + start
            if self.table[i].lexeme == lexeme:
                return self.table[i]

        return self.find_row(lexeme, Semantic().scope_tree[scope_no].father)

    def find_func_ret_val_jp_addr(self, scope_no: int):
        start, end = self.scope_boundary[scope_no]
        if end is None:
            end = len(self.table)

        for i in range(start, end):
            i = i + start
            if isinstance(self.table[i].attribute, FuncAttribute):
                row = self.table[i]
                return (row.attribute.ret_val_addr, row.attribute.jp_addr)
        