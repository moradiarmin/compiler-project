from .scanner import Token
from typing import Callable, List, Dict, Optional, Tuple, Union


class NonTerminal:
    S = 'S'
    # ...

class Terminal:
    virgool = ';'

class RHS:
    pass


class Parser:

    def __init__(self, get_next_token: Callable[[], Token]) -> None:
        self._parse_table: Dict[Tuple[NonTerminal, Terminal], Optional[RHS]] = dict()
        self.call_scanner = get_next_token
        self.stack: List[Union[NonTerminal, Terminal]] = ['S$']
        self._errs: List[str] = list()
        pass

    def parse(self): 
        # TODO: creating parse tree
        # TODO: creating parse table
        token = self.call_scanner()
        lineno = token.line
        exp = self.stack[0]

        if isinstance(exp, Terminal):
            self.stack.pop(0)
            if exp != token:
                self._errs(f'lineno {lineno}: syntax error; missing {token}')

        else:
            cell = self._parse_table[exp, token]
            if cell != 'null' and cell != 'sync':
                self.stack.pop(0)
                self.stack = list(cell) + self.stack
            elif cell == 'sync':
                self.stack.pop(0)
                self._errs(f'lineno {lineno}: syntaxt error; missing {exp}')
            else:
                self._errs(f'lineno {lineno}: syntaxt error; illegal {token}')

