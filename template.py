import json

from sympy import Symbol, linsolve

from equation import Equation


class Template(object):
    def __init__(self, equations, solution):
        self.equations = equations
        self.solution = solution

    @classmethod
    def from_equations_and_nlp(cls, equations, nlp):
        with_unknowns = cls.generalize_unknowns(equations)
        with_all_slots = cls.generalize_numbers(with_unknowns, nlp)
        solution = cls.solve(with_all_slots)
        return Template(with_all_slots, solution)

    @staticmethod
    def generalize_unknowns(equations):
        new_equations = [eq.full for eq in equations]
        symbols = {s for eq in equations for s in eq.symbols}

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
                    replacement = Symbol(unknown)
                    new_equations[i] = new_equations[i].replace(symbol,
                                                                replacement)

        return [Equation(eq) for eq in new_equations]

    @classmethod
    def generalize_numbers(cls, equations, nlp):
        numbers = cls.numbers_from_nlp(nlp)
        new_equations = [eq.full for eq in equations]

        replacements_by_eq = list()
        for eq in new_equations:
            replacements = list()
            for sym in eq.free_symbols:
                coef = abs(eq.coeff(sym))
                if coef in numbers:
                    numbers.remove(coef)
                    replacements.append(eq.coeff(sym)*sym)

                eq -= eq.coeff(sym)*sym

            # After removing all variable terms, only a constant remains
            if eq != 0:
                if abs(eq) in numbers:
                    numbers.remove(abs(eq))
                    replacements.append(eq)

            replacements_by_eq.append(replacements)

        count = 0
        for i, replacements in enumerate(replacements_by_eq):
            for replacement in replacements:
                slot = Symbol('n_{}'.format(count))
                count += 1

                syms = replacement.free_symbols
                if syms:
                    sym = list(syms)[0]
                    mult = -1 if replacement.coeff(sym) < 0 else 1
                    sub = slot * sym
                else:
                    mult = -1 if replacement < 0 else 1
                    sub = mult * slot

                new_equations[i] = new_equations[i].replace(replacement, sub)

        return [Equation(eq) for eq in new_equations]

    @classmethod
    def numbers_from_nlp(cls, nlp):
        tokens = list()
        for s in nlp.sentences:
            tokens.extend(s.tokens)

        numbers = list()
        for t in tokens:
            from_word = cls.try_parse_float(t.word)
            if from_word is not None:
                numbers.append(from_word)
                continue

            # In question 2189 there is a blank in the text '___'
            # which is interpreted as a NUMBER but with no value
            if t.ner == 'NUMBER' and t.normalized_ner is not None:
                from_ner = cls.try_parse_float(t.normalized_ner)
                if from_ner is not None:
                    numbers.append(from_ner)
                    continue

        return numbers

    @staticmethod
    def try_parse_float(s):
        try:
            return float(s)
        except ValueError:
            return None

    @classmethod
    def solve(cls, equations):
        unified, unknowns = cls.unify_unknowns(equations)
        sol_set = linsolve([eq.full for eq in unified], unknowns)
        if sol_set.is_EmptySet:
            return None

        # The output of linsolve is either empty set or a set of size 1
        raw_sol = list(sol_set)[0]
        sol = dict()
        for i, u in enumerate(unknowns):
            sol[u] = raw_sol[i]

        return sol

    @staticmethod
    def unify_unknowns(equations):
        replacements = dict()
        for eq in equations:
            for s in eq.symbols:
                splits = str(s).split('_')
                if splits[0] != 'u':
                    continue

                replacements[s] = Symbol('u_{}'.format(splits[1]))

        new_equations = [eq.full for eq in equations]
        for i in range(len(new_equations)):
            for old, new in replacements.iteritems():
                new_equations[i] = new_equations[i].replace(old, new)

        return ([Equation(eq) for eq in new_equations],
                list(set(replacements.values())))

    # TODO(Eric): should be possible to compare templates
    # for equality now that each unknown is solved as
    # an expression involving the number slots and constants
    def __eq__(self, other):
        return False

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'equations': [e.to_json() for e in self.equations],
                'solution': {str(k): str(v)
                             for k, v in self.solution.iteritems()}}
