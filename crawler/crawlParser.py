import tokenizer
from bs4 import BeautifulSoup
from bs4.element import Comment
import re


def filter_nontext(element):
    if isinstance(element, Comment):
        return False
    if element.parent.name in ['[document]', 'script', 'meta', 'head', 'html', 'input', 'style', 'noscript', 'canvas'
        , 'div']:
        return False
    if re.match(r'[\r\s\n]+', str(element)):
        return False
    return True


class CrawlParser:
    def __init__(self):
        pass

    # need pre-parse html, arg is a html file
    def parse(self, file):
        token = tokenizer.tokenizer()
        soup = BeautifulSoup(file, features="html.parser")
        # strip html header
        text = soup.find_all(text=True)
        visible_text = filter(filter_nontext, text)
        visible_list = []
        for t in visible_text:
            visible_list.append(t)

        word_dict = token.Tokenize(visible_list)
        return word_dict

    # persistent results to files
    def persistent(self, tokens):
        pass


if __name__ == "__main__":
    f = open("../test/Donald Bren School of Information and Computer Sciences @ University of California, Irvine.html", "r")
    texts = f.read()
    c = CrawlParser()
    c.parse(texts)
