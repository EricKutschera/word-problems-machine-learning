import json

from sympy import Symbol


class FeatureExtractor(object):
    def __init__(self, unique_templates, word_problems):
        self.unigrams = self.find_unigrams(word_problems)
        self.bigrams = self.find_bigrams(word_problems)
        self.lemmas = self.find_lemmas(word_problems)

        self.template_count = len(unique_templates)
        self.constants = self.find_constants(unique_templates)
        self.dependency_types = self.find_dependency_types(unique_templates)
        signatures = self.find_slot_signatures(unique_templates)
        self.single_slot_signatures = signatures['single']
        self.slot_pair_signatures = signatures['pair']

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

    @staticmethod
    def find_slot_signatures(templates):
        single_slots = set()
        slot_pairs = set()
        for template_index, template in enumerate(templates):
            single_slots.update(set(
                template.single_slot_signatures(template_index)))
            slot_pairs.update(set(
                template.slot_pair_signatures(template_index)))

        return {'single': sorted(single_slots),
                'pair': sorted(slot_pairs)}

    @staticmethod
    def solution_features():
        return [Feature.solution_all_integer(),
                Feature.solution_all_positive()]

    def single_slot_features(self):
        features = list()
        for signature in self.single_slot_signatures:
            features.extend([Feature.slot_is_one(signature),
                             Feature.slot_is_two(signature)])

        return features

    def slot_pair_features(self):
        features = list()
        for signature in self.slot_pair_signatures:
            features.append(Feature.slot_pair_in_same_sentence(signature))

        return features

    # TODO
    def order_all_features(self):
        unigrams = [Feature.from_unigram(u) for u in self.unigrams]
        bigrams = [Feature.from_bigram(b) for b in self.bigrams]
        is_template = [Feature.from_template_index(i)
                       for i in range(self.template_count)]
        return (unigrams
                + bigrams
                + is_template
                + self.solution_features()
                + self.single_slot_features()
                + self.slot_pair_features())

    def extract(self, derivation):
        prepared = PreparedDerivation(derivation)
        instance = [f.indicator(prepared) for f in self.ordered_features]
        return Features(self.ordered_features, instance)


class PreparedDerivation(object):
    '''Extracts and stores the relevant info for determining features.
       This makes it easy to apply each feature indicator function'''
    def __init__(self, derivation):
        self.derivation = derivation
        self.unigrams = derivation.word_problem.nlp.words()
        self.bigrams = derivation.word_problem.nlp.bigrams()
        self.template_index = derivation.template_index
        self.solution = derivation.solve()
        self.single_slots = self.initialize_single_slots()
        self.slot_pairs = self.initialize_slot_pairs()

    def initialize_single_slots(self):
        single_slots = dict()
        template = self.derivation.template
        signatures = template.single_slot_signatures(self.template_index)
        for signature in signatures:
            single_slots[signature] = self.initialize_single_slot(signature)

        return single_slots

    def initialize_single_slot(self, signature):
        return SingleSlotData(self.number_for_slot(signature))

    def initialize_slot_pairs(self):
        slot_pairs = dict()
        template = self.derivation.template
        signatures = template.slot_pair_signatures(self.template_index)
        for signature in signatures:
            slot_pairs[signature] = self.initialize_slot_pair(signature)

        return slot_pairs

    def initialize_slot_pair(self, signature):
        sentence1 = self.sentence_for_slot(signature.slot1)
        sentence2 = self.sentence_for_slot(signature.slot2)
        return SlotPairData((sentence1, sentence2))

    def number_for_slot(self, signature):
        if (self.derivation.template_index != signature.template_index
                or signature.symbol[0] != 'n'):
            return None

        sym = Symbol(signature.symbol)
        return self.derivation.number_map[sym]['number']

    def sentence_for_slot(self, signature):
        if self.derivation.template_index != signature.template_index:
            return None

        sym = Symbol(signature.symbol)
        if signature.symbol[0] == 'n':
            return self.derivation.number_map[sym]['sentence']

        return self.derivation.unknown_map[sym]['sentence']


class SingleSlotData(object):
    '''Holds the relevant info needed to check each
       single slot feature'''
    def __init__(self, number):
        self.number = number

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'number': self.number}


class SlotPairData(object):
    '''Holds the relevant info needed to check each
       slot pair feature'''
    def __init__(self, sentences):
        self.sentences = sentences

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'sentences': self.sentences}


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

    @staticmethod
    def slot_is_one(slot_signature):
        def check(prepared):
            slot_data = prepared.single_slots.get(slot_signature)
            if slot_data is None:
                return False

            return slot_data.number == 1

        return Feature('{} is 1'.format(slot_signature), check)

    @staticmethod
    def slot_is_two(slot_signature):
        def check(prepared):
            slot_data = prepared.single_slots.get(slot_signature)
            if slot_data is None:
                return False

            return slot_data.number == 2

        return Feature('{} is 2'.format(slot_signature), check)

    @staticmethod
    def slot_pair_in_same_sentence(slot_signature):
        def check(prepared):
            slot_data = prepared.slot_pairs.get(slot_signature)
            if slot_data is None:
                return False

            return slot_data.sentences[0] == slot_data.sentences[1]

        return Feature('{} in same sentence'.format(slot_signature), check)
