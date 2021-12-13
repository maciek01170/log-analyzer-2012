from datetime import datetime
import functools
import re


class ReFilter:
    def AND(a, b):
        # print(f" ***** AND: a = {a}, b = {b} -> {not (a is None and b is None)}")
        return a is not None and b is not None

    def OR(a, b):
        # print(f" ***** OR: a = {a}, b = {b} -> {not (a is None or b is None)}")
        return a is not None or b is not None

    def matches(_filter, text, operator=OR):
        return _filter and _filter._matches(text, operator)

    def __init__(self, filters):
        self.filters = filters

    def _matches(self, text, operator=OR):
        # l = [re.search(x, text) for x in self.filters]
        # print(f" *** l = {l}")
        return any(r is not None for r in [re.search(x, text) for x in self.filters])
        # return functools.reduce(operator, [re.search(x, text) for x in self.filters])


class DateFilter:
    def __init__(self, start_date, end_date):
        self.start = start_date and datetime.strptime(start_date, '%Y-%m-%d').date() or None
        self.end = end_date and datetime.strptime(end_date, '%Y-%m-%d').date() or None

    def _between(self, request_time):
        if self.start is not None and request_time.date() < self.start:
            return False
        if self.end is not None and self.end < request_time.date():
            return False
        return True

    def between(date_filter, request_time):
        return True if date_filter is None else date_filter._between(request_time)

