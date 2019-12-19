#!/usr/bin/env python
# coding=utf-8

from lxml import etree
import re
import os
import sys
import fileinput
from tempfile import mkstemp
from shutil import move
from os import remove, close
from lxml.html import builder as E

ScriptPath = os.path.dirname(os.path.realpath(__file__))
SECIndexesPath = ScriptPath + "\\SECIndexes"
SECEdgar485BPOSPath = ScriptPath + "\\SECEdgar485BPOS"

# LARGE
fSource = "C:\\Files2013_EDGAR\\pyEDGAR\\SECEdgar485BPOS\\20130322\\Anchored\\DFA_INVESTMENT_DIMENSIONS_GROUP_INC__20130322__355437__001_id.htm"
# SMALL
fSource = 'C:\\Files2013_EDGAR\\pyEDGAR\\SECEdgar485BPOS\\20130322\\Anchored\\SATURNA_INVESTMENT_TRUST__20130322__811860__001_id.htm'
fSource = 'C:\\Files2013_EDGAR\\pyEDGAR\\SECEdgar485BPOS\\20130322\\Anchored\\DFA_INVESTMENT_DIMENSIONS_GROUP_INC__20130322__355437__001_id.htm'

fTarget = 'C:\\Files2013_EDGAR\\pyEDGAR\\SECEdgar485BPOS\\20130322\\Anchored\\atestsection.htm'

parser = etree.HTMLParser()

lProcYYYYMMDDFolders = []
lProcFilesSource = []
lProcFilesTarget = []
lProcFilesTargetPath = []

lIgnoreBegin = []
lBeginFind = ['management of the funds','management of the trust']
lMiddleFind = ['aggregate compensation','total compensation']
lEndFind = ['control persons','principal holders of securities']
lMarkers = []
CurrPN = ''

e1 =''
e2 =''
e3 =''
eid =''


def findSectionExact():

    lExactStarts = ['management of the funds','management of the trust','directors and officers']
    lExactEnds = ['control persons','services to the fund']
    ExactStart =''
    ExactEnd =''

    with open(fSource) as fp:
        tree = etree.parse(fp, parser)
        for e in tree.xpath("//*"):

            for myid in e.attrib:
                if myid == 'pn':
                    currPN = e.attrib['pn']

            # look at h tags
            if e.tag == 'h1' or e.tag == 'h2' or e.tag == 'h3':
                etxt = etree.tostring(e).strip().lower()

                for ft in lExactStarts:
                    if etxt.find(ft) > -1:
                        print "Found: " + ft + " at " + currPN
                        ExactStart = currPN

                for ft in lExactEnds:
                    if etxt.find(ft) > -1:
                        if ExactEnd == '':
                            print "Found: " + ft + " at " + currPN
                            ExactEnd = currPN

            # look at anchors that are names
            if e.tag == 'a':
                etxt = etree.tostring(e).strip().lower()

                for ft in lExactStarts:
                    if etxt.find(ft) > -1:
                        if ExactStart == '':
                            print "Found: " + ft + " at " + currPN
                            ExactStart = currPN

                for ft in lExactEnds:
                    if etxt.find(ft) > -1:
                        if ExactEnd == '':
                            print "Found: " + ft + " at " + currPN
                            ExactEnd = currPN


    return ExactStart, ExactEnd


def findSectionGuess():
    pass
    with open(fSource) as fp:
        tree = etree.parse(fp, parser)

        for e in tree.xpath("//*"):
            if e.text != None:
                s = e.text
                s = s.lower()
                # FIND BEGINING
                for lb in lBeginFind:
                    if s.find(lb) > -1: #'Management of the Funds':
                        e1 = e.text
                        # parent of text, because text might be in font
                        e2 = etree.tostring(e.getparent())
                        # parent of parent , like tr to td
                        ep = e.getparent()
                        epp= ep.getparent()
                        e3 = etree.tostring(epp)

                        if 'id' in e.attrib:
                            print 'B_ID=' + e.attrib['id']
                            lMarkers.append('B_ID=' + e.attrib['id'])
                        if 'id' in ep.attrib:
                            print 'B_ID=' + ep.attrib['id']
                            lMarkers.append('B_ID=' + ep.attrib['id'])
                        if 'id' in epp.attrib:
                            print 'B_ID=' + epp.attrib['id']
                            lMarkers.append('B_ID=' + epp.attrib['id'])

                # FIND MIDDLE
                for lm in lMiddleFind:
                    if s.find(lm) > -1: #'Management of the Funds':
                        e1 = e.text
                        # parent of text, because text might be in font
                        e2 = etree.tostring(e.getparent())
                        # parent of parent , like tr to td
                        ep = e.getparent()
                        epp = ep.getparent()
                        e3 = etree.tostring(epp)

                        if 'id' in e.attrib:
                            print 'C_ID=' + e.attrib['id']
                            lMarkers.append('C_ID=' + e.attrib['id'])
                        if 'id' in ep.attrib:
                            print 'C_ID=' + ep.attrib['id']
                            lMarkers.append('C_ID=' + ep.attrib['id'])
                        if 'id' in epp.attrib:
                            print 'C_ID=' + epp.attrib['id']
                            lMarkers.append('C_ID=' + epp.attrib['id'])

                # FIND END
                for le in lEndFind:
                    if s.find(le) > -1: #'Management of the Funds':
                        e1 = e.text
                        # parent of text, because text might be in font
                        e2 = etree.tostring(e.getparent())
                        # parent of parent , like tr to td
                        ep = e.getparent()
                        epp = ep.getparent()
                        e3 = etree.tostring(epp)

                        if 'id' in e.attrib:
                            print 'E_ID=' + e.attrib['id']
                            lMarkers.append('E_ID=' + e.attrib['id'])
                        if 'id' in ep.attrib:
                            print 'E_ID=' + ep.attrib['id']
                            lMarkers.append('E_ID=' + ep.attrib['id'])
                        if 'id' in epp.attrib:
                            print 'E_ID=' + epp.attrib['id']
                            lMarkers.append('E_ID=' + epp.attrib['id'])


    print "Done"
    lMarkersSort = sorted(lMarkers)
    for s in lMarkersSort:
        print s


def writeSectionAsFile(argfSource, argfTarget, argPNbegin, argPNend):

#    for getfile, getfiletarget in zip(lProcFilesSource,lProcFilesTarget):
   # for getfile in lProcFilesSource:
        fSource = argfSource
        fTarget = argfTarget

        cnt = 1
        flagRemove = False
        flagRemoveNext = False

        PNbegin = argPNbegin #'002018'
        PNend = argPNend #'002190'

        removeTags = []
        #includeTags = []
        currPN = ''

        if str(fSource).endswith('.htm'):

            with open(fSource) as fp:
                tree = etree.parse(fp, parser)

                cnt = 1

                for e in tree.xpath("//*"):
                # When IDs are out of range set for delete/remove
                    for myid in e.attrib:
                        if myid == 'pn':
                            currPN = e.attrib['pn']
                            # From first element to start of Section we want
                            if (e.attrib['pn'] <= PNbegin): # and (e.attrib['pn'] >= 'id000002'):
                                flagRemove = True
                            # REMOVE everthing past seciton we want
                            if e.attrib['pn'] >= PNend:
                                flagRemove = True
                            # KEEP, turn off delete if in section we want
                            if e.attrib['pn'] <= PNend and e.attrib['pn'] >= PNbegin:
                                flagRemove = False
                                #removeTags.append(e)

                    # If we're in a part we want removed add to remove list
                    if flagRemove == True:
                        removeTags.append(e)
                    #if flagRemove == False:
                    #    includeTags.append(e)

                    if flagRemoveNext == True:
                        flagRemove = True
                        flagRemoveNext = False
                    if e.tag == 'title':
                        print "found " + e.tag
                        flagRemoveNext = True

                    if e.tag == 'h3':
                        etxt = etree.tostring(e).strip().lower()
                        if etxt.find('management of the funds') > -1:
                            print "management of the funds"
                            print "current PN is: " + currPN


            # Now go through list and remove tags
            for rt in removeTags:
                rt.getparent().remove(rt)

            # Write result to file
            with open(fTarget,"w") as fp:
                fp.write(etree.tostring(tree))


def GetDirInfo():
    for name in os.listdir(SECEdgar485BPOSPath):
        m = re.search('\d{8}', name)
        if m:
            # Directory, like 20130125
            lProcYYYYMMDDFolders.append(m.group(0)) # "dir"
            # Path to Anchored, target path
            lProcFilesTargetPath.append(SECEdgar485BPOSPath + "\\" + m.group(0) + "\\Anchored")
            # Now get the files in each YYYYMMDD directory and save them,
            # And what will be our target write file with IDs inserted
            for myfile in os.listdir(SECEdgar485BPOSPath + "\\"+ m.group(0)):
                lProcFilesSource.append(SECEdgar485BPOSPath + "\\"+ m.group(0) + "\\" + myfile)
                lProcFilesTarget.append(SECEdgar485BPOSPath + "\\" + m.group(0) + "\\Anchored\\" + myfile.replace('.htm','_id.htm'))

    for newpath in lProcFilesTargetPath:
        if not os.path.exists(newpath):
            os.makedirs(newpath)

def main():
 #   GetDirInfo()
 #   writeIDs()
    mytest = False
    mytest= True


    rES, rEE = findSectionExact()
    print "Returned: " + rES + " + " + rEE

    if mytest == True:
        if rES != '' and rEE != '':
            fTarget = fSource.replace('_id.htm','_id_section.htm')
            writeSectionAsFile(fSource, fTarget, rES,rEE)

if __name__ == '__main__':
    main()

