from utils import *

# TODO: create LRProduction to abstract the productions
    # should generate LRItem
    # should be print-able

# TODO have LRItem inherit LR0Item

class LR0Item:
    def __init__(self, nonterminal, symbols):
        self.nonterminal = nonterminal
        self.symbols = symbols
        self.dot_position = 0

    def get_symbols(self):
        return self.symbols

    def get_nonterminal(self):
        return self.nonterminal

    def __hash__(self):
        return hash((self.nonterminal, tuple(self.symbols), self.dot_position))

    def __eq__(self, other):
        if self.nonterminal != other.nonterminal:
            return False

        if self.symbols != other.symbols:
            return False

        if self.dot_position != other.dot_position:
            return False

        return True

    def __str__(self):
        symbol_str = ["$" + symbol[1] if symbol[0] else symbol[1] for symbol in self.symbols]
        return f"{self.nonterminal} => {' '.join(symbol_str)}"

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

    def merge(self, other):
        self.lookaheads.update(other.lookaheads)

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

    def get_lr0_item(self):
        new_lr0_item = LR0Item(self.nonterminal, self.symbols)
        new_lr0_item.dot_position = self.dot_position
        return new_lr0_item

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
        return f"{self.nonterminal} => {' '.join(symbol_str[:self.dot_position])} . {' '.join(symbol_str[self.dot_position:])} ,LA={''.join(self.lookaheads)}"

# TODO: write merge and for parser state, join similar items
class ParserState:
    def __init__(self, items, grammar):
        self.lr_items = dict()
        self.grammar = grammar

        # ensure similar items are merged
        for item in items:
            item_core = item.get_lr0_item()
            if item_core in self.lr_items:
                self.lr_items[item_core].merge(item)
            else:
                self.lr_items[item_core] = item

        # new items is subset of items
        new_lr_items = self.lr_items.copy()
        while len(new_lr_items) > 0:
            curr_item_core, curr_item = new_lr_items.popitem()

            if curr_item.is_complete():
                continue

            closure_items = curr_item.get_closure_items(grammar)
            for new_item in closure_items:
                new_item_core = new_item.get_lr0_item()
                if new_item_core in self.lr_items:
                    self.lr_items[new_item_core].merge(new_item)
                    continue

                self.lr_items[new_item_core] = new_item
                new_lr_items[new_item_core] = new_item

    def merge(self, other):
        if len(other.lr_items) != len(self.lr_items):
            raise ApplicationError("Parser state cannot be merged! Invalid number of items")

        for item_core, item in other.lr_items.items():
            if item_core not in self.lr_items:
                raise ApplicationError("Parser state cannot be merged! Invalid items detected!")

            self.lr_items[item_core].merge(item)

    def get_item_cores(self):
        return frozenset(self.lr_items.keys())

    def get_goto_states(self):
        transitions = dict()

        for _, item in self.lr_items.items():
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

        for item_core, item in self.lr_items.items():
            if not item.is_complete():
                continue

            completed_items.add(item)

        return completed_items

    def display(self):
        for lr_item in self.lr_items.values():
            print(str(lr_item))

    def __hash__(self):
        hashable_set = frozenset(self.lr_items.values())
        return hash(hashable_set)

    def __eq__(self, other):
        return self.lr_items == other.lr_items
