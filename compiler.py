# Armin Moradi 96106077
# Alireza Dizaji 96107545

from scanner import Scanner
from parser import Parser

my_scanner = Scanner(f"./input.txt", f".")
my_parser = Parser('grammar.txt', my_scanner.pass_next_token_to_parser)

my_parser.parse()