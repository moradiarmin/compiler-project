from dataclasses import dataclass
from typing import Optional

from enums.addressing import AddressType
from enums.command import Command

@dataclass
class Arg:
    type: AddressType
    val: int

    @property
    def comb(self) -> str:
        return self.type + str(self.val)

@dataclass
class AddressingMode:
    command: Command
    first: Arg
    second: Optional[Arg]
    third: Optional[Arg]

    @property
    def three_mode(self) -> str:
        second_comb = "" if self.second is None else self.second.comb
        third_comb = "" if self.third is None else self.third.comb
        
        parts = [self.command, self.first.comb, second_comb, third_comb]
        joined = ", ".join(parts)
        return f"({joined})"