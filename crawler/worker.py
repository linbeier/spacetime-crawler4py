from threading import Thread

from inspect import getsource

from bs4 import BeautifulSoup

from utils.download import download
from utils import get_logger
import scraper
import time
from parser import crawlParser
import re


def parse_html(resp):
    try:
        if resp.status == 200:
            soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
            return soup
        else:
            print("resp.error = ", resp.error)
            return None
    except AttributeError:
        return None


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.word_frequency = {}
        self.max_words_number = 0
        self.max_words_url = ""
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {
            -1}, "Do not use requests from scraper.py"
        super().__init__(daemon=True)

    def run(self):
        subdomains = {}
        p = crawlParser.CrawlParser()
        # write urls in a text file - single thread

        while True:
            tbd_url = self.frontier.get_tbd_url()

            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                fd = open("word_frequency", "w")
                count = 0
                for k, v in sorted(self.word_frequency.items(), key=lambda x: x[1], reverse=True):
                    count += 1
                    if count > 50:
                        break
                    fd.write(k + " = " + v)

                fd.close()
                fd = open("max_words_url", "w")
                fd.write(self.max_words_url + " = " + str(self.max_words_number))
                fd.close()

                subdomains = sorted(subdomains.items())
                f_subdomain = open("subdomain.txt", "w")
                for d in subdomains:
                    f_subdomain.write(d, "\n")
                f_subdomain.close()
                break

            resp = download(tbd_url, self.config, self.logger)
            soup = parse_html(resp)

            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")

            if soup is None:
                continue

            tokens = p.parse(resp, soup)
            if len(tokens) < 50:
                continue

            scraped_urls = scraper.scraper(tbd_url, resp, soup)


            if re.match(r'(.*)ics.uci.edu(.*)', tbd_url):
                find_sub_domain(subdomains, tbd_url, scraped_urls)

            # count word number, get max url
            if self.max_words_number < len(tokens):
                self.max_words_number = len(tokens)
                self.max_words_url = tbd_url

            # calculate word frequency
            crawlParser.WordFrequency(tokens, self.word_frequency)

            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)


'''
subdomains - dictionary that contains <domain, pageset>
url - domain that has subdomain ics.uci.edu
list - pages scrapted from the url
'''


def find_sub_domain(subdomains, url, list):
    if url not in subdomains:
        s = set()
        for page in list:
            s.add(page)
        subdomains[url] = s
