import argparse

from labeled_example import LabeledExample
from nlp import NLP
from word_problem import WordProblem


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['print'],
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

if __name__ == '__main__':
    main()
