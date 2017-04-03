#!/usr/bin/env python
# Dyens crawler
# ===================================

# Built-in modules
import time
import urllib
import argparse
from urllib.parse import urljoin
from urllib.error import URLError
from urllib.request import urlopen
from html.parser import HTMLParser
from http.client import BadStatusLine


avoid = ["facebook", "youtube", "twitter", "t.co", ".pptx", ".ppt", ".xls",
         ".xlsx", ".xml", ".xlt", ".pdf", ".jpg", ".png", ".svg", ".doc",
         ".docx", "play.google", "goo.gl", "mailto:", ".pps"]

parser = argparse.ArgumentParser(prog="dyens", description="Dyens CLI")
parser.add_argument("start_url", help="Base URL to start crawling from.")
parser.add_argument("words", help="Words to look for.")
args = parser.parse_args()


def analyse_resource_extension(url):
    match = [ext in url for ext in avoid]
    return any(element is True for element in match)


class LinkParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for (key, value) in attrs:
                if key == "href":
                    new_url = urljoin(self.base_url, value)
                    self.links += [new_url]

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
            self.feed(html_string)
            return (html_string, self.links)
        else:
            return ("", [])


def crawler(words, start_url, max_pages=1000000):
    pages_to_visit, number_visited, previous_time = [start_url], 0, 0
    pages_seen = set(pages_to_visit)
    parser = LinkParser()
    search_start_time = time.time()
    while number_visited < max_pages and pages_to_visit:
        current_url = pages_to_visit[0]
        pages_to_visit = pages_to_visit[1:]
        previous_time = time.time()
        data, links = parser.get_links(current_url)
        # Avoid asking for non-HTML resources or HTML of humongous size.
        links = list(filter(
            lambda x: analyse_resource_extension(x) is False, links))
        # Process elapsed time.
        previous_time = time.time() - previous_time
        minutes, seconds = divmod((time.time() - search_start_time), 60)
        hours, minutes = divmod(minutes, 60)
        print("{:02.0f}:{:02.0f}:{:02.0f}".format(hours, minutes, seconds),
              "| #", number_visited, "- Visited:", current_url, "in",
              "{0:.5f}".format(previous_time), "seconds.")
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
        words = [args.words]
        crawler(words, args.start_url)
    else:
        print("Not enough arguments.")