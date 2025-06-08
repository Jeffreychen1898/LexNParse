from lexer import Lexer
from parser import Parser

def read_lex_file(filename):
    token_rules = []
    with open(filename, "r") as file:
        for line in file:
            # remove trailing spaces and empty lines
            stripped_line = line.strip()
            if len(stripped_line) == 0:
                continue

            token_rules.append(stripped_line)

    return token_rules

def main():
    token_rules = read_lex_file("./tests/test.txt")
    lex = Lexer(token_rules)
    lex.construct_dfa()
    #parser = Parser()

main()
