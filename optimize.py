import numpy
from scipy.optimize import fmin_l_bfgs_b

from classifier import Classifier

MAX_ITERATIONS = 50


def optimize_parameters(feature_extractor, word_problems, unique_templates):
    wp_template_indices = list()
    for wp in word_problems:
        wp_template_indices.append(find_template_index(wp, unique_templates))

    ordered_features = feature_extractor.ordered_features
    feature_count = len(ordered_features)

    # TODO(Eric): try random initialization in [0,1]
    weights = numpy.ones(feature_count)

    classifier = Classifier(feature_extractor, weights)

    # TODO(Eric): add regularization
    #             L^{2} norm and \lambda = 0.1
    def func_to_min(parameters):
        classifier.parameters = parameters
        return -classifier.log_likelihood(word_problems, wp_template_indices,
                                          unique_templates)

    # TODO(Eric): verify that the negative here is correct
    def gradient(parameters):
        classifier.parameters = parameters
        return -classifier.log_likelihood_gradient(word_problems,
                                                   wp_template_indices,
                                                   unique_templates)

    optimal, final_value, details = fmin_l_bfgs_b(func_to_min, weights,
                                                  fprime=gradient,
                                                  maxiter=MAX_ITERATIONS)
    print('final_value: {}'.format(final_value))
    print('details: {}'.format(details))
    classifier.parameters = optimal
    return classifier


# TODO(Eric): This is expensive. It should only get called
#             once per word problem at the start of parameter
#             optimization.
def find_template_index(wp, templates):
    correct_template = wp.extract_template()
    for i, template in enumerate(templates):
        if correct_template == template:
            return i

    raise Exception('equations and nlp do not match a template')
