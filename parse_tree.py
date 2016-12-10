import json


class ParseTree(object):
    def __init__(self, value, children):
        self.value = value
        self.children = children

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return {'value': self.value,
                'children': [c.to_json() for c in self.children]}

    def token_count(self):
        if len(self.children) == 0:
            return 1

        count = 0
        for c in self.children:
            count += c.token_count()

        return count

    @classmethod
    def from_parse_string(cls, parse_string):
        parse_string = parse_string.strip()
        expand_parens = (parse_string
                         .replace('(', '( ')
                         .replace(')', ' )'))
        tokens = [s.strip() for s in expand_parens.split()]
        if tokens[0] != '(' or tokens[1] != 'ROOT' or tokens[-1] != ')':
            raise Exception('could not parse: {}'.format(parse_string))

        return cls.from_tokens('Root', tokens[2:-1])

    @classmethod
    def from_tokens(cls, root, tokens):
        if len(tokens) == 1:
            return ParseTree(root, [ParseTree(tokens[0], list())])

        sub_trees = list()
        sub_tree = list()
        nesting_depth = 0
        for t in tokens:
            sub_tree.append(t)
            if t == '(':
                nesting_depth += 1

            if t == ')':
                nesting_depth -= 1

            if nesting_depth == 0:
                sub_trees.append(sub_tree)
                sub_tree = list()

        if nesting_depth != 0:
            raise Exception('could not parse: {}'.format(tokens))

        parsed_trees = list()
        for tree in sub_trees:
            if len(tree) < 4 or tree[0] != '(' or tokens[-1] != ')':
                raise Exception('could not parse: {}'.format(tokens))

            parsed_trees.append(cls.from_tokens(tree[1], tree[2:-1]))

        return ParseTree(root, parsed_trees)
