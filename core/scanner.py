from typing import List, Optional, Tuple
from enums.error import ScannerErrorType as SEType

from enums.token_type import TokenType
from data_class.error import ScannerError as SError
from data_class.token import Token
from modules.semantic import Semantic
from modules.symbol_table import Attribute, Row, SymbolTable
from modules.dfa import *
from utils.constants import EOF

class Scanner:
    """scanner module

    Args:
        input_dir (str): directory of the input code to be scanned
        save_dir (str): directory where scanner outputs are saved
    """
    def __init__(self, input_dir: str, save_dir: str) -> None:
        self._inp_file: str = "def output(x):\n\tprint(x);\n\treturn 0;\n;\n\n" + open(input_dir).read() + " "
        self._save_dir: str = save_dir

        self._current_line_num: int = 1
        self._current_token_type: TokenType = None
        self._p1: int = 0
        self._p2: int = self._p1

        self._multiline_comment_start_line = None

        self._tokens: List[Token] = list()
        self._errs: List[SError] = list()


    def _select_dfa(self):
        """specifies suitable DFA for the current token based on its first character

        Args:
            first_char (str): first character of the current token
        """
        self._current_token_type = None
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


    def _get_err_type(self, lexeme: str) -> SEType:
        """specifies type of the leximal error"""

        if self._current_token_type == TokenType.NUMBER:
            return SEType.INVALID_NUMBER        
        elif self._current_token_type == TokenType.COMMENT:
            return SEType.UNCLOSED_COMMENT
        elif lexeme == "*/":
            return SEType.UNMATCHED_COMMENT
        else:
            return SEType.INVALID_INPUT


    def _get_next_token(self):
        """extracts next existing token, O.W. finds its error"""

        dfa: Optional[DFA] = self._select_dfa()
        new_token: Optional[Token] = None
        new_err: Optional[SError] = None
        
        if dfa is not None:
            if dfa is CommentDFA:
                self._multiline_comment_start_line = self._current_line_num # exactly when each '/' character is seen
            dfa.reset(dfa)

            while self._p2 < len(self._inp_file):
                ch = self._inp_file[self._p2]
            
                # handle new line
                if ch=="\n":
                    self._current_line_num += 1
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
                
                if lexeme in SymbolTable().keywords:
                    self._current_token_type = TokenType.KEYWORD
                
                token_type = self._current_token_type
                new_token = Token(self._current_line_num, lexeme, token_type)

                if self._current_token_type in [TokenType.ID, TokenType.KEYWORD, TokenType.KEYWORD]:
                    SymbolTable().add_row(lexeme, self._current_token_type)
                
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
            if not err_type == SEType.UNCLOSED_COMMENT:
                new_err = SError(self._current_line_num, lexeme, err_type)

            else:
                new_err = SError(self._multiline_comment_start_line, lexeme, err_type)

            self._errs.append(new_err)

        # update attributes for extracting the next token
        self._p2 += 1
        self._p1 = self._p2

        return new_token

    
    def _save_tokens(self) -> None:
        """save tokens into a text file"""
        
        line_num = 1
        tokens_in_line: List[Token] = list()
        save_dir = 'tokens.txt'
        
        with open(save_dir, 'w') as f:
            for token in self._tokens:
                if token.line > line_num:
                    if tokens_in_line:
                        tokens = f"{line_num}.\t" + " ".join(tokens_in_line)
                        f.write(tokens)
                        f.write("\n")
                        
                    line_num = token.line
                    tokens_in_line.clear()
                
                tokens_in_line.append(token.all_in_one)

            tokens = f"{line_num}.\t" + " ".join(tokens_in_line)
            f.write(tokens)
            f.write("\n")

    
    def _save_errs(self) -> None:
        """saves all errors found in a text file"""

        line_num = 1
        errs_in_line: List[Token] = list()
        save_dir = 'lexical_errors.txt'
        
        with open(save_dir, 'w') as f:
            if len(self._errs) == 0:
                f.write("There is no lexical error.")
            else:
                for err in self._errs:
                    if err.line > line_num:
                        if errs_in_line:
                            errs = f"{line_num}.\t" + " ".join(errs_in_line)
                            f.write(errs)
                            f.write("\n")

                        line_num = err.line                        
                        errs_in_line.clear()
                    
                    errs_in_line.append(err.all_in_one)

                errs = f"{line_num}.\t" + " ".join(errs_in_line)
                f.write(errs)
                f.write("\n")

    
    def _save_symbol_table(self) -> None:
        """saves symbol table into a text file"""

        save_dir = 'symbol_table.txt'
        with open(save_dir, 'w') as f:
            for ix, row in enumerate(SymbolTable().table):
                f.write(f"{ix + 1}.\t{row.lexeme}\n")

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

    
    def pass_next_token_to_parser(self) -> Tuple[Token, TokenType]:
        """ passes the next next token to parser (EXCEPT for comments and whitespaces) """

        while self._p1 < len(self._inp_file):
            token = self._get_next_token()
            if token is None or self._current_token_type in [TokenType.COMMENT, TokenType.WHITESPACE]:
                continue
            
            return token, self._current_token_type
        
        self._current_token_type = TokenType.EOF
        token_eof = Token(self._current_line_num, EOF, self._current_token_type)
        return token_eof, self._current_token_type