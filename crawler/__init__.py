from utils import get_logger
from crawler.frontier import Frontier
from crawler.worker import Worker
from parser.crawlParser import CrawlParser
import threading

class Crawler(object):
    def __init__(self, config, restart, frontier_factory=Frontier, worker_factory=Worker):
        self.config = config
        self.logger = get_logger("CRAWLER")
        self.frontier = frontier_factory(config, restart)
        self.workers = list()
        self.worker_factory = worker_factory
        self.parser = CrawlParser()
        self.parser_lock = threading.Lock()

    def start_async(self):
        self.workers = [
            self.worker_factory(worker_id, self.config, self.frontier, self.parser, self.parser_lock)
            for worker_id in range(self.config.threads_count)]
        for worker in self.workers:
            worker.start()

    def start(self):
        self.start_async()
        # dispatch urls in batches
        self.crawl()
        self.join()
        self.display()

    def join(self):
        for worker in self.workers:
            worker.join()

    # Each queued link is a new job
    def create_jobs(self):
        self.frontier.tbd_to_queue()
        # block until added tasks batch is done
        self.logger.info(f"New Batch => batch size: {self.frontier.get_queue_size()}, tbd count: {self.frontier.get_tbd_size()}")
        self.frontier.await_batch()
        self.logger.info("Batch Complete")
        self.crawl()

    # Check if there are items in the queue, if so crawl them
    def crawl(self):
        tbd_count = self.frontier.get_tbd_size()
        print(tbd_count)
        if tbd_count > 0:
            self.create_jobs()
        else:
            self.logger.info("Nothing to crawl")

    def display(self):
        with open("word_frequency", "w") as f:
            count = 0
            for k, v in sorted(self.parser.word_freq.items(), key=lambda x: x[1], reverse=True):
                count += 1
                if count > 50:
                    break
                f.write(k + " = " + v)

        with open("max_url", "w") as f:
            f.write(self.parser.max_url + " = " + str(self.parser.max_words))
