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
    #             be in [0,1]. I think that's ok but might
    #             need to do a beam search.
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
            correct_index = self.find_template_index(wp, unique_templates)
            solutions = wp.labeled_example.solutions

            def validator_func(d):
                return self.can_derive_correct_equations(d, correct_index,
                                                         solutions)

            total += beam_search(wp, unique_templates, score_func,
                                 validator_func, final_evaluation_func)

        return total

    def log_likelihood_gradient(self, word_problems, unique_templates):

        def score_func(derivation):
            return self.probability_of_derivation(derivation)

        def final_evaluation_func(derivations):
            gradient = numpy.zeros(len(self.parameters))
            for d in derivations:
                instance = self.feature_extractor.extract(d).instance
                gradient += numpy.array(instance)

            return gradient

        total_gradient = numpy.zeros(len(self.parameters))
        for wp in word_problems:
            correct_index = self.find_template_index(wp, unique_templates)
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

    # TODO(Eric): this might be expensive. Could map word_problems to
    #             unique templates once at start
    @staticmethod
    def find_template_index(wp, templates):
        correct_template = wp.extract_template()
        for i, template in enumerate(templates):
            if correct_template == template:
                return i

        raise Exception('equations and nlp do not match a template')

    @staticmethod
    def can_derive_correct_equations(derivation, correct_template_index,
                                     correct_solutions):
        if derivation.template_index != correct_template_index:
            return False

        solutions = derivation.solve()
        usable_solutions = list()
        for s in solutions:
            try:
                usable_solutions.append(float(s))
            except:
                # TODO once this works -> remove print
                # also specify ValueError
                print(s)
                print('could not use as solution^')

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
