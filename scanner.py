class Token:
    def __init__(self, type, lexeme):
        self.type = type
        self.lexeme = lexeme

class SymbolTable:
        def __init__(self):
            self.arr = []
        def add_symbol(token):
            pass

class Error:
        def __init__(self, line, text, type):
            self.line = line
            self.text = text
            self.type = type

from ctypes import pointer
from enum import Enum
from typing import List

class ErrorType(Enum):
    INVALID_INPUT = 1
    INVALID_NUMBER = 2
    UNCLOSED_COMMENT = 3
    UNMATCHED_COMMENT = 4


class Scanner:
    def __init__(self, input_address: str) -> None:
        self.input_file: str = open(input_address).read()
        self.current_line_num: int = 1
        self.pointer1: int = 0
        self.pointer2: int = 0

        self.tokens: List[Token] = list()
        self.symbol_table = SymbolTable()
        self.errors: List[Error] = list()

    def select_dfa(self):
        pass

    def _get_next_token(self): # handle \n here
        first_char = self.input_file[self.pointer1]
        dfa = self.select_dfa(first_char)
        output = dfa(self.pointer1, self.input_file) # also decides pointer2, and errors
        return output


    def scan(self):                
        while self.pointer1 < len(self.input_file):
            token, error, is_token_finished = self.get_next_token() # ISSUE: is is_token finished needed?
            if is_token_finished:
                self.pointer1 = self.pointer2

def whitespace_dfa():
    pass
def ID_dfa():
    pass
def symbol_dfa():
    pass
# complete each of these functions...