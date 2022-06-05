from typing import Dict, List
from data_class.addressing_mode import Arg
from data_class.node import Node

from utils.patterns.singleton import Singleton


class Semantic(metaclass=Singleton):

    def __init__(self) -> None:
        self.stack: List[Arg] = None
        self.stack_recorder: List[int] = list()
        self.current_scope: int = None
        self.scope_tree: Dict[int, Node] = None
        self.no_scopes: int = None

    def __enter__(self) -> 'Semantic':
        self._start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stack.clear()
        self.scope_tree.clear()
        self.no_scopes = None

    def _start(self) -> None:
        self.stack = list()
        self.no_scopes = 1
        self.current_scope: int = 0

        self.scope_tree = dict()
        root = Node(self.current_scope)
        self.scope_tree[self.current_scope] = root

    def create_new_scope(self):
        father = self.scope_tree[self.current_scope]
        node = Node(self.no_scopes, father)
        self.scope_tree[self.no_scopes] = node
        self.switch_scope(self.no_scopes)    
        self.no_scopes += 1

    def switch_scope(self, scope_no: int):
        self.current_scope = scope_no