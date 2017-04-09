# Dyens processor
# ===================================

"""Gets words' frequency from crawled websites."""

# Built-in modules
import json
import string
from collections import defaultdict


class Processor(object):
    def __init__(self, path):
        self.words_frequency = {}
        with open(path, "r") as f:
            self.words_by_site = json.load(f)

    def set_freq(self):
        """Returs a dictionary with the word frequency for each website."""
        for site, tags in self.words_by_site.items():
            self.words_frequency[site] = defaultdict(int)
            words = tags.split(" ")
            for word in words:
                match = [char in word for char in string.punctuation]
                if all(m is False for m in match):
                    self.words_frequency[site][word] += 1
        return self.words_frequency
