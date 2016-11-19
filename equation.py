import json

from sympy.parsing.sympy_parser import parse_expr
from sympy import Mul, Add, Integer


class Equation(object):
    def __init__(self, full):
        self.full = full
        self.symbols = full.free_symbols

    @classmethod
    def from_string(cls, s):
        lhs, rhs = [cls.parse_side(side) for side in s.split('=')]
        # full = lhs - rhs: without simplifing
        full = Add(lhs, Mul(Integer(-1), rhs, evaluate=False), evaluate=False)
        return Equation(full)

    @staticmethod
    def clean(s):
        SUBSTITUTIONS = {'0.275000.0': '0.275000'}
        KEYWORDS = ['print', 'fraction', 'floor']

        for kw in KEYWORDS:
            s = s.replace(kw, '{}_'.format(kw))

        for find, replace in SUBSTITUTIONS.iteritems():
            s = s.replace(find, replace)

        return s

    @classmethod
    def parse_side(cls, s):
        s = cls.clean(s)
        base = parse_expr(s, evaluate=False)
        return base.expand()

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'full': str(self.full),
                'symbols': [str(s) for s in self.symbols]}
