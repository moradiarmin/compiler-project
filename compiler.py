# Armin Moradi 96106077
# Alireza Dizaji 96107545


from core.scanner import Scanner
from core.parser import Parser
from data_class.symbol_table import FuncAttribute
from modules.memory import Memory
from modules.semantic import Semantic
from modules.symbol_table import SymbolTable
from utils.routines import MAIN_FUNC_DEF

if __name__ == "__main__":
    keywords = ["break", "continue", "def", "else","if", "return", "while", "global", "print"]
    
    with Semantic():
        with SymbolTable(keywords):
            with Memory(unit=4, prog_size=100, data_size=400, capacity=900):
                my_scanner = Scanner(f"./input.txt", f".")
                my_parser = Parser('grammar_v2.txt', my_scanner.pass_next_token_to_parser)
                my_parser.parse()
                my_parser.code_generator.fill_first_and_last()
                
                # check for `main` function definition
                row = SymbolTable().find_row('main', 0)
                if row is None or not isinstance(row.attribute, FuncAttribute):
                    MAIN_FUNC_DEF()