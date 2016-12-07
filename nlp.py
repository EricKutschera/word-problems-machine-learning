import json
import os
import xml.etree.ElementTree as ET

from text_to_int import text_to_int

from util import try_parse_float


class NLP(object):
    FILE_FORMAT = 'question-{}.xml'

    def __init__(self, sentences):
        self.sentences = sentences

    @classmethod
    def read(cls, parse_dir, i):
        file_name = cls.FILE_FORMAT.format(i)
        file_path = os.path.join(parse_dir, file_name)

        xml_tree = ET.parse(file_path)

        return cls.from_xml(xml_tree.getroot())

    @staticmethod
    def from_xml(xml):
        sentences = list()
        for sentence in xml.find('document').find('sentences'):
            sentences.append(Sentence.from_xml(sentence))

        return NLP(sentences)

    # These number words are fair game to replace in the text
    # since they are a natural language representation of numerical
    # operation. 'Twice' is equivalent to '2.0 times'
    # This is distinct from the case of 'problem constants' like
    # 0.01 for percent (%) problems
    @staticmethod
    def try_parse_number_word(w):
        number_word_map = {'twice': 2.0,
                           'triple': 3.0,
                           'half': 0.5,
                           'thrice': 3.0,
                           'double': 2.0}
        special = number_word_map.get(w.lower())
        if special is not None:
            return special

        try:
            return float(text_to_int(w))
        except:
            return None

    @staticmethod
    def clean(s):
        for c in ['<', '>']:
            s = s.replace(c, '')

        return s

    def words(self):
        words = list()
        for s in self.sentences:
            for t in s.tokens:
                words.append(t.word)

        return words

    def nouns(self):
        nouns = list()
        for s in self.sentences:
            for t in s.tokens:
                if t.pos in ['NN', 'NNS']:
                    nouns.append(t.word)

        return nouns

    def numbers(self):
        tokens = list()
        for s in self.sentences:
            tokens.extend(s.tokens)

        numbers = list()
        for t in tokens:
            from_number_word = self.try_parse_number_word(t.word)
            if from_number_word is not None:
                numbers.append(from_number_word)
                continue

            from_word = try_parse_float(t.word)
            if from_word is not None:
                numbers.append(from_word)
                continue

            if '-' in t.word:
                for part in t.word.split('-'):
                    from_split = try_parse_float(part)
                    if from_split is not None:
                        numbers.append(from_split)
                        continue
                    from_split_word = self.try_parse_number_word(part)
                    if from_split_word is not None:
                        numbers.append(from_split_word)
                        continue

            # In question 2189 there is a blank in the text '___'
            # which is interpreted as a NUMBER but with no value
            if t.ner == 'NUMBER' and t.normalized_ner is not None:
                cleaned = self.clean(t.normalized_ner)
                from_number_ner = try_parse_float(cleaned)
                if from_number_ner is not None:
                    numbers.append(from_number_ner)
                    continue

            if t.ner == 'MONEY':
                no_dollar_sign = t.normalized_ner.strip('$')
                from_money_ner = try_parse_float(no_dollar_sign)
                if from_money_ner is not None:
                    numbers.append(from_money_ner)
                    continue

        return list({abs(n) for n in numbers})

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'sentences': [s.to_json() for s in self.sentences]}


class Sentence(object):
    def __init__(self, tokens, parse, dependencies):
        self.tokens = tokens
        self.parse = parse
        self.dependencies = dependencies

    @staticmethod
    def from_xml(xml):
        tokens = [Token.from_xml(t) for t in xml.find('tokens')]
        parse = xml.findtext('parse')

        dependencies = list()
        for d in xml.findall('dependencies'):
            dependencies.extend(Dependency.from_xml(d))

        return Sentence(tokens, parse, dependencies)

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'tokens': [t.to_json() for t in self.tokens],
                'parse': self.parse,
                'dependencies': [d.to_json() for d in self.dependencies]}


class Token(object):
    def __init__(self, word, lemma, pos, ner, normalized_ner):
        self.word = word
        self.lemma = lemma
        self.pos = pos
        self.ner = ner  # Named Entity Recognizer
        self.normalized_ner = normalized_ner

    @staticmethod
    def from_xml(xml):
        word = xml.findtext('word')
        lemma = xml.findtext('lemma')
        pos = xml.findtext('POS')
        ner = xml.findtext('NER')
        normalized_ner = xml.findtext('NormalizedNER')
        return Token(word, lemma, pos, ner, normalized_ner)

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'word': self.word,
                'lemma': self.lemma,
                'pos': self.pos}


class Dependency(object):
    def __init__(self, kind, relation, governor_index, dependent_index):
        self.kind = kind
        self.relation = relation
        self.governor_index = governor_index
        self.dependent_index = dependent_index

    @staticmethod
    def from_xml(xml):
        kind = xml.get('type')
        kind = kind.replace('-dependencies', '')

        deps = list()
        for d in xml.findall('dep'):
            relation = d.get('type')
            gov = d.find('governor')
            gov_i = gov.get('idx')
            dep = d.find('dependent')
            dep_i = dep.get('idx')
            deps.append(Dependency(kind, relation, gov_i, dep_i))
        return deps

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'kind': self.kind,
                'relation': self.relation,
                'governor_index': self.governor_index,
                'dependent_index': self.dependent_index}
