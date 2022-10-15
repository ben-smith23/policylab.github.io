from urllib.request import urlopen as Ureq
from bs4 import BeautifulSoup as soup

policyurl = "file:///C:/Users/Ben/OneDrive/Desktop/Policy%20Lab/Policy%20Lab%20Code/policylab/Policy%20Lab/index.html"

enacted2020 = Ureq(policyurl)
ppage = enacted2020.read()
enacted2020.close()
page_soup = soup(ppage, "html.parser")
bills = page_soup.findAll("div",{"class":"fullbill"})

bill = bills[0]

#filename ="bills2020.xls"
#f = open(filename, "w")

headers = "Summary"
#f.write(headers)

"""
for bill in bills:
    billsum = bill.findAll("b",{"class":"summary"})
    oldsum = billsum[0].text
    summarytext = oldsum.strip()
    
    print(summarytext)

    #f.write(summarytext)
#f.close()
"""