from utils import *

class ParseTable:
    def __init__(self):
        self.table = []

    def insert_entry(self, state, symbol, action):
        while state >= len(self.table):
            self.table.append(dict())

        if symbol in self.table[state]:
            if self.table[state][symbol] == action:
                return

            raise InvalidParse("A conflict is encountered in the LALR(1) grammar!")

        self.table[state][symbol] = action

    def display(self):
        for i, row in enumerate(self.table):
            entry_str = []
            for symbol, action in row.items():
                entry_str.append(f"[{symbol[1]} => {action}]")

            print(f"state {i}: {', '.join(entry_str)}")
