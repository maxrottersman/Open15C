#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      maxi7
#
# Created:     14/03/2013
# Copyright:   (c) maxi7 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import os
import sys
import re

ScriptPath = os.path.dirname(os.path.realpath(__file__))
SECIndexesPath = ScriptPath + "\\SECIndexes"
SECEdgar485BPOSPath = ScriptPath + "\\SECEdgar485BPOS"

myList = []

def main():

    #f = open(SECEdgar485BPOSPath+ '\\prospectus_links.htm','w')

    # Look through YYYYMMDD folders
    for dname in os.listdir(SECEdgar485BPOSPath):
        m = re.search('\d{8}', dname)
        if m:
            # If found, loop through files
            for fname in os.listdir(SECEdgar485BPOSPath + "\\" + m.group(0)):
                print dname + '/' + fname
                myx = fname.split('__')
                myList.append(myx[0])
                myurl = '<a href="' + dname + '/' + fname + '">' + myx[0] + '</a></br>'
                f.write(myurl + os.linesep)

    f = open(SECEdgar485BPOSPath+ '\\prospectus_links.htm','w')
    myList.sort
        for txt in myList:
            f.write()

    f.close()

if __name__ == '__main__':
    main()
