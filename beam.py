from derivation import initialize_partial_derivations_for_all_templates

MAX_TOTAL = 200
MAX_PER_TEMPLATE = 20


def beam_search(word_problem, unique_templates,
                score_func, validation_func,
                final_evaluation_func):
    initial_beam = initialize_partial_derivations_for_all_templates(
        word_problem, unique_templates)
    beam = prune_beam(initial_beam, validation_func)
    full_derivations = search_to_completion(beam, score_func, validation_func)
    return final_evaluation_func(full_derivations)


def prune_beam(beam, validation_func):
    return [d for d in beam if validation_func(d)]


# TODO
def search_to_completion(beam, score_func, validation_func):
    return beam
