from utils import *

class ParseTable:
    def __init__(self):
        self.table = []

    def insert_entry(self, state, symbol, action):
        if symbol[0] and action[0] != "g":
            raise ApplicationError("A nonterminal symbol can ONLY have GOTO action!")
        if not symbol[1] and action[0] == "g":
            raise ApplicationError("A terminal symbol CANNOT have GOTO action!")

        while state >= len(self.table):
            self.table.append(dict())

        if symbol in self.table[state]:
            if self.table[state][symbol] == action:
                return

            print(self.table[state][symbol])
            print(action)
            raise InvalidParse("A conflict is encountered in the LALR(1) grammar!")

        self.table[state][symbol] = action

    def display(self):
        for i, row in enumerate(self.table):
            entry_str = []
            for symbol, action in row.items():
                entry_str.append(f"[{symbol[1]} => {action}]")

            print(f"state {i}: {', '.join(entry_str)}")
