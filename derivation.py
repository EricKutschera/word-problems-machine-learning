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
    for template in templates:
        all_derivations.extend(derive_wp_and_template(wp, template))

    return all_derivations


# TODO(Eric): need to match up nouns with unknown slots
#             and numbers with number slots
def derive_wp_and_template(wp, template):
    derivations = list()
    return derivations
