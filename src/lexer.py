from utils import BitMap, InvalidParse
import strsplit
from regex_sequence import RegexSequence

from nfa import NFA

LEXER_AMBIGUITY_STRICT = "strict"
LEXER_AMBIGUITY_FIRST = "first"
LEXER_AMBIGUITY_LAST = "last"

class Lexer:
    def __init__(self, tokens, ambig_resolution=LEXER_AMBIGUITY_STRICT):
        self.ambiguity_resolution = ambig_resolution
        self.assert_valid_ambiguity_resolution()

        self.regex_sequences = []
        for i, (token_name, token_regex) in enumerate(tokens):
            split_str = strsplit.StringSplit(token_regex)
            tokens, types = split_str.run()

            tokens, types = self.regex_rewriting(tokens, types)
            regex_sequence = RegexSequence(tokens, types, (token_name, i))
            regex_sequence.generate_nfa()

            self.regex_sequences.append(regex_sequence)

        nfa = NFA(nfa_lst=[r.nfa for r in self.regex_sequences])
        dfa = nfa.gen_dfa()
        self.dfa = dfa.gen_minimal_dfa()

    def tokenize(self, input_stream):
        token_sequence = []
        token_value = ""

        prev_accept = None
        prev_index = 0

        curr_index = 0
        while curr_index < len(input_stream):
            try:
                self.dfa.step(input_stream[curr_index])
            except InvalidParse:
                if prev_accept is None:
                    raise InvalidParse("Error on parsing token!")
                token_sequence.append(prev_accept)
                curr_index = prev_index

                prev_accept = None
                token_value = ""
                self.dfa.reset()
                curr_index += 1
                continue

            token_value += input_stream[curr_index]

            state_attribs = self.dfa.get_state_attributes(self.dfa.get_current_state())
            select_attrib = self.select_state_attrib(state_attribs)
            if select_attrib:
                prev_accept = (token_value, select_attrib)
                prev_index = curr_index
            elif curr_index == len(input_stream) - 1:
                if prev_accept is None:
                    raise InvalidParse("Error on parsing token!")
                token_sequence.append(prev_accept)
                curr_index = prev_index

                prev_accept = None
                token_value = ""
                self.dfa.reset()

            curr_index += 1

        if prev_accept is None or prev_index != len(input_stream) - 1:
            raise InvalidParse("Lexer has rejected the input stream")
        self.dfa.reset()

        token_sequence.append(prev_accept)

        return token_sequence

    def select_state_attrib(self, state_attribs):
        if self.ambiguity_resolution == LEXER_AMBIGUITY_STRICT:
            if len(state_attribs) > 1:
                raise InvalidParse("Ambiguity detected while tokenizing input stream!")

            if state_attribs:
                return state_attribs.pop()[0]
            else:
                return None

        elif self.ambiguity_resolution == LEXER_AMBIGUITY_FIRST:
            if len(state_attribs) > 0:
                return min(state_attribs, key=lambda elem: elem[1])[0]
            else:
                return None

        elif self.ambiguity_resolution == LEXER_AMBIGUITY_LAST:
            if len(state_attribs) > 0:
                return max(state_attribs, key=lambda elem: elem[1])[0]
            else:
                return None

        return None

    def assert_valid_ambiguity_resolution(self):
        if self.ambiguity_resolution == LEXER_AMBIGUITY_STRICT:
            return
        if self.ambiguity_resolution == LEXER_AMBIGUITY_FIRST:
            return
        if self.ambiguity_resolution == LEXER_AMBIGUITY_LAST:
            return

        raise InvalidParse(f"Invalid lexer ambiguity resolution {self.ambiguity_resolution}")

    def get_dfa(self):
        return self.dfa

    def regex_rewriting(self, tokens, types):
        rewritten_tokens = []
        rewritten_types = []

        for tk, ty in zip(tokens, types):
            if type(tk) is list:
                sub_tks, sub_tys = self.regex_rewriting(tk, ty)
                rewritten_tokens.append(sub_tks)
                rewritten_types.append(sub_tys)

            elif ty != strsplit.SYMBOL_TYPE_RULE:
                rewritten_tokens.append(tk)
                rewritten_types.append(ty)

            elif tk == "+":
                if len(rewritten_tokens) == 0 or rewritten_types[-1] == strsplit.SYMBOL_TYPE_RULE:
                    raise InvalidParse("The regex rule: \"+\" must be preceded by a token!")

                # example: a+ => aa*
                rewritten_tokens.append(rewritten_tokens[-1])
                rewritten_types.append(rewritten_types[-1])
                rewritten_tokens.append("*")
                rewritten_types.append(strsplit.SYMBOL_TYPE_RULE)

            else:
                rewritten_tokens.append(tk)
                rewritten_types.append(ty)

            prev_tk = tk
            prev_ty = ty

        return (rewritten_tokens, rewritten_types)

    def construct_dfa(self):
        regex_sequences = []
        for token_type, token_defn in self.lexer_tokens.items():
            split_str = strsplit.StringSplit(token_defn[1:-1])
            tokens, types = split_str.run()

            tokens, types = self.regex_rewriting(tokens, types)
            regex_sequence = RegexSequence(tokens, types, token_type)
            regex_sequence.generate_nfa()

            regex_sequences.append(regex_sequence)

        self.lexer_dfa = NFA(nfa_lst=[r.nfa for r in regex_sequences])
        self.lexer_dfa = self.lexer_dfa.gen_dfa()
        self.lexer_dfa = self.lexer_dfa.gen_minimal_dfa()

        self.lexer_dfa.display()
