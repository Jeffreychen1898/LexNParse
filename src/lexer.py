from utils import BitMap, InvalidParse
import strsplit
from strsplit import StringSplit
from regex_sequence import RegexSequence

from nfa import NFA

TOKEN_DEFN_REGEX = "[a-zA-Z_$]+"

class Regex:
    def __init__(self, regex_string):
        self.regex = regex_string
        self.regex_tokenize = []
        # split string
        # rewriting

        # bitmap evaluation
            # matches
            # eval(.) and tokens
        # nfa generation
        # dfa conversion
        # minimal dfa

    def string_split(self, str):
        pass

class Lexer:
    def __init__(self, tokens):
        # split the string and tokenize
        """splitter = StringSplit("(0\-9+)*.a+[^0\\-9a-zAZ]*f?|bb")
        strs, types = splitter.run()

        # rewrite extension rules
        new_tks, new_tys = self.regex_rewriting(strs, types)
        regex_sequence = RegexSequence(new_tks, new_tys)
        regex_sequence.generate_dfa()

        regex_sequence.nfa.display()"""

        splitter1 = StringSplit("(0\-9+)*.a+[^0\\-9a-zAZ]*f?")
        strs1, types1 = splitter1.run()

        new_tks1, new_tys1 = self.regex_rewriting(strs1, types1)
        regex_sequence1 = RegexSequence(new_tks1, new_tys1, "long_seq")
        regex_sequence1.generate_nfa()

        #regex_sequence1.nfa.display()

        splitter2 = StringSplit("bb")
        strs2, types2 = splitter2.run()

        new_tks2, new_tys2 = self.regex_rewriting(strs2, types2)
        regex_sequence2 = RegexSequence(new_tks2, new_tys2, "bb")
        regex_sequence2.generate_nfa()

        #regex_sequence2.nfa.display()

        final_nfa = NFA(nfa_lst=[regex_sequence1.nfa, regex_sequence2.nfa])
        final_nfa = final_nfa.gen_dfa()
        final_nfa = final_nfa.gen_minimal_dfa()
        print("displaying final dfa")
        final_nfa.display()

        test_seq = "0-90-9paaa![]("
        for c in test_seq:
            final_nfa.step(c)

        print(final_nfa.get_state_attributes(final_nfa.get_current_state()))

    def complete_regex_parse(self, tks, tys, tbs):
        separated_tks = []
        separated_tys = []

        # split the regex by the | symbol into different chunks
        print("========")
        l_ptr = 0
        r_ptr = 0
        while r_ptr < len(tks):
            if tks[r_ptr] == "|" and tys[r_ptr] == "rule":
                separated_tks.append(tks[l_ptr:r_ptr])
                separated_tys.append(tys[l_ptr:r_ptr])
                l_ptr = r_ptr + 1
            r_ptr += 1

        if l_ptr < r_ptr:
            separated_tks.append(tks[l_ptr:r_ptr])
            separated_tys.append(tys[l_ptr:r_ptr])
        else:
            raise InvalidParse("Unexpected last rule |")

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

    def parse(self):
        pass

    def generate_dfa(self):
        pass
