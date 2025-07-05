import os
import argparse

from lexer import Lexer
from parser_dfa import ParserDFA
from grammar import Grammar
from cpp_generator import CppGenerator
from parse_file_reader import ParseFileReader
from utils import *

DEFAULT_TEMPLATE_PATH = "./template"
DEFAULT_OUTPUT_PATH = "./"
DEFAULT_NAME = "parser"

class CLI:
    def __init__(self):
        self.tool_version = "1.0.0"

        self.arg_parser = argparse.ArgumentParser()
        self.arg_parser.add_argument("parsefile", help="Path to the parse file")
        self.arg_parser.add_argument("-v", "--version", action="version", help="Display the version of the program", version=f"LexNParse {self.tool_version}")
        self.arg_parser.add_argument("-o", "--output", type=str, help="Set the output directory", default="./")
        self.arg_parser.add_argument("-n", "--name", type=str, help="Set the name of the project", default=DEFAULT_NAME)
        self.arg_parser.add_argument("-t", "--template", type=str, help="Set the directory of the code generation templates", default=DEFAULT_TEMPLATE_PATH)
        self.arg_parser.add_argument("-e", "--evaluate", action="store_true", help="Evaluate the parse file and the grammar involved")
        self.arg_parser.add_argument("-d", "--dfa", action="store_true", help="Display the lexer dfa")
        self.arg_parser.add_argument("-p", "--parsetable", action="store_true", help="Display the parse table")

    def parse_arguments(self):
        args = self.arg_parser.parse_args()

        parse_file = args.parsefile

        if args.evaluate:
            self.invoke_evaluate(parse_file)
            return
        elif args.dfa:
            self.invoke_dfa(parse_file)
            return
        elif args.parsetable:
            self.invoke_parsetable(parse_file)
            return

        template_hpp_path = os.path.join(args.template, "template.hpp")
        template_cpp_path = os.path.join(args.template, "template.cpp")
        output_hpp_path = os.path.join(args.output, args.name + ".hpp")
        output_cpp_path = os.path.join(args.output, args.name + ".cpp")

        self.invoke_generator(
            parse_file,
            (template_hpp_path, template_cpp_path),
            (output_hpp_path, output_cpp_path)
        )

    def invoke_generator(self, parsefile, templatepaths, outpaths):
        print(f"[1/6] Reading parse file: {parsefile}!")
        file_reader = ParseFileReader()

        parse_file_ast = file_reader.read_file(parsefile)

        ambig_priority = parse_file_ast.get_ambiguity_priority()
        header = parse_file_ast.get_header()
        tokens = parse_file_ast.get_tokens()
        grammars = parse_file_ast.get_grammars()
        externs = parse_file_ast.get_externs()

        print("[2/6] Building the lexer!")
        generated_lexer = Lexer(tokens, ambig_resolution=ambig_priority)

        print("[3/6] Building the grammar!")
        generated_grammar = Grammar()

        for grammar, info in grammars.items():
            for rule in info[0]:
                grammar_symbols = []
                for symbol, _ in rule:
                    if symbol == "__epsilon__":
                        break
                    grammar_symbols.append((symbol in grammars, symbol))

                generated_grammar.insert_rule(grammar, grammar_symbols)

        print("[4/6] Evaluating grammar FIRST set!")
        generated_grammar.eval_FIRST_set()

        print("[5/6] Building the LR table!")
        lr_parser = ParserDFA(generated_grammar, file_reader.get_start_grammar())
        action_table = lr_parser.get_table().get_action_table()

        print("[6/6] Generating code!")
        generator = CppGenerator(
            header,
            externs,
            generated_lexer.get_dfa(),
            ambig_priority,
            (file_reader.get_start_grammar(), grammars, generated_grammar),
            lr_parser.get_table()
        )

        generator.generate(
            templatepaths[0],
            templatepaths[1],
            outpaths[0],
            outpaths[1]
        )

    def invoke_evaluate(self, parsefile):
        print(f"[1/5] Reading parse file: {parsefile}!")
        file_reader = ParseFileReader()

        parse_file_ast = file_reader.read_file(parsefile)

        ambig_priority = parse_file_ast.get_ambiguity_priority()
        header = parse_file_ast.get_header()
        tokens = parse_file_ast.get_tokens()
        grammars = parse_file_ast.get_grammars()
        externs = parse_file_ast.get_externs()

        print("[2/5] Building the lexer!")
        generated_lexer = Lexer(tokens, ambig_resolution=ambig_priority)

        print("[3/5] Building the grammar!")
        generated_grammar = Grammar()

        for grammar, info in grammars.items():
            for rule in info[0]:
                grammar_symbols = []
                for symbol, _ in rule:
                    if symbol == "__epsilon__":
                        break
                    grammar_symbols.append((symbol in grammars, symbol))

                generated_grammar.insert_rule(grammar, grammar_symbols)

        print("[4/5] Evaluating grammar FIRST set!")
        generated_grammar.eval_FIRST_set()

        print("[5/5] Building the LR table!")
        lr_parser = ParserDFA(generated_grammar, file_reader.get_start_grammar())

        print("All Passed!")

    def invoke_dfa(self, parsefile):
        print(f"[1/2] Reading parse file: {parsefile}!")
        file_reader = ParseFileReader()

        parse_file_ast = file_reader.read_file(parsefile)

        ambig_priority = parse_file_ast.get_ambiguity_priority()
        header = parse_file_ast.get_header()
        tokens = parse_file_ast.get_tokens()
        grammars = parse_file_ast.get_grammars()
        externs = parse_file_ast.get_externs()

        print("[2/2] Building the lexer!")
        generated_lexer = Lexer(tokens, ambig_resolution=ambig_priority)

        transition_table = generated_lexer.get_dfa().get_transition_table()
        print(transition_table)

    def invoke_parsetable(self, parsefile):
        print(f"[1/5] Reading parse file: {parsefile}!")
        file_reader = ParseFileReader()

        parse_file_ast = file_reader.read_file(parsefile)

        ambig_priority = parse_file_ast.get_ambiguity_priority()
        header = parse_file_ast.get_header()
        tokens = parse_file_ast.get_tokens()
        grammars = parse_file_ast.get_grammars()
        externs = parse_file_ast.get_externs()

        print("[2/5] Building the lexer!")
        generated_lexer = Lexer(tokens, ambig_resolution=ambig_priority)

        print("[3/5] Building the grammar!")
        generated_grammar = Grammar()

        for grammar, info in grammars.items():
            for rule in info[0]:
                grammar_symbols = []
                for symbol, _ in rule:
                    if symbol == "__epsilon__":
                        break
                    grammar_symbols.append((symbol in grammars, symbol))

                generated_grammar.insert_rule(grammar, grammar_symbols)

        print("[4/5] Evaluating grammar FIRST set!")
        generated_grammar.eval_FIRST_set()

        print("[5/5] Building the LR table!")
        lr_parser = ParserDFA(generated_grammar, file_reader.get_start_grammar())
        action_table = lr_parser.get_table()

        action_table.display()
