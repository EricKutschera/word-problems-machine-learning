import json


class FeatureExtractor(object):
    def __init__(self, unique_templates, word_problems):
        self.unigrams = self.find_unigrams(word_problems)
        self.bigrams = self.find_bigrams(word_problems)
        self.lemmas = self.find_lemmas(word_problems)

        self.template_count = len(unique_templates)
        self.constants = self.find_constants(unique_templates)
        self.dependency_types = self.find_dependency_types(unique_templates)
        self.slot_signatures = self.find_slot_signatures(unique_templates)

        self.ordered_features = self.order_all_features()

    @staticmethod
    def find_unigrams(word_problems):
        unigrams = set()
        for wp in word_problems:
            unigrams.update(set(wp.nlp.words()))

        return sorted(unigrams)

    # TODO
    @staticmethod
    def find_bigrams(word_problems):
        pass

    # TODO
    @staticmethod
    def find_lemmas(word_problems):
        pass

    # TODO
    @staticmethod
    def find_constants(templates):
        pass

    # TODO
    @staticmethod
    def find_dependency_types(templates):
        pass

    # TODO
    @staticmethod
    def find_slot_signatures(templates):
        pass

    # TODO
    def order_all_features(self):
        return [Feature.from_unigram(u) for u in self.unigrams]

    def extract(self, derivation):
        prepared = PreparedDerivation(derivation)
        instance = [f.indicator(prepared) for f in self.ordered_features]
        return Features(self.ordered_features, instance)


class PreparedDerivation(object):
    '''Extracts and stores the relevant info for determining features.
       This makes it easy to apply each feature indicator function'''
    def __init__(self, derivation):
        self.unigrams = derivation.word_problem.nlp.words()


class Features(object):
    def __init__(self, features, instance):
        self.features = features
        self.instance = instance

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {f.name: self.instance[i]
                for i, f in enumerate(self.features)}


class Feature(object):
    def __init__(self, name, indicator):
        self.name = name
        self.indicator = indicator

    @staticmethod
    def from_unigram(unigram):
        return Feature(unigram,
                       lambda prepared: unigram in prepared.unigrams)
