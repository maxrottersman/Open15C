#!/usr/bin/env python
# coding=utf-8

import re
import os
import sys
import fileinput
import string

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
#fSource = 'C:\\Files2013_EDGAR\\pyEDGAR\\SECEdgar485BPOS\\20130322\\DFA_INVESTMENT_DIMENSIONS_GROUP_INC__20130322__355437__001.htm'

#fSource = 'C:\\Files2013_EDGAR\\pyEDGAR\\SECEdgar485BPOS\\20130322\\Anchored\\testtidy.htm'

fTargetPath = 'C:\\Files2013_EDGAR\\pyEDGAR\\SECEdgar485BPOS\\20130322\\Anchored\\'
fTargetName = fTargetPath + 'asect1.htm'

valid_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

# (?<=\bfndda=")[^"]*
# works, but includes tag: fddat="([^"]*)


def extractSectionsLineMethod(fSource,fTargetPath):
    pass

    flagWriteSection = False
    flagTargetFileCreated = False
    myFileNum = 1
    FileNameMeta = ''
    searchstr = 'fddat="(.*)"'
    cleanstr = ''

    # Move through Source File
    for line in open(fSource,'r'):

        # Start looking for section
        if line.find('fndmta') > -1 and flagWriteSection == False:
            flagWriteSection = True


            # We're in our first section, Create output file
            if flagTargetFileCreated == False:

            # Get METADATA
                m = re.search(searchstr, line)
                if m:
                    cleanstr = str(m.group(0))
                    cleanstr = cleanstr.replace(' ','_')
                    cleanstr = cleanstr.replace('fddat','')
                    cleanstr = ''.join(c for c in cleanstr if c in valid_chars)
                    if len(cleanstr) > 80:
                        cleanstr = 'agarbage' + str(myFileNum) + '.htm'
                    FileNameMeta = '' + cleanstr + '.htm'
                else:
                    FileNameMeta = '' + str(myFileNum) + '.htm'

                fTargetName = fTargetPath + '\\' + FileNameMeta
                print "Creating: " + fTargetName
                myFileNum = myFileNum + 1
                fT = open(fTargetName,"w")
                fT.write(line)
                flagTargetFileCreated = True

        # If we're in write mode but not at section start, write line
        if flagWriteSection == True:
            fT.write(line)

        # If we're already in section
        if line.find('fndmta') > -1 and flagWriteSection == True and flagTargetFileCreated ==True:
            # Close first target
            fT.close()
            # Get METADATA
            m = re.search(searchstr, line)
            if m:
                cleanstr = str(m.group(0))
                cleanstr = cleanstr.replace(' ','_')
                cleanstr = cleanstr.replace('fddat','')
                cleanstr = ''.join(c for c in cleanstr if c in valid_chars)
                if len(cleanstr) > 80:
                    cleanstr = 'agarbage' + str(myFileNum) + '.htm'
                FileNameMeta = '' + cleanstr + '.htm'
            else:
                FileNameMeta = '' + str(myFileNum) + '.htm'

            fTargetName = fTargetPath + '\\' + FileNameMeta
            print "Creating: " + fTargetName
            myFileNum = myFileNum + 1
            fT = open(fTargetName,"w")
            fT.write(line)
            flagTargetFileCreated = True

        if line == None:
            fT.close()


if __name__ == '__main__':
    # Get path of source file
    dirname, filename = os.path.split(os.path.abspath(fSource))
    # Create a directory for sections named after cik (we already know date, below)
    tsplit = fSource.split('__')
    fTargetPath = dirname + '\\cik' + tsplit[2]
    print fTargetPath
    if not os.path.exists(fTargetPath):
            os.makedirs(fTargetPath)

    #sys.exit()
    # Okay, now parse out sections
    extractSectionsLineMethod(fSource,fTargetPath)

