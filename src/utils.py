MATCHES_LITERAL_TAG = "|"
MATCHES_RULE_TAG = ":"

class BitMap:
    def __init__(self, chars):
        self.bitmap = bytearray([0x00 for _ in range(12)])
        self.rule = None

        if type(chars) is int:
            self.set_bit(chars)
        elif type(chars) is str:
            for c in chars:
                char_int = ord(c) - 32
                self.set_bit(char_int)
        else:
            print("error")

    def __str__(self):
        return "0x" + self.bitmap.hex()

    def get_bit(self, idx):
        if idx >= 96 or idx < 0:
            raise IndexError("BitMap index out of range in .get_bit()")
        which_byte = len(self.bitmap) - 1 - idx // 8
        bit_index = idx % 8
        return self.bitmap[which_byte] & (1 << bit_index)

    def set_epsilon_bit(self):
        self.bitmap[0] |= 0x80

    def flip_bits(self):
        self.bitmap = bytearray(a ^ 0xff for a in self.bitmap)

    def set_bit(self, idx):
        if idx >= 96 or idx < 0:
            raise IndexError("BitMap index out of range in .set_bit()")
        which_byte = len(self.bitmap) - 1 - idx // 8
        bit_index = idx % 8
        self.bitmap[which_byte] |= (1 << bit_index)

    def set_bits(self, bitfrom, bitto):
        if bitfrom >= 96 or bitfrom < 0 or bitto >= 96 or bitto < 0:
            raise IndexError("BitMap index out of range in .set_bits()")
        # could be a bit more optimal :/
        num_bits = bitto - bitfrom
        curr_byte = bitfrom // 8
        curr_index = bitfrom % 8
        for i in range(num_bits + 1):
            self.bitmap[len(self.bitmap) - 1 - curr_byte] |= (1 << curr_index)
            curr_index += 1
            if curr_index >= 8:
                curr_byte += 1
                curr_index = 0

    def bitxor(self, other):
        self.bitmap = bytearray(a ^ b for a, b in zip(self.bitmap, other.bitmap))

    def bitor(self, other):
        self.bitmap = bytearray(a | b for a, b in zip(self.bitmap, other.bitmap))

class InvalidParse(Exception):
    pass

class InvalidDFA(Exception):
    pass