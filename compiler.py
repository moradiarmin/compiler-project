# Armin Moradi 96106077
# Alireza Dizaji 96107545


from core.scanner import Scanner
from core.parser import Parser
from modules.memory import Memory
from modules.semantic_stack import Semantic
from modules.symbol_table import SymbolTable

if __name__ == "__main__":
    keywords = ["break", "continue", "def", "else","if", "return", "while"]
    with SymbolTable(keywords):
        with Memory(prog_size=100, data_size=400, capacity=900):
            with Semantic():
                my_scanner = Scanner(f"./input.txt", f".")
                my_parser = Parser('grammar.txt', my_scanner.pass_next_token_to_parser)
                my_parser.parse()