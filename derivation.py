import json
from copy import deepcopy


class Derivation(object):
    def __init__(self, unknown_map, number_map, template,
                 template_index, word_problem, nouns, numbers):
        self.unknown_map = unknown_map
        self.number_map = number_map
        self.template = template
        self.template_index = template_index
        self.word_problem = word_problem
        self.nouns = nouns
        self.numbers = numbers

    def copy(self):
        return Derivation(deepcopy(self.unknown_map),
                          deepcopy(self.number_map),
                          self.template, self.template_index,
                          self.word_problem, self.nouns,
                          deepcopy(self.numbers))

    def all_unknowns_filled(self):
        return not any(v is None for v in self.unknown_map.itervalues())

    def all_numbers_filled(self):
        return not any(v is None for v in self.number_map.itervalues())

    def is_complete(self):
        self.all_unknowns_filled() and self.all_numbers_filled()

    def all_ways_to_fill_next_slot(self):
        if not self.all_numbers_filled():
            return self.all_ways_to_fill_next_number()

        if not self.all_unknowns_filled():
            return self.all_ways_to_fill_next_unknown()

        return None

    def all_ways_to_fill_next_number(self):
        next_number_slot = sorted(s for s in self.number_map
                                  if self.number_map[s] is None)[0]

        derivations = list()
        for number in self.numbers:
            derivation = self.copy()
            derivation.number_map[next_number_slot] = number
            derivation.numbers.remove(number)
            derivations.append(derivation)

        return derivations

    def all_ways_to_fill_next_unknown(self):
        next_unknown_slot = sorted(s for s in self.unknown_map
                                   if self.unknown_map[s] is None)[0]

        derivations = list()
        for noun in self.nouns:
            derivation = self.copy()
            derivation.unknown_map[next_unknown_slot] = noun
            derivations.append(derivation)

        return derivations

    def solve(self):
        solutions = list()
        for equation in self.template.solution.itervalues():
            subs = {k: v['number'] for k, v in self.number_map.iteritems()}
            solutions.append(equation.full.xreplace(subs))

        return solutions

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'unknown_map': {str(k): v for k, v
                                in self.unknown_map.iteritems()},
                'number_map': {str(k): v for k, v
                               in self.number_map.iteritems()},
                'template': self.template.to_json(),
                'template_index': self.template_index,
                'word_problem': self.word_problem.to_json(),
                'nouns': self.nouns,
                'numbers': self.numbers}


def initialize_partial_derivations_for_all_templates(wp, templates):
    numbers = wp.nlp.numbers()
    nouns = wp.nlp.nouns()
    partial_derivations = list()
    for template_index, template in enumerate(templates):
        slots = set()
        for eq in template.equations:
            slots.update(eq.symbols)

        unknown_slots = [s for s in slots if 'u_' in str(s)]
        number_slots = [s for s in slots if 'n_' in str(s)]
        unknown_map = {u: None for u in unknown_slots}
        number_map = {n: None for n in number_slots}

        partial_derivations.append(Derivation(unknown_map, number_map,
                                              template, template_index,
                                              wp, nouns,
                                              deepcopy(numbers)))

    return partial_derivations
