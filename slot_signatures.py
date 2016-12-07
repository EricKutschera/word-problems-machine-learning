import functools
import json


@functools.total_ordering
class SingleSlotSignature(object):
    '''Essentially a collections.namedtuple.
       Using a custom class for flexibility'''
    def __init__(self, template_index, equation_index, symbol):
        self.template_index = template_index
        self.equation_index = equation_index
        self.symbol = symbol

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'template_index': self.template_index,
                'equation_index': self.equation_index,
                'symbol': self.symbol}

    def to_tuple(self):
        return (self.template_index,
                self.equation_index,
                self.symbol)

    def __eq__(self, other):
        return self.to_tuple() == other.to_tuple()

    def __lt__(self, other):
        return self.to_tuple() < other.to_tuple()

    def __hash__(self):
        return hash(self.to_tuple())
