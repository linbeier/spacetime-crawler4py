import tokenizer
from bs4 import BeautifulSoup
from bs4.element import Comment

def filter_nontext(element):
    if isinstance(element, Comment):
        return False
    if element.parent.name in ['[document]', 'script', 'meta', 'head', 'html', 'input', 'style', 'noscript', 'canvas']:
        return False
    return True

class CrawlParser:
    def __init__(self):
        pass

    #need pre-parse html, arg is a html file
    def parse(self, file):
        t = tokenizer.tokenizer()
        soup = BeautifulSoup(file, features="html.parser")
        #strip html header
        text = soup.find_all(text=True)
        visible_text = filter(filter_nontext, text)
        for t in visible_text:
            print(t.strip())

        # word_dict = t.Tokenize(text)
        # print(word_dict)
        pass

    #persistent results to files
    def persistent(self, tokens):
        pass


if __name__ == "__main__":
    f = open("../test/www.ics.uci.edu.html", "r")
    texts = f.read()
    c = CrawlParser()
    c.parse(texts)
