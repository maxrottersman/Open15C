#-------------------------------------------------------------------------------
# Created:     22/02/2013 updated 12/2019
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
from pathlib import Path, PureWindowsPath

url = 'https://www.sec.gov/Archives/edgar/daily-index/2019/QTR1/'

ScriptPath = Path.cwd() # new way of getting script folder in both win/linux
ScriptPathParent = Path.cwd().resolve().parent # Parent
DataPath = ScriptPathParent / 'Open15C_Data'
SECIndexesPath = DataPath / 'SEC_IndexFiles' # / adds right in all os
print(SECIndexesPath)
#exit()
#DataPathSQLiteDB = DataPath / 'SECedgar.sqlite'

#exit()
#filename = 'master.20130306.idx'

def main():
    pass

    # Read in current index list
    #with open(SECIndexesPath + "\\aLatestIndexes.txt") as f:
    #    EDGARindexfiles = f.readlines()

    response = requests.get(url)
    print(response)
    #print(response.text)
    
    soup = BeautifulSoup(response.content, "html.parser")
    #print(soup)    
    for td in soup.findAll("td"):
        for a in td.findAll("a"):
            if a.find(text=re.compile("master")):
                SECIndexFileNameOnly = str(a.text)
                SECIndexFile = SECIndexesPath / SECIndexFileNameOnly # full path and name
                
                urlToGet = url + str(SECIndexFileNameOnly)
                #print(urlToGet)
                #print(SECIndexFile)

                r = requests.get(urlToGet)
                               
                with open(SECIndexFile, 'wb') as f:
                    f.write(r.content)

                #return #debug test one
    
if __name__ == '__main__':
    main()


