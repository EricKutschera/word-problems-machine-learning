import argparse
import json

from labeled_example import LabeledExample
from nlp import NLP
from word_problem import WordProblem
from template import Template
from features import FeatureExtractor
from optimize import optimize_parameters


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['print', 'find-template-set',
                                           'count-unique', 'extract-features',
                                           'fold'],
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
    parser.add_argument('-p', '--parameters', type=str,
                        default='parameters.json',
                        help='file to write or read optimal parameters')
    parser.add_argument('-tf', '--testfold', type=int,
                        default=0,
                        help='fold to use as test set')
    parser.add_argument('-nf', '--numfolds', type=int,
                        default=5,
                        help='number of folds for cross validation')
    parser.add_argument('-fo', '--foldoutput', type=str,
                        default='{}_folds_test_{}.json',
                        help='template for file name of fold results')
    args = parser.parse_args()

    if args.action == 'print':
        call_print(args.json, args.index, args.nlp)

    if args.action == 'find-template-set':
        call_find_template_set(args.json, args.nlp, args.templates)

    if args.action == 'count-unique':
        call_count_unique(args.json, args.unique, args.nlp)

    if args.action == 'extract-features':
        call_extract_features(args.json, args.nlp, args.templates,
                              args.parameters)

    if args.action == 'fold':
        call_fold(args.testfold, args.numfolds, args.foldoutput,
                  args.json, args.nlp, args.templates,
                  args.parameters)


def make_fold_indices(num_folds, total):
    min_per = total / num_folds
    extra = total % num_folds
    indices = list()
    count = 0
    for i in range(num_folds):
        plus = 0
        if extra > 0:
            plus = 1
            extra -= 1

        indices.append(range(count, count + min_per + plus))
        count += min_per + plus

    return indices


def call_fold(arg_testfold, arg_numfolds, arg_foldoutput,
              arg_json, arg_nlp, arg_templates, arg_parameters):
    examples = LabeledExample.read(arg_json)
    indices = [e.index for e in examples.itervalues()][:5]  # TODO just 5 for testing
    natural_language = {i: NLP.read(arg_nlp, i) for i in indices}
    word_problems = [WordProblem(examples[i], natural_language[i])
                     for i in indices]

    fold_indices = make_fold_indices(arg_numfolds, len(word_problems))
    test_indices = fold_indices.pop(arg_testfold)
    train_indices = list()
    for per_fold in fold_indices:
        train_indices.extend(per_fold)

    with open(arg_templates, 'rt') as f_handle:
        raw = f_handle.read()

    parsed = json.loads(raw)
    unique_templates = [Template.from_json(j) for j in parsed['templates']]
    wp_template_map = {int(k): v
                       for k, v in parsed['wp_template_map'].iteritems()}

    train_wps = [word_problems[i] for i in train_indices]
    train_templates_indices = list({wp_template_map[wp.labeled_example.index]
                                    for wp in train_wps})
    remap_templates = {wp.labeled_example.index:
                       train_templates_indices.index(
                           wp_template_map[wp.labeled_example.index])
                       for wp in train_wps}
    train_templates = [unique_templates[i] for i in train_templates_indices]

    feature_extractor = FeatureExtractor(train_templates, train_wps)
    classifier = optimize_parameters(feature_extractor, train_wps,
                                     train_templates, remap_templates)
    with open(arg_parameters, 'wt') as f_handle:
        f_handle.write(json.dumps(classifier.to_json()))

    # TODO classify the test set
    correct = 0
    print('{} correct out of {}'.format(correct, len(test_indices)))


def call_extract_features(arg_json, arg_nlp, arg_templates, arg_parameters):
    examples = LabeledExample.read(arg_json)
    indices = [e.index for e in examples.itervalues()]
    natural_language = {i: NLP.read(arg_nlp, i) for i in indices}
    word_problems = [WordProblem(examples[i], natural_language[i])
                     for i in indices]

    with open(arg_templates, 'rt') as f_handle:
        raw = f_handle.read()

    parsed = json.loads(raw)
    unique_templates = [Template.from_json(j) for j in parsed['templates']]
    wp_template_map = {int(k): v
                       for k, v in parsed['wp_template_map'].iteritems()}

    # TODO(Eric): using only 2 word problems for testing
    # unique_templates = unique_templates[:2]
    word_problems = word_problems[:2]

    feature_extractor = FeatureExtractor(unique_templates, word_problems)
    classifier = optimize_parameters(feature_extractor, word_problems,
                                     unique_templates, wp_template_map)
    with open(arg_parameters, 'wt') as f_handle:
        f_handle.write(json.dumps(classifier.to_json()))


def call_count_unique(arg_json, arg_unique, arg_nlp):
    examples = LabeledExample.read(arg_json)
    templates = list()
    for index in arg_unique:
        example = examples[index]
        natural_language = NLP.read(arg_nlp, index)
        wp = WordProblem(example, natural_language)
        templates.append(wp.extract_template())

    print(len(set(templates)))
    print(json.dumps([t.to_json() for t in templates]))


def call_find_template_set(arg_json, arg_nlp, arg_templates):
    examples = LabeledExample.read(arg_json)
    indices = [e.index for e in examples.itervalues()]
    natural_language = {i: NLP.read(arg_nlp, i) for i in indices}
    word_problems = [WordProblem(examples[i], natural_language[i])
                     for i in indices]
    templates = [wp.extract_template() for wp in word_problems]

    unique = list()
    wp_template_map = dict()
    for wp in word_problems:
        template = wp.template
        wp_index = wp.labeled_example.index
        found_template = False
        for unique_i, u in enumerate(unique):
            if template == u:
                wp_template_map[wp_index] = unique_i
                found_template = True
                break

        if not found_template:
            unique.append(template)
            wp_template_map[wp_index] = len(unique) - 1

    print('{} total and {} unique templates'.format(len(templates),
                                                    len(unique)))
    with open(arg_templates, 'wt') as f_handle:
        out_json = {'templates': [t.to_json() for t in unique],
                    'wp_template_map': wp_template_map}
        f_handle.write(json.dumps(out_json))


def call_print(arg_json, arg_index, arg_nlp):
    examples = LabeledExample.read(arg_json)
    example = examples[arg_index]
    natural_language = NLP.read(arg_nlp, arg_index)
    wp = WordProblem(example, natural_language)
    wp.extract_template()
    print(wp)
    print('questions: {}'
          .format([(s.as_text(), s.object_of_sentence())
                   for s in wp.nlp.questions().itervalues()]))
    print('commands: {}'
          .format([(s.as_text(), s.object_of_sentence())
                   for s in wp.nlp.commands().itervalues()]))


if __name__ == '__main__':
    main()
