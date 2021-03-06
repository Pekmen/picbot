#!/usr/bin/python
# -*- coding: <encoding name> -*-
#
#
# This program will check front page of any given subreddit and download
# all imgur images posted as submissions to folders in directory where thed
# script is located. Each user has folder containing his submitted images in
# the last {limit} submissions at front page.
# Duplicate images would be ignored.
# Imgur API evaded because more fun.

import os
import sys
import requests
from bs4 import BeautifulSoup
import time


"""
    Handler for downloading pics from Reddit front page.
"""
class RedditPicsHandler():

    def __init__(self, subr, limit=100):
        # limit number of parsed links
        self.limit = limit
        self.subr = subr
        self.fp_url = 'http://www.reddit.com/r/%s/.json?limit=%s' % (self.subr,
                                                                     self.limit)
        self.limit = limit
        self.children = requests.get(self.fp_url).json()['data']['children']

    def extract_album(self, alb_url):
        """
        Returns a list of all images in an album.
        """
        self.alb_url = alb_url
        html_source = requests.get(self.alb_url)
        soup = BeautifulSoup(html_source.text)
        img_links = set(soup.select('.album-view-image-link a'))
        album = [link.get('href') for link in img_links]
        return album

    def extract_links(self):
        """
        Extracting images links from url using generators.
        """
        for child in self.children:
            author = child['data']['author']
            img_url = child['data']['url']

            # is not an imgur link
            if "imgur.com" not in img_url:
                continue
            # is album
            elif "imgur.com/a/" in img_url:
                for pic in self.extract_album(img_url):
                    yield (author, "http:%s" % pic)
            # is direct link to pic
            elif "i.imgur" in img_url:
                yield (author, img_url)
            else:
                yield (author, "%s.jpg" % img_url)

    def download_image(self, img_url, local_file_name):
        self.img_url = img_url
        self.local_file_name = local_file_name
        response = requests.get(self.img_url)
        if response.status_code == 200:
            print "Downloading %s..." % (self.local_file_name)
            with open(self.local_file_name, 'wb') as fo:
                for chunk in response.iter_content(4096):
                    fo.write(chunk)

    def write_to_file(self, author, img_url):
        self.author = author
        self.img_url = img_url

        curr_dir = os.getcwd()
        dirpath = os.path.join(curr_dir, self.author)
        filename = self.img_url[self.img_url.find('.com') + 5:]
        filepath = os.path.join(dirpath, filename)
        try:
            os.mkdir(dirpath)
        except OSError:
            pass
        if not os.path.exists(filepath):
            self.download_image(self.img_url, filepath)


def main():
    start = time.time()

    subreddit = sys.argv[1]
    sub_handler = RedditPicsHandler(subreddit)
    for author, img_url in sub_handler.extract_links():
        sub_handler.write_to_file(author, img_url)

    end = time.time()
    print "Time elapsed: %s seconds" % (int(end - start))

if __name__ == "__main__":
    main()