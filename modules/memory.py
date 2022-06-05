from typing import List, Optional, Union
from enums.addressing import AddressType
from data_class.addressing_mode import AddressingMode, Arg
from enums.command import Command

from utils.patterns.singleton import Singleton


class Memory(metaclass=Singleton):
    """ Runtime memory """

    def __init__(self, unit: int=4, prog_size: int = 100, data_size: int = 400, capacity=1000) -> None:
        
        self.start_prog_p: int = 0
        self._start_data_p: int = prog_size
        self.start_tmp_p: int = prog_size + data_size
        self._capacity: int = capacity
        self.unit: int = unit
        self.pow_idx: int = None
        self.prog_p: int = self.start_prog_p + self.unit
        r""" program block pointer (NOTE: first one is reserved for jumping into `main()`) """

        self.data_p: int = self._start_data_p
        """ data block pointer """
        
        self._tmp_p: int = self.start_tmp_p
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
        if addressing.command == Command.JP and addressing.first.type == AddressType.NUM:
            addressing.first.type = AddressType.DIRECT
        elif addressing.command == Command.JPF and addressing.second.type == AddressType.NUM:
            addressing.second.type = AddressType.DIRECT
        if idx is not None:
            self._space[idx] = addressing.three_mode
        else:
            self._space[self.prog_p] = addressing.three_mode
            self.prog_p += self.unit

    def get_new_data_addr(self) -> int:
        p = self.data_p
        self.data_p += self.unit
        return p

    def get_new_tmp(self) -> int:
        p = self._tmp_p
        self._tmp_p += self.unit
        return p