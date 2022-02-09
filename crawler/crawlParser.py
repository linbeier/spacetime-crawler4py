from crawler import tokenizer
from bs4 import BeautifulSoup
from bs4.element import Comment
import re

#
# def filter_nontext(element):
#     if isinstance(element, Comment):
#         return False
#     if element.parent.name in ['[document]', 'script', 'meta', 'head', 'html', 'input', 'style', 'noscript', 'canvas']:
#         return False
#     if re.match(r'[\r\s\n]+', str(element)):
#         return False
#     return True
def WordFrequency(tokenList, tokenDict):
    for token in tokenList:
        if token in tokenDict:
            tokenDict[token] += 1
        else:
            tokenDict[token] = 1


class CrawlParser:
    def __init__(self):
        self.stopwrds = self.load_stopwrds()
        pass

    def load_stopwrds(self, Lang = 'Eng'):
        file_name = 'stop_words_' + Lang
        stopwrds = set()
        with open(file_name, 'r', encoding = "utf-8") as f:
            for line in f:
                stopwrds.add(line.strip())
        return stopwrds

    # need pre-parse html, arg is a html file
    def parse(self, file):
        token = tokenizer.tokenizer()
        soup = BeautifulSoup(file, features="html.parser")
        # strip html header
        text = soup.get_text()
        # print(text)
        word_set = token.Tokenize(text)
        print(word_set) # todo
        word_set = self.remove_stopwrds(word_set)
        print(word_set) # todo
        return word_set

    def remove_stopwrds(self, word_set, lang = 'Eng'):
        for word in word_set:
            if word in self.stopwrds:
                word_set.remove(word)
        return word_set

    # persistent results to files
    def persistent(self, tokens):
        pass


if __name__ == "__main__":
    f = open("../test/Donald Bren School of Information and Computer Sciences @ University of California, Irvine.html",
            "r", encoding = "utf-8")
    texts = f.read()
    c = CrawlParser()
    c.parse(texts)
