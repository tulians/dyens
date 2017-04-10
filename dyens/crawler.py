#!/usr/bin/env python
# Dyens crawler
# ===================================

"""Crawls websites looking for a set of words given a starting site."""

# Project specific modules
from utils import dump_as_json
from processor import Processor

# Built-in modules
import re
import sys
import json
import time
import argparse
from os.path import isfile
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
        if not isfile(args.path):
            with open(args.path, "w") as f:
                json.dump(self.sites_content, f)

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
            if sys.getsizeof(self.sites_content) > 10e2:
                dump_as_json(self.sites_content, args.path)
                self.sites_content = {}

    def get_links(self, url):
        self.links = []
        self.base_url = url
        try:
            response = urlopen(url)
        except (URLError, UnicodeEncodeError, BadStatusLine,
                ConnectionResetError):
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
        print("Visiting", current_url)
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
                  "sites pending to visit. Accumulated words size",
                  sys.getsizeof(parser.sites_content), "bytes.")
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


if __name__ == '__main__':
    if args.start_url and args.words:
        try:
            crawler(args.words, args.start_url)
        except KeyboardInterrupt:
            p = Processor(args.path)
            word_frequency_per_visited_site = p.set_freq()
    else:
        print("Not enough arguments.")
