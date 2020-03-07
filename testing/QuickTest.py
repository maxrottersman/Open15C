import os

s = 'http://www.sec.gov/Archives/edgar/data/1547950/000161577420002432/0001615774-20-002432-index.htm'

head, tail = os.path.split(s)

print(head)
print(tail)

zipfile = tail.replace('-index.htm','-xbrl.zip')

url = head + r'/' + zipfile

print(url)