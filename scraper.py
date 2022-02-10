import re
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup

def scraper(url, resp, soup):
    print("enter scraper")
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

    # print("url = ", url)
    # print("resp.url = ", resp.url)
    # print("resp.status = ", resp.status)
    urls = []
    urls_raw = []
    # if resp.status == 200:
    #     # print("resp.raw_response.url = ", resp.raw_response.url)
    #     # print("resp.raw_response.content = ", resp.raw_response.content)
    #     soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
        
    for link in soup.find_all('a'):
        # print(link.get('href'))
        urls_raw.append(link.get('href'))
    # else:
    #     print("resp.error = ", resp.error)
    
    # soup = BeautifulSoup(resp.text, 'html.parser')
    for url_raw in urls_raw:
        assembled = process_link(url, url_raw)
        if assembled:
            urls.append(assembled)
    f = open("url_assembled.txt", "a")
    for line in urls:
        f.write(line + "\n")
    f.close()
    print("urls.length = ", len(urls))
    return urls

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    domains = [".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu", "today.uci.edu/department/information_computer_sciences"]
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        b = False
        for domain in domains:
            if(parsed.netloc.find(domain) != -1):
                b = True
                break
        if not b:
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

def process_link(pageUrl, link):
    if 'http' in link:
        return link
    origin = urlparse(pageUrl.rstrip('/'))
    processed = f"{origin.scheme}:"
    try:
        if link[:2] == '//':
            processed += link
        elif link[:2] == '..':
            back_path = '/'.join(origin.path.split('/')[:-1])
            processed += f"//{origin.netloc}{back_path}{link[2:]}" 
        elif link[:2] == './':
            processed += f"//{origin.netloc}{origin.path}{link[1:]}"
        elif link[0] == '/':
            processed += f"//{origin.netloc}{link}"
        elif link[0] == '#':
            return None
        else:
            processed += f"//{origin.netloc}{origin.path}/{link}"
    except Exception:
        return None
    return processed