from tabulate import tabulate

from utils import *

class ParseTable:
    def __init__(self):
        self.table = []
        self.productions = []

    def insert_entry(self, state, symbol, action):
        if symbol[0] and action[0] != "g":
            raise ApplicationError("A nonterminal symbol can ONLY have GOTO action!")
        if not symbol[0] and action[0] == "g":
            raise ApplicationError("A terminal symbol CANNOT have GOTO action!")

        while state >= len(self.table):
            self.table.append(dict())

        if symbol in self.table[state]:
            if self.table[state][symbol] == action:
                return

            raise InvalidParse("A conflict is encountered in the LALR(1) grammar!")

        self.table[state][symbol] = action

    def set_productions(self, productions):
        self.productions = productions

    def get_action(self, state, symbol):
        if state < 0 or state >= len(self.table):
            raise ApplicationError("Parse table state out of bounds!")
        if symbol not in self.table[state]:
            raise ApplicationError(f"Parse table is empty for symbol {symbol[1]} in state {state}!")

        return self.table[state][symbol]

    def get_production(self, production):
        if production < 0 or production >= len(self.productions):
            raise ApplicationError("Production index out of range in parse table!")

        return self.productions[production]

    def get_productions(self):
        return self.productions

    def get_action_table(self):
        symbols_index = dict()
        symbols_lst = []

        for state in self.table:
            for symbol in state.keys():
                if symbol not in symbols_index:
                    symbols_index[symbol] = None
                    symbols_lst.append(symbol)

        symbols_lst.sort(key=lambda e: e[1])
        for i, symbol in enumerate(symbols_lst):
            symbols_index[symbol] = i

        action_table = []
        for state in self.table:
            row = [(None, 0) for _ in symbols_lst]
            for symbol, action in state.items():
                index_lookup = symbols_index[symbol]
                row[index_lookup] = action

            action_table.append(row)

        return (symbols_lst, action_table)

    def display(self):
        print_table = []
        for i, state in enumerate(self.table):
            row = dict()
            row["state"] = i
            for symbol, action in state.items():
                row[symbol[1]] = action[0] + str(action[1])
            print_table.append(row)

        print(tabulate(print_table, headers="keys", tablefmt="grid"))
