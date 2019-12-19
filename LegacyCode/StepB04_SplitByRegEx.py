#!/usr/bin/env python
# coding=utf-8

import re
import os
import sys
import fileinput

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

fTarget = 'C:\\Files2013_EDGAR\\pyEDGAR\\SECEdgar485BPOS\\20130322\\Anchored\\atestregexed.htm'




def main():
    pass
    # COULD NOT GET REGEX TO WORK
    # create regular expression pattern
    #chop = re.compile('cutat030.*?cutat031', re.DOTALL)
    # chop text between #chop-begin and #chop-end
    #data_chopped =  "<html><body>" + chop.sub('', data) + "</body></html>"


    # open file
    f = open(fSource, 'r')
    data = f.read()
    f.close()

    # chop text between #chop-begin and #chop-end
    #data_chopped =  "<html><body>" + chop.sub('', data) + "</body></html>"

    # save result
    f = open(fTarget, 'w')
    f.write(data_chopped)
    f.close()

if __name__ == '__main__':
    main()

