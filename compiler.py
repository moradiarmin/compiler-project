# Armin Moradi 96106077
# Alireza Dizaji 96107545

from .scanner import Scanner

if __name__ == '__main__':
    my_scanner = Scanner("./compiler-project/test_cases/phase1/T02/input.txt", "./compiler-project/res/phase1/T01")
    my_scanner.scan()