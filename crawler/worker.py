from threading import Thread

from inspect import getsource
from bs4 import BeautifulSoup
from utils.download import download
from utils import get_logger
import scraper
import time


class Worker(Thread):
    def __init__(self, worker_id, config, frontier, parser):
        self.logger = get_logger(f"Worker-{worker_id}")
        self.config = config
        self.frontier = frontier
        self.parser = parser
        self.lock = parser.lock
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

            tokens = self.parser.parse(resp, soup)
            if len(tokens) < 50:
                self.logger.info("Low info. Continue.")
                self.frontier.task_done()
                continue

            self.lock.aquire()
            self.parser.analyze(tokens, tbd_url)
            self.lock.release()

            scraped_urls = scraper.scraper(tbd_url, resp, soup)
            self.logger.info(f'[Before add] Valid links: {len(scraped_urls)}')
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.logger.info(f"[Add complete] Current count of tbd: {self.frontier.get_tbd_size()}")
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)

    def parse_html(self, resp):
        if resp.status == 200:
            soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
            return soup
        else:
            print("resp.error = ", resp.error)
            return None