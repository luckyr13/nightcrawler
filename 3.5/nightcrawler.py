"""
    +===================
    + NightCrawler
    +===================

    Last Update: 07OCT2016
    Remarks: Migrated from Python 2.7

    @author: snoopymx
    @date: 27AUG2016
"""

# http://docs.python-requests.org/en/master/
import requests
# https://docs.python.org/3/library/html.parser.html
from html.parser import HTMLParser
# https://docs.python.org/3/library/urllib.parse.html
from urllib.parse import urlparse
from urllib.parse import urlsplit
import time

# Change this value for the web page domain that you want to crawl
# Don't forget the "http://" part
ROOT = 'http://www.example.com/'
# Time out time for http connections
TIMEOUT = (5, 10)

VERSION = 1.5

class Parse(HTMLParser):
    """
        Parse HTML text
    """
    
    def __init__(self):
        HTMLParser.__init__(self)
        self.DATA = []
        self.HREF = []
        self.CTAG = ''
        
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.CTAG = tag
            for at in attrs:
                if at[0] == 'href':
                    my_href = at[1].encode('ascii','ignore').strip()
                    if my_href:
                        self.HREF.append(my_href)
        else:
            self.CTAG = ''
            
    def handle_endtag(self, tag):
        #print "Encountered an end tag :", tag
        pass
        
    def handle_data(self, data):
        if self.CTAG == 'a':
            self.DATA.append(data)

    def get_DATA(self):
        return self.DATA[:]

    def get_HREF(self):
        return self.HREF[:]

    def clear(self):
        self.DATA = []
        self.HREF = []
        self.CTAG = ''
        
class Crawler(object):
    """
        Main crawler object
    """

    def __init__(self, root):
        self.base_url = self.parse_base_url(root)
        # This is a list because we want
        # all our elements in an ordered sequence
        # so we can traverse the list by an index
        self.CHILD_LINKS = [self.base_url]
        # This variables can be "sets" because
        # we dont want duplicate elements
        self.BROKEN_LINKS = set()
        self.EMAIL_ACCOUNTS = set()
        self.TEL_NUMS = set()
        
    def parse_base_url(self, url):
        """
            Create a valid base url

            @param url: Url to clean
            @type url: string
        """
        r1 = urlsplit(url)
        r1 = '{0}://{1}/'.format(r1.scheme, r1.netloc)
        return r1

    def clean_url(self, url):
        """
            Clear url parameters and querys

            @param url: Url to clean
            @type url: string
        """
        r1 = urlsplit(url)
        r1 = '{0}://{1}{2}'.format(r1.scheme, r1.netloc, r1.path)
        return r1

  
    def get_contype(self, headerct = ''):
        """
            Return MIME type from a valid 'content-type' HTTP header

            @param headerct: content-type
            @type headerct: string
        """
        
        content_type = headerct.split(';')
        content_type = content_type[0].strip()
        return content_type

    def map_files(self, url):
        """
            This function first verifies if the url has the valid MIME type
            and then calls fetch_links_from_url() to parse the HTML data

            @param url: Base url from where to start crawling
            @type url: string
        """
        
        rq = None
        mfiles = []
        r1 = urlsplit(url)
        if not r1.scheme and not r1.netloc:
            url = self.base_url + url
        
        print('\n+ Crawling: {0}'.format(url))
        
        try:
            rq = requests.get(url, timeout=TIMEOUT)
        except:
            raise Exception('Connection error (1):(')

        # Dont proceed if this page dont exists
        if rq.status_code != 200:
            rq.raise_for_status()

        # Check for content-type == text/html
        contype = self.get_contype(rq.headers['content-type'])
        print('    - Content-Type:', contype)

        if contype != 'text/html':
            print('\tERROR: Is not a text/html\n')
            return mfiles

        # Parse page and search links
        self.fetch_links_from_url(rq.text, url)

    def start(self):
        """
            Trigger function that starts to fetch links from self.base_url
        """
        
        time_start = time.time()
        print('NightCrawler v{0}'.format(VERSION,))
        print('Please stand by ...\n')
        print('BASE URL: {0}'.format(self.base_url))

        # This variable is my index for the list of child links
        # we are going to analize child by child until there
        # are no more new childs
        i = 0
        
        while i < len(self.CHILD_LINKS):
            self.map_files(self.CHILD_LINKS[i])
            i += 1

        print()
        print('-'*32)
        print('Results:')
        print('{0:d} email accounts, {1:d} tel. numbers and {2:d} links' \
              '({3:6f} seconds) ... \n'.format(len(self.EMAIL_ACCOUNTS), len(self.TEL_NUMS),
                                          len(self.CHILD_LINKS), time.time() - time_start))
        print('Links:')
        print(self.CHILD_LINKS)
        print('Emails:')
        print(self.EMAIL_ACCOUNTS)
        print('T:')
        print(self.TEL_NUMS)

        
   
   
    def fetch_links_from_url(self, base_text = '', url = ''):
        """
        Parse a webpage and return a list of valid links (urls)

        @param base_text: HTML Content
        @type base_text: string
        @param url: Url 
        """

        prep_url = self.clean_url(url)
        
        urls = []
        data = []
        print('+ Fetch children from Base url:', prep_url)

        # Parse the HTML code
        parser = Parse()
        parser.feed(base_text)

        # Its possible to use the other data parsed
        # e.g. Search in the data for emails, phones, etc
        #data = parser.get_DATA()
        
        # Get links that the parser fetched from the "a" tags
        urls = parser.get_HREF()

        #print "URLS FOUND: %s" % (urls,)
        #print "PREP URL: %s" % (prep_url,)

        # Iterate over the urls and get all the possible childs
        for u in urls:
            tmp_url_src = urlsplit(u)
            
            tmp_path = tmp_url_src.path.decode('utf-8').strip()
            tmp_scheme = tmp_url_src.scheme.decode('utf-8')
            tmp_netloc = tmp_url_src.netloc.decode('utf-8')
            # Skip email addresses
            if tmp_scheme == 'mailto':
                self.EMAIL_ACCOUNTS.add(tmp_path)
                continue
            if tmp_scheme == 'tel':
                self.TEL_NUMS.add(tmp_path)
                continue

            # Skip urls not in my domain
            if tmp_netloc not in self.base_url:
                continue


            # Black List
            # Skip binary files (we only want web pages for now)
            IN_BLACK_LIST = False
            for ext_path in [".jpg", ".jpeg", ".pdf", ".doc", ".xl",
                             ".png", ".gif", ".mp"]:
                if ext_path in tmp_path:
                    IN_BLACK_LIST = True

            if IN_BLACK_LIST:
                continue
            
            # Skip empty links and relative urls
            if not tmp_path or tmp_path == '/':
                continue

            # Remove trailing /
            if tmp_path[0] == '/':
                tmp_path = tmp_path[1:]
                
            tmp_url = self.base_url + tmp_path

            # Continue to the next if already on childs list
            # Skip urls in broken links
            if tmp_path in self.CHILD_LINKS or tmp_path in self.BROKEN_LINKS:
                continue
            
            try:
                rq = requests.get(tmp_url, timeout=TIMEOUT)
            except:
                print('Connection error (3) > {0}'.format(tmp_url))
                self.BROKEN_LINKS.add(tmp_path)
                continue

            # Dont proceed if the page doesn't exists
            if rq.status_code != 200:
                print('ER03: Can not connect ({0})\n'.format(tmp_url))
                self.BROKEN_LINKS.add(tmp_path)
                continue

            # Add to my list if is a new child
            print('    - Child found ({0})'.format(tmp_path))
            self.CHILD_LINKS.append(tmp_path)

        # END OF FUNC

  


# You can start NightCrawler from here :)
if __name__ == "__main__":
    try:
        crawler = Crawler(ROOT)
        crawler.start()
    except Exception as err:
        print('Ups: ', err)
