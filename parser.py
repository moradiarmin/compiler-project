from typing import Callable, List, Dict, Literal, Optional, Tuple, Union

from .scanner import Token


NULL = 'null'
SYNC = 'sync'

class Parser:
    """ parser module

    Args:
        grammar_addr (str): directory of text file containing all rules of the language
        call_scanner(Callable[..., Token]): function from Scanner module for extracting the next token
    """
    def __init__(self, 
            grammar_addr: str,
            call_scanner: Callable[..., Token]) -> None:
        
        self._parsing_started: bool = False
        """ if true then parser has got the first token from scanner """

        self._terminals: List[str] = list()
        """ list of all terminals exist for the given grammar """
        
        self._non_terminals: List[str] = list()
        """ list of all non-terminals existed for the given grammar """
        
        self._rules: List[List[str]] = [[]]
        """ all rules existed for the given grammar. NOTE: to start indexing from one, a null list is added at first """

        self._parse_grammar_file(grammar_addr)

        self._parse_table: Dict[Tuple[str, str], Union[int, SYNC]] = dict()
        """ maps a non-terminal and terminal to the rule number or 'SYNC' """

        self._call_scanner: Callable[..., Token] = call_scanner
        
        self.stack: List[str] = [self._non_terminals[0]] + ['$']
        """ parser stack """
        
        self._errs: List[str] = list()
        """ all errors occured during parsing """


    def _parse_grammar_file(self,
            grammar_addr: str):
        """parses the grammar file to extract terminals and non terminals expression plus rules.
        
        Args:
            grammar_addr (str): directory of text file containing all rules of the language
        """
        
        all_exps = list()
        with open(grammar_addr, 'r') as f:

            for rule in f.read().split("\n"):
                lhs_non_terminal, rhs = rule.split(" -> ")
                self._non_terminals.append(lhs_non_terminal)
                
                rhs_exps = rhs.split()
                self._rules.append(rhs_exps)
                all_exps += [lhs_non_terminal] + rhs_exps
            
            all_exps = list(set(all_exps))
            self._non_terminals = list(set(self._non_terminals))
            self._terminals = [x for x in all_exps if x not in self._non_terminals]
        

    def parse(self): 
        # TODO: creating parse tree
        # TODO: creating parse table
        
        if not self._parsing_started:
            token: Token = self._call_scanner()
            self._parsing_started = True

        line_no = token.line
        X = self.stack[0]

        # X is terminal
        if X in self._terminals:
            self.stack.pop(0)
            if X == token:
                token = self._call_scanner()
            else:
                self._errs.append(f'#{line_no}: syntax error; missing {token}')

        # X is non-terminal
        elif X in self._non_terminals:
            try:
                rule_no = self._parse_table[X, token]
            except:
                rule_no = NULL
            
            if isinstance(rule_no, int):
                self.stack.pop(0)
                self.stack = self._rules[rule_no] + self.stack
            
            elif rule_no == SYNC:
                self.stack.pop(0)
                self._errs(f'#{line_no}: syntax error; missing {exp}')
            
            else:
                self._errs(f'#{line_no}: syntax error; illegal {token}')
                token = self._call_scanner()
