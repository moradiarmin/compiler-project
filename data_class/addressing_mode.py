from dataclasses import dataclass
from typing import Optional, TypeVar

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
        parts = [self.command, self.first.comb, self.second.comb, self.third.comb]
        return ", ".join(parts)