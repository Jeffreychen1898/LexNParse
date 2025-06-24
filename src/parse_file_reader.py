from utils import *
from lexer import Lexer, LEXER_AMBIGUITY_FIRST, LEXER_AMBIGUITY_STRICT

class ParseFileReader:
    def __init__(self):
        self.parse_file_tokens = [
            ("comment_single", "//"),
            ("comment_multi_beg", "/\*"),
            ("comment_multi_end", "\*/"),

            ("varname", "[a-zA-Z0-9][a-zA-Z0-9_]*"),

            ("tk_defn", ":"),
            ("tk_regex", "\".*\""),

            ("scope_beg", "{"),
            ("scope_end", "}"),
            ("special_variable", "__[a-z_]+__"),
            ("semicolon", ";"),

            ("space", " *"),
            ("arbitrary", ".")
        ]

        self.token_enumeration = {
            "varname": 'v',
            "tk_defn": 'd',
            "tk_regex": 'r',
            "scope_beg": 'b',
            "scope_end": 'e',
            "special_variable": 's',
            "semicolon": 'c',
            "space": 'p'
        }

        rules = [
            ("new_token", "vp?dp?rp?c"),
            ("new_grammar", "vp?bp?(((v|s)p?)+p?cp?)+e"),
            ("ambig_priority", "vpvp?c")
        ]
        self.token_reader_lexer = Lexer(rules, ambig_resolution=LEXER_AMBIGUITY_STRICT)

        self.lexer = Lexer(self.parse_file_tokens, ambig_resolution=LEXER_AMBIGUITY_FIRST)
        self.filename = ""
        self.tokens = []

        self.ambig_priority = LEXER_AMBIGUITY_STRICT
        self.defined_tokens = dict()
        self.defined_grammar = dict()

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
                if len(line.strip()) == 0:
                    token_sequences.append([])
                    continue

                line_tokens = self.lexer.tokenize(line.strip())
                token_sequences.append(line_tokens)

        self.parse_file(token_sequences)

    def parse_file(self, token_sequences):
        self.tokens = self.remove_comments(token_sequences)
        self.read_tokens()
        self.validate_file()

    def validate_file(self):
        for grammar_rule in self.defined_grammar.values():
            for production in grammar_rule:
                for each_tk in production:
                    if each_tk[1] == "special_variable":
                        continue
                    if each_tk[0] in self.defined_tokens:
                        continue
                    if each_tk[0] in self.defined_grammar:
                        continue

                    raise SyntaxErr(f"Token or grammar rule {each_tk[0]} referenced in line {each_tk[2] + 1} cannot be found!")
        # TODO:
        # ensure all tokens are defined
        pass

    def read_tokens(self):
        tk_reader_dfa = self.token_reader_lexer.get_dfa()

        prev_accept = None
        prev_index = 0

        curr_index = 0
        parse_tokens = []
        while curr_index < len(self.tokens):
            symbol = self.token_enumeration[self.tokens[curr_index][1]]
            try:
                tk_reader_dfa.step(symbol)
            except InvalidParse:
                if prev_accept is None:
                    raise ApplicationError("Error on parsing token!")
                self.parse_block(prev_accept[0], prev_accept[1])
                curr_index = prev_index

                prev_accept = None
                parse_tokens = []
                tk_reader_dfa.reset()
                curr_index += 1
                continue

            parse_tokens.append(self.tokens[curr_index])
            state_attribs = tk_reader_dfa.get_state_attributes(tk_reader_dfa.get_current_state())
            if len(state_attribs) > 1:
                raise ApplicationError("Ambiguity detected while reading tokens!")
            if state_attribs:
                prev_accept = (parse_tokens.copy(), state_attribs.pop())
                prev_index = curr_index
            elif curr_index == len(self.tokens) - 1:
                if prev_accept is None:
                    raise ApplicationError("Error detected while reading tokens!")
                self.parse_block(prev_accept[0], prev_accept[1])
                curr_index = prev_index

                prev_accept = None
                parse_tokens = []
                tk_reader_dfa.reset()

            curr_index += 1

        if prev_accept is None or prev_index != len(self.tokens) - 1:
            raise ApplicationError("Lexer has rejected the input stream while reading tokens!")
        tk_reader_dfa.reset()

        self.parse_block(prev_accept[0], prev_accept[1])

    def parse_block(self, block_tokens, block_type):
        if block_type[0] == "ambig_priority":
            self.parse_ambig_priority(block_tokens)
        elif block_type[0] == "new_token":
            self.parse_new_token(block_tokens)
        elif block_type[0] == "new_grammar":
            self.parse_new_grammar(block_tokens)

    def parse_ambig_priority(self, tks):
        tk_counter = 0
        for tk in tks:
            if tk[2] != 0:
                raise SyntaxErr("Lexer ambiguity priority must be defined on line 1!")

            if tk[1] == "space":
                continue

            if tk_counter == 1:
                self.ambig_priority = tk[0]
            tk_counter += 1

    def parse_new_token(self, tks):
        token_name = ""
        token_regex = ""
        line_number = tks[0][2] + 1
        for tk in tks:
            if tk[1] == "varname":
                token_name = tk[0]
            elif tk[1] == "tk_regex":
                token_regex = tk[0]

        if token_name in self.defined_tokens or token_name in self.defined_grammar:
            raise SyntaxErr(f"Duplicate variable name found on line {line_number}!")

        self.defined_tokens[token_name] = token_regex[1:-1]

    def parse_new_grammar(self, tks):
        grammar_name = tks[0][0]
        line_number = tks[0][2] + 1
        if grammar_name in self.defined_tokens or grammar_name in self.defined_grammar:
            raise SyntaxErr(f"Duplicate variable name found on line {line_number}!")

        self.defined_grammar[grammar_name] = set()
        token_seq = []
        for tk in tks[1:]:
            if tk[1] == "varname" or tk[1] == "special_variable":
                token_seq.append(tk)
            elif tk[1] == "semicolon":
                self.defined_grammar[grammar_name].add(tuple(token_seq))
                token_seq = []

        if len(token_seq) > 0:
            self.defined_grammar[grammar_name].add(tuple(token_seq))

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

                if token[1] == "arbitrary":
                    raise SyntaxErr(f"Syntax error in file {self.filename} on line {i + 1}!")

                new_token_list.append((token[0], token[1], i))

        return new_token_list
