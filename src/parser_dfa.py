from parser_state import ParserState, LRProduction
from parse_table import ParseTable

class ParserDFA:
    def __init__(self, grammar, start_symbol):
        # create the initial state
        start_sym = (True, start_symbol)
        start_productions = [LRProduction(start_symbol, rule) for rule in grammar.get_rules(start_symbol)]

        start_state = ParserState(set(start_productions), grammar)

        self.states = [start_state]

        self.parse_table = ParseTable()

        # build the dfa until all transitions are covered
        open_set = dict()
        close_set = dict()

        open_set[start_state] = 0

        while len(open_set) > 0:
            curr_state, curr_state_id = open_set.popitem()
            close_set[curr_state] = curr_state_id

            goto_states = curr_state.get_goto_states()
            if len(goto_states) == 0:
                self.parse_table.insert_entry(curr_state_id, (False, "\\"), ("r", 0))
            for (symbol, goto_state) in goto_states:
                if goto_state in open_set:
                    goto_state_id = open_set[goto_state]
                    action = ("s", goto_state_id)
                    self.parse_table.insert_entry(curr_state_id, symbol, action)
                    # push transition
                elif goto_state in close_set:
                    goto_state_id = close_set[goto_state]
                    action = ("s", goto_state_id)
                    self.parse_table.insert_entry(curr_state_id, symbol, action)
                    # push transition
                else:
                    new_state_id = len(self.states)
                    self.states.append(goto_state)
                    open_set[goto_state] = new_state_id

                    action = ("s", new_state_id)
                    self.parse_table.insert_entry(curr_state_id, symbol, action)
                    # push transition

        self.parse_table.display()
