from utils import BitMap, InvalidParse
import strsplit
from strsplit import StringSplit
from regex_sequence import RegexSequence

from nfa import NFA

TOKEN_REGEX = ["[a-zA-Z0-9_$]*", " *: *", "\".*\""]

class Lexer:
    def __init__(self, lexer_tokens):
        self.lexer_tokens = dict()
        self.lexer_dfa = None

        # generate nfa to parse the lexer file
        regex_sequences = []
        for i, tk_re in enumerate(TOKEN_REGEX):
            split_str = StringSplit(tk_re)
            tokens, types = split_str.run()

            tokens, types = self.regex_rewriting(tokens, types)
            regex_sequence = RegexSequence(tokens, types, str(i))
            regex_sequence.generate_nfa()

            regex_sequences.append(regex_sequence)

        nfa = NFA(nfa_lst=[r.nfa for r in regex_sequences])
        dfa = nfa.gen_dfa()
        dfa = dfa.gen_minimal_dfa()

        # parse the token rules
        for tk in lexer_tokens:
            token_seq = []
            tk_val = ""
            prev_accept = None
            prev_idx = 0
            curr_idx = 0
            while curr_idx < len(tk):
                try:
                    dfa.step(tk[curr_idx])
                except InvalidParse:
                    if prev_accept is None:
                        raise InvalidParse("Error on parsing token!")
                    token_seq.append(prev_accept)
                    curr_idx = prev_idx
                    prev_accept = None
                    tk_val = ""
                    dfa.reset()
                    curr_idx += 1
                    continue

                tk_val += tk[curr_idx]
                state_attribs = dfa.get_state_attributes(dfa.get_current_state())
                if len(state_attribs) > 1:
                    raise ApplicationError("Ambiguity detected in token regexes!")
                if state_attribs:
                    prev_accept = (tk_val, state_attribs.pop())
                    prev_idx = curr_idx

                curr_idx += 1


            if prev_accept is None or prev_idx != len(tk) - 1:
                raise InvalidParse("Error on parsing token!")
            token_seq.append(prev_accept)
            dfa.reset()

            # ensure the tokens are in the right order
            prev_tk = -1
            for tk in token_seq:
                if int(tk[1]) < prev_tk:
                    raise InvalidParse("Invalid Syntax in lexer file!")
                prev_tk = int(tk[1])

            if token_seq[0] in self.lexer_tokens:
                raise InvalidParse(f"Token {token_seq[0][0]} is already defined!")

            self.lexer_tokens[token_seq[0][0]] = token_seq[2][0]

        print(self.lexer_tokens)

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
            split_str = StringSplit(token_defn[1:-1])
            tokens, types = split_str.run()

            tokens, types = self.regex_rewriting(tokens, types)
            regex_sequence = RegexSequence(tokens, types, token_type)
            regex_sequence.generate_nfa()

            regex_sequences.append(regex_sequence)

        self.lexer_dfa = NFA(nfa_lst=[r.nfa for r in regex_sequences])
        self.lexer_dfa = self.lexer_dfa.gen_dfa()
        self.lexer_dfa = self.lexer_dfa.gen_minimal_dfa()

        self.lexer_dfa.display()
