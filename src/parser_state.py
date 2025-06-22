from utils import *

# TODO: create LRProduction to abstract the productions
    # should generate LRItem
    # should be print-able

class LRItem:
    def __init__(self, nonterminal, symbols, lookaheads):
        self.nonterminal = nonterminal
        self.symbols = symbols # rule: [(nonterminal?, symbol)]
        self.dot_position = 0
        self.lookaheads = lookaheads

    def copy(self):
        new_copy = LRItem(self.nonterminal, self.symbols, self.lookaheads.copy())
        new_copy.dot_position = self.dot_position

        return new_copy

    def is_complete(self):
        return self.dot_position >= len(self.symbols)

    def shift_dot(self):
        if self.is_complete():
            raise ApplicationError("An LR Item has encountered an error!")

        self.dot_position += 1

    def get_production(self):
        return (self.nonterminal, tuple(self.symbols))

    def get_next_symbol(self):
        return self.symbols[self.dot_position]

    def eval_next_symbol_lookaheads(self, grammar):
        lookahead_set = set()
        
        inherit_parent_lookahead = True
        for i in range(self.dot_position + 1, len(self.symbols)):
            next_symbol = self.symbols[i][1]
            if not self.symbols[i][0]:
                lookahead_set.add(next_symbol)
                inherit_parent_lookahead = False
                break

            first_set = grammar.get_FIRST_set(next_symbol)
            lookahead_set.update(first_set)

            if not grammar.contains_epsilon(next_symbol):
                inherit_parent_lookahead = False
                break

        if inherit_parent_lookahead:
            lookahead_set.update(self.lookaheads)

        return lookahead_set

    def get_lookaheads(self):
        return self.lookaheads

    def get_closure_items(self, grammar):
        closure_set = set()
        if self.is_complete():
            return closure_set

        next_symbol = self.get_next_symbol()
        if not next_symbol[0]:
            return closure_set

        lookahead_set = self.eval_next_symbol_lookaheads(grammar)

        closure_nonterminal = next_symbol[1]
        grammar_rules = grammar.get_rules(closure_nonterminal)
        if grammar_rules is None:
            return closure_set

        for rule in grammar_rules:
            item = LRItem(closure_nonterminal, rule, lookahead_set)
            closure_set.add(item)

        return closure_set

    def __hash__(self):
        return hash((self.nonterminal, tuple(self.symbols), self.dot_position, frozenset(self.lookaheads)))

    def __eq__(self, other):
        if self.nonterminal != other.nonterminal:
            return False

        if self.dot_position != other.dot_position:
            return False

        if self.symbols != other.symbols:
            return False

        if self.lookaheads != other.lookaheads:
            return False

        return True

    def __str__(self):
        symbol_str = ["$" + symbol[1] if symbol[0] else symbol[1] for symbol in self.symbols]
        return f"{self.nonterminal} => {' '.join(symbol_str)} ,LA={''.join(self.lookaheads)}"

class ParserState:
    def __init__(self, items, grammar):
        self.items = items
        self.grammar = grammar

        # new items is subset of items
        new_items = self.items.copy()
        while len(new_items) > 0:
            curr_item = new_items.pop()

            if curr_item.is_complete():
                continue

            closure_items = curr_item.get_closure_items(grammar)
            for new_item in closure_items:
                if new_item in self.items:
                    continue

                self.items.add(new_item)
                new_items.add(new_item)

    def get_goto_states(self):
        transitions = dict()

        for item in self.items:
            if item.is_complete():
                continue

            next_symbol = item.get_next_symbol()
            new_item = item.copy()
            new_item.shift_dot()
            if next_symbol in transitions:
                transitions[next_symbol].add(new_item)
            else:
                transitions[next_symbol] = set([new_item])

        new_states = []
        for symbol, item in transitions.items():
            new_state = ParserState(item, self.grammar)
            new_states.append((symbol, new_state))

        return new_states

    def get_completed_items(self):
        completed_items = set()

        for item in self.items:
            if not item.is_complete():
                continue

            completed_items.add(item)

        return completed_items

    def __hash__(self):
        hashable_set = frozenset(self.items)
        return hash(hashable_set)

    def __eq__(self, other):
        return self.items == other.items
