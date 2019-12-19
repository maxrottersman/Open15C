#!/usr/bin/env python
# coding=utf-8

from lxml import etree
from lxml.builder import E
#from tidylib import tidy_document # was not working
import lxml.html
from bs4 import BeautifulSoup
import re
import os
import sys
import fileinput
from tempfile import mkstemp
from shutil import move
from os import remove, close

ScriptPath = os.path.dirname(os.path.realpath(__file__))
SECIndexesPath = ScriptPath + "\\SECIndexes"
SECEdgar485BPOSPath = ScriptPath + "\\SECEdgar485BPOS"

# LARGE
fSource = "C:\\Files2013_EDGAR\\pyEDGAR\\SECEdgar485BPOS\\20130322\\Anchored\\DFA_INVESTMENT_DIMENSIONS_GROUP_INC__20130322__355437__001_id.htm"
# SMALL
fSource = 'C:\\Files2013_EDGAR\\pyEDGAR\\SECEdgar485BPOS\\20130322\\Anchored\\SATURNA_INVESTMENT_TRUST__20130322__811860__001_id.htm'
fSource = 'C:\\Files2013_EDGAR\\pyEDGAR\\SECEdgar485BPOS\\20130322\\Anchored\\DFA_INVESTMENT_DIMENSIONS_GROUP_INC__20130322__355437__001_id.htm'
#fSource = 'C:\\Files2013_EDGAR\\pyEDGAR\\SECEdgar485BPOS\\20130322\\Anchored\\NORTHERN_FUNDS__20130322__916620__001_id.htm'
#fSource = 'C:\\Files2013_EDGAR\\pyEDGAR\\SECEdgar485BPOS\\20130322\\NORTHERN_FUNDS__20130322__916620__001.htm'
fSource = 'C:\\Files2013_EDGAR\\pyEDGAR\\SECEdgar485BPOS\\20130322\\DFA_INVESTMENT_DIMENSIONS_GROUP_INC__20130322__355437__001.htm'
#fSource = r'C:\Files2013_EDGARFilings\SECEdgar485BPOS\20130418\0001193125-13-160823\d521284d485bpos.htm'

#fSource = 'C:\\Files2013_EDGAR\\pyEDGAR\\SECEdgar485BPOS\\20130322\\Anchored\\testtidy.htm'

fTarget = 'C:\\Files2013_EDGAR\\pyEDGAR\\SECEdgar485BPOS\\20130322\\Anchored\\atestsection.htm'

parser = etree.HTMLParser(remove_blank_text=False)


def findAnchorNames():
    t = ''
    tsect = ''
    flagInSection = False

    lSectionFinds = ['management of the funds','trustees','directors']

    html = page = (E.html(E.head(E.title("section")), E.body(E.p(""))))
    #print etree.tostring(html)
    new_root = lxml.html.fromstring(etree.tostring(html))
    insertat = new_root.find("body")

    with open(fSource) as fp:

        # First Tidy HTML
        #document, errors = tidy_document(fp,
        #    options={'numeric-entities':1})
        #fp = document

        result = ""
        tree = etree.parse(fp, parser)
        for e in tree.xpath("//*/text/*"): # find all elements directly below text

            #print etree.tostring(e)
            t = lxml.html.tostring(e)
            t = t.lower().strip()

            # catch closing header
           # turn off it we were in section
            if flagInSection == True and t.find("></a>") > -1:
                flagInSection = False

            # catch opening header
            for ft in lSectionFinds:
                if t.find("</a>" + ft) > -1:
                    #print e.tail

                    flagInSection = True

            # add all enclosed elements to our result string
            if flagInSection == True:
                pass
                #print etree.tostring(e)
                #curr = insertat.getparent()
                #insertat.append(e)
                #e.getparent().remove(e);
                result += lxml.html.tostring(e)
                #tsect = tsect + lxml.etree.tostring(e,with_tail=True)

                #if e.text != None:
                #    tsect = tsect + e.tail

    #print etree.tostring(new_root)
    #print tsect
    with open(fTarget,"w") as fp:
        fp.write("<html><body>" + result + "</body></html>")
    # Write result to file
    #with open(fTarget,"w") as fp:
        #fp.write(etree.tostring(new_root))




def main():
    findAnchorNames()
 #   GetDirInfo()
 #   writeIDs()
#    mytest = False
#    mytest= True


 #   rES, rEE = findSectionExact()
 #   print "Returned: " + rES + " + " + rEE

 #   if mytest == True:
 #       if rES != '' and rEE != '':
 #           fTarget = fSource.replace('_id.htm','_id_section.htm')
 #           writeSectionAsFile(fSource, fTarget, rES,rEE)

if __name__ == '__main__':
    main()

