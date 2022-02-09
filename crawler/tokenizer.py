import re
import sys


class tokenizer():
    # Uses regular expression to tokenize, generally need O(2^m)+O(n), where m represents regular expression length
    # and n represents length of input. Since we only compile regular expression once, the overall time complexity is O(n)
    # refactor from tokenize line by line to tokenize whole file
    def Tokenize(self, file):
        tokens = []
        prog = re.compile(r"(?=[ -~])([A-Za-z0-9@#*&']{2,})")
        temptoken = prog.findall(file)
        if temptoken:
            temptoken = [x.lower() for x in temptoken]
            tokens.extend(temptoken)
        return tokens

    # Use hash map to store token and its frequency, time complexity is O(n)
    def WordFrequency(self, file):
        tokenList = self.Tokenize(file)
        tokenDict = {}
        for token in tokenList:
            if token in tokenDict:
                tokenDict[token] += 1
            else:
                tokenDict[token] = 1
        return tokenDict

    # Iterate hash map and print key and value, time complexity is O(n)
    def PrintFrequency(self, tokenMap):
        for k, v in sorted(tokenMap.items(), key=lambda x: x[1], reverse=True):
            print (k, "=", v)


if __name__ == "__main__":
    file = open(sys.argv[1], "r")
    t = tokenizer()
    t.PrintFrequency(t.WordFrequency(t.Tokenize(file)))
