import os
import shelve
import threading

from threading import Thread, RLock
from queue import Queue, Empty

from utils import get_logger, get_urlhash, normalize
from scraper import is_valid

class Frontier(object):
    def __init__(self, config, restart):
        self.logger = get_logger("FRONTIER")
        self.config = config
        # links to be downloaded (current batch and next batch)
        # detected urls set, used to keep unique pages
        self.urls_lock = threading.Lock()
        self.detected_urls = set()

        self.unique_page_lock = threading.Lock()
        self.unique_page = 0

        # global crawled links
        # self.dow_lock = threading.Lock()
        # self.downloaded = set()
        # thread-safe queue containing tbd links in the current batch
        self.work_queue = Queue()

        self.task_done_times = 0
        # self.batch_size = 0
        
        if not os.path.exists(self.config.save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.save_file}, "
                f"starting from seed.")
        elif os.path.exists(self.config.save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.save_file}, deleting it.")
            os.remove(self.config.save_file)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.save_file)
        if restart:
            for url in self.config.seed_urls:
                self.add_url(url)
        else:
            # Set the frontier state with contents of save file.
            self._parse_save_file()
            if not self.save:
                for url in self.config.seed_urls:
                    self.add_url(url)

    def _parse_save_file(self):
        ''' This function can be overridden for alternate saving techniques. '''
        total_count = len(self.save)
        tbd_count = 0
        for url, completed in self.save.values():
            if not completed and is_valid(url):
                self.work_queue.put(url)
                tbd_count += 1
        self.logger.info(
            f"Found {tbd_count} urls to be downloaded from {total_count} "
            f"total urls discovered.")

    def get_tbd_url(self):
        try:
            return self.work_queue.get()
        except Empty:
            return None

    def add_url(self, url):
        url = normalize(url)
        urlhash = get_urlhash(url)

        if urlhash in self.save:
            return

        self.urls_lock.acquire()
        if url in self.detected_urls:
            return
        self.urls_lock.release()

        # self.dow_lock.acquire()
        # if url in self.downloaded:
        #     return
        # self.dow_lock.release()

        self.save[urlhash] = (url, False)
        self.save.sync()

        self.urls_lock.acquire()
        self.detected_urls.add(url)
        self.urls_lock.release()

        self.work_queue.put(url)
    
    def mark_url_complete(self, url):
        self.unique_page_lock.acquire()
        self.unique_page += 1
        self.unique_page_lock.release()

        # self.dow_lock.acquire()
        # self.downloaded.add(url)
        # self.dow_lock.release()

        print(f"=====> Crawled {self.unique_page} urls <========")
        print(f"=====> queue size: {self.work_queue.qsize()}")
        self.task_done()
        urlhash = get_urlhash(url)
        if urlhash not in self.save:
            # This should not happen.
            self.logger.error(
                f"Completed url {url}, but have not seen it before.")
        self.save[urlhash] = (url, True)
        self.save.sync()

    def task_done(self):
        # thread calls task_done() to indicate that the item was retrieved and all work on it is complete
        self.work_queue.task_done()
        self.task_done_times += 1
        self.logger.critical(f"@@@@@@@@ task done {self.task_done_times} times @@@@@@@")

    # def tbd_to_queue(self):
    #     for url in self.to_be_downloaded:
    #         self.work_queue.put(url)
    #     self.batch_size = self.work_queue.qsize()
    #
    # def get_tbd_size(self):
    #     self.tbd_lock.acquire()
    #     tbd_len = len(self.to_be_downloaded)
    #     self.tbd_lock.release()
    #     return tbd_len

    def wait_q(self):
        self.logger.info("Waiting queue to be finished")
        self.work_queue.join()
        self.task_done_times = 0
        # self.batch_size = 0

    def get_queue_size(self):
        return self.work_queue.qsize()