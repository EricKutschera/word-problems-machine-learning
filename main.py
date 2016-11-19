import argparse

from labeled_example import LabeledExample
from nlp import NLP
from word_problem import WordProblem


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['print', 'process'],
                        help='What to do with the data')
    parser.add_argument('-j', '--json', type=str,
                        default='data/questions.json',
                        help='file path of json word problems')
    parser.add_argument('-n', '--nlp', type=str,
                        default='parses',
                        help='directory path of NLP parses for each problem')
    parser.add_argument('-i', '--index', type=int, default=2598,
                        help='iIndex of a specific word problem')
    args = parser.parse_args()

    if args.action == 'print':
        examples = LabeledExample.read(args.json)
        example = examples[args.index]
        natural_language = NLP.read(args.nlp, args.index)
        wp = WordProblem(example, natural_language)
        print(wp.extract_template())

    if args.action == 'process':
        examples = LabeledExample.read(args.json)
        indices = [e.index for e in examples.itervalues()]
        natural_language = {i: NLP.read(args.nlp, i) for i in indices}
        word_problems = [WordProblem(examples[i], natural_language[i])
                         for i in indices]
        templates = [wp.extract_template() for wp in word_problems]
        print('{} total and {} unique templates'.format(len(templates),
                                                        len(set(templates))))


if __name__ == '__main__':
    main()
