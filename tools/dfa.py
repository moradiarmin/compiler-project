from abc import abstractmethod
from typing import Dict, List, Optional

FINAL_STATE = -1
UNKNOWN = -2

class DFA:
    """a general DFA class to define its policy"""
    
    state: int = 0
    """ current state of the DFA"""

    lookahead: bool = False
    """whether lookahead occured or not"""

    def reset(cls):
        """reset DFA to initial state"""
        cls.state = 0
        cls.lookahead = False
        
    @abstractmethod
    @classmethod
    def move(cls, action: str) -> Optional[int]:
        """move within DFA and return next state"""


class NumberDFA(DFA):

    def move(cls, action: str):
        state = cls.state
        next_state: int = UNKNOWN

        if state == 0 and action.isdigit():
            next_state = 1

        elif state == 1:
            if action.isdigit():
                next_state = 1
            elif action == ".":
                next_state = 2
            elif not action.isalpha() and not action in ["!", "$"]:
                cls.lookahead = True
                next_state = FINAL_STATE
        
        elif state == 2 and action.isdigit():
            next_state = 3
        
        elif state == 3:
            if action.isdigit():
                next_state = 3
            elif not action.isalpha() and not action in ["!", "$"]:
                cls.lookahead = True
                next_state = FINAL_STATE
        
        if next_state == UNKNOWN:
            cls.lookahead = True

        cls.state = next_state
        return next_state

                