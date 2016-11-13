import json


class LabeledExample(object):
    def __init__(self, index, question, equations, solutions):
        self.index = index
        self.question = question
        self.equations = equations
        self.solutions = solutions

    @staticmethod
    def read(file_path):
        with open(file_path, 'rt') as f_handle:
            example_list = json.load(f_handle)

        example_dict = dict()
        for e in example_list:
            i = e['iIndex']
            example_dict[i] = LabeledExample(i, e['sQuestion'],
                                             e['lEquations'], e['lSolutions'])

        return example_dict

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'index': self.index,
                'question': self.question,
                'equations': self.equations,
                'solutions': self.solutions}
