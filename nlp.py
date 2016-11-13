import json
import os
import xml.etree.ElementTree as ET


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
    def __init__(self, word, lemma, pos):
        self.word = word
        self.lemma = lemma
        self.pos = pos

    @staticmethod
    def from_xml(xml):
        word = xml.findtext('word')
        lemma = xml.findtext('lemma')
        pos = xml.findtext('POS')
        return Token(word, lemma, pos)

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
