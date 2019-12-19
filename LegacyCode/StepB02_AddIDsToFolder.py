#!/usr/bin/env python
# coding=utf-8

from lxml import etree
import re
import os
import sys
import bs4 as beautifulsoup
import fileinput
from tempfile import mkstemp
from shutil import move
from os import remove, close

ScriptPath = os.path.dirname(os.path.realpath(__file__))
SECIndexesPath = ScriptPath + "\\SECIndexes"
SECEdgar485BPOSPath = ScriptPath + "\\SECEdgar485BPOS"

myfile = "C:\Files2013_WebDev\pyEDGAR\HTMLpremailer.htm"
myfile2 = "C:\Files2013_WebDev\pyEDGAR\HTMLpremailer_id.htm"

parser = etree.HTMLParser(remove_blank_text=True)

lProcYYYYMMDDFolders = []
lProcFilesSource = []
lProcFilesTarget = []
lProcFilesTargetPath = []

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


def checkForAnchorNames():

    for getfile, getfiletarget in zip(lProcFilesSource,lProcFilesTarget):
        cntatags = 0
        if str(getfile).endswith('.htm'):
            with open(getfile) as fp:
                tree = etree.parse(fp, parser)

                for e in tree.xpath("//*"):
                    if (e.tag == 'a'):
                        for myid in e.attrib:
                            if myid == 'name':
                                cntatags = cntatags + 1
        print "Found " + str(cntatags) + " in " + getfile


def writeIDs():

    for getfile, getfiletarget in zip(lProcFilesSource,lProcFilesTarget):
   # for getfile in lProcFilesSource:
        cnt = 1
        icutat = 1

        if str(getfile).endswith('.htm'):

            with open(getfile) as fp:
                tree = etree.parse(fp, parser)

                for e in tree.xpath("//*"):
                    if (e.tag == 'p' or e.tag == 'div'
                    or e.tag == 'table' or
                    e.tag == 'h1' or e.tag == 'h2' or e.tag == 'h3'
                    or e.tag =='td'
                    or e.tag == 'span'):
                        e.attrib['id'] = str(cnt).zfill(6)
                        cnt += 1

                    if e.tag == "a" and e.get("name") != '' and e.get("href") == None:
                            # WORKS BUT CREATEING NEW ELEMENT BELOW
                            #e.attrib['scut'] = "cutat" + str(icutat).zfill(3)
                            #if e.tail != None:
                            #    e.attrib['scutname'] = e.tail
                            #else:
                            #    e.attrib['scutname'] = e.get("name")


                            a_desc = etree.Element("a", name="fndmta")
                            if e.tail != None:
                                a_desc.attrib['fddat'] = e.tail
                            else:
                                a_desc.attrib['fddat'] = e.get("name")
                            e.append(a_desc)
                            icutat = icutat + 1


            with open(getfiletarget,"w") as fp:
                fp.write(etree.tostring(tree, pretty_print=True))

def writeAnchors():
    for myfile in lProcFilesTarget:
        if os.path.exists(myfile):
            print myfile
            for line in fileinput.input(myfile, inplace=1):
                if 'total compensation' in line.lower():
                    line = line.lower()
                    line = line.replace('total compensation','<a name="comp">total compensation</a>')
                if 'id="id000001"' in line.lower():
                    line = line.replace('id="id000001">','id="id000001">'+'<a href="#comp">Compensation Section</a>')
                sys.stdout.write(line)

def main():
    GetDirInfo()
    checkForAnchorNames()
    #writeIDs()
    #writeAnchors()

if __name__ == '__main__':
    main()

