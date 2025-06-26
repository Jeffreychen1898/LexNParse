from lexer import Lexer
from parser_dfa import ParserDFA
from grammar import Grammar
from utils import *

from parse_file_reader import ParseFileReader

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
    parse_reader = ParseFileReader()
    ambig_priority, tokens, grammars = parse_reader.read_file("./tests/test.txt")

    try:
        token_lexer = Lexer(tokens, ambig_resolution=ambig_priority)
    except InvalidParse as e:
        print(e)
        raise InvalidParse(e)

    for tk in tokens:
        print(tk)

    print()
    for grammar, info in grammars.items():
        print(f"{grammar} => {info[2]}")
        print(f"\t{info[0]}")
        print(f"\t== CODE BLOCK ==")
        print(f"{info[1]}")

    #print(parse_reader.get_ambig_priority())
    #print(parse_reader.get_defined_tokens())
    #print(parse_reader.get_defined_grammar())

    """grammar = Grammar()
    grammar.insert_rule("G", [(True, "S"), (False, "$")])
    grammar.insert_rule("S", [(True, "A")])
    grammar.insert_rule("A", [(False, "("), (True, "A"), (True, "B"), (False, ")")])
    grammar.insert_rule("A", [(False, "("), (False, ")")])
    grammar.insert_rule("B", [(False, "("), (True, "A"), (False, ")")])
    grammar.insert_rule("B", [(False, "("), (False, ")")])"""

    """grammar.insert_rule("G", [(True, "S")])
    grammar.insert_rule("S", [(True, "C"), (True, "C")])
    grammar.insert_rule("C", [(False, "c"), (True, "C")])
    grammar.insert_rule("C", [(False, "d")])"""

    """grammar.insert_rule("G", [(True, "S")])
    grammar.insert_rule("S", [(True, "C"), (True, "C")])
    grammar.insert_rule("C", [(False, "c"), (True, "C")])
    grammar.insert_rule("C", [(False, "d")])"""

    """grammar.eval_FIRST_set()
    print(grammar.get_FIRST_set("DEFNS"))

    parser_dfa = ParserDFA(grammar, "DEFNS")"""

main()
