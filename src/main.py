from lexer import Lexer
from parser_dfa import ParserDFA
from grammar import Grammar

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
    #token_rules = read_lex_file("./tests/test.txt")
    #lex = Lexer(token_rules)
    #lex.construct_dfa()

    """parse_reader = ParseFileReader()
    parse_reader.read_file("./tests/test.txt")

    print(parse_reader.get_ambig_priority())
    print(parse_reader.get_defined_tokens())
    print(parse_reader.get_defined_grammar())"""

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

    grammar = Grammar()

    """grammar.insert_rule("DEFNS", [(True, "AMBIGUITY_CHECK"), (True, "GAP"), (True, "DEFN")])
    #grammar.insert_rule("DEFNS", [(True, "DEFN")])

    grammar.insert_rule("DEFN", [(True, "TOKEN"), (True, "GAP"), (True, "DEFN")])
    grammar.insert_rule("DEFN", [(True, "GRAMMAR"), (True, "GAP"), (True, "DEFN")])
    grammar.insert_rule("DEFN", [])

    grammar.insert_rule("TOKEN", [(False, "varname"), (True, "SPACE"), (False, "tk_defn"), (True, "GAP"), (False, "tk_regex"), (True, "SPACE"), (False, "semicolon")])

    grammar.insert_rule("GRAMMAR", [(False, "varname"), (True, "GAP"), (False, "scope_beg"), (True, "GAP"), (True, "PRODUCTIONS"), (False, "scope_end"), (True, "CODE")])

    grammar.insert_rule("PRODUCTIONS", [(True, "PRODUCTION"), (True, "SPACE"), (False, "semicolon"), (True, "GAP"), (True, "PRODUCTIONS")])
    grammar.insert_rule("PRODUCTIONS", [])
    grammar.insert_rule("PRODUCTION", [(True, "PRODUCTION"), (True, "GAP"), (True, "SYMBOL")])
    grammar.insert_rule("PRODUCTION", [])

    grammar.insert_rule("SYMBOL", [(True, "VARIABLE"), (True, "SPACE"), (True, "RENAME")])
    grammar.insert_rule("RENAME", [(False, "angle_open"), (True, "VARIABLE"), (False, "angle_close")])
    grammar.insert_rule("RENAME", [])

    grammar.insert_rule("CODE", [(True, "GAP"), (False, "codeblock")])
    grammar.insert_rule("VARIABLE", [(False, "varname")])
    grammar.insert_rule("VARIABLE", [(False, "special_variable")])

    grammar.insert_rule("AMBIGUITY_CHECK", [(False, "varname"), (False, "varname")])
    #grammar.insert_rule("AMBIGUITY_CHECK", [])

    grammar.insert_rule("SPACE", [(False, "space")])
    grammar.insert_rule("SPACE", [])

    grammar.insert_rule("GAP", [(False, "space"), (True, "GAP")])
    grammar.insert_rule("GAP", [])"""

    grammar.insert_rule("DEFNS", [(True, "AMBIGUITY_CHECK"), (True, "SPACE"), (True, "DEFN")])
    grammar.insert_rule("DEFNS", [(True, "DEFN")])
    grammar.insert_rule("DEFN", [(True, "TOKEN"), (True, "SPACE"), (True, "DEFN")])
    grammar.insert_rule("DEFN", [(True, "GRAMMAR"), (True, "SPACE"), (True, "DEFN")])
    grammar.insert_rule("DEFN", [])

    grammar.insert_rule("TOKEN", [(False, "varname"), (True, "SPACE"), (False, "tk_defn"), (True, "SPACE"), (False, "tk_regex"), (True, "SPACE"), (False, "semicolon")])

    grammar.insert_rule("GRAMMAR", [(False, "varname"), (True, "SPACE"), (False, "scope_beg"), (True, "SPACE"), (True, "PRODUCTIONS"), (False, "scope_end"), (True, "CODE")])
    grammar.insert_rule("PRODUCTIONS", [(False, "PRODUCTION"), (True, "SPACE"), (False, "semicolon"), (True, "SPACE"), (True, "PRODUCTIONS")])
    grammar.insert_rule("PRODUCTIONS", [])
    grammar.insert_rule("PRODUCTION", [(True, "PRODUCTION"), (True, "SPACE"), (True, "SYMBOL")])
    grammar.insert_rule("PRODUCTION", [])

    grammar.insert_rule("SYMBOL", [(True, "VARIABLE"), (True, "SPACE"), (True, "RENAME")])

    grammar.insert_rule("RENAME", [(False, "angle_open"), (True, "VARIABLE"), (False, "angle_close")])
    grammar.insert_rule("RENAME", [])

    grammar.insert_rule("VARIABLE", [(False, "varname")])
    grammar.insert_rule("VARIABLE", [(False, "special_variable")])

    grammar.insert_rule("CODE", [(True, "SPACE"), (False, "codeblock")])

    grammar.insert_rule("AMBIGUITY_CHECK", [(False, "varname"), (False, "space"), (False, "varname")])

    grammar.insert_rule("SPACE", [(False, "space"), (True, "SPACE")])
    grammar.insert_rule("SPACE", [])

    grammar.eval_FIRST_set()
    print(grammar.get_FIRST_set("DEFNS"))

    parser_dfa = ParserDFA(grammar, "DEFNS")

main()
