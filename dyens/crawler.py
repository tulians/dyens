#!/usr/bin/env python
# Dyens crawler
# ===================================

"""Crawls websites looking for a set of words given a starting site."""

# Project specific modules
from processor import Processor
from utils import dump_as_json, mkdir, mk_json_file

# Built-in modules
import re
import sys
import json
import time
import signal
import argparse
# import matplotlib.pyplot as plt
# from PIL import Image
from os import popen
from os.path import join
from random import randrange
from urllib.parse import urljoin
from urllib.error import URLError
from urllib.request import urlopen
from html.parser import HTMLParser
from http.client import BadStatusLine, IncompleteRead


parser = argparse.ArgumentParser(prog="dyens", description="Dyens CLI")
parser.add_argument("start_url", help="Base URL to start crawling from.")
parser.add_argument("path", help="Directory in which to save data.")
args = parser.parse_args()


class LinkContentParser(HTMLParser):
    """Returns an HTML file along with the URLs in it."""
    def __init__(self):
        HTMLParser.__init__(self)
        self.sites_content = {}
        self.linker = {}
        self.assets_path = mkdir(args.path, "assets")
        self.image_assets_path = mkdir(self.assets_path, "images")
        self.pdfs_assets_path = mkdir(self.assets_path, "pdfs")
        self.raw_data = mk_json_file(args.path, "dump.json")
        self.linker_path = mk_json_file(self.assets_path, "linker.json")

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
                dump_as_json(self.sites_content, self.raw_data)
                self.sites_content = {}

    def get_links(self, url):
        """Returns HTML files and downloads other assets."""
        def _get_and_link_resource(asset_path):
            """Links downloaded asset name with its soure URL."""
            path = join(asset_path, str(randrange(1000000)))
            with open(path, "wb") as f:
                f.write(response.read())
            self.linker[url] = path
            dump_as_json(self.linker, self.linker_path)
            return ("", [])

        self.links = []
        self.base_url = url
        try:
            with self._Timeout(120):
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
                    # Feed the HTML Parser with data to be parsed by handling
                    # functs.
                    self.feed(html_string)
                    return (html_string, self.links)
                elif "image/" in response.getheader("Content-Type"):
                    return _get_and_link_resource(self.image_assets_path)
                elif "application/pdf" in response.getheader("Content-Type"):
                    try:
                        return _get_and_link_resource(self.pdfs_assets_path)
                    except IncompleteRead:
                        return ("", [])
                else:
                    return ("", [])
        except self._Timeout.Timeout:
            print("TIMEOUT")
            return ("", [])

    class _Timeout():
        """Timeout class using ALARM signal."""
        class Timeout(Exception):
            pass

        def __init__(self, sec):
            self.sec = sec

        def __enter__(self):
            signal.signal(signal.SIGALRM, self.raise_timeout)
            signal.alarm(self.sec)

        def __exit__(self, *args):
            signal.alarm(0)

        def raise_timeout(self, *args):
            raise self.Timeout()


def crawler(start_url, max_pages=None, display=True):
    """Performs web crawling, returning the site that holds the words."""
    pages_to_visit, number_visited, previous_time = [start_url], 0, 0
    pages_seen, parser = set(pages_to_visit), LinkContentParser()
    search_start_time = time.time()
    while pages_to_visit:
        current_url = pages_to_visit[0]
        print("Visiting", current_url)
        pages_to_visit = pages_to_visit[1:]
        # Measure how much time it takes to get page links.
        previous_time = time.time()
        data, links = parser.get_links(current_url)
        # Process elapsed time.
        previous_time = time.time() - previous_time
        # Presents time elapsed in console.
        minutes, seconds = divmod((time.time() - search_start_time), 60)
        hours, minutes = divmod(minutes, 60)
        if display:
            _, columns = popen('stty size', 'r').read().split()
            print("{:02.0f}:{:02.0f}:{:02.0f}".format(hours, minutes, seconds),
                  "| #", number_visited, "- Visited:", current_url, "in",
                  "{0:.5f}".format(previous_time), "seconds. Set size:",
                  sys.getsizeof(pages_seen), "bytes. Set length:",
                  len(pages_seen), "elements.", len(pages_to_visit),
                  "sites pending to visit. Accumulated words size",
                  sys.getsizeof(parser.sites_content), "bytes.\n{}".format(
                      "-" * int(columns)))
        number_visited += 1
        if max_pages and number_visited >= max_pages:
            break
        # Avoid returning to the same websites. Checks for duplicates
        # with O(1) complexity.
        for link in links:
            if link not in pages_seen:
                pages_seen.add(link)
                pages_to_visit.append(link)


if __name__ == '__main__':
    if args.start_url:
        try:
            crawler(args.start_url)
        except KeyboardInterrupt:
            p = Processor(args.path)
            word_frequency_per_visited_site = p.set_freq()
    else:
        print("Not enough arguments.")
