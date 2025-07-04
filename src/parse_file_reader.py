from utils import *
from lexer import Lexer, LEXER_AMBIGUITY_FIRST
from parser_dfa import ParserDFA
from grammar import Grammar
from parse_file_ast import *

CODE_BLOCK_TK = "codeblock"

class ParseFileReader:
    def __init__(self):
        self.parse_file_tokens = [
            ("comment_single", "//"),
            ("comment_multi_beg", "/\*"),
            ("comment_multi_end", "\*/"),

            ("code_begin", "=>"),

            ("extern", "__extern__"),
            ("start", "__start__"),
            ("ambig_priority", "__lexer_ambig_priority__"),
            ("varname", "[a-zA-Z0-9_][a-zA-Z0-9_$]*"),
            ("codetype", "\([^\(\)]+\)"),

            ("tk_defn", ":"),
            ("tk_regex", "\".*\""),

            ("angle_open", "<"),
            ("angle_close", ">"),

            ("scope_begin", "{%"),
            ("scope_end", "%}"),
            ("semicolon", ";"),

            ("space", " *"),
            ("arbitrary", ".")
        ]

        self.grammar = Grammar()
        self.setup_parse_file_grammar()
        self.parse_file_dfa = ParserDFA(self.grammar, "DEFNS")

        self.lexer = Lexer(self.parse_file_tokens, ambig_resolution=LEXER_AMBIGUITY_FIRST)
        self.filename = ""
        self.tokens = []

        self.ambig_priority = LEXER_AMBIGUITY_STRICT
        self.start_grammar = ""

    def get_ambig_priority(self):
        return self.ambig_priority

    def get_defined_tokens(self):
        return self.defined_tokens

    def get_defined_grammar(self):
        return self.defined_grammar

    def read_file(self, filename):
        self.filename = filename
        token_sequences = []
        with open(filename, "r") as file:
            for line in file:
                cleaned_line = line.rstrip("\n").replace("\t", " " * 4)
                if len(cleaned_line) == 0:
                    token_sequences.append([])
                    continue

                line_tokens = self.lexer.tokenize(cleaned_line)
                token_sequences.append(line_tokens)

        return self.parse_file(token_sequences)

    def parse_file(self, token_sequences):
        cleaned_tokens = self.remove_comments(token_sequences)
        self.tokens = self.assemble_code_blocks(cleaned_tokens)

        ast = self.read_token_stream()
        ast.validate()

        # tokens = ast.get_tokens()
        # grammars = ast.get_grammars()
        # ambig_priority = ast.get_ambiguity_priority()
        # header = ast.get_header()

        self.start_grammar = ast.get_start_grammar()

        return ast
        #return (ambig_priority, header, tokens, grammars)

    def get_start_grammar(self):
        return self.start_grammar

    def assemble_code_blocks(self, tks):
        new_tokens = []
        code_block = ""
        code_block_line_number = -1
        code_block_curr_line = -1
        in_code_block = False

        for tk in tks:
            if tk[1] == "code_begin":
                if in_code_block:
                    raise SyntaxErr(f"Invalid token {self.parse_file_tokens['code_begin']} on line {tk[2]}!")

                in_code_block = True
                code_block_line_number = tk[2]
                code_block_curr_line = code_block_line_number
            elif tk[1] == "scope_end" and in_code_block:
                in_code_block = False
                num_newline = tk[2] - code_block_curr_line
                code_block += "\n" * num_newline
                new_tokens.append((code_block, CODE_BLOCK_TK, code_block_line_number))
                code_block = ""
            else:
                if not in_code_block:
                    new_tokens.append(tk)
                    continue

                num_newline = tk[2] - code_block_curr_line
                code_block += "\n" * num_newline
                code_block_curr_line += num_newline
                code_block += tk[0]

        if in_code_block:
            raise SyntaxErr(f"Code block opened on line {code_block_line_number} not closed!")

        return new_tokens

    def remove_comments(self, token_sequences):
        multicomment_on = False
        new_token_list = []

        for i, token_sequence in enumerate(token_sequences):
            for token in token_sequence:
                if token[1] == "comment_single" and not multicomment_on:
                    break

                if token[1] == "comment_multi_beg":
                    multicomment_on = True
                elif token[1] == "comment_multi_end":
                    multicomment_on = False
                    continue

                if multicomment_on:
                    continue

                new_token_list.append((token[0], token[1], i))

        return new_token_list

    def read_token_stream(self):
        parse_stack = [(0, None, None)]
        stream_index = 0
        parse_table = self.parse_file_dfa.get_table()

        ast_handler = ParseFileAST()
        self.tokens += [(None, "$", -1)]

        while stream_index < len(self.tokens):
            curr_state = parse_stack[-1][0]
            tk = self.tokens[stream_index][1]
            action = None
            try:
                query_token = (False, tk)
                action = parse_table.get_action(curr_state, query_token)

                if action[0] == "s":
                    parse_stack.append((action[1], self.tokens[stream_index], None))
                    stream_index += 1
                else:
                    production = parse_table.get_production(action[1])
                    nonterminal, value = self.reduce_symbol(ast_handler, parse_stack, production)
                    if nonterminal == "DEFNS":
                        break

                    prior_state = parse_stack[-1][0]
                    goto_action = parse_table.get_action(prior_state, (True, nonterminal))
                    parse_stack.append((goto_action[1], (nonterminal, self.tokens[stream_index][2]), value))

            except ApplicationError as e:
                raise SyntaxErr(f"Invalid syntax on line {self.tokens[stream_index][2]}!")

        return ast_handler

    def reduce_symbol(self, ast_handler, stack, production):
        symbols = production.get_symbols()
        nonterminal = production.get_nonterminal()

        result = ast_handler.handleGrammar(nonterminal, stack[len(stack)-len(symbols):])

        for _ in symbols:
            stack.pop()

        return nonterminal, result

    def setup_parse_file_grammar(self):
        self.grammar.insert_rule("DEFNS", [(True, "AMBIGUITY_CHECK"), (True, "SPACE"), (True, "HEADER"), (True, "DEFN")])
        self.grammar.insert_rule("DEFNS", [(True, "DEFN")])
        self.grammar.insert_rule("DEFN", [(True, "EXTERN"), (True, "SPACE"), (True, "DEFN")])
        self.grammar.insert_rule("DEFN", [(True, "TOKEN"), (True, "SPACE"), (True, "DEFN")])
        self.grammar.insert_rule("DEFN", [(True, "START"), (True, "SPACE"), (True, "DEFN")])
        self.grammar.insert_rule("DEFN", [(True, "GRAMMAR"), (True, "SPACE"), (True, "DEFN")])
        self.grammar.insert_rule("DEFN", [])

        self.grammar.insert_rule("HEADER", [(False, CODE_BLOCK_TK), (True, "SPACE")])
        self.grammar.insert_rule("HEADER", [])

        self.grammar.insert_rule("EXTERN", [(False, "extern"), (True, "SPACE"), (False, "varname"), (True, "SPACE"), (False, "semicolon")])

        self.grammar.insert_rule("TOKEN", [(False, "varname"), (True, "SPACE"), (False, "tk_defn"), (True, "SPACE"), (False, "tk_regex"), (True, "SPACE"), (False, "semicolon")])

        self.grammar.insert_rule("GRAMMAR", [(False, "varname"), (True, "SPACE"), (True, "TYPE"), (False, "scope_begin"), (True, "SPACE"), (True, "PRODUCTIONS"), (False, CODE_BLOCK_TK)])
        self.grammar.insert_rule("GRAMMAR", [(False, "varname"), (True, "SPACE"), (True, "TYPE"), (False, "scope_begin"), (True, "SPACE"), (True, "PRODUCTIONS"), (False, "scope_end")])
        self.grammar.insert_rule("PRODUCTIONS", [(True, "SYMBOL"), (False, "semicolon"), (True, "SPACE"), (True, "PRODUCTIONS")])
        self.grammar.insert_rule("PRODUCTIONS", [(True, "SYMBOL"), (False, "semicolon"), (True, "SPACE")])
        self.grammar.insert_rule("SYMBOL", [(False, "varname"), (True, "SPACE"), (True, "RENAME"), (True, "SYMBOL")])
        self.grammar.insert_rule("SYMBOL", [(False, "varname"), (True, "SPACE"), (True, "RENAME")])

        self.grammar.insert_rule("RENAME", [(False, "angle_open"), (False, "varname"), (False, "angle_close"), (True, "SPACE")])
        self.grammar.insert_rule("RENAME", [])

        #self.grammar.insert_rule("TYPE", [(False, "paren_open"), (True, "SPACE"), (False, "varname"), (True, "SPACE"), (False, "paren_close"), (True, "SPACE")])
        self.grammar.insert_rule("TYPE", [(False, "codetype"), (True, "SPACE")])
        self.grammar.insert_rule("TYPE", [])

        self.grammar.insert_rule("AMBIGUITY_CHECK", [(False, "ambig_priority"), (False, "space"), (False, "varname"), (False, "semicolon")])
        self.grammar.insert_rule("START", [(False, "start"), (True, "SPACE"), (False, "varname"), (True, "SPACE"), (False, "semicolon")])

        self.grammar.insert_rule("SPACE", [(False, "space"), (True, "SPACE")])
        self.grammar.insert_rule("SPACE", [])

        self.grammar.eval_FIRST_set()
