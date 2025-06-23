from utils import *
from parser_state import ParserState, LRItem
from parse_table import ParseTable

class ParserDFA:
    def __init__(self, grammar, start_symbol):
        # create the initial state
        self.parse_table = ParseTable()
        self.productions = []

        start_sym = (True, start_symbol)
        start_items = [LRItem(start_symbol, rule, {"$"}) for rule in grammar.get_rules(start_symbol)]

        start_state = ParserState(set(start_items), grammar)

        self.states = []
        self.transitions = []

        self.generate_transitions(start_state)
        self.merge_states()
        self.generate_table()

        self.display()

    def generate_transitions(self, start):
        self.states = [start]
        self.transitions = [dict()]

        open_set = dict()
        close_set = dict()

        open_set[start] = 0

        while len(open_set) > 0:
            curr_state, curr_state_id = open_set.popitem()
            close_set[curr_state] = curr_state_id

            goto_states = curr_state.get_goto_states()

            for (symbol, goto_state) in goto_states:
                goto_state_id = len(self.states) # default assume new state

                if goto_state in open_set:
                    goto_state_id = open_set[goto_state]
                elif goto_state in close_set:
                    goto_state_id = close_set[goto_state]
                else:
                    self.states.append(goto_state)
                    self.transitions.append(dict())
                    open_set[goto_state] = goto_state_id

                self.transitions[curr_state_id][symbol] = goto_state_id

    def merge_states(self):
        new_states = []
        unique_states = dict()
        state_map = dict()

        # create new states
        for i, state in enumerate(self.states):
            state_core = state.get_item_cores()
            if state_core in unique_states:
                new_state_id = unique_states[state_core]
                new_states[new_state_id].merge(state)
                state_map[i] = new_state_id
            else:
                new_state_id = len(new_states)
                unique_states[state_core] = new_state_id
                new_states.append(state)
                state_map[i] = new_state_id

        # create new transitions
        new_transitions = [dict() for _ in new_states]
        for i, old_state_transition in enumerate(self.transitions):
            new_index = state_map[i]
            for symbol, goto_state_id in old_state_transition.items():
                goto_state_new_id = state_map[goto_state_id]
                new_transitions[new_index][symbol] = goto_state_new_id

        self.transitions = new_transitions
        self.states = new_states

    def generate_table(self):
        # add shift and goto actions
        for i, transition in enumerate(self.transitions):
            for symbol, goto_state_id in transition.items():
                action = ("g" if symbol[0] else "s", goto_state_id)
                self.parse_table.insert_entry(i, symbol, action)

        # add reduce actions
        production_ids = dict()
        for i, state in enumerate(self.states):
            complete_items = state.get_completed_items()
            for complete_item in complete_items:
                item_core = complete_item.get_lr0_item()
                production_id = None
                if item_core in production_ids:
                    production_id = production_ids[item_core]
                else:
                    production_id = len(self.productions)
                    self.productions.append(item_core)
                    production_ids[item_core] = production_id

                action = ("r", production_id)
                lookahead_symbols = complete_item.get_lookaheads()
                for lookahead in lookahead_symbols:
                    symbol = (False, lookahead)
                    self.parse_table.insert_entry(i, symbol, action)

    def display(self):
        for i, production in enumerate(self.productions):
            print(f"{i}: {production}")
        print("===")
        self.parse_table.display()
