import argparse
import json

from labeled_example import LabeledExample
from nlp import NLP
from word_problem import WordProblem
from derivation import derive_wp_for_all_templates
from template import Template


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['print', 'find-template-set',
                                           'count-unique', 'extract-features'],
                        help='What to do with the data')
    parser.add_argument('-j', '--json', type=str,
                        default='data/questions.json',
                        help='file path of json word problems')
    parser.add_argument('-n', '--nlp', type=str,
                        default='parses',
                        help='directory path of NLP parses for each problem')
    parser.add_argument('-i', '--index', type=int, default=2598,
                        help='iIndex of a specific word problem')
    parser.add_argument('-u', '--unique', type=int, default=[2598], nargs='+',
                        help='iIndexs of word problems')
    parser.add_argument('-t', '--templates', type=str,
                        default='unique_templates.json',
                        help='file to write or read set of unique templates')
    args = parser.parse_args()

    if args.action == 'print':
        examples = LabeledExample.read(args.json)
        example = examples[args.index]
        natural_language = NLP.read(args.nlp, args.index)
        wp = WordProblem(example, natural_language)
        wp.extract_template()
        print(wp)

    if args.action == 'find-template-set':
        examples = LabeledExample.read(args.json)
        indices = [e.index for e in examples.itervalues()]
        natural_language = {i: NLP.read(args.nlp, i) for i in indices}
        word_problems = [WordProblem(examples[i], natural_language[i])
                         for i in indices]
        templates = [wp.extract_template() for wp in word_problems]
        unique = set(templates)
        print('{} total and {} unique templates'.format(len(templates),
                                                        len(unique)))
        with open(args.templates, 'wt') as f_handle:
            f_handle.write(json.dumps([t.to_json() for t in unique]))

    if args.action == 'count-unique':
        examples = LabeledExample.read(args.json)
        templates = list()
        for index in args.unique:
            example = examples[index]
            natural_language = NLP.read(args.nlp, index)
            wp = WordProblem(example, natural_language)
            templates.append(wp.extract_template())

        print(len(set(templates)))
        print(json.dumps([t.to_json() for t in templates]))

    if args.action == 'extract-features':
        examples = LabeledExample.read(args.json)
        example = examples[args.index]
        natural_language = NLP.read(args.nlp, args.index)
        wp = WordProblem(example, natural_language)

        with open(args.templates, 'rt') as f_handle:
            raw = f_handle.read()

        unique_templates = [Template.from_json(j) for j in json.loads(raw)]
        derivations = derive_wp_for_all_templates(wp, unique_templates)
        print(json.dumps(derivations.next().to_json()))
        count = 1
        for _ in derivations:
            count += 1
        print('{} derivations'.format(count))


if __name__ == '__main__':
    main()
