"""
A customized implementation of the deque data type with these extensions:

- Adds `push` as an alias for appendleft
- Adds an `average` method, returns the average of the values on the deque
- Adds a `max` method, returns the maximum value
- Adds a `min` method, returns the minimum value

d = Deck(maxlen=3)
d.push(1)
d.push(3.114)
d.push(1.8753)
print("Average to 3 decimal places:", d.average(precision=3))
print("Max value", d.max())
print("Min value", d.min())

Works with integer or float values
"""
from collections import deque
from decimal import Decimal


class Deck(deque):
    def __init__(self, maxlen=None):
        super(Deck, self).__init__(maxlen=maxlen)
        self.push = self.appendleft

    def average(self, precision=None):
        if precision is not None:
            temp_deck = []
            for i in self:
                temp_deck.append(i)
            return Decimal(str(sum(temp_deck) / len(temp_deck))).quantize(
                Decimal("1.{}".format("0" * precision)))
        return sum(self) / len(self)

    def max(self):
        return max(self)

    def min(self):
        return min(self)
