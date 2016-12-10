import math
import json

import numpy

from features import Features


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

    # TODO
    def log_likelihood(self, word_problems, unique_templates):
        return 0.5

    # TODO
    def log_likelihood_gradient(self, word_problems, unique_templates):
        return numpy.zeros(len(self.parameters))

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'parameters': list(self.parameters),
                'features': self.features.to_json()}
