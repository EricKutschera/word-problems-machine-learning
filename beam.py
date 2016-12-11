from collections import defaultdict

from derivation import initialize_partial_derivations_for_all_templates

MAX_TOTAL = 200
MAX_PER_TEMPLATE = 20


def beam_search(word_problem, unique_templates,
                score_func, validation_func,
                final_evaluation_func):
    initial_beam = initialize_partial_derivations_for_all_templates(
        word_problem, unique_templates)
    full_derivations = search_to_completion(initial_beam, score_func,
                                            validation_func)
    return final_evaluation_func(full_derivations)


def prune_beam(beam, validation_func):
    return [d for d in beam if validation_func(d)]


def search_to_completion(beam, score_func, validation_func):
    pre_pruned = prune_beam(beam, validation_func)
    if all(derivation.is_complete() for derivation in pre_pruned):
        return pre_pruned

    candidates = list()
    for derivation in beam:
        if derivation.is_complete():
            candidates.append(derivation)
        else:
            candidates.extend(derivation.all_ways_to_fill_next_slot())

    post_pruned = prune_beam(candidates, validation_func)
    best_first = sorted(post_pruned, key=score_func, reverse=True)
    by_template = defaultdict(list)
    for derivation in best_first:
        by_template[derivation.template_index].append(derivation)

    total_after_limit = 0
    limited_by_template = dict()
    for template_index, best in by_template.iteritems():
        # want the best at the end for calls to pop() below
        limited_by_template[template_index] = list(reversed(
            best[:MAX_PER_TEMPLATE]))
        total_after_limit += len(limited_by_template[template_index])

    # cycle through the templates and keep adding the best derivation
    # for each template until MAX_TOTAL are taken or there are no more
    output_size = min(total_after_limit, MAX_TOTAL)
    output_beam = list()
    keys = limited_by_template.keys()
    key_index = 0
    count = 0
    while count < output_size:
        key = keys[key_index]
        derivations = limited_by_template[key]
        if derivations:
            output_beam.append(derivations.pop())
            count += 1

        key_index = (key_index + 1) % len(keys)

    return search_to_completion(output_beam, score_func, validation_func)
