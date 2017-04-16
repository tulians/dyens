# Dyens utilities
# ===================================

# Built-in modules
import json
import operator
from os import makedirs
from os.path import join, isfile, exists


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
        if a != b:
            return a + " " + b
        return a
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


def mkdir(path, name):
    """Creates a directory with name 'name' under 'path'."""
    new_directory_path = join(path, name)
    if not exists(new_directory_path):
        makedirs(new_directory_path)
    return new_directory_path


def mk_json_file(path, name, content={}):
    """Creates a json file with name 'name' under 'path' with 'content'."""
    new_file_path = join(path, name)
    if not isfile(new_file_path):
        with open(new_file_path, "w") as f:
            json.dump(content, f)
    return new_file_path
