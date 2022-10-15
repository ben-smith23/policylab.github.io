from urllib.request import urlopen as Ureq
from bs4 import BeautifulSoup as soup

policyurl = "https://www.ncsl.org/research/elections-and-campaigns/elections-legislation-database.aspx"

enacted2020 = Ureq(policyurl)