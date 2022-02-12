from threading import Thread

from inspect import getsource
from bs4 import BeautifulSoup
from utils.download import download
from utils import get_logger
from urllib.parse import urlparse
import scraper
import time


class Worker(Thread):
    def __init__(self, worker_id, config, frontier, parser, domain_time, domain_lock, subdomain, subdomain_lock):
        self.logger = get_logger(f"Worker-{worker_id}")
        self.config = config
        self.frontier = frontier
        self.domain_time = domain_time
        self.domain_lock = domain_lock
        self.parser = parser
        self.lock = parser.lock
        self.subdomain = subdomain
        self.subdomain_lock = subdomain_lock
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests from scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                self.frontier.task_done()
                break

            domain = self.extract_domain(tbd_url)
            if domain is None:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                self.frontier.task_done()
                continue

            self.domain_lock.acquire()
            if not self.check_polite(time.time(), domain):
                time.sleep(self.config.time_delay)
            self.domain_lock.release()
            
            self.logger.info(f"Downloading url: {tbd_url}")
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
            if len(tokens) < 50:
                self.logger.info("Low info. Continue.")
                self.frontier.task_done()
                continue

            self.lock.acquire()
            self.parser.analyze(tokens, tbd_url)
            self.lock.release()

            scraped_urls = scraper.scraper(tbd_url, resp, soup)
            tbd_url_subdomain = self.extract_domain(tbd_url)
            if(re.match(r'(.*)ics.uci.edu(.*)', tbd_url_subdomain)):
                self.subdomain_lock.acquire()
                subdomain_temp = subdomain.get(tbd_url_subdomain, 0) + 1
                subdomain[tbd_url_subdomain] = subdomain_temp
                self.subdomain_lock.release()
            

            self.subdomain[tbd_url] = len(scraped_urls)
            self.logger.info(f'[Before add] Valid links: {len(scraped_urls)}')
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.logger.info(f"[Add complete] Current count of tbd: {self.frontier.get_tbd_size()}")
            self.frontier.mark_url_complete(tbd_url)
            # time.sleep(self.config.time_delay)

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

    def check_polite(self, cur_time, domain):
        if domain not in self.domain_time:
            self.domain_time[domain] = cur_time
        else:
            if cur_time < self.domain_time[domain] + 0.5:
                self.domain_time[domain] = cur_time
                return False
            else:
                self.domain_time[domain] = cur_time
                return True


    def extract_domain(self, url):
        if url is None:
            return None
        parsed = urlparse(url)
        return parsed.hostname