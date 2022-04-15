import os
from typing import Callable, List, Optional, Tuple, Union
from xml.etree.ElementTree import Comment

from pygments import lex

from tools.dfa import *


class TokenType:
    NUMBER = "NUMBER"
    ID = "ID"
    KEYWORD = "KEYWORD"
    SYMBOL = "SYMBOL"
    COMMENT = "COMMENT" # seems ugly :)
    WHITESPACE = "WHITESPACE" # seems ugly :)

class Token:
    def __init__(self, line: int, lexeme: str, type: TokenType) -> None:
        self.line: int = line
        self.lexeme: str = lexeme
        self.type: TokenType = type

    @property
    def all_in_one(self):
        return f"({self.type}, {self.lexeme})"

class ErrorType:
    INVALID_INPUT = "Invalid input"
    INVALID_NUMBER = "Invalid number"
    UNCLOSED_COMMENT = "Unclosed comment"
    UNMATCHED_COMMENT = "Unmatched comment"

class Error:
    def __init__(self, line: int, lexeme: str, type: ErrorType) -> None:
        self.line: int = line
        self.lexeme: str = lexeme
        self.type: ErrorType = type

    @property
    def all_in_one(self):
        return f"({self.lexeme}, {self.type})"

class Scanner:
    """scanner module

    Args:
        input_dir (str): directory of the input code to be scanned
        save_dir (str): directory where scanner outputs are saved
    """
    def __init__(self, input_dir: str, save_dir: str) -> None:
        self._inp_file: str = open(input_dir).read() + " "
        self._save_dir: str = save_dir
        os.makedirs(self._save_dir, exist_ok=True)

        self._current_line_num: int = 1
        self._current_token_type: TokenType = None
        self._p1: int = 0
        self._p2: int = self._p1

        self._multiline_comment_start_line = None

        self._tokens: List[Token] = list()
        self._keywords = ["break", "continue", "def", "else","if", "return", "while"]
        self._symbol_table: List[Token] = [*self._keywords]
        self._errs: List[Error] = list()


    def _select_dfa(self) -> Optional[DFA]:
        """specifies suitable DFA for the current token based on its first character

        Args:
            first_char (str): first character of the current token
        """

        first_char = self._inp_file[self._p1]
        
        if first_char.isdigit():
            self._current_token_type = TokenType.NUMBER
            return NumberDFA
        
        elif first_char in WhitespaceDFA.whitespace_chars:
            self._current_token_type = TokenType.WHITESPACE
            return WhitespaceDFA

        elif first_char in SymbolDFA.chars:
            self._current_token_type = TokenType.SYMBOL
            return SymbolDFA
        
        elif first_char.isalpha():
            self._current_token_type = TokenType.ID # a final check on being a keyword while creating the lexeme
            return IDDFA
        
        elif first_char in CommentDFA.chars:
            self._current_token_type = TokenType.COMMENT
            return CommentDFA

        return None


    def _get_err_type(self, lexeme: str) -> ErrorType:
        """specifies type of the leximal error"""

        if self._current_token_type == TokenType.NUMBER:
            return ErrorType.INVALID_NUMBER        
        elif self._current_token_type == TokenType.COMMENT:
            return ErrorType.UNCLOSED_COMMENT
        elif lexeme == "*/":
            return ErrorType.UNMATCHED_COMMENT
        else:
            return ErrorType.INVALID_INPUT


    def _get_next_token(self) -> Union[Token, Error]:
        """extracts next existing token, O.W. finds its error"""

        dfa: Optional[DFA] = self._select_dfa()
        new_token: Optional[Token] = None
        new_err: Optional[Error] = None
        
        if dfa is not None:
            if dfa is CommentDFA:
                self._multiline_comment_start_line = self._current_line_num # exactly when each '/' character is seen
            dfa.reset()

            while self._p2 < len(self._inp_file):
                ch = self._inp_file[self._p2]
            
                # handle new line
                if ch=="\n":
                    self._current_line_num += 1
                    print('*****', self._inp_file[self._p1:self._p2])
                dfa.move(dfa, ch)
                if dfa.state in [FINAL_STATE, UNKNOWN]:
                    break
                self._p2 += 1

            if dfa.lookahead and dfa.state == FINAL_STATE:
                self._p2 -= 1
                if ch=="\n":
                    self._current_line_num -= 1

            # process new token
            if dfa.state == FINAL_STATE and self._current_token_type not in \
                    [TokenType.WHITESPACE, TokenType.COMMENT]:
                lexeme = self._inp_file[self._p1: self._p2 + 1]
                if lexeme in self._keywords:
                    self._current_token_type = TokenType.KEYWORD
                token_type = self._current_token_type
                new_token = Token(self._current_line_num, lexeme, token_type)
                if lexeme not in self._symbol_table and \
                        self._current_token_type in [TokenType.ID, TokenType.KEYWORD]:
                    print("TOKEN", self._current_line_num, lexeme)
                    self._symbol_table.append(lexeme)
                self._tokens.append(new_token)

        # process error caused by the lexeme
        if dfa is None or (dfa is not None and dfa.state == UNKNOWN) or \
                self._p2 == len(self._inp_file):

            if self._current_token_type == TokenType.COMMENT:
                # comment opened only by character '/'
                if dfa.state == UNKNOWN:
                    self._current_token_type = None
                    lexeme = self._inp_file[self._p1: self._p1 + 1]

                    if self._inp_file[self._p2] == "\n":
                        self._current_line_num -=1
                    #lookahead is not permitted
                    self._p2 -= 1
                    
                # comment opened by '/*' and not closed
                else:
                    lexeme = self._inp_file[self._p1: self._p1+10]
                    if self._p2 > self._p1 + 9:
                        lexeme += "..."
            else:
                lexeme = self._inp_file[self._p1: self._p2 + 1]

            err_type = self._get_err_type(lexeme)
            if not err_type == ErrorType.UNCLOSED_COMMENT:
                new_err = Error(self._current_line_num, lexeme, err_type)
                print('ERROR', self._current_line_num, lexeme)

            else:
                new_err = Error(self._multiline_comment_start_line, lexeme, err_type)

            self._errs.append(new_err)

        # update attributes for extracting the next token
        self._p2 += 1
        self._p1 = self._p2

        return new_token if new_token is not None else new_err

    
    def _save_tokens(self) -> None:
        """save tokens into a text file"""
        
        line_num = 1
        tokens_in_line: List[Token] = [f"{line_num}."]
        save_dir = os.path.join(self._save_dir, 'tokens.txt')
        
        with open(save_dir, 'w') as f:
            for token in self._tokens:
                if token.line > line_num:
                    line_num = token.line
                    if len(tokens_in_line) > 1:
                        f.write(" ".join(tokens_in_line))
                        f.write("\n")
                        
                    tokens_in_line.clear()
                    tokens_in_line.append(f"{line_num}.")
                
                tokens_in_line.append(token.all_in_one)

            f.write(" ".join(tokens_in_line))

    
    def _save_errs(self) -> None:
        """saves all errors found in a text file"""

        line_num = 1
        errs_in_line: List[Token] = [f"{line_num}."]
        save_dir = os.path.join(self._save_dir, 'lexical_errors.txt')
        
        with open(save_dir, 'w') as f:
            if len(self._errs) == 0:
                f.write("There is no lexical error.")
            else:
                for err in self._errs:
                    if err.line > line_num:
                        line_num = err.line
                        if len(errs_in_line) > 1:
                            f.write(" ".join(errs_in_line))
                            f.write("\n")
                        
                        errs_in_line.clear()
                        errs_in_line.append(f"{line_num}.")
                    
                    errs_in_line.append(err.all_in_one)

                f.write(" ".join(errs_in_line))

    
    def _save_symbol_table(self) -> None:
        """saves symbol table into a text file"""

        save_dir = os.path.join(self._save_dir, 'symbol_table.txt')
        with open(save_dir, 'w') as f:
            for ix, symbol in enumerate(self._symbol_table):
                f.write(f"{ix + 1}. {symbol}\n")

    def _save(self):
        """saves tokens, errors and the symbol table in separate text files"""

        self._save_tokens()
        self._save_errs()
        self._save_symbol_table()

    def scan(self):                
        """scans the whole input file to extract all tokens, errors and a single symbol table"""

        while self._p1 < len(self._inp_file):
            self._get_next_token()

        self._save()