from utils import *

class Grammar:
    def __init__(self):
        self.nonterminals = dict() # nonterminals, [rule]
        self.id_lookup_table = dict()

        self.first_sets = dict()
        self.epsilon_set = set()

    def insert_rule(self, nonterminal, rule):
        # rule: [(nonterminal?, symbol)]
        if nonterminal in self.nonterminals:
            current_id = len(self.nonterminals[nonterminal])
            self.id_lookup_table[(nonterminal, tuple(rule))] = current_id
            self.nonterminals[nonterminal].append(rule)
        else:
            self.nonterminals[nonterminal] = [rule]
            self.id_lookup_table[(nonterminal, tuple(rule))] = 0

    def lookup_rule_id(self, production):
        nonterminal = production.get_nonterminal()
        rule = production.get_symbols()

        key = (nonterminal, tuple(rule))
        if key not in self.id_lookup_table:
            return None

        return self.id_lookup_table[key]

    def eval_FIRST_set(self):
        self.first_sets = dict()
        self.epsilon_set = set()

        # append initial set
        for nonterminal, rules in self.nonterminals.items():
            self.first_sets[nonterminal] = set()

        while True:
            prev_first_set = self.copy_FIRST_sets()
            prev_epsilon_set = self.epsilon_set.copy()

            for nonterminal, rules in self.nonterminals.items():
                for rule in rules:
                    if len(rule) == 0:
                        self.epsilon_set.add(nonterminal)
                        continue

                    implicitly_epsilon = True
                    for symbol in rule:
                        if symbol[0]:
                            self.first_sets[nonterminal].update(prev_first_set[symbol[1]])

                            if symbol[1] not in prev_epsilon_set:
                                implicitly_epsilon = False
                                break
                        else:
                            self.first_sets[nonterminal].add(symbol[1])
                            implicitly_epsilon = False
                            break

                    if implicitly_epsilon:
                        self.epsilon_set.add(nonterminal)


            if prev_first_set == self.first_sets and prev_epsilon_set == self.epsilon_set:
                break

    def get_rules(self, nonterminal): # return [rule]
        if nonterminal not in self.nonterminals:
            raise ApplicationError(f"{nonterminal} does not exist in the provided grammar!")

        return self.nonterminals[nonterminal]

    def get_FIRST_set(self, nonterminal):
        if nonterminal not in self.nonterminals:
            raise ApplicationError(f"{nonterminal} does not exist in the provided grammar!")

        if len(self.first_sets) == 0:
            self.eval_FIRST_set()

        return self.first_sets[nonterminal]

    def contains_epsilon(self, nonterminal):
        if nonterminal not in self.nonterminals:
            raise ApplicationError(f"{nonterminal} does not exist in the provided grammar!")

        return nonterminal in self.epsilon_set

    # should be private
    def copy_FIRST_sets(self):
        new_FIRST_set = dict()
        for k, v in self.first_sets.items():
            new_FIRST_set[k] = v.copy()

        return new_FIRST_set
