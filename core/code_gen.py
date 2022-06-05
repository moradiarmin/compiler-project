from importlib import import_module
from re import S
from typing import List
from data_class.symbol_table import FuncAttribute
from enums.addressing import AddressType

from enums.command import Command
from data_class.addressing_mode import AddressingMode, Arg

from enums.semantic_action import Action
from modules.memory import Memory
from modules.symbol_table import SymbolTable

class CodeGenerator:

    def __init__(self) -> None:
        self.last_parsed_token: str = None

    def code_gen(self, action:Action) -> None:
        if action in [Action.ADD, Action.SUB, Action.MULT]:
            prev_action = action
            action = "#MATH"
        
        routines = import_module(f"utils.routines")
        func = getattr(routines, action[1:])

        if action in [Action.CALL, Action.CHG_SCOPE, Action.PID, Action.PNUM]:
            func(self.last_parsed_token)
        elif action == "#MATH":
            func(prev_action[1:])
        else:
            func()

    def fill_first_and_last(self):
        def _find_main_row():
            for row in SymbolTable().table:
                if row.lexeme == "main" and isinstance(row.attribute, FuncAttribute):
                    return row
        main = _find_main_row()

        p = Memory().prog_p

        # fill first program block row (jumping to main())
        Memory().set_new_command(
            AddressingMode(
                Command.JP,
                Arg(AddressType.NUM, p),
                None,
                None
            ),
            idx=Memory().start_prog_p
        )

        # fill last program block row (running main())
        Memory().set_new_command(
            AddressingMode(
                Command.JP,
                Arg(AddressType.NUM, main.attribute.start_addr_in_PB),
                None,
                None
            )
        )