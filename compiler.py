# Armin Moradi 96106077
# Alireza Dizaji 96107545


from core.scanner import Scanner
from core.parser import Parser
from modules.memory import Memory
from modules.semantic import Semantic
from modules.symbol_table import SymbolTable

if __name__ == "__main__":
    keywords = ["break", "continue", "def", "else","if", "return", "while", "global,"]
    
    with Semantic():
        with SymbolTable(keywords):
            with Memory(unit=1, prog_size=100, data_size=400, capacity=900):
                my_scanner = Scanner(f"./input.txt", f".")
                my_parser = Parser('grammar_editted.txt', my_scanner.pass_next_token_to_parser)
                my_parser.parse()
                my_parser.code_generator.fill_first_and_last()

                print(Memory()._space[:Memory().prog_p])
