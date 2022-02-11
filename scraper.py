import re
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup


def scraper(url, resp, soup):
    links = extract_next_links(url, resp, soup)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp, soup):
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
    urls_raw = []

    fd = open("url_raw.txt", "a")
    for link in soup.find_all('a'):
        urls_raw.append(link.get('href'))

    for l in urls_raw:
        if l:
            fd.write(l + "\n")

    fd.close()

    for url_raw in urls_raw:
        assembled = process_link(url, url_raw)
        if assembled:
            urls.append(assembled)

    print("urls.length = ", len(urls))
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

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf|ply"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|txt|log"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz"
            + r"|java|class|cpp|c|py|cc|xml|r|m|h)$", parsed.path.lower())

    except TypeError:
        print("TypeError for ", parsed)
        raise


def check_domain(parsed):
    domains = set([".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu",
                   "today.uci.edu/department/information_computer_sciences"])
    matched = next(filter(lambda domain: domain in parsed.netloc, domains), None)
    return matched is not None

def process_link(pageUrl, link):
    processed = ""
    if link is None:
        return None
    parsed = urlparse(link)
    # Ignore links with schemes set other than http and https. eg: mailto:, mri:
    if parsed.scheme:
        if parsed.scheme not in set(["http", "https"]):
            return None
        processed = link
    else:
        # anaylze origin pageUrl
        origin = urlparse(pageUrl.rstrip('/'))
        # check is php or html
        path = origin.path
        if re.match(r".*\.(php|html|htm)$", path):
            path = '/'.join(path.split('/')[:-1])
        processed = f"{origin.scheme}:"
        try:
            if link[:2] == '//':
                processed += link
            elif link[:3] == '../':
                back_count = link.count('../')
                back_path = '/'.join(path.split('/')[:-back_count])
                processed += f"//{origin.netloc}{back_path}/{link[back_count * 3:]}"
            elif link[:2] == './':
                processed += f"//{origin.netloc}{path}/{link[2:]}"
            elif link[0] == '/':
                processed += f"//{origin.netloc}/{link[1:]}"
            elif link[0] == '#':
                return None
            else:
                processed += f"//{origin.netloc}{path}/{link}"
        except Exception:
            return None

    processed = strip_query(processed)
    return urldefrag(processed)[0] if processed else None

def strip_query(url):
    if '?' in url:
        url = url.split("?")[0]
    return url


def check_calender(url):
    res = re.match(r'\/event\/\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$', url)
    if res is None:
        return False
    print(f"filtered url: {url}")
    return True


def repeated(s):
    REPEATER = re.compile(r"(.+/)\1+")
    match = REPEATER.findall(f"{s}/")
    return len(match) > 0

a = 'https://www.ics.uci.edu/grad/policies/GradPolicies_Defense.php'
b = 'forms/index.php'
print(process_link(a, b))