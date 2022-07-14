from typing import Dict, List, Literal
from data_class.addressing_mode import Arg
from data_class.node import Node
from enums.error import SemanticErrorType
from utils.patterns.singleton import Singleton

_semantic_error_msg: Dict[SemanticErrorType, str] = {
    SemanticErrorType.SCOPING: "#{} : Semantic Error! '{}' is not defined appropriately.",
    SemanticErrorType.CONT_STMT: "#{} : Semantic Error! No 'while' found for 'continue'.",
    SemanticErrorType.BREAK_STMT: "#{} : Semantic Error! No 'while' found for 'break'.",
    SemanticErrorType.MISMATCH_PARAM_FUNC: "#{} : Semantic Error! Mismatch in numbers of arguments of '{}'.",
    SemanticErrorType.MAIN_FUNC_DEF: "#{} : Semantic Error! main function not found.",
    SemanticErrorType.TYPE_MISMATCH: "#{} : Semantic Error! Void type in operands."
}

class Semantic(metaclass=Singleton):

    def __init__(self) -> None:
        self.stack: List[Arg] = None
        self.errs: List[str] = None
        self.stack_recorder: List[int] = list()
        self.current_scope: int = None
        self.scope_tree: Dict[int, Node] = None
        self.no_scopes: int = None
        self.lineno: int = None

    def __enter__(self) -> 'Semantic':
        self._start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        with open('semantic_errors.txt', 'w') as f:
            if not self.errs:
                f.write('The input program is semantically correct.')
            else:
                for err in self.errs:
                    f.write(err)
                    f.write("\n")

                # override output of code generator
                with open('output.txt', 'w') as f2:
                    f2.write('The output code has not been generated.')

        self.errs.clear()
        self.stack.clear()
        self.scope_tree.clear()
        self.no_scopes = None
        self.lineno = None

    def _start(self) -> None:
        self.stack = list()
        self.errs = list()
        self.lineno = -4
        self.no_scopes = 1
        self.current_scope: int = 0
        
        self.scope_tree = dict()
        root = Node(self.current_scope)
        self.scope_tree[self.current_scope] = root

    def create_new_scope(self):
        father = self.scope_tree[self.current_scope]
        node = Node(self.no_scopes, father)
        self.scope_tree[self.no_scopes] = node
        self.switch_scope(self.no_scopes)    
        self.no_scopes += 1

    def switch_scope(self, scope_no: int):
        self.current_scope = scope_no

    def error_handler(self, err_type: SemanticErrorType, lexeme: str=None) -> None:
        if err_type in [SemanticErrorType.SCOPING, SemanticErrorType.MISMATCH_PARAM_FUNC]:
            msg = _semantic_error_msg[err_type].format(self.lineno, lexeme)     
        else:
            msg = _semantic_error_msg[err_type].format(self.lineno)
        
        self.errs.append(msg)
        