import re
from urllib.parse import urlparse, urldefrag, urljoin
from bs4 import BeautifulSoup


def scraper(url, soup):
    links = extract_next_links(url, soup)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, soup):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    urls = []
    
    for link in soup.find_all('a'):
        urls.append(process_link(url, link.get('href')))

    print("found urls = ", len(urls))
    return urls


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    if url is None:
        return False

    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if not check_domain(parsed):
            return False
        if check_calender(url):
            return False
        if repeated(url):
            return False
        if block(url):
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico|img"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf|ply"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|txt|log|bib|at|diff|lif"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|mpg"
            + r"|java|class|cpp|c|py|cc|xml|r|m|h|apk)$", parsed.path.lower())

    except TypeError:
        print("TypeError for ", parsed)
        raise


def check_domain(parsed):
    domains = set([".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu", "today.uci.edu/department/information_computer_sciences"])
    matched = next(filter(lambda domain: domain in parsed.netloc, domains), None)
    return matched is not None

def process_link(base, href):
    if href is None:
        return None
    href = href.replace(r"index.php/","")
    href = href.replace(r"index.php","")
    if href == "":
        return None
    parsed = urlparse(href)
    # print(parsed.hostname)
    # Ignore links with schemes set other than http and https. eg: mailto:, mri:
    if parsed.scheme and parsed.scheme not in set(["http", "https"]):
        return None
    if href[0] == '#':
        return None
    processed = urljoin(base, href)
    # remove query
    processed = processed.split("?")[0]
    # remove fragment
    return urldefrag(processed)[0] if processed else None

def check_calender(url):
    c = re.compile(r'\d{4}-(0[1-9]|1[0-2])-?(0[1-9]|[12][0-9]|3[01])?/?$')
    res = c.findall(f"{url}")
    if len(res) == 0:
        return False
    print(f"filtered url: {url}")
    return True

def repeated(s):
    REPEATER = re.compile(r"(.+/)\1+")
    match = REPEATER.findall(f"{s}/")
    return len(match) > 0

def block(url):
    b1 = re.compile(r'.*.ics.uci.edu/ugrad/honors/.*')
    b2 = re.compile(r'.*.ics.uci.edu/honors/.*')
    b3 = re.compile(r'www.informatics.uci.edu/files/')

    m1 = b1.findall(url)
    m2 = b2.findall(url)
    m3 = b3.findall(url)
    if len(m1) > 0 or len(m2) > 0 or len(m3) > 0:
        print(f"Block url: {url}")
        return True
    return False

if __name__ == "__main__":
    u = "https://mt-live.ics.uci.edu/events/category/corporate-engagement/day/2021-10"
    u1 = "https://www.ics.uci.edu/grad/honors/index.php/degrees/resources/computing"
    u2 = "https://www.informatics.uci.edu/very-top-footer-menu-items/people/"
    u3 = "https://www.ics.uci.edu/ugrad/honors/index.php/resources/sao/resources/overview/forms.php"
    u4 = "https://www.ics.uci.edu/honors/degrees/resources/advising/resources/Title_IX_Resources.php"
    u5 = "https://www.informatics.uci.edu/files/pdf/"
    print(is_valid(u3))
