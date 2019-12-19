# Created:     22/02/2013
# Copyright:   (c) Max Rottersman 2013
# Licence:     <your licence>
# PARSES EDGAR INDEX FILE AND COPIES 485BPOS ENTERIES WITH NEW FILENAMES TO USE FOR PROSPECTUSES
# INTO listmaster.YYYYDDYY.txt

import csv
import os
import string
import re
import urlparse

sfilename = 'master.20130215.idx'
EDGAR485BPOSListfilename = 'List20130215.txt'
# FOR REFERENCE: pre = 'http://www.sec.gov/Archives/edgar/data/869365/'
ScriptPath = os.path.dirname(os.path.realpath(__file__))
SECIndexesPath = ScriptPath + "\\SECIndexes"
SECEdgar485BPOSPath = ScriptPath + "\\SECEdgar485BPOS"

filenamewithpath = SECIndexesPath + "\\aLatestIndexes.txt"


def getIndexFiles():
     # Read in current index list
    global EDGARindexfiles
    with open(SECIndexesPath + "\\aLatestIndexes.txt") as f:
        EDGARindexfiles = f.readlines()


def get_first_and_last_column(filename, separator):
    with file(filename, 'rb') as file_obj:
        for line in csv.reader(file_obj,
              delimiter=separator,    # Your custom delimiter.
              skipinitialspace=True): # Strips whitespace after delimiter.
            if line: # Make sure there's at least one entry.
                if len(line) > 3:
                        if line[2] == '485BPOS':

                            fn = os.path.basename(line[4]) # Gets trailing filename
                            path = str(line[4]).replace(fn,'')
                            fnnum = re.sub("\D", "", fn) # removes dashes (-) in string, making numeric only
                            nurl = "http://www.sec.gov/Archives/" + path + "" + fnnum + "/" + fn.replace('.txt','-index.htm')

                            # CIK, name, form, date, file
                            yield line[0] , line[1], line[2], line[3], line[4], nurl

#
#  CALL MAIN
#
if __name__ == '__main__':
    getIndexFiles()
    global newfilename
    global oldfilename
    oldfilename = ''
    for fn in EDGARindexfiles:
        fn = fn.rstrip('\n')
        if not os.path.isfile(SECIndexesPath + "\\list" + fn.replace('.idx','.txt')):
            f = open(SECIndexesPath + "\\list" + fn.replace('.idx','.txt'),'w')
            fcnt = 1
            for pair in get_first_and_last_column(SECIndexesPath + "\\" +fn, '|'):
                print pair # or could be pair[1]
                regname = pair[1]
                regname = regname.translate(None, ",!.;&//()")
                regname = regname.replace(' ','_')
                # thare are dups in SEC data, so check for it and don't write
                newfilename = regname + "__" + pair[3] + "__" + pair[0] + "__" + str(fcnt).zfill(3) + ".htm"
                if newfilename <> oldfilename:
                    f.write(regname+"|"+pair[3]+"|"+pair[0] + "|" +pair[5] + "|" + newfilename + "\n")

                oldfilename = newfilename
            fcnt += 1
            f.close()
