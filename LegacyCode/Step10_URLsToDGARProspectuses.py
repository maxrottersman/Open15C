# Created:     26/02/2013
# Copyright:   (c) Max Rottersman 2013
# Licence:     <your licence>
# DOWNLOAD PROSPECTUS IF NOT XBRL

import requests
import re
from BeautifulSoup import BeautifulSoup
import os
import sys
import glob

import httplib

URLnormal = 'http://www.sec.gov/Archives/edgar/data/838802/000111183013000177/0001111830-13-000177-index.htm'
URLXBRL = 'http://www.sec.gov/Archives/edgar/data/917713//000119312513062155/0001193125-13-062155-index.htm'
EDGAR485BPOSList = 'C:\\Files2013_WebDev\\pyEDGAR\SECIndexes\\485bpos_List20130215.txt'

ScriptPath = os.path.dirname(os.path.realpath(__file__))
SECIndexesPath = ScriptPath + "\\SECIndexes"
SECEdgar485BPOSPath = ScriptPath + "\\SECEdgar485BPOS"

pre = 'http://www.sec.gov/'

def main():
    pass

    f = open(SECEdgar485BPOSPath+ '\\prospectus_SEClinks.htm','w')

    gfl = [] # good file list
    # Get listmaster file list from folder
    fl = glob.glob(SECIndexesPath + "\\listmaster*.txt")
    #print "\n".join(fl)
    for j in fl:
        x1 = j.split('.')
        if x1[1] > '20130227':
            #print x1[1] # date YYYYMMDD
            gfl.append(x1[1])

        for fn in gfl:
            dirYYYYMMDD = SECEdgar485BPOSPath + "\\" + fn # YYYYMMDD folder

            file = open(SECIndexesPath + '\\listmaster.'+fn+'.txt', 'r')
            table = [row.strip().split('|') for row in file]
            file.close()

            icnt = 1
            for myrow in table:

                filename = myrow[4]

                r = requests.get(myrow[3])

                soup = BeautifulSoup(r.text)

                table = soup("table", {'class' : 'tableFile' })
                rows = table[0].findAll('tr', limit=2)
                for tr in rows:
                    cols = tr.findAll('td')

                # Company Name
                if len(cols) > 0:
                        print cols[1].text

                    # URL
                s = str(cols[2:3]).strip('[]')
                match = re.search(r'href=[\'"]?([^\'" >]+)', s)
                if match:
                        print pre + match.group(0)[7:]
                        URLnormal = pre + match.group(0)[7:]

                    # print r.headers
                        if 'XBRL INSTANCE' in r.text:
                            print "FOUND XBRL"
                        else:
                            print "NORMAL, Getting HEADER"

                            if URLnormal.endswith != '.txt':
                                conn=httplib.HTTPConnection("www.sec.gov", timeout=5)
                                #conn.sock.settimeout(5.0)
                                getHeadLink = URLnormal.replace('http://www.sec.gov/','')
                                conn.request("HEAD", getHeadLink)
                                res=conn.getresponse()

                                # Only if over 100k
                                clength = res.getheader('content-length')
                                ##or res.getheaders() for all headers
                                conn.close()

                                if clength != None:
                                    if int(clength) > 100000:
                                        f.write(URLnormal + "</br>")
                                #myrow[0]+'|'+
                                #r = requests.get(URLnormal)
                                #with open(dirYYYYMMDD +"\\" + filename, "w") as code:
                                #    code.write(r.content)
    print "DONE"
    f.close()

    #icnt += 1

  #          if icnt > 15:
  #              sys.exit()

if __name__ == '__main__':
    main()

#import httplib
#conn=httplib.HTTPConnection("www.abc.com")
#conn.request("HEAD", "/dir/file1.mp3")
#res=conn.getresponse()
#fileSize=res.getheader('content-length')
##or res.getheaders() for all headers
#conn.close()

