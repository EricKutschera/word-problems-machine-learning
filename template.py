import json

import sympy

from equation import Equation


class Template(object):
    def __init__(self, equations):
        self.equations = equations

    @classmethod
    def from_equations(cls, equations):
        # TODO(Eric): need to replace the symbols in
        # the equations with number slots (n_{i})
        # that requires having the problem text to see
        # if the number appears in the text
        # (yes_in_text -> slot, no -> constant)
        # Then canonicalize by solving the system in terms of each
        # slot. sympy.linsolve(equations, unknowns)
        with_unknowns = cls.generalize_unknowns(equations)
        return Template(with_unknowns)

    @staticmethod
    def generalize_unknowns(equations):
        new_equations = [eq.full for eq in equations]
        symbols = set()
        for equation in equations:
            for symbol in equation.symbols:
                symbols.add(symbol)

        symbol_to_unknown = dict()
        for i, symbol in enumerate(symbols):
            symbol_to_unknown[symbol] = {'base': 'u_{}'.format(i),
                                         'occurences': 0}

        for i, equation in enumerate(equations):
            for symbol, unknown_info in symbol_to_unknown.iteritems():
                if symbol in equation.symbols:
                    unknown = '{}_{}'.format(unknown_info['base'],
                                             unknown_info['occurences'])
                    unknown_info['occurences'] += 1
                    replacement = sympy.Symbol(unknown)
                    new_equations[i] = new_equations[i].replace(symbol,
                                                                replacement)

        return [Equation(eq) for eq in new_equations]

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'equations': [e.to_json() for e in self.equations]}
