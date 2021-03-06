import json

from sympy.parsing.sympy_parser import parse_expr
from sympy import Symbol

from util import try_parse_float


class Equation(object):
    def __init__(self, full):
        self.full = full
        self.symbols = full.free_symbols

    @classmethod
    def from_string(cls, s):
        lhs, rhs = [cls.parse_side(side) for side in s.split('=')]
        full = cls.symbols_to_numbers(lhs - rhs)
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
        return cls.numbers_to_symbols(base).expand()

    @classmethod
    def numbers_to_symbols(cls, e):
        if not e.args:
            if not e.is_number:
                return e

            sym = Symbol(str(abs(e)))
            if e < 0:
                return -sym
            return sym

        replaced = [cls.numbers_to_symbols(arg) for arg in e.args]
        return e.func(*replaced)

    @classmethod
    def symbols_to_numbers(cls, e):
        if not e.args:
            f = try_parse_float(str(e))
            if f is not None:
                return f

            return e

        replaced = [cls.symbols_to_numbers(arg) for arg in e.args]
        return e.func(*replaced, evaluate=False)

    def constants(self):
        return self.constants_for_eq(self.full)

    def constants_for_eq(self, eq):
        constants = set()
        for arg in eq.args:
            if arg.is_number:
                if abs(arg) != 1.0:
                    constants.add(abs(float(arg)))
            else:
                constants.update(self.constants_for_eq(arg))

        return constants

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'full': str(self.full),
                'symbols': [str(s) for s in self.symbols]}

    @staticmethod
    def from_json(j):
        return Equation(parse_expr(j['full']))
