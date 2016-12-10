import json

import numpy
from scipy.optimize import fmin_l_bfgs_b

from features import Features


class Parameters(object):
    def __init__(self, weights, features):
        self.weights = weights
        self.features = features

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'weights': list(self.weights),
                'features': self.features.to_json()}


# TODO
def optimize_parameters(feature_extractor, word_problems, unique_templates):
    ordered_features = feature_extractor.ordered_features
    feature_count = len(ordered_features)
    features = Features(ordered_features, [0 for _ in range(feature_count)])
    weights = numpy.ones(feature_count)

    def func_to_min(parameters):
        return -log_likelihood(word_problems, unique_templates, parameters)

    def gradient(parameters):
        return log_likelihood_gradient(word_problems, unique_templates,
                                       parameters)

    optimal, final_value, details = fmin_l_bfgs_b(func_to_min, weights,
                                                  fprime=gradient)
    print('final_value: {}'.format(final_value))
    print('details: {}'.format(details))
    return Parameters(optimal, features)


# TODO
def log_likelihood(word_problems, unique_templates, parameters):
    return 0.5


# TODO
def log_likelihood_gradient(word_problems, unique_templates, parameters):
    return numpy.zeros(len(parameters))
