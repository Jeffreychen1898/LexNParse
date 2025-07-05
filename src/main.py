from lexer import Lexer
from parser_dfa import ParserDFA
from grammar import Grammar
from cpp_generator import CppGenerator
from utils import *

from parse_file_reader import ParseFileReader

# implement parser_table.get_action_table()

from cli import CLI

def main():
    try:
        cli = CLI()
        cli.parse_arguments()
    except FileNotFoundError as e:
        print(f"File Not Found Error: {e}")
    except SyntaxErr as e:
        print(f"Syntax Error: {e}")
    except DuplicateVariable as e:
        print(f"Duplicate Variable Error: {e}")
    except UndefinedVariable as e:
        print(f"Undefined Variable Error: {e}")
    except GrammarError as e:
        print(f"Grammar Error: {e}")
    except InvalidParse as e:
        print(f"Invalid Parse Error: {e}")
    except InvalidDFA as e:
        print(f"Invalid DFA Error: {e}")
    except ApplicationError as e:
        print(f"Application Error: {e}")

main()
