# Dyens utilities
# ===================================

# Built-in modules
import json
from collections import Counter


def dump_as_json(data, path):
    # If the file is opened with r+ the file pointer moves down and creates
    # confict when trying to write back.
    with open(path, "r") as f:
        d = json.load(f)
    with open(path, "w") as f:
        d = merge(d, data)
        json.dump(d, f)


def merge(a, b):
    def _add(a, b):
        return a + " " + b
    # Get keys in either dictionary a or b but not both.
    merged = {k: a.get(k, b.get(k)) for k in a.keys() ^ b.keys()}
    # Append the value of those keys in both dictionaries.
    merged.update({k: _add(A[k], B[k]) for k in a.keys() & b.keys()})
    return merged
