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

    def display(self):
        for i, row in enumerate(self.table):
            entry_str = []
            for symbol, action in row.items():
                entry_str.append(f"[{symbol[1]} {symbol[0]} => {action}]")

            print(f"state {i}: {', '.join(entry_str)}")
