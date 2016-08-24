# NightCrawler v1.1
## NightCrawler Web Scraper

NightCrawler is a tool developed on Python 2.7 that we can use against our own web pages for footprinting.

The tool tries to fetch:

- A list [CHILD_LINKS] with all the pages linked from a ROOT node
- A list [EMAIL_ACCOUNTS] with all the email accounts that the parser founds on the visited pages
- An a list [TEL_NUMS] with all the telephone numbers that the parser founds

NightCrawler is Object Oriented (a Class), so you can reuse the code for make a better (more interesting?) program. The code at this point only follows links to web pages, not to binary files, but you can reuse the data that the "crawler" object generates through the Class fields: CHILD_LINKS, BROKEN_LINKS, EMAIL_ACCOUNTS, TEL_NUMS

Any improvement and comments to the code would be apreciate it.

Usage:
- You only need to change on line 18 the base url parameter named ROOT:

ROOT = "http://www.google.com/"

Requires:
- Module Requests: HTTP for Humans (can be installed with the "pip" command) http://docs.python-requests.org/en/master/

