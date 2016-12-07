import json
import itertools


class Derivation(object):
    def __init__(self, unknown_map, number_map, template,
                 template_index, word_problem):
        self.unknown_map = unknown_map
        self.number_map = number_map
        self.template = template
        self.template_index = template_index
        self.word_problem = word_problem

    def solve(self):
        solutions = list()
        for equation in self.template.solution.itervalues():
            solutions.append(equation.full.xreplace(self.number_map))

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
                'word_problem': self.word_problem.to_json()}


# Since there are a lot of derivations, these functions
# are implemented as generators. This avoids a huge
# memory requirement
def derive_wp_for_all_templates(wp, templates):
    # TODO(Eric): might need to map numbers to place in question
    #             with a tuple of indices (sentence, token).
    #             Similarly for nouns
    numbers = wp.nlp.numbers()
    nouns = wp.nlp.nouns()
    for template_index, template in enumerate(templates):
        for deriv in derive_wp_and_template(wp, template, template_index,
                                            numbers, nouns):
            yield deriv


# TODO(Eric): This is a very expensive operation that can find
#             millions of derivations for a template wp pair.
#             might need to optimize the ordering of
#             returned derivations to help the search later on
def derive_wp_and_template(wp, template, template_index, numbers, nouns):
    slots = set()
    for eq in template.equations:
        slots.update(eq.symbols)

    unknown_slots = [s for s in slots if 'u_' in str(s)]
    number_slots = [s for s in slots if 'n_' in str(s)]

    for noun_selection in permutations(len(unknown_slots), nouns,
                                       replacement=True):
        for number_selection in permutations(len(number_slots), numbers,
                                             replacement=False):
            unknown_map = dict(zip(unknown_slots, noun_selection))
            number_map = dict(zip(number_slots, number_selection))
            yield Derivation(unknown_map, number_map, template,
                             template_index, wp)


def permutations(count, items, replacement=False):
    if not replacement:
        return itertools.permutations(items, count)

    result = set()
    for comb in itertools.combinations_with_replacement(items, count):
        for perm in itertools.permutations(comb):
            result.add(perm)

    return result
