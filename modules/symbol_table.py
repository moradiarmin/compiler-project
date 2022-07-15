from typing import List, Tuple, Dict, Optional, Union


from core.scanner import TokenType
from data_class.symbol_table import Attribute, FuncAttribute, ItmtAttribute, Row
from modules.semantic import Semantic
from utils.patterns.singleton import Singleton

        
class SymbolTable(metaclass=Singleton):
    
    def __init__(self, keywords: List[str]=list()) -> None:
        self.keywords = keywords
        self.table: List[Row] = list()
        self.scope_boundary: Dict[int, Tuple[int, int]] = dict()

    def __enter__(self) -> 'SymbolTable':
        self._put_keywords_in_table()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._reset()
        
    def _put_keywords_in_table(self) -> None:
        self.table = [Row(lexeme, TokenType.KEYWORD, Attribute(Semantic().current_scope, None)) 
                for lexeme in self.keywords]
        self.scope_boundary[Semantic().current_scope] = (0, None)
        

    def _reset(self) -> None:
        self.table.clear()
        self.scope_boundary.clear()

    def add_row(self, lexeme: str, token_type: TokenType) -> None:
        recursive = True
        if lexeme in self.keywords:
            recursive = False
        existed = self.find_row(lexeme, Semantic().current_scope, recursive=recursive)

        if existed is not None:
            if not isinstance(existed.attribute, FuncAttribute) and existed.attribute.scope_no == Semantic().current_scope:
                return

        SymbolTable().table.append(
            Row(lexeme, token_type, Attribute(Semantic().current_scope, None))
        )

    def find_row(self, lexeme: str, scope_no: int, force_mem_addr: bool = False, all: bool = False, recursive: bool=True) -> Optional[Row]:
        start, end = self.scope_boundary[scope_no]
        if end is None:
            end = len(self.table) - 1

        all_vals: List[Row] = []
        for i in range(end, start - 1, -1):
            if self.table[i].lexeme != lexeme or self.table[i].attribute.scope_no != scope_no:
                continue
            if force_mem_addr and self.table[i].attribute.mem_addr is None:
                continue

            row = self.table[i]
            if not all:
                return row
            all_vals.append(row)
        
        # not found
        if scope_no == 0:
            return None

        if recursive:
            return self.find_row(lexeme, Semantic().scope_tree[scope_no].father.scope_no, force_mem_addr)
        else:
            return None if not all else all_vals

    def find_func_scope(self, scope_no: int, lexeme: Optional[str]=None, all: bool = False) -> Union[Row, List[Row]]:
        start, end = self.scope_boundary[scope_no]
        if end is None:
            end = len(self.table) - 1
        all_funcs: List[Row] = list()
        for i in range(end, start - 1, -1):
            if isinstance(self.table[i].attribute, FuncAttribute):
                row = self.table[i]
                if lexeme is not None and row.lexeme != lexeme:
                    continue

                if not all:
                    return row
                all_funcs.append(row)

        if len(all_funcs) == 0:
            try:
                father_scope = Semantic().scope_tree[scope_no].father.scope_no
                return self.find_func_scope(father_scope, lexeme, all)
            except:
                return all_funcs
        else:
            return all_funcs