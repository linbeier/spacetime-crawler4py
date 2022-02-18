import threading

class Throttler(object):
    def __init__(self, config):
      self.config = config
      self.domain_time = {}
      self.lock = threading.Lock()

    def check_polite(self, cur_time, domain):
        result = False
        self.lock.acquire()
        if domain not in self.domain_time:
            result = True
        elif cur_time >= (self.domain_time[domain] + self.config.time_delay):
            result = True
        else:
            result = False
        if result:
            self.domain_time[domain] = cur_time
        self.lock.release()
        return result

    def last_crawl_time(self, domain):
      return self.domain_time[domain]