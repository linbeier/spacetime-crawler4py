from threading import Thread

from inspect import getsource
from bs4 import BeautifulSoup
from utils.download import download
from utils import get_logger
from urllib.parse import urlparse
import scraper
import time
import re


class Worker(Thread):
    def __init__(self, worker_id, config, frontier, parser, throttler, subdomain, subdomain_lock):
        self.logger = get_logger(f"Worker-{worker_id}")
        self.config = config
        self.frontier = frontier
        self.throttler = throttler
        self.parser = parser
        self.subdomain = subdomain
        self.subdomain_lock = subdomain_lock
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {
            -1}, "Do not use requests from scraper.py"
        super().__init__(daemon=True)

    def run(self):
        while True:
            try:
                tbd_url = self.frontier.get_tbd_url()
                if not tbd_url:
                    self.logger.info("Frontier is empty. Stopping Crawler.")
                    # self.frontier.task_done()
                    break

                domain = self.extract_domain(tbd_url)
                if domain is None:
                    self.logger.info("Domain is none. Continue.")
                    self.frontier.task_done()
                    continue

                if not self.throttler.check_polite(time.time(), domain):
                    # print(f"now time: {time.time()}, last crawled: {self.throttler.last_crawl_time(domain)}, domain: {domain}")
                    # time.sleep(self.config.time_delay)
                    # bypass urls hashset and add to work_queue
                    self.frontier.work_queue.put(tbd_url)
                    self.frontier.task_done()
                    continue

                resp = download(tbd_url, self.config, self.logger)
                soup = self.parse_html(resp)

                self.logger.info(
                    f"Downloaded {tbd_url}, status <{resp.status}>, "
                    f"using cache {self.config.cache_server}.")

                if soup is None:
                    self.logger.info("Soup is None. Continue.")
                    self.frontier.task_done()
                    continue

                tokens = self.parser.parse(soup)
                # if len(tokens) < 50:
                #     self.logger.info("Low info. Continue.")
                #     self.frontier.task_done()
                #     continue

                scraped_urls = scraper.scraper(tbd_url, soup, self.subdomain, self.subdomain_lock)
                # tbd_url_subdomain = self.extract_domain(tbd_url)
                # if re.match(r'(.*)\.ics.uci.edu(.*)', tbd_url_subdomain):
                #     self.subdomain_lock.acquire()
                #     subdomain_temp = self.subdomain.get(tbd_url_subdomain, 0) + 1
                #     self.subdomain[tbd_url_subdomain] = subdomain_temp
                #     self.subdomain_lock.release()

                for scraped_url in scraped_urls:
                    self.frontier.add_url(scraped_url)

                if len(tokens) < 50:
                    self.logger.info("Low info. Continue.")
                    self.frontier.task_done()
                    continue
                self.parser.analyze(tokens, tbd_url)

                self.frontier.mark_url_complete(tbd_url)
                # time.sleep(self.config.time_delay)
            except Exception as e:
                self.frontier.task_done()
                self.logger.error(e)

    def parse_html(self, resp):
        try:
            if resp.status == 200:
                soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
                return soup
            else:
                print("resp.error = ", resp.error)
                return None
        except AttributeError:
            return None

    def extract_domain(self, url):
        if url is None:
            return None
        parsed = urlparse(url)
        return parsed.hostname
