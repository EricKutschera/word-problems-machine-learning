import json


class Template(object):
    def __init__(self, equations):
        self.equations = equations

    @staticmethod
    def from_equations(equations):
        # TODO(Eric): need to replace the symbols in
        # the equations with unknown and number slots (u_{i}^{j}, n_{i})
        # also need to canonicalize
        # (from Section 6 "Model Details" of the Kushman paper)
        return Template(equations)

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'equations': [e.to_json() for e in self.equations]}
