import json


class Derivation(object):
    def __init__(self):
        pass

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self):
        return dict()


def derive_wp_for_all_templates(wp, templates):
    all_derivations = list()
    # TODO(Eric): might need to map numbers to place in question
    #             with a tuple of indices (sentence, token).
    #             Similarly for nouns
    numbers = wp.nlp.numbers()
    nouns = wp.nlp.nouns()
    print(numbers)
    print(nouns)
    for template in templates:
        all_derivations.extend(derive_wp_and_template(wp, template,
                                                      numbers, nouns))

    return all_derivations


# TODO(Eric): need to match up nouns with unknown slots
#             and numbers with number slots
def derive_wp_and_template(wp, template, numbers, nouns):
    derivations = list()
    return derivations
