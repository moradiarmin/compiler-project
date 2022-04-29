# Armin Moradi 96106077
# Alireza Dizaji 96107545

from scanner import Scanner
from .parser import Parser

my_scanner = Scanner(f"./input.txt", f".")
my_parser = Parser(my_scanner._get_next_token)

while not my_parser.stack(): # I'm not sure
    my_parser.parse()