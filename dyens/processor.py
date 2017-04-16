# Dyens processor
# ===================================

"""Gets word frequency from crawled websites."""

# Project specific modules
from utils import dump_as_json, mkdir, mk_json_file

# Built-in modules
import json
import string
from os.path import join, isfile
from collections import defaultdict


class Processor(object):
    """Parses the tags file and gets word frequency for each website."""
    def __init__(self, path):
        self.path = path
        self.word_frequency = {}
        with open(join(self.path, "dump.json"), "r") as f:
            self.words_by_site = json.load(f)
        self.freqs_file_path = mk_json_file(self.path, "freqs.json")

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
