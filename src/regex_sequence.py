from utils import *
from nfa import NFA

# TODO: RegexSubsequence and BitMap should share a class (RegexItem) with rules set
class RegexSubsequence:
    def __init__(self):
        self.sequences = []
        self.rule = None

        self.matches_dfa = NFA()
        self.matches_states = [0 for _ in range(9)]
        self.matches_accept_states = {}
        self.create_matches_dfa()

    def resolve(self, tokens, types):
        tokens_chunk = []
        types_chunk = []
        # split the tokens
        l_ptr = 0
        r_ptr = 0
        while r_ptr < len(tokens):
            if tokens[r_ptr] == "|" and types[r_ptr] == "rule":
                tokens_chunk.append(tokens[l_ptr:r_ptr])
                types_chunk.append(types[l_ptr:r_ptr])
                l_ptr = r_ptr + 1

            r_ptr += 1

        if l_ptr < r_ptr:
            tokens_chunk.append(tokens[l_ptr:r_ptr])
            types_chunk.append(types[l_ptr:r_ptr])
        else:
            raise InvalidParse("Unexpected token: |")

        # evaluate bitmaps
        for tks, tys in zip(tokens_chunk, types_chunk):
            bitmaps = self.eval_bitmaps(tks, tys)
            self.sequences.append(bitmaps)

    def count(self):
        return len(self.sequences)

    def __str__(self):
        seq_rules = self.rule if self.rule else ""
        chunk_strs = []
        for chunk in self.sequences:
            elem_strs = []
            for sequence in chunk:
                if type(sequence) is RegexSubsequence:
                    elem_strs.append(str(sequence))
                else:
                    rules_str = sequence.rule if sequence.rule else ""
                    elem_strs.append(f"Token<{rules_str}>")

            elem_str = ", ".join(elem_strs)
            chunk_strs.append(f"[{elem_str}]")

        chunk_str = " | ".join(chunk_strs)
        return f"RegexSubsequence({chunk_str})<{seq_rules}>"

    def eval_bitmaps(self, tokens, types):
        bitmaps = []
        for tk, ty in zip(tokens, types):
            if type(tk) is list:
                nested_sequence = RegexSubsequence()
                nested_sequence.resolve(tk, ty)
                bitmaps.append(nested_sequence)
                continue

            if ty == "token":
                bitmaps.append(self.eval_token(tk))
            elif ty == "matches":
                bitmaps.append(self.eval_matches(tk))
            elif ty == "eval":
                bitmaps.append(self.eval_type(tk))
            elif ty == "rule":
                if tk not in "*?":
                    raise InvalidParse(f"Invalid token: {tk}")

                if type(bitmaps[-1]) is RegexSubsequence:
                    bitmaps[-1].rule = tk
                else:
                    bitmaps[-1].rule = tk

        return bitmaps

    def eval_matches(self, matches):
        self.matches_dfa.reset()

        # parse through the matches expression
        character_list = []
        should_negate = False
        for m in matches:
            self.matches_dfa.step(m)
            if self.matches_dfa.get_current_state() == self.matches_states[2]:
                should_negate = True
            elif self.matches_dfa.get_current_state() == self.matches_states[4]:
                character_list.append(m)
            elif self.matches_dfa.get_current_state() == self.matches_states[8]:
                character_list[-1] = (character_list[-1], m)

        if self.matches_dfa.get_current_state() not in self.matches_accept_states:
            raise InvalidParse("Incomplete expression inside match statement!")

        # generate the bitmap
        bitmap = BitMap("")
        for c in character_list:
            if type(c) is tuple:
                from_bit = ord(c[0]) - 32
                to_bit = ord(c[1]) - 32
                bitmap.set_bits(from_bit, to_bit)
            elif type(c) is str:
                bitmap.set_bit(ord(c) - 32)

        if should_negate:
            bitmap.set_epsilon_bit()
            bitmap.flip_bits()

        return bitmap

    def eval_token(self, token):
        bitmap = BitMap(token)
        return bitmap

    def eval_type(self, token):
        if token == ".":
            bitmap = BitMap("")
            bitmap.set_epsilon_bit()
            bitmap.flip_bits()
            return bitmap

        raise Exception("An unexpected error has occured!")

    def create_matches_dfa(self):
        transition_rule = BitMap(MATCHES_RULE_TAG)
        transition_caret = BitMap("^")
        transition_literal = BitMap(MATCHES_LITERAL_TAG)
        transition_dash = BitMap("-")
        transition_any = BitMap("")
        transition_any.set_epsilon_bit()
        transition_any.flip_bits()

        self.matches_states[0] = 0
        self.matches_states[1] = self.matches_dfa.new_state(self.matches_states[0], transition_rule)
        self.matches_states[2] = self.matches_dfa.new_state(self.matches_states[1], transition_caret)
        self.matches_states[3] = self.matches_dfa.new_state(self.matches_states[0], transition_literal)
        self.matches_states[4] = self.matches_dfa.new_state(self.matches_states[3], transition_any)
        self.matches_states[5] = self.matches_dfa.new_state(self.matches_states[4], transition_rule)
        self.matches_states[6] = self.matches_dfa.new_state(self.matches_states[5], transition_dash)
        self.matches_states[7] = self.matches_dfa.new_state(self.matches_states[6], transition_literal)
        self.matches_states[8] = self.matches_dfa.new_state(self.matches_states[7], transition_any)

        self.matches_dfa.new_transitions(self.matches_states[2], self.matches_states[3], transition_literal)
        self.matches_dfa.new_transitions(self.matches_states[4], self.matches_states[3], transition_literal)
        self.matches_dfa.new_transitions(self.matches_states[8], self.matches_states[3], transition_literal)

        self.matches_accept_states = {
            self.matches_states[4],
            self.matches_states[8]
        }

class RegexSequence:
    def __init__(self, tokens, types, accept_label):
        self.sequence = RegexSubsequence()
        self.sequence.resolve(tokens, types)

        self.nfa = None
        self.epsilon_bitmap = BitMap("")
        self.epsilon_bitmap.set_epsilon_bit()
        self.accept = accept_label

    def generate_nfa(self):
        self.nfa = NFA()

        last_node = self.parse_sequence_rule(0, self.sequence, toplevel=True)

    def generate_dfa(self):
        self.nfa = self.nfa.gen_dfa()

    # definitely need refactoring
    def parse_sequence_rule(self, prev_state, seq, toplevel=False):
        if seq.rule == "*":
            helper_node_a = self.nfa.new_state(prev_state, self.epsilon_bitmap)
            helper_node_b = self.nfa.new_state(helper_node_a, self.epsilon_bitmap)
            seq_node = self.parse_sequence_chain(helper_node_b, seq, toplevel=toplevel)
            helper_node_c = self.nfa.new_state(seq_node, self.epsilon_bitmap)

            self.nfa.new_transitions(helper_node_a, helper_node_c, self.epsilon_bitmap)
            self.nfa.new_transitions(seq_node, helper_node_b, self.epsilon_bitmap)

            return helper_node_c
        elif seq.rule == "?":
            helper_node_a = self.nfa.new_state(prev_state, self.epsilon_bitmap)
            seq_node = self.parse_sequence_chain(helper_node_a, seq, toplevel=toplevel)

            self.nfa.new_transitions(helper_node_a, seq_node, self.epsilon_bitmap)

            return seq_node
        else:
            return self.parse_sequence_chain(prev_state, seq, toplevel=toplevel)

    def parse_sequence_chain(self, prev_state, seqs, toplevel=False):
        begin_node = self.nfa.new_state(prev_state, self.epsilon_bitmap)
        end_node = None

        # if seqs is BitMap, ye definately need to refactor this
        if type(seqs) == BitMap:
            new_state = self.nfa.new_state(begin_node, seqs)
            end_node = self.nfa.new_state(new_state, self.epsilon_bitmap)

            return end_node

        # if seqs is actually a sequence
        for seq in seqs.sequences:
            # append the sequence
            prev_node = begin_node
            for item in seq:
                if type(item) is RegexSubsequence or item.rule is not None:
                    prev_node = self.parse_sequence_rule(prev_node, item)
                elif type(item) is BitMap:
                    prev_node = self.nfa.new_state(prev_node, item)
                else:
                    print("unreachable!")

            # connect the end node
            if end_node:
                self.nfa.new_transitions(prev_node, end_node, self.epsilon_bitmap)
            else:
                end_node = self.nfa.new_state(prev_node, self.epsilon_bitmap)
                if toplevel:
                    self.nfa.add_state_attribute(end_node, self.accept)

        if end_node:
            return end_node
        else:
            return begin_node
