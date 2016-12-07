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

    @staticmethod
    def find_bigrams(word_problems):
        bigrams = set()
        for wp in word_problems:
            bigrams.update(set(wp.nlp.bigrams()))

        return sorted(bigrams)

    @staticmethod
    def find_lemmas(word_problems):
        lemmas = set()
        for wp in word_problems:
            lemmas.update(set(wp.nlp.lemmas()))

        return sorted(lemmas)

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

    @staticmethod
    def solution_features():
        return [Feature.solution_all_integer(),
                Feature.solution_all_positive()]

    # TODO
    def order_all_features(self):
        unigrams = [Feature.from_unigram(u) for u in self.unigrams]
        bigrams = [Feature.from_bigram(b) for b in self.bigrams]
        is_template = [Feature.from_template_index(i)
                       for i in range(self.template_count)]
        return (unigrams
                + bigrams
                + is_template
                + self.solution_features())

    def extract(self, derivation):
        prepared = PreparedDerivation(derivation)
        instance = [f.indicator(prepared) for f in self.ordered_features]
        return Features(self.ordered_features, instance)


class PreparedDerivation(object):
    '''Extracts and stores the relevant info for determining features.
       This makes it easy to apply each feature indicator function'''
    def __init__(self, derivation):
        self.unigrams = derivation.word_problem.nlp.words()
        self.bigrams = derivation.word_problem.nlp.bigrams()
        self.template_index = derivation.template_index
        self.solution = derivation.solve()


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

    @staticmethod
    def from_bigram(bigram):
        return Feature(str(bigram),
                       lambda prepared: bigram in prepared.bigrams)

    @staticmethod
    def from_template_index(index):
        return Feature('is template {}'.format(index),
                       lambda prepared: prepared.template_index == index)

    @staticmethod
    def solution_all_integer():
        return Feature('solution all integer',
                       lambda prepared: all(round(v) == v
                                            for v in prepared.solution))

    @staticmethod
    def solution_all_positive():
        return Feature('solution all positive',
                       lambda prepared: all(v > 0
                                            for v in prepared.solution))
