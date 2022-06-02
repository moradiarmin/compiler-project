from typing import List
from data_class.addressing_mode import Arg

from utils.patterns.singleton import Singleton


class Semantic(metaclass=Singleton):

    def __init__(self) -> None:
        self.stack: List[Arg] = None

    def __enter__(self) -> 'Semantic':
        self._create_empty_stack()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stack.clear()

    def _create_empty_stack(self) -> None:
        self.stack = List[Arg]()