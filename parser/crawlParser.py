from parser import tokenizer
import threading

def WordFrequency(tokenList, tokenDict):
    for token in tokenList:
        if token in tokenDict:
            tokenDict[token] += 1
        else:
            tokenDict[token] = 1

class CrawlParser:
    def __init__(self):
        self.stopwrds = self.load_stopwrds()
        self.max_words = 0
        self.max_url = ""
        self.word_freq = {}
        self.lock = threading.Lock()

    def load_stopwrds(self, Lang='Eng'):
        file_name = './parser/stop_words_' + Lang
        stopwrds = set()
        with open(file_name, 'r', encoding="utf-8") as f:
            for line in f:
                stopwrds.add(line.strip())
        return stopwrds

    # need pre-parse html, arg is a html file
    def parse(self, soup):
        token = tokenizer.tokenizer()
        # strip html header
        text = soup.get_text()
        # print(text)
        word_list = token.Tokenize(text)
        word_list = self.remove_stopwrds(word_list)
        return word_list

    def analyze(self, word_list, url):
        self.lock.acquire()
        # calculate word frequency
        WordFrequency(word_list, self.word_freq)
        # count word number, get max url
        if self.max_words < len(word_list):
            self.max_words = len(word_list)
            self.max_url = url
            print(f"max_url update: {self.max_url}")
        self.lock.release()


    def remove_stopwrds(self, word_list, lang='Eng'):
        return list(filter(self.filter_stop_word, word_list))

    # persistent results to files
    def persistent(self, tokens):
        pass

    def filter_stop_word(self, val):
        if val in self.stopwrds:
            return False
        return True

    def display(self):
        with open("word_frequency.txt", "w") as f:
            count = 0
            for k, v in sorted(self.word_freq.items(), key=lambda x: x[1], reverse=True):
                count += 1
                if count > 50:
                    break
                f.write(f"{k} = {v}\n")

        with open("max_url.txt", "w") as f:
            f.write(f"{self.max_url}  =  {self.max_words}\n")