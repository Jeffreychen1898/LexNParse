from utils import *

class LRProduction: # NOTE: LRItem is probably a more fitting name
    def __init__(self, nonterminal, symbols, lookaheads):
        self.nonterminal = nonterminal
        self.symbols = symbols # rule: [(nonterminal?, symbol)]
        self.dot_position = 0
        self.lookaheads = lookaheads

    def copy(self):
        new_copy = LRProduction(self.nonterminal, self.symbols, self.lookaheads.copy())
        new_copy.dot_position = self.dot_position

        return new_copy

    def is_complete(self):
        return self.dot_position >= len(self.symbols)

    def shift_dot(self):
        if self.is_complete():
            raise ApplicationError("An LR Production has encountered an error!")

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

    def get_closure_productions(self, grammar):
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

        # construct the LRProductions
        for rule in grammar_rules:
            production = LRProduction(closure_nonterminal, rule, lookahead_set)
            closure_set.add(production)

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
    def __init__(self, productions, grammar):
        self.productions = productions
        self.grammar = grammar

        # new productions is subset of productions
        new_productions = self.productions.copy()
        while len(new_productions) > 0:
            curr_production = new_productions.pop()

            if curr_production.is_complete():
                continue

            closure_productions = curr_production.get_closure_productions(grammar)
            for new_production in closure_productions:
                if new_production in self.productions:
                    continue

                self.productions.add(new_production)
                new_productions.add(new_production)

    def get_goto_states(self):
        transitions = dict()

        for production in self.productions:
            if production.is_complete():
                continue

            next_symbol = production.get_next_symbol()
            new_production = production.copy()
            new_production.shift_dot()
            if next_symbol in transitions:
                transitions[next_symbol].add(new_production)
            else:
                transitions[next_symbol] = set([new_production])

        new_states = []
        for symbol, production in transitions.items():
            new_state = ParserState(production, self.grammar)
            new_states.append((symbol, new_state))

        return new_states

    def get_completed_productions(self):
        completed_productions = set()

        for production in self.productions:
            if not production.is_complete():
                continue

            completed_productions.add(production)

        return completed_productions

    def __hash__(self):
        hashable_set = frozenset(self.productions)
        return hash(hashable_set)

    def __eq__(self, other):
        return self.productions == other.productions
