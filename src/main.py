"""
lexer pipeline:
    regex parser
        regex -> tree
    preprocessor
        tree -> tree
    NFA Generator
        tree -> NFA
    NFA to DFA
        NFA -> DFA
    minimal DFA
        DFA -> minimal DFA

lexer file
    number : [0-9]+.?[0-9]+
"""

from lexer import Lexer

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
    token_rules = read_lex_file("./tests/basic_lex.txt")
    lex = Lexer(token_rules)

main()
