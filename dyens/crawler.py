#!/usr/bin/env python
# Dyens crawler
# ===================================

# Built-in modules
import re
import sys
import json
import time
import argparse
from urllib.parse import urljoin
from urllib.error import URLError
from urllib.request import urlopen
from html.parser import HTMLParser
from collections import defaultdict
from http.client import BadStatusLine


parser = argparse.ArgumentParser(prog="dyens", description="Dyens CLI")
parser.add_argument("start_url", help="Base URL to start crawling from.")
parser.add_argument("path", help="Document in which to save data.")
parser.add_argument("words", nargs="*", help="Words to look for.")
args = parser.parse_args()


class LinkContentParser(HTMLParser):
    """Returns an HTML file along with the URLs in it."""

    def __init__(self):
        HTMLParser.__init__(self)
        self.sites_content = {}

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for (key, value) in attrs:
                if key == "href":
                    new_url = urljoin(self.base_url, value)
                    self.links += [new_url]

    def handle_data(self, tag):
        # Work only with non-empty tag strings.
        if re.sub("[\s+]", "", tag):
            if self.base_url not in self.sites_content:
                self.sites_content[self.base_url] = tag
            else:
                self.sites_content[self.base_url] += " " + tag
            if sys.getsizeof(self.sites_content) > 10e6:
                dump(self.sites_content, args.path)
                self.sites_content = None

    def get_links(self, url):
        self.links = []
        self.base_url = url
        try:
            response = urlopen(url)
        except (URLError, UnicodeEncodeError, BadStatusLine):
            return ("", [])
        if "text/html" in response.getheader("Content-Type"):
            html_bytes = response.read()
            try:
                html_string = html_bytes.decode("utf-8")
            except UnicodeDecodeError:
                html_string = html_bytes.decode("latin-1")
            # Feed the HTML Parser with data to be parsed by handling functs.
            self.feed(html_string)
            return (html_string, self.links)
        else:
            return ("", [])


def crawler(words, start_url, max_pages=10000, display=True):
    """Performs web crawling, returning the site that holds the words."""
    pages_to_visit, number_visited, previous_time = [start_url], 0, 0
    pages_seen, parser = set(pages_to_visit), LinkContentParser()
    search_start_time = time.time()
    while number_visited < max_pages and pages_to_visit:
        current_url = pages_to_visit[0]
        pages_to_visit = pages_to_visit[1:]
        # Measure how much time it takes to get page links.
        previous_time = time.time()
        data, links = parser.get_links(current_url)
        # Process elapsed time.
        previous_time = time.time() - previous_time
        minutes, seconds = divmod((time.time() - search_start_time), 60)
        hours, minutes = divmod(minutes, 60)
        if display:
            print("{:02.0f}:{:02.0f}:{:02.0f}".format(hours, minutes, seconds),
                  "| #", number_visited, "- Visited:", current_url, "in",
                  "{0:.5f}".format(previous_time), "seconds. Set size:",
                  sys.getsizeof(pages_seen), "bytes.", len(pages_to_visit),
                  "sites pending to visit.")
        number_visited += 1
        check_if_contained = [data.find(word) for word in words]
        if all(check > -1 for check in check_if_contained):
            break
        # Avoid returning to the same websites. Checks for duplicates
        # with O(1) complexity.
        for link in links:
            if link not in pages_seen:
                pages_seen.add(link)
                pages_to_visit.append(link)
    if number_visited < max_pages:
        print("SUCCESS:", words, "found at", current_url)
    else:
        print("FAILED: Words never found.")


def dump(data, path):
    with open(path, "w+") as f:
        d = json.load(f)
        # BUG: when same key exists in both dicts.
        d = {**d, **data}
        f.write(json.dumps(d,
                           sort_keys=True,
                           indent=4,
                           separators=(",", ": ")))


if __name__ == '__main__':
    if args.start_url and args.words:
        crawler(args.words, args.start_url)
    else:
        print("Not enough arguments.")