from utils import get_logger
from crawler.frontier import Frontier
from crawler.worker import Worker
from crawler.throttler import Throttler
import threading

class Crawler(object):
    def __init__(self, config, restart, parser, frontier_factory=Frontier, worker_factory=Worker):
        self.config = config
        self.logger = get_logger("CRAWLER")
        self.frontier = frontier_factory(config, restart)
        self.workers = list()
        self.throtter = Throttler(config)
        self.worker_factory = worker_factory
        self.parser = parser
        self.subdomain = {}
        self.subdomain_lock = threading.Lock()

    def start_async(self):
        self.workers = [
            self.worker_factory(worker_id, self.config, self.frontier, self.parser, self.throtter, self.subdomain, self.subdomain_lock)
            for worker_id in range(self.config.threads_count)]
        for worker in self.workers:
            worker.start()

    def start(self):
        self.start_async()
        # dispatch urls in batches
        self.crawl()
        self.join()
        # wirte all unique urls to text
        self.write_unique_url()
        self.wirte_subdomain()

    def join(self):
        for worker in self.workers:
            worker.join()

    # Each queued link is a new job
    def create_jobs(self):
        # self.frontier.tbd_to_queue()
        # block until added tasks batch is done
        self.logger.info(f"New Batch => queue size: {self.frontier.get_queue_size()}, unique count: {self.frontier.unique_page}")
        self.frontier.wait_q()
        self.logger.info("Batch Complete")
        self.crawl()

    # Check if there are items in the queue, if so crawl them
    def crawl(self):
        tbd_count = self.frontier.get_queue_size()
        print(tbd_count)
        if tbd_count > 0:
            self.create_jobs()
        else:
            self.logger.info("Nothing to crawl")

    # write all unique urls from frontier to text
    def write_unique_url(self):
        with open("unique_url.txt", "w") as f:
            for url in self.frontier.detected_urls:
                f.write(url + '\n')

    # sort subdomain with its key in alphabetical order and write to text
    def wirte_subdomain(self):
        self.subdomain = sorted(self.subdomain.items())
        with open("subdomain.txt", "w") as f:
            for d in self.subdomain:
                f.write(str(d))
                f.write('\n')