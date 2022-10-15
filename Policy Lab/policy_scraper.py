from urllib.request import urlopen as Ureq
from bs4 import BeautifulSoup as soup

policyurl = "https://github.com/ben-smith23/policylab/raw/main/Policy%20Lab/enacted2020.html"

enacted2020 = Ureq(policyurl)