#-------------------------------------------------------------------------------
# Created:     22/02/2013
# Copyright:   (c) Max Rottersman 2013
# Licence:     <your licence>
# OPENS aLatestIndexes.txt and download index file IF NOT EXISTS LOCALLY
#-------------------------------------------------------------------------------

import requests
import urllib.request
import time
import csv
import os
from bs4 import BeautifulSoup
import re
import wget

ScriptPath = os.path.dirname(os.path.realpath(__file__))
SECIndexesPath = ScriptPath + "\\SECIndexes\\"
print(SECIndexesPath)
#filename = 'master.20130306.idx'

def main():
    pass

    # Read in current index list
    #with open(SECIndexesPath + "\\aLatestIndexes.txt") as f:
    #    EDGARindexfiles = f.readlines()

    url = 'https://www.sec.gov/Archives/edgar/daily-index/2019/QTR1/'
    response = requests.get(url)
    print(response)
    #print(response.text)
    
    soup = BeautifulSoup(response.content, "html.parser")
    #print(soup)    
    #Call main()
    for td in soup.findAll("td"):
        for a in td.findAll("a"):
            if a.find(text=re.compile("master")):
                print(a.text)
                urlToGet = url + a.text
                #url = 'http://i3.ytimg.com/vi/J---aiyznGQ/mqdefault.jpg'
                try:
                    os.remove(SECIndexesPath + a.text)
                except OSError:
                    pass
                
                wget.download(urlToGet, SECIndexesPath + a.text)
                #return #debug test one
    
if __name__ == '__main__':
    main()


