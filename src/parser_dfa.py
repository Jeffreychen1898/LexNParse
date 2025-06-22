from parser_state import ParserState, LRItem
from parse_table import ParseTable

class ParserDFA:
    def __init__(self, grammar, start_symbol):
        # create the initial state
        start_sym = (True, start_symbol)
        start_items = [LRItem(start_symbol, rule, {"$"}) for rule in grammar.get_rules(start_symbol)]

        start_state = ParserState(set(start_items), grammar)

        self.states = [start_state]

        self.parse_table = ParseTable()

        self.reduce_productions = []

        # build the dfa until all transitions are covered
        open_set = dict()
        close_set = dict()

        open_set[start_state] = 0

        reduce_productions_id = dict()

        while len(open_set) > 0:
            curr_state, curr_state_id = open_set.popitem()
            close_set[curr_state] = curr_state_id

            goto_states = curr_state.get_goto_states()

            # reduce
            for item in curr_state.get_completed_items():
                for lookahead in item.get_lookaheads():
                    production_id = -1
                    production = item.get_production()
                    if production in reduce_productions_id:
                        production_id = reduce_productions_id[production]
                    else:
                        production_id = len(self.reduce_productions)
                        self.reduce_productions.append(production)
                        reduce_productions_id[production] = production_id

                    self.parse_table.insert_entry(curr_state_id, (False, lookahead), ("r", production_id))

            for (symbol, goto_state) in goto_states:
                if goto_state in open_set:
                    goto_state_id = open_set[goto_state]
                    action = ("g" if symbol[0] else "s", goto_state_id)
                    self.parse_table.insert_entry(curr_state_id, symbol, action)
                    # push transition
                elif goto_state in close_set:
                    goto_state_id = close_set[goto_state]
                    action = ("g" if symbol[0] else "s", goto_state_id)
                    self.parse_table.insert_entry(curr_state_id, symbol, action)
                    # push transition
                else:
                    new_state_id = len(self.states)
                    self.states.append(goto_state)
                    open_set[goto_state] = new_state_id

                    action = ("g" if symbol[0] else "s", new_state_id)
                    self.parse_table.insert_entry(curr_state_id, symbol, action)
                    # push transition

        for i, item in enumerate(self.reduce_productions):
            print(f"{i}: {item}")
        self.parse_table.display()
