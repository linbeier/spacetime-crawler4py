from parser import tokenizer

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
        # calculate word frequency
        WordFrequency(word_list, self.word_freq)
        # count word number, get max url
        if self.max_words < len(word_list):
            self.max_words = len(word_list)
            self.max_url = url


    def remove_stopwrds(self, word_list, lang='Eng'):
        return list(filter(self.filter_stop_word, word_list))

    # persistent results to files
    def persistent(self, tokens):
        pass

    def filter_stop_word(self, val):
        if val in self.stopwrds:
            return False
        return True


if __name__ == "__main__":
    f = open("../test/Donald Bren School of Information and Computer Sciences @ University of California, Irvine.html",
             "r", encoding="utf-8")
    texts = f.read()
    c = CrawlParser()
    c.parse()
