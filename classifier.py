import math
import json

import numpy

from features import Features
from beam import beam_search


class Classifier(object):
    def __init__(self, feature_extractor, parameters):
        self.feature_extractor = feature_extractor
        self.parameters = parameters
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

            def validator_func(d):
                return self.can_derive_correct_equations(d, correct_index,
                                                         solutions)

            total += beam_search(wp, unique_templates, score_func,
                                 validator_func, final_evaluation_func)

        return total

    def log_likelihood_gradient(self, word_problems, wp_template_indices,
                                unique_templates):

        def score_func(derivation):
            return self.probability_of_derivation(derivation)

        def final_evaluation_func(derivations):
            gradient = numpy.zeros(len(self.parameters))
            probs = list()
            for d in derivations:
                prob = score_func(d)
                probs.append(prob)
                instance = self.feature_extractor.extract(d).instance
                gradient += prob * numpy.array(instance)

            return gradient / sum(probs)

        total_gradient = numpy.zeros(len(self.parameters))
        for i, wp in enumerate(word_problems):
            correct_index = wp_template_indices[i]
            solutions = wp.labeled_example.solutions

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
        for s in solutions:
            print(s)
            try:
                usable_solutions.append(float(s))
                print('^was usable^')
            except:
                # TODO once this works -> remove print
                # also specify ValueError
                print('^could not use as solution^')

        correct_solutions = correct_solutions[:]
        for s in usable_solutions:
            if s not in correct_solutions:
                return False
            correct_solutions.remove(s)

        return True

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'parameters': list(self.parameters),
                'features': self.features.to_json()}
