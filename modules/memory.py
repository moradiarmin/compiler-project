from typing import List, Optional, Union
from enums.addressing import AddressType
from data_class.addressing_mode import AddressingMode, Arg

from utils.patterns.singleton import Singleton


class Memory(metaclass=Singleton):
    """ Runtime memory """

    def __init__(self, prog_size: int = 100, data_size: int = 400, capacity=1000) -> None:
        
        self._start_prog_p: int = 0
        self._start_data_p: int = prog_size
        self._start_tmp_p: int = prog_size + data_size
        self._capacity: int = capacity
        
        self.prog_p: int = self._start_prog_p
        """ program block pointer """

        self._data_p: int = self._start_data_p
        """ data block pointer """
        
        self._tmp_p: int = self._start_prog_p
        """ temporary block pointer """

        self._space: List[Union[str, int, None]] = None

    def __enter__(self) -> 'Memory':
        self._create_empty_space()
        return self
    
    def _create_empty_space(self) -> None:
        self._space = [None] * self._capacity

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._reset_space()
    
    def _reset_space(self):
        for i in range(self._capacity):
            self._space[i] = None

    def set_new_command(self, addressing: AddressingMode, idx: Optional[int] = None) -> None:
        if idx is not None:
            self._space[idx] = addressing.three_mode
        else:
            self._space[self.prog_p] = addressing.three_mode

    # def get_data(self, arg: Arg) -> int:
    #     if arg.type == AddressType.INDIRECT:
    #         idx = self._space[arg.val]
    #     elif arg.type == AddressType.DIRECT:
    #         idx = arg.val
            
    #     assert idx >= self._start_data_p and idx < self._start_tmp_p, \
    #         f"data block address ({idx}) is out of bound({self._start_data_p}, {self._start_tmp_p})"

    #     return self._space[idx]

    def get_new_data_addr(self) -> int:
        p = self._data_p
        self._data_p += 1
        return p

    # def get_tmp(self, arg: Arg) -> int:
    #     if arg.type == AddressType.INDIRECT:
    #         idx = self._space[arg.val]
    #     elif arg.type == AddressType.DIRECT:
    #         idx = arg.val
            
    #     assert idx >= self._start_tmp_p and idx < self._capacity, \
    #         f"temporary block address ({idx}) is out of bound({self._start_prog_p}, {self._capacity})"

    #     return self._space[idx]

    def get_new_tmp(self) -> int:
        p = self._tmp_p
        self._tmp_p += 1
        return p