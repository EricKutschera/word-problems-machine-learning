import itertools
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
            sol[u] = Equation(raw_sol[i])

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

    @staticmethod
    def map_symbols(a_syms, b_syms):
        if len(a_syms) != len(b_syms):
            return list()

        mappings = list()
        for perm in itertools.permutations(b_syms):
            mappings.append(dict(zip(a_syms, perm)))
        return mappings

    def __hash__(self):
        return 1

    # TODO(Eric): should be possible to compare templates
    # for equality now that each unknown is solved as
    # an expression involving the number slots and constants
    # Kushman paper says that there are 28 unique templates out of 514
    def __eq__(self, other):
        self_unks = set(self.solution.keys())
        other_unks = set(other.solution.keys())
        if self_unks != other_unks:
            return False

        self_num_slots = {n for eq in self.solution.values()
                          for n in eq.symbols}
        other_num_slots = {n for eq in other.solution.values()
                           for n in eq.symbols}
        if self_num_slots != other_num_slots:
            return False

        unk_mappings = self.map_symbols(self_unks, other_unks)
        num_mappings = self.map_symbols(self_num_slots, other_num_slots)
        for n_map in num_mappings:
            for u_map in unk_mappings:
                for self_u, other_u in u_map.iteritems():
                    self_eq = self.solution[self_u].full
                    other_eq = other.solution[other_u].full
                    for old_n, new_n in n_map.iteritems():
                        other_eq = other_eq.replace(old_n, new_n)

                    # If the equations are not equal after this
                    # transformation, then this combo of n_map, u_map
                    # will not work
                    if self_eq != other_eq:
                        break

                    # All equations match under this mapping
                    # Thus there exists a mapping s.t. the templates
                    # are exactly the same
                    print(str(self))  # TODO
                    print(str(other))
                    print(n_map)
                    print(u_map)
                    return True

        return False

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'equations': [e.to_json() for e in self.equations],
                'solution': {str(k): v.to_json()
                             for k, v in self.solution.iteritems()}}
