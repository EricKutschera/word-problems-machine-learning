import math
import json
from collections import defaultdict

import numpy

from features import Features
from beam import beam_search


class Classifier(object):
    def __init__(self, feature_extractor, parameters, unique_templates):
        self.feature_extractor = feature_extractor
        self.parameters = parameters
        self.unique_templates = unique_templates
        feature_count = len(feature_extractor.ordered_features)
        self.features = Features(feature_extractor.ordered_features,
                                 [0 for _ in range(feature_count)])

    # TODO(Eric): these probabilities are not normalized to
    #             be in [0,1]. When applying this calculation
    #             in computing the log probablity and the gradient
    #             need to normalize.
    def probability_of_derivation(self, derivation):
        features = self.feature_extractor.extract(derivation)
        array = numpy.array(features.instance)
        return math.exp(array.dot(self.parameters))

    def log_likelihood(self, word_problems, wp_template_indices,
                       unique_templates):

        def score_func(derivation):
            return self.probability_of_derivation(derivation)

        def final_evaluation_func(derivations):
            if len(derivations) == 0:
                print('no derivations in beam for log likelihood')
            probs = list()
            for d in derivations:
                probs.append(score_func(d))

            total = sum(probs)
            result = 0
            for p in probs:
                result += math.log(p / total)

            return result

        total = 0
        for i, wp in enumerate(word_problems):
            correct_index = wp_template_indices[i]
            solutions = wp.labeled_example.solutions

            print('ll for wp: {} with template: {}, with solutions: {}'
                  .format(i, correct_index, solutions))

            def validator_func(d):
                return self.can_derive_correct_equations(d, correct_index,
                                                         solutions)

            total += beam_search(wp, unique_templates, score_func,
                                 validator_func, final_evaluation_func)
            print('log likelihood total after word problem: {} is {}'
                  .format(i, total))

        return total

    def log_likelihood_gradient(self, word_problems, wp_template_indices,
                                unique_templates):

        def score_func(derivation):
            return self.probability_of_derivation(derivation)

        def final_evaluation_func(derivations):
            if len(derivations) == 0:
                print('no derivations in beam for log likelihood gradient')
            gradient = numpy.zeros(len(self.parameters))
            probs = list()
            for d in derivations:
                prob = score_func(d)
                probs.append(prob)
                instance = self.feature_extractor.extract(d).instance
                gradient += prob * numpy.array(instance)

            total_prob = sum(probs)
            if total_prob == 0:
                print('no probablity to normalize in gradient')
                return gradient

            return gradient / total_prob

        total_gradient = numpy.zeros(len(self.parameters))
        for i, wp in enumerate(word_problems):
            correct_index = wp_template_indices[i]
            solutions = wp.labeled_example.solutions

            print('ll gradient for wp: {} with template: {}'
                  .format(i, correct_index))

            def validator_func(d):
                return self.can_derive_correct_equations(d, correct_index,
                                                         solutions)

            total_gradient += beam_search(wp, unique_templates, score_func,
                                          validator_func,
                                          final_evaluation_func)

            total_gradient -= beam_search(wp, unique_templates, score_func,
                                          lambda d: True,
                                          final_evaluation_func)

        return total_gradient

    @staticmethod
    def can_derive_correct_equations(derivation, correct_template_index,
                                     correct_solutions):
        if derivation.template_index != correct_template_index:
            return False

        solutions = derivation.solve()
        usable_solutions = list()
        pending_solutions = 0
        for s in solutions:
            try:
                usable_solutions.append(float(s))
            except TypeError:
                pending_solutions += 1

        # Need to have all the correct solutions.
        # Some problems involve equations with multiple
        # unknowns, but the quesition only wants to know the
        # value of one of them. So having extra values is fine.
        correct_solutions = correct_solutions[:]
        for s in correct_solutions:
            if s not in usable_solutions:
                if pending_solutions == 0:
                    return False
                pending_solutions -= 1
            else:
                usable_solutions.remove(s)

        return True

    def solve(self, wp):

        def score_func(d):
            return self.probability_of_derivation(d)

        def final_eval_func(derivations):
            total_probs = defaultdict(int)
            for d in derivations:
                sol = d.solve()
                total_probs[tuple(sorted(sol))] += score_func(d)

            best_prob = max(total_probs.values())
            for sol, prob in total_probs.iteritems():
                if prob == best_prob:
                    return list(sol)

            return None

        solution = beam_search(wp, self.unique_templates, score_func,
                               lambda d: True, final_eval_func)

        correct_sol = wp.labeled_example.solutions[:]
        correct = True
        for c in correct_sol:
            if c in solution:
                solution.remove(c)
            else:
                correct = False
                break

        print('guessed: {}, correct: {}, got it?: {}'
              .format(solution, correct_sol, correct))
        return int(correct)

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'parameters': list(self.parameters),
                'features': self.features.to_json()}
