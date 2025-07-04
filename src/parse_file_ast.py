from utils import *
from lexer import LEXER_AMBIGUITY_STRICT

class ParseFileAST:
    def __init__(self):
        self.lexer_ambiguity = LEXER_AMBIGUITY_STRICT
        self.tokens = []
        self.grammars = dict()
        self.header_code = ""
        self.start_grammar = ""
        self.externs = set()

    def validate(self):
        token_set = set(["__epsilon__"])
        token_set.update(self.externs)
        for tk in self.tokens:
            if tk[0] in token_set:
                raise DuplicateVariable(f"Token or grammar {tk[0]} is already defined!")

            token_set.add(tk[0])

        for grammar in self.grammars.keys():
            if grammar in token_set:
                raise DuplicateVariable(f"Token or grammar {grammar} is already defined!")

            token_set.add(grammar)

        for grammar, productions in self.grammars.items():
            for production in productions[0]:
                for symbol in production:
                    if symbol[0] not in token_set:
                        raise UndefinedVariable(f"Symbol {symbol[0]} is not defined in grammar {grammar}")

                    if symbol[0] == "__epsilon__" and len(production) > 1:
                        raise GrammarError(f"A non-nullable production contains an __epsilon__ in grammar {grammar}")

        if len(self.start_grammar) == 0:
            raise UndefinedVariable("The starting grammar was not defined. Define using __start__ <MyStartingGrammar>!")

        if self.start_grammar not in self.grammars:
            raise GrammarError(f"Starting grammar {self.start_grammar} is not defined!")

        if len(self.grammars[self.start_grammar][1]) == 0:
            raise GrammarError(f"Starting grammar {self.start_grammar} does not contain return type!")

    def get_ambiguity_priority(self):
        return self.lexer_ambiguity

    def get_tokens(self):
        return self.tokens

    def get_externs(self):
        return self.externs

    def get_grammars(self):
        return self.grammars

    def get_header(self):
        return self.header_code

    def get_start_grammar(self):
        return self.start_grammar

    def handle_DEFNS(self, symbols):
        return 0

    def handle_DEFN(self, symbols):
        return 0

    def handle_START(self, symbols):
        if len(self.start_grammar) > 0:
            raise DuplicateVariable("The starting grammar is already defined!")

        self.start_grammar = symbols[2][1][0]

        return 0

    def handle_HEADER(self, symbols):
        if len(symbols) > 0:
            self.header_code = symbols[0][1][0]

        return 0

    def handle_EXTERN(self, symbols):
        token_name = symbols[2][1][0]

        self.externs.add(token_name)

        return 0

    def handle_TOKEN(self, symbols):
        token_name = symbols[0][1][0]
        token_regex = symbols[4][1][0][1:-1]

        self.tokens.append((token_name, token_regex))
        return 0

    def handle_GRAMMAR(self, symbols):
        grammar = symbols[0][1][0]
        productions = symbols[5][2]
        return_type = symbols[2][2]

        codeblock = ""
        if symbols[-1][1][1] == "codeblock":
            codeblock = symbols[-1][1][0]

        if grammar in self.grammars:
            raise DuplicateVariable(f"{grammar} is already defined!")

        self.grammars[grammar] = (productions, codeblock, return_type)
        return 0

    def handle_PRODUCTIONS(self, symbols):
        production = symbols[0][2]

        if len(symbols) == 4:
            prev_productions = symbols[3][2]
            return [production] + prev_productions

        return [production]

    def handle_SYMBOL(self, symbols):
        new_symbol = (symbols[0][1][0])
        rename = symbols[2][2]
        symbol = [(new_symbol, rename)]
        if len(symbols) == 4:
            prev_symbols = symbols[3][2]
            return symbol + prev_symbols

        return symbol

    def handle_RENAME(self, symbols):
        if len(symbols) == 0:
            return ""

        return symbols[1][1][0]

    def handle_TYPE(self, symbols):
        if len(symbols) == 0:
            return ""

        return symbols[0][1][0]

    def handle_AMBIGUITY_CHECK(self, symbols):
        self.lexer_ambiguity = symbols[2][1][0]
        return 0

    def handle_SPACE(self, symbols):
        return 0

    def handleGrammar(self, nonterminal, symbols):
        if nonterminal == "DEFNS":
            return self.handle_DEFNS(symbols)
        elif nonterminal == "DEFN":
            return self.handle_DEFN(symbols)
        elif nonterminal == "HEADER":
            return self.handle_HEADER(symbols)
        elif nonterminal == "EXTERN":
            return self.handle_EXTERN(symbols)
        elif nonterminal == "TOKEN":
            return self.handle_TOKEN(symbols)
        elif nonterminal == "GRAMMAR":
            return self.handle_GRAMMAR(symbols)
        elif nonterminal == "PRODUCTIONS":
            return self.handle_PRODUCTIONS(symbols)
        elif nonterminal == "SYMBOL":
            return self.handle_SYMBOL(symbols)
        elif nonterminal == "RENAME":
            return self.handle_RENAME(symbols)
        elif nonterminal == "TYPE":
            return self.handle_TYPE(symbols)
        elif nonterminal == "AMBIGUITY_CHECK":
            return self.handle_AMBIGUITY_CHECK(symbols)
        elif nonterminal == "SPACE":
            return self.handle_SPACE(symbols)
        elif nonterminal == "START":
            return self.handle_START(symbols)
        else:
            raise ApplicationError(f"{nonterminal} handling is not defined!")