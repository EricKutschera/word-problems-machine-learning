import json


class WordProblem(object):
    def __init__(self, labeled_example, nlp):
        self.labeled_example = labeled_example
        self.nlp = nlp

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'labeled_example': self.labeled_example.to_json(),
                'nlp': self.nlp.to_json()}
