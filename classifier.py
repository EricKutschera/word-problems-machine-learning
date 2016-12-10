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

    def probability_of_derivation(self, derivation):
        features = self.feature_extractor.extract(derivation)
        array = numpy.array(features.instance)
        return math.exp(array.dot(self.parameters))

    def log_likelihood(self, word_problems, unique_templates):

        def score_func(derivation):
            return math.log(self.probability_of_derivation(derivation))

        def final_evaluation_func(derivations):
            result = 0
            for d in derivations:
                result += score_func(d)

            return result

        total = 0
        for wp in word_problems:

            def validator_func(d):
                correct_equations = wp.labeled_example.equations
                return self.can_derive_correct_equations(d, correct_equations)

            total += beam_search(wp, unique_templates, score_func,
                                 validator_func, final_evaluation_func)

        return total

    # TODO
    @staticmethod
    def can_derive_correct_equations(derivation, correct_equations):
        return True

    # TODO
    def log_likelihood_gradient(self, word_problems, unique_templates):
        return numpy.zeros(len(self.parameters))

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'parameters': list(self.parameters),
                'features': self.features.to_json()}
