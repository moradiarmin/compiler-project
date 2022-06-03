from typing import Dict, List
from data_class.addressing_mode import Arg
from data_class.node import Node
from modules.symbol_table import SymbolTable

from utils.patterns.singleton import Singleton


class Semantic(metaclass=Singleton):

    def __init__(self) -> None:
        self.stack: List[Arg] = None
        self.scope_tree: Dict[int, Node] = None
        self.scope_no: int = None

    def __enter__(self) -> 'Semantic':
        self._start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stack.clear()
        self.scope_tree.clear()
        self.scope_no = None

    def _start(self) -> None:
        self.stack = List[Arg]()
        self.scope_no = 0

        self.scope_tree = Dict[str, Node]()
        root = Node(self.scope_no)
        self.scope_tree[self.scope_no] = root
        SymbolTable().scope_boundary[self.scope_no] = (0, None)

    def create_new_scope(self):
        father = self.scope_tree[self.scope_no]
        self.scope_no += 1
        node = Node(self.scope_no, father)
        self.scope_tree[self.scope_no] = node
        SymbolTable().scope_boundary[self.scope_no] = (0, None)