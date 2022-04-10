from enum import Enum
from typing import Callable, List, Optional, Tuple

from .tools.dfa import *


class TokenType(Enum):
    NUMBER = "NUMBER"
    ID = "ID"
    KEYWORD = "KEYWORD"
    SYMBOL = "SYMBOL"
    COMMENT = "COMMENT" # seems ugly :)
    WHITESPACE = "WHITESPACE" # seems ugly :)

class Token:
    def __init__(self, type: TokenType, lexeme: str) -> None:
        self.type: TokenType = type
        self.lexeme: str = lexeme

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
class ErrorType(Enum):
    INVALID_INPUT = 1
    INVALID_NUMBER = 2
    UNCLOSED_COMMENT = 3
    UNMATCHED_COMMENT = 4

class Scanner:
    def __init__(self, input_address: str) -> None:
        self.input_file: str = open(input_address).read()
        self.current_line_num: int = 1
        self.current_token_type: TokenType = None
        self.pointer1: int = 0
        self.pointer2: int = self.pointer1

        self.tokens: List[Token] = list()
        self.symbol_table = SymbolTable()
        self.errors: List[Error] = list()


    def _select_dfa(self) -> Optional[DFA]:
        """specifies suitable DFA for the current token

        Args:
            first_char (str): first character of the current token
        """

        first_char = self.input_file[self.pointer1]
        
        if first_char.isdigit():
            self.current_token_type = TokenType.NUMBER
            return NumberDFA
        
        elif first_char in WhitespaceDFA.whitespace_chars:
            self.current_token_type = TokenType.WHITESPACE
            return WhitespaceDFA

        elif first_char in SymbolDFA.symbol_chars:
            self.current_token_type = TokenType.SYMBOL
            return SymbolDFA
        
        elif first_char.isalpha():
            self.current_token_type = TokenType.ID # a final check on being a keyword while creating the lexeme

        return None


    def _get_err_type(self, lexeme: str) -> ErrorType:
        """specifies type of the leximal error"""

        if self.current_token_type == TokenType.NUMBER:
            return ErrorType.INVALID_NUMBER        
        elif lexeme == "*/":
            return ErrorType.UNMATCHED_COMMENT
        elif self.current_token_type is None:
            return ErrorType.INVALID_INPUT


    def _get_next_token(self) -> Tuple[Optional[Token], Optional[Error]]:
        dfa: Optional[DFA] = self._select_dfa() # q: shouldnt select dfa have an input?
        new_token: Optional[Token] = None
        new_err: Optional[Error] = None
        
        if dfa is not None:   
            dfa.reset()

            while True:
                ch = self.input_file[self.pointer2]
            
                # handle new line
                if ch=="\n":
                    self.current_line_num += 1
            
                dfa.move(ch)
                if dfa.state in [FINAL_STATE, UNKNOWN]:
                    break
                self.pointer2 += 1

            if dfa.lookahead and dfa.state == FINAL_STATE:
                self.pointer2 -= 1

            # process new token
            if dfa.state == FINAL_STATE and self.current_token_type not in \
                    [TokenType.WHITESPACE, TokenType.COMMENT]:
                lexeme = self.input_file[self.pointer1: self.pointer2 + 1]
                if current_token_type == TokenType.ID and lexeme in KeywordDFA.keywords:
                    current_token_type = TokenType.KEYWORD
                token_type = self.current_token_type
                new_token = Token(token_type, lexeme)
                self.tokens.append(new_token)

        # process error lexeme
        if dfa is None or (dfa is not None and dfa.state == UNKNOWN):
            if self.current_token_type != TokenType.COMMENT:
                lexeme = self.input_file[self.pointer1: self.pointer2 + 1]
            else:
                # NOTE: handle error lexeme of comments (just the first 10 characters)
                pass
            err_type = self._get_err_type()
            new_err = Error(self.current_line_num, lexeme, err_type)
            self.errors.append(new_err)

        # update attributes for extracting the next token
        self.pointer2 += 1
        self.pointer1 = self.pointer2

        return new_token, new_err


    def scan(self):                
        while self.pointer1 < len(self.input_file):
            token, error, is_token_finished = self._get_next_token() # ISSUE: is is_token finished needed?
            if is_token_finished:
                self.pointer1 = self.pointer2

def whitespace_dfa():
    pass
def ID_dfa():
    pass
def symbol_dfa():
    pass
        
# complete each of these functions...