class FeatureExtractor(object):
    def __init__(self, unique_templates, word_problems):
        # TODO(Eric): determine the ordering of the total feature vector
        pass

    def extract(self, derivation):
        # TODO(Eric): find all features for a particular derivation
        pass

    def to_vector(self, features):
        # TODO(Eric): take in an instance of Features and transform
        #             into a vector of all possible features where
        #             features which are not present take zero as the value
        pass


class Features(object):
    # TODO(Eric): hold the features for a particular derivation
    def __init__(self):
        pass
