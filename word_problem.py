import json

from equation import Equation
from template import Template


class WordProblem(object):
    def __init__(self, labeled_example, nlp):
        self.labeled_example = labeled_example
        self.nlp = nlp

    def extract_template(self):
        parsed_equations = [Equation.from_string(eq)
                            for eq in self.labeled_example.equations]
        return Template.from_equations_and_nlp(parsed_equations, self.nlp)

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'labeled_example': self.labeled_example.to_json(),
                'nlp': self.nlp.to_json()}
