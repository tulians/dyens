# Dyens processor
# ===================================

"""Gets word frequency from crawled websites."""

# Project specific modules
from utils import dump_as_json

# Built-in modules
import json
import string
from collections import defaultdict
from os.path import join, split, abspath, isfile


class Processor(object):
    def __init__(self, path):
        self.path = path
        self.word_frequency = {}
        with open(self.path, "r") as f:
            self.words_by_site = json.load(f)
        self.freqs_file_path = join(split(abspath(self.path))[0], "freqs.json")
        if not isfile(self.freqs_file_path):
            with open(self.freqs_file_path, "w") as f:
                json.dump(self.word_frequency, f)

    def set_freq(self):
        """Returs a dictionary with the word frequency for each website."""
        for site, tags in self.words_by_site.items():
            self.word_frequency[site] = defaultdict(int)
            words = tags.split(" ")
            for word in words:
                # Save words containing no punctuation characters.
                match = [char in word for char in string.punctuation]
                if all(m is False for m in match) and len(word) > 3:
                    self.word_frequency[site][word] += 1
        dump_as_json(self.word_frequency, self.freqs_file_path)
        return self.word_frequency
