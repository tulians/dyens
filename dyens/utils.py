# Dyens utilities
# ===================================

# Built-in modules
import json
import operator


def dump_as_json(data, path):
    # If the file is opened with r+ the file pointer moves down and creates
    # confict when trying to write back.
    with open(path, "r") as f:
        d = json.load(f)
    with open(path, "w") as f:
        d = merge(d, data)
        json.dump(d, f)


def merge(a, b):
    """Merges content of two dictionaries taking into account their keys."""
    def _add(a, b):
        return a + " " + b
    # Get keys in either dictionary a or b but not both.
    merged = {k: a.get(k, b.get(k)) for k in a.keys() ^ b.keys()}
    # Append the value of those keys in both dictionaries.
    merged.update({k: _add(a[k], b[k]) for k in a.keys() & b.keys()})
    return merged


def order_by_frequency(d, amount=10, high_to_low=True):
    """Orders a dictionary by its values."""
    sorted_dict = sorted(d.items(), key=operator.itemgetter(1))
    if high_to_low:
        sorted_dict.reverse()
    return sorted_dict[:amount]
