import copy
from utils import *

EPSILON_TRANSITION_INDEX = 95

def ascii_char_index(c):
    return ord(c) - 32

class State:
    def __init__(self):
        self.transition_matrix = [[] for _ in range(96)]
        self.transitions_catalog = dict()
        self.attributes = set()

    def add_attribute(self, attrib):
        self.attributes.add(attrib)

    def add_attributes(self, attribs):
        self.attributes.update(attribs)

    def has_attribute(self, attrib):
        return attrib in self.attributes

    def clear_attributes(self):
        self.attributes = set()

    def get_attributes(self):
        return self.attributes.copy()

    def shift_state_indices(self, shift_amount):
        for i in range(len(self.transition_matrix)):
            self.transition_matrix[i] = [j + shift_amount for j in self.transition_matrix[i]]

    def get_transition_matrix(self):
        return self.transition_matrix

    def append_transition_catalog(self, transition, next_state):
        if next_state in self.transitions_catalog:
            self.transitions_catalog[next_state].bitor(transition)
        else:
            self.transitions_catalog[next_state] = transition

    def new_transition(self, transition, next_state):
        self.append_transition_catalog(transition, next_state)
        for i in range(96):
            bit = transition.get_bit(i)
            if bit > 0:
                self.transition_matrix[i].append(next_state)

    def next_state_id(self, c):
        char_idx = ascii_char_index(c)
        return self.transition_matrix[char_idx]

    def has_epsilon_transition(self):
        return len(self.transition_matrix[-1]) > 0

    def get_epsilon_transitions(self):
        return self.transition_matrix[-1]

    # definately not efficient, do not use in non-debug mode
    def __str__(self):
        transitions = []
        for state, bitmap in self.transitions_catalog.items():
            transitions.append(f"{bitmap} => {state}")

        transitions_str = ", ".join(transitions)
        attribs_str = ",".join([ str(attrib) for attrib in list(self.attributes)])
        return f"[{transitions_str}] <{attribs_str}>"

class NFA:
    def __init__(self, nfa_lst=None):
        self.states = [State()]

        if nfa_lst is not None:
            epsilon_transition = BitMap("")
            epsilon_transition.set_epsilon_bit()
            shift_counter = 1
            for nfa in nfa_lst:
                for each_state in nfa.states:
                    copy_state = copy.copy(each_state)
                    copy_state.shift_state_indices(shift_counter)
                    self.states.append(copy_state)

                self.new_transitions(0, shift_counter, epsilon_transition)
                shift_counter = len(self.states)

        self.curr_state = 0
        self.epsilon_closures = dict()

    def reset(self):
        self.curr_state = 0

    def add_state_attribute(self, state, attrib):
        self.states[state].add_attribute(attrib)

    def add_state_attributes(self, state, attribs):
        self.states[state].add_attributes(attribs)

    def state_has_attribute(self, state, attrib):
        return self.states[state].has_attribute(attrib)

    def state_clear_attributes(self, state):
        self.states[state].clear_attributes()

    def get_state_attributes(self, state):
        return self.states[state].get_attributes()

    def new_transitions(self, fromstate, tostate, transitions):
        if fromstate >= len(self.states) or fromstate < 0:
            raise IndexError("NFA state index out of range in .new_transitions()")
        if tostate >= len(self.states) or tostate < 0:
            raise IndexError("NFA state index out of range in .new_transitions()")

        self.states[fromstate].new_transition(transitions, tostate)

    def new_state(self, prev, transitions):
        if prev >= len(self.states) or prev < 0:
            raise IndexError("NFA state index out of range in .new_state()")

        state_id = len(self.states)

        self.states.append(State())
        self.states[prev].new_transition(transitions, state_id)

        return state_id

    def get_current_state(self):
        return self.curr_state

    def step(self, char):
        if self.states[self.curr_state].has_epsilon_transition():
            raise InvalidParse("Epsilon transition detected. Only DFA can be traversed!")

        possible_states = self.states[self.curr_state].next_state_id(char)
        if len(possible_states) == 0:
            raise InvalidParse("DFA has rejected the sequence!")

        elif len(possible_states) == 1:
            self.curr_state = possible_states[0]

        else:
            raise InvalidParse("Multiple paths detected. Only DFA can be traversed!")

    def display(self):
        for i, state in enumerate(self.states):
            print(f"state {i}: {state}")

    def gen_dfa(self):
        self.epsilon_closures = dict()

        dfa = NFA()

        open_set = dict()
        closed_set = dict()

        open_set[frozenset(self.compute_epsilon_closures(0))] = 0

        while len(open_set) > 0:
            closure_states, dfa_state = open_set.popitem()
            closed_set[closure_states] = dfa_state

            dfa_transitions = [set() for _ in range(95)]
            for state in closure_states:
                transitions = self.states[state].get_transition_matrix()
                for i, tostates in enumerate(transitions):
                    if i == 95:
                        continue
                    dfa_transitions[i].update(tostates)
                    for tostate in tostates:
                        dfa_transitions[i].update(self.compute_epsilon_closures(tostate))

            for i, states in enumerate(dfa_transitions):
                if len(states) == 0:
                    continue
                state_set = frozenset(states)
                transition_bitmap = BitMap(i)
                if state_set in open_set:
                    dfa.new_transitions(dfa_state, open_set[state_set], transition_bitmap)
                elif state_set in closed_set:
                    dfa.new_transitions(dfa_state, closed_set[state_set], transition_bitmap)
                else:
                    new_state = dfa.new_state(dfa_state, transition_bitmap)
                    for each_state in states:
                        dfa.add_state_attributes(new_state, self.states[each_state].get_attributes())
                    open_set[state_set] = new_state

        return dfa

    def partition_states_by_attrib(self):
        state_attributes = dict()
        for i, state in enumerate(self.states):
            attribs = frozenset(state.get_attributes())
            if attribs in state_attributes:
                state_attributes[attribs].add(i)
            else:
                state_attributes[attribs] = {i}

        return [v for k, v in state_attributes.items()]

    def state_partition_lookup_table(self, partition):
        lookup_table = [0 for _ in self.states]
        for i, group in enumerate(partition):
            for state in group:
                if state < 0 or state >= len(self.states):
                    raise IndexError("DFA state index out of range in .state_partition_lookup_table()")

                lookup_table[state] = i

        return lookup_table

    def gen_minimal_dfa(self):
        partitions = self.partition_states_by_attrib()
        lookup_table = self.state_partition_lookup_table(partitions)

        # table size: num states x num symbols
        table = [[-1 for _ in range(95)] for _ in self.states]

        while True:
            # fill out the table
            for i, state in enumerate(self.states):
                transition_matrix = state.get_transition_matrix()
                for j, next_states in enumerate(transition_matrix):
                    # skip over epsilon transition
                    if j == EPSILON_TRANSITION_INDEX:
                        if len(next_states) == 0:
                            continue
                        else:
                            raise InvalidParse("Epsilon transition detected. Only DFA can be minimized!")

                    # nfa detection
                    if len(next_states) > 1:
                        raise InvalidParse("Multiple paths detected. Only DFA can be minimized!")

                    # filling out the table
                    if len(next_states) == 0:
                        table[i][j] = -1
                    else:
                        table[i][j] = lookup_table[next_states[0]]

            # re-partition the states
            new_partition = []
            for group in partitions:
                dictionary = dict()
                for state in group:
                    state_transition_group = tuple(table[state])
                    if state_transition_group in dictionary:
                        dictionary[state_transition_group].add(state)
                    else:
                        dictionary[state_transition_group] = {state}

                for _, group in dictionary.items():
                    new_partition.append(group)

            is_stable = new_partition == partitions

            partitions = new_partition
            lookup_table = self.state_partition_lookup_table(partitions)

            if is_stable:
                break

        # construct the minimal dfa
        minimal_dfa = NFA()

        state_queue = dict()
        completed_states = dict()

        state_queue[lookup_table[0]] = 0

        while len(state_queue) > 0:
            group_id, group_state = state_queue.popitem()
            completed_states[group_id] = group_state

            first_state_in_group = next(iter(partitions[group_id]))
            group_attribs = self.states[first_state_in_group].get_attributes()
            minimal_dfa.add_state_attributes(group_state, group_attribs)

            for i, transition in enumerate(table[first_state_in_group]):
                if transition == -1:
                    continue

                transition_bitmap = BitMap(chr(i + 32))
                if transition in state_queue:
                    minimal_dfa.new_transitions(group_state, state_queue[transition], transition_bitmap)
                elif transition in completed_states:
                    minimal_dfa.new_transitions(group_state, completed_states[transition], transition_bitmap)
                else:
                    new_state = minimal_dfa.new_state(group_state, transition_bitmap)
                    state_queue[transition] = new_state

        return minimal_dfa

    def compute_epsilon_closures(self, idx):
        if idx in self.epsilon_closures:
            return self.epsilon_closures[idx]

        found_states = set()
        found_states.add(idx)
        epsilon_transitions = self.states[idx].get_epsilon_transitions()
        for state in epsilon_transitions:
            found_states.update(self.compute_epsilon_closures(state))
            found_states.add(state)

        self.epsilon_closures[idx] = found_states
        return found_states
