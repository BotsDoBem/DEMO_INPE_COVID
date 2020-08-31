__author__='thiagocastroferreira'

import json

import nlg.structuring as structuring
import nlg.lexicalization as lexicalization
import nlg.reference as reference
from nlg.realization import Realization

class Generation:
    def __init__(self, structuring_path, lexicalization_path, references_path, lexicon_path):
        self.structuring_grammar = json.load(open(structuring_path))
        self.lexicalization_grammar = json.load(open(lexicalization_path))
        self.references = json.load(open(references_path))
        self.realization = Realization(lexicon_path)

    def generate(self, messages, strategy='random'):
        # structuring
        paragraphs = structuring.generate(messages, self.structuring_grammar, strategy)
        # lexicalization
        templates, struct = lexicalization.generate(paragraphs, self.lexicalization_grammar, strategy)
        # referring expression generation
        paragraphs = reference.realize(templates, self.references, strategy)

        # surface realization
        paragraphs = self.realization.realize(paragraphs)
        return struct, templates, paragraphs