from lexer import Lexer
from parser import Parser
from parser_dfa import ParserDFA
from grammar import Grammar

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
    #token_rules = read_lex_file("./tests/test.txt")
    #lex = Lexer(token_rules)
    #lex.construct_dfa()

    #parser = Parser()
    grammar = Grammar()
    """grammar.insert_rule("G", [(True, "S"), (False, "$")])
    grammar.insert_rule("S", [(True, "A")])
    grammar.insert_rule("A", [(False, "("), (True, "A"), (True, "B"), (False, ")")])
    grammar.insert_rule("A", [(False, "("), (False, ")")])
    grammar.insert_rule("B", [(False, "("), (True, "A"), (False, ")")])
    grammar.insert_rule("B", [(False, "("), (False, ")")])"""

    grammar.insert_rule("G", [(True, "S")])
    grammar.insert_rule("S", [(True, "C"), (True, "C")])
    grammar.insert_rule("C", [(False, "c"), (True, "C")])
    grammar.insert_rule("C", [(False, "d")])

    grammar.eval_FIRST_set()
    print(grammar.get_FIRST_set("G"))

    parser_dfa = ParserDFA(grammar, "G")

main()
