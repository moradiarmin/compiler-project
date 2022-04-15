# Armin Moradi 96106077
# Alireza Dizaji 96107545

from scanner import Scanner

if __name__ == '__main__':
    N = 6
    my_scanner = Scanner(f"./test_cases/phase1/T0{N}/input.txt", f"./res2/phase1/T0{N}")
    my_scanner.scan()