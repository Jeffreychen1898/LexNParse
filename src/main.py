from lexer import Lexer
from parser_dfa import ParserDFA
from grammar import Grammar
from cpp_generator import CppGenerator
from utils import *

from parse_file_reader import ParseFileReader

# implement parser_table.get_action_table()

def main():
    parse_reader = ParseFileReader()
    ambig_priority, header, tokens, grammars = parse_reader.read_file("./tests/basic_lex.txt")

    #print(header)
    token_lexer = None

    try:
        token_lexer = Lexer(tokens, ambig_resolution=ambig_priority)
        """transition_table = token_lexer.get_dfa().get_transition_table()
        print(token_lexer.get_dfa().get_num_states())
        print(len(transition_table[0]))
        print(transition_table)"""
    except InvalidParse as e:
        print(e)
        raise InvalidParse(e)

    for tk in tokens:
        pass
        #print(tk)

    print()
    for grammar, info in grammars.items():
        pass
        #print(f"{grammar} => {info[2]}")
        #print(f"\t{info[0]}")
        #print(f"\t== CODE BLOCK ==")
        #print(f"{info[1]}")

    file_grammar = Grammar()
    for grammar, info in grammars.items():
        for rule in info[0]:
            grammar_symbols = []
            for symbol, _ in rule:
                if symbol == "__epsilon__":
                    break
                grammar_symbols.append((symbol in grammars, symbol))

            file_grammar.insert_rule(grammar, grammar_symbols)

    file_grammar.eval_FIRST_set()
    parser = ParserDFA(file_grammar, parse_reader.get_start_grammar())
    action_table = parser.get_table().get_action_table()

    generator = CppGenerator(header, token_lexer.get_dfa(), ambig_priority, (parse_reader.get_start_grammar(), grammars, file_grammar), parser.get_table())

    generator.generate(
        "./template/template.hpp",
        "./template/template.cpp",
        "./template/parser.hpp",
        "./template/parser.cpp"
    )

main()
