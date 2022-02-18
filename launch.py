from configparser import ConfigParser
from argparse import ArgumentParser
import signal
import sys

from utils.server_registration import get_cache_server
from utils.config import Config
from crawler import Crawler
from parser.crawlParser import CrawlParser

def save_on_interupt(parser):
    def signal_handler(sig, frame):
        parser.display()
        print('############ Result Saved on Interuption #############')
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

def main(config_file, restart):
    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)
    config.cache_server = get_cache_server(config, restart)
    parser = CrawlParser()
    crawler = Crawler(config, restart, parser)
    # On Ctrl+C, save result
    save_on_interupt(parser)
    crawler.start()
    # Display statistic results
    parser.display()

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()
    main(args.config_file, args.restart)
