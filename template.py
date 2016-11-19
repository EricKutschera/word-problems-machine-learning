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

    @classmethod
    def generalize_unknowns(cls, equations):
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
                    new_equations[i] = cls.no_eval_replace(new_equations[i],
                                                           symbol,
                                                           replacement)

        return [Equation(eq) for eq in new_equations]

    @classmethod
    def generalize_numbers(cls, equations, nlp):
        numbers = cls.numbers_from_nlp(nlp)
        new_equations = [eq.full for eq in equations]

        count = 0
        for num in numbers:
            for i, eq in enumerate(new_equations):
                if eq.has(num):
                    slot = Symbol('n_{}'.format(count))
                    count += 1
                    new_equations[i] = cls.no_eval_replace(new_equations[i],
                                                           num,
                                                           slot)

        return [Equation(eq) for eq in new_equations]

    # TODO(Eric): for question 2239, the number 2340 appears
    # in the text as '2,340.00 dollars'. It is not found by
    # this function
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
        # At this point all substitution is finished so simplify() is safe
        simplified = [eq.full.simplify() for eq in unified]
        sol_set = linsolve(simplified, unknowns)
        if sol_set.is_EmptySet:
            return None

        # The output of linsolve is either empty set or a set of size 1
        raw_sol = list(sol_set)[0]
        sol = dict()
        for i, u in enumerate(unknowns):
            sol[u] = Equation(raw_sol[i])

        return sol

    @classmethod
    def unify_unknowns(cls, equations):
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
                new_equations[i] = cls.no_eval_replace(new_equations[i],
                                                       old,
                                                       new)

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

    @classmethod
    def no_eval_replace(cls, e, old, new):
        if e == old:
            return new

        if not e.args:
            return e

        replaced = [cls.no_eval_replace(arg, old, new) for arg in e.args]
        return e.func(*replaced, evaluate=False)

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
                        other_eq = self.no_eval_replace(other_eq, old_n, new_n)

                    # If the equations are not equal after this
                    # transformation, then this combo of n_map, u_map
                    # will not work
                    if self_eq != other_eq:
                        break

                    # All equations match under this mapping
                    # Thus there exists a mapping s.t. the templates
                    # are exactly the same
                    return True

        return False

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'equations': [e.to_json() for e in self.equations],
                'solution': {str(k): v.to_json()
                             for k, v in self.solution.iteritems()}}
