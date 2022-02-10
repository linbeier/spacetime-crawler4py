from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
from crawler import crawlParser


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.word_frequency = {}
        self.max_words_number = 0
        self.max_words_url = ""
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests from scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        p = crawlParser.CrawlParser()
        # write urls in a text file - single thread
        fo = open("url.txt", "a")
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                fd = open("word_frequency", "w")
                for k, v in sorted(self.word_frequency.items(), key=lambda x: x[1], reverse=True):
                    fd.write(k + " = " + v)
                fd.close()
                fd = open("max_words_url", "w")
                fd.write(self.max_words_url + " = " + self.max_words_number)
                fd.close()
                fo.close()
                break
            fo.write(tbd_url + "\n")
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            tokens = p.parse(resp)

            # count word number, get max url
            if self.max_words_number < len(tokens):
                self.max_words_number = len(tokens)
                self.max_words_url = tbd_url
            # calculate word frequency
            crawlParser.WordFrequency(tokens, self.word_frequency)
            # crawlParser.CrawlParser.persistent(tokens)
            scraped_urls = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
