import functools
import re


class ReFilter:
    def AND(a, b):
        # print(f" ***** AND: a = {a}, b = {b} -> {not (a is None and b is None)}")
        return a is not None and b is not None

    def OR(a, b):
        # print(f" ***** OR: a = {a}, b = {b} -> {not (a is None or b is None)}")
        return a is not None or b is not None

    def __init__(self, filters):
        self.filters = filters

    def matches(self, text, operator=OR):
        # l = [re.search(x, text) for x in self.filters]
        # print(f" *** l = {l}")
        return functools.reduce(operator, [re.search(x, text) for x in self.filters])

