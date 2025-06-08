"""
DFA machine:

A => B on (
A => C on [
B => A on ) and count = 0
C => A on ]
A => A on not ()[]
B => B on not )
C => C on not ()[]

on state A, push previous symbol
on state B, record p
"""
from nfa import NFA
from utils import BitMap, InvalidParse

ESCAPE_SYMBOL = "\\"

# TODO: handle ^$ beg and end of line
RULES_SYMBOLS = {"^", "-", "*", "+", ".", "?", "|"}
EVAL_SYMBOLS = {"."}

SYMBOL_TYPE_TOKEN = "token"
SYMBOL_TYPE_RULE = "rule"
SYMBOL_TYPE_MATCHES = "matches"
SYMBOL_TYPE_EVAL = "eval"

MATCHES_LITERAL_TAG = "|"
MATCHES_RULE_TAG = ":"

class StringSplit:
    def __init__(self, string):
        self.str = string
        self.tokens = []

        self.dfa = NFA()
        self.state_a = 0
        self.state_b = 1
        self.state_c = 2
        self.create_dfa()

    def run(self):
        replaced_tokens = self.escape_substution()
        split, types = self.split(self.str)
        replace_idx = self.tag_tokens(split, types, replaced_tokens, 0)

        if replace_idx != len(replaced_tokens):
            raise Exception("An unexpected error has occured!")

        return split, types

    def escape_substution(self):
        new_str = ""
        replaced_tokens = []
        
        sub_enabled = False
        for c in self.str:
            # following character is escaped
            if sub_enabled:
                new_str += ESCAPE_SYMBOL
                replaced_tokens.append(c)
                sub_enabled = False
                continue

            # current character is the escape symbol
            if c == ESCAPE_SYMBOL:
                sub_enabled = True
                continue

            # append character
            new_str += c

        self.str = new_str
        return replaced_tokens

    def tag_tokens(self, split, types, replaced_tk, replaced_idx):
        for i, (s, t) in enumerate(zip(split, types)):
            if type(s) is list:
                replaced_idx = self.tag_tokens(s, t, replaced_tk, replaced_idx)
                continue

            #print(s) # TODO: left off here
            if s == ESCAPE_SYMBOL:
                split[i] = replaced_tk[replaced_idx]
                types[i] = SYMBOL_TYPE_TOKEN
                replaced_idx += 1

            elif s in RULES_SYMBOLS:
                if s in EVAL_SYMBOLS:
                    types[i] = SYMBOL_TYPE_EVAL
                else:
                    types[i] = SYMBOL_TYPE_RULE

            elif t == SYMBOL_TYPE_MATCHES:
                replaced_idx, matches_tagged = self.tag_matches(s, replaced_tk, replaced_idx)
                split[i] = matches_tagged

        return replaced_idx

    def tag_matches(self, matches, replaced_tk, replaced_idx):
        new_str = ""
        for s in matches:
            if s == ESCAPE_SYMBOL:
                new_str += MATCHES_LITERAL_TAG + replaced_tk[replaced_idx]
                replaced_idx += 1
                continue

            if s in RULES_SYMBOLS:
                new_str += MATCHES_RULE_TAG + s
            else:
                new_str += MATCHES_LITERAL_TAG + s

        return (replaced_idx, new_str)

    def split(self, string):
        record = ""
        str_split = []
        types = []

        open_paren_cnt = 0
        for c in string:
            symbol = c
            # modify symbol to irrelevant symbol on open_paren_cnt > 0
            if open_paren_cnt > 1:
                symbol = " "

            # run the dfa
            self.dfa.step(symbol)

            # track the number of parenthesis
            if c == "(":
                open_paren_cnt += 1
            elif c == ")":
                open_paren_cnt -= 1

            # perform actions when encountering certain states
            if self.dfa.get_current_state() == self.state_a:
                if c == ")":
                    sub_str, sub_str_types = self.split(record[1:])
                    str_split.append(sub_str)
                    types.append(sub_str_types)
                    record = ""
                elif c == "]":
                    str_split.append(record[1:])
                    types.append(SYMBOL_TYPE_MATCHES)
                    record = ""
                else:
                    str_split.append(c)
                    types.append(SYMBOL_TYPE_TOKEN)

            elif self.dfa.get_current_state() == self.state_b:
                record += c

            elif self.dfa.get_current_state() == self.state_c:
                record += c

        return (str_split, types)

    def create_dfa(self):
        # transition to other states
        a_to_b = BitMap("(")
        a_to_c = BitMap("[")
        b_to_a = BitMap(")")
        c_to_a = BitMap("]")

        # transition A => A and C => C
        to_self = BitMap("()[]")
        to_self.set_epsilon_bit()
        to_self.flip_bits()

        # transition B => B
        b_to_self = BitMap(")")
        b_to_self.set_epsilon_bit()
        b_to_self.flip_bits()

        # create the states
        self.state_a = 0
        self.state_b = self.dfa.new_state(self.state_a, a_to_b)
        self.state_c = self.dfa.new_state(self.state_a, a_to_c)

        # transitions back to A
        self.dfa.new_transitions(self.state_b, self.state_a, b_to_a)
        self.dfa.new_transitions(self.state_c, self.state_a, c_to_a)

        # transitions to self
        self.dfa.new_transitions(self.state_a, self.state_a, to_self)
        self.dfa.new_transitions(self.state_b, self.state_b, to_self)
        self.dfa.new_transitions(self.state_c, self.state_c, to_self)