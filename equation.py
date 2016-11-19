import json

from sympy.parsing.sympy_parser import parse_expr


class Equation(object):
    def __init__(self, full):
        self.full = full
        self.symbols = full.free_symbols

    @classmethod
    def from_string(cls, s):
        lhs, rhs = [cls.parse_side(side) for side in s.split('=')]
        full = lhs - rhs
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

    # TODO(Eric): equation 6158 has an equation:
    # "2.0*0.01*two_acid+5.0*0.01*five_acid=4.0*0.01*24.0"
    # which parses as
    # lhs = 0.05*five_acid + 0.02*two_acid
    # rhs = 0.96
    # This drops information necessary to pull out slots from
    # the question text
    # parse_expr(s, evaluate=False) might work
    @classmethod
    def parse_side(cls, s):
        s = cls.clean(s)
        return parse_expr(s)

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'full': str(self.full),
                'symbols': [str(s) for s in self.symbols]}
