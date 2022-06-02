from typing import Callable, List, Dict, Tuple

from anytree import Node, RenderTree

from core.scanner import EOF, Token, TokenType
from utils.constants import EPSILON, SYNC, NULL

class Parser:
    """ parser module using LL(1) algorithm

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

        self._call_scanner: Callable[..., Tuple[Token, TokenType]] = call_scanner

        self._root = Node('Program')

        self.stack: List[Node] = [self._root, Node('$', parent=self._root)]
        """ parser stack """
        
        self._errs: List[str] = list()
        """ all errors occured during parsing """

        self._parse_table: Dict[Tuple[str, str], int] = {
            'Program': {'break': 1, 'continue': 1, 'ID': 1, 'return': 1, 'global': 1, 'def': 1, 'if': 1, 'while': 1, '$': 1},
            'Statements': {'break': 2, 'continue': 2, 'ID': 2, 'return': 2, 'global': 2, 'def': 2, 'if': 2, 'while': 2, 'if': 2, ';': 3, 'else': 3, '$': 3},
            'Statement': {'def': 4, 'if': 4, 'while': 4, 'break': 5, 'continue': 5, 'ID': 5, 'return': 5, 'global': 5},
            'Simple_stmt': {'ID': 6, 'return': 7, 'global': 8, 'break': 9, 'continue': 10},
            'Compound_stmt': {'def': 11, 'if': 12, 'while': 13},
            'Assignment_Call': {'ID': 14},
            'B': {'=': 15, '[': 16, '(': 17},
            'C': {'ID': 18, 'NUM': 18, '[': 19},
            'List_Rest': {',': 20, ']': 21},
            'Return_stmt': {'return': 22},
            'Return_Value': {'ID': 23, 'NUM': 23, ';': 24},
            'Global_stmt': {'global': 25},
            'Function_def': {'def': 26},
            'Params': {'ID': 27, ')': 28},
            'Params_Prime': {',': 29, ')': 30},
            'If_stmt': {'if': 31},
            'Else_block': {'else': 32, ';': 33},
            'Iteration_stmt': {'while': 34},
            'Relational_Expression': {'ID': 35, 'NUM': 35},
            'Relop': {'==': 36, '<': 37},
            'Expression': {'ID': 38, 'NUM': 38},
            'Expression_Prime': {'+': 39, '-': 40, ';': 41, ']': 41, ')': 41, ',': 41, ':': 41, '==': 41, '<': 41},
            'Term': {'ID': 42, 'NUM': 42},
            'Term_Prime': {'*': 43, ';': 44, ']': 44, ')': 44, ',': 44, ':': 44, '==': 44, '<': 44, '+': 44, '-': 44},
            'Factor': {'ID': 45, 'NUM': 45},
            'Power': {'**': 46, ';': 47, '[': 47, '(': 47, ']': 47, ')': 47, ',': 47, ':': 47, '==': 47, '<': 47, '+': 47, '-': 47, '*': 47},
            'Primary': {'[': 48, '(': 49, ';': 50, ']': 50, ')': 50, ',': 50, ':': 50, '==': 50, '<': 50, '+': 50, '-': 50, '*': 50},
            'Arguments': {'ID': 51, 'NUM': 51, ')': 52},
            'Arguments_Prime': {',': 53, ')': 54},
            'Atom': {'ID': 55, 'NUM': 56},
        }
        """ maps a non-terminal and terminal to the rule number or 'SYNC' """

        self._follow: Dict[str, List[str]] = {
            'Program': ['$'],
            'Statements': [';', 'else', '$'],
            'Statement': [';'],
            'Simple_stmt': [';'],
            'Compound_stmt': [';'],
            'Assignment_Call': [';'],
            'B': [';'],
            'C': [';'],
            'List_Rest': [']'],
            'Return_stmt': [';'],
            'Return_Value': [';'],
            'Global_stmt': [';'],
            'Function_def': [';'],
            'Params': [')'],
            'Params_Prime': [')'],
            'If_stmt': [']'],
            'Else_block': [';'],
            'Iteration_stmt': [';'],
            'Relational_Expression': [')', ':'],
            'Relop': ['ID', 'NUM'],
            'Expression': [';', ')', ']', ',', ':', '==', '<'],
            'Expression_Prime': [';', ')', ']', ',', ':', '==', '<'],
            'Term': [';', ')', ']', ',', ':', '==', '<', '+', '-'],
            'Term_Prime': [';', ')', ']', ',', ':', '==', '<', '+', '-'],
            'Factor': [';', ')', ']', ',', ':', '==', '<', '+', '-', '*'],
            'Power': [';', ')', ']', ',', ':', '==', '<', '+', '-', '*'],
            'Primary': [';', ')', ']', ',', ':', '==', '<', '+', '-', '*'],
            'Arguments': [')'],
            'Arguments_Prime': [')'],
            'Atom': [';', '[', '(', ')', ']', ',', ':', '==', '<', '+', '-', '*', '**'],
        }
        """ maps a non-terminal to its list of follow """


    def _parse_grammar_file(self,
            grammar_addr: str):
        """parses the grammar file to extract terminals and non terminals expression plus rules.
        
        Args:
            grammar_addr (str): directory of text file containing all rules of the language
        """
        
        T_NT = list()
        with open(grammar_addr, 'r') as f:

            for rule in f.read().split("\n"):
                lhs_non_terminal, rhs = rule.split(" -> ")
                self._non_terminals.append(lhs_non_terminal)
                
                rhs_exps = rhs.split()
                self._rules.append(rhs_exps)
                T_NT += [lhs_non_terminal] + rhs_exps
            
            T_NT = list(set(T_NT))
            self._non_terminals = list(set(self._non_terminals))
            self._terminals = [x for x in T_NT if x not in self._non_terminals]   


    def parse(self): 

        root: Node = self.stack[0]

        while self.stack[0].name != EOF:

            if not self._parsing_started:
                token, token_type = self._call_scanner()
                self._parsing_started = True

            line_no = token.line
            X = self.stack[0].name

            # X is terminal
            if X in self._terminals:
                node = self.stack.pop(0)
                
                if X == EPSILON:
                    node.name = node.name.lower()
                    continue
                
                if X == token.lexeme or X == token_type:
                    node.name = token.all_in_one
                    token, token_type = self._call_scanner()
                
                else:
                    node.parent = None
                    self._errs.append(f'#{line_no} : syntax error, missing {X}')
                
            # X is non-terminal
            elif X in self._non_terminals:
                T = token_type if token_type in [TokenType.ID, TokenType.NUMBER] else token.lexeme
                try:
                    rule_no = self._parse_table[X][T]
                except:
                    rule_no = SYNC if T in self._follow[X] else NULL

                if isinstance(rule_no, int):
                    lhs = self.stack.pop(0)
                    rhs = self._rules[rule_no]

                    self.stack = [Node(r, parent=lhs) for r in rhs] + self.stack          

                elif rule_no == SYNC:
                    # drop from parse tree
                    node = self.stack.pop(0)
                    node.parent = None

                    self._errs.append(f'#{line_no} : syntax error, missing {X}')
                
                else:
                    if token.lexeme == EOF:
                        self._errs.append(f'#{line_no} : syntax error, Unexpected EOF') 
                        break                   
                    else:
                        self._errs.append(f'#{line_no} : syntax error, illegal {T}')
                    token, token_type = self._call_scanner()

        # Unexpected EOF occured then remove all nodes remained in stack tree
        if len(self.stack) > 1:
            
            # remove all nodes remained in stack from tree
            while self.stack:
                node = self.stack.pop(0)
                node.parent = None

        # O.W. reorder eof sign in parser tree to the right most side            
        else:
            eof_node = self.stack.pop(0)
            eof_node.parent = None
            Node("$", parent=root)
    
        self._save()


    def _save_errs(self):
        """ saves occured errors within a text file """

        with open('syntax_errors.txt', 'w') as f:
            if not self._errs:
                f.write('There is no syntax error.')
            else:
                for err in self._errs:
                    f.write(err)
                    f.write('\n')


    def _save_parser_tree(self):
        """ saves the parser tree within a text file """

        with open('parse_tree.txt', 'w') as f:
            for pre, _, node in RenderTree(self._root):
                f.write(f"{pre}{node.name}\n")
    

    def _save(self):
        """ save parse tree and errors """

        self._save_errs()
        self._save_parser_tree()