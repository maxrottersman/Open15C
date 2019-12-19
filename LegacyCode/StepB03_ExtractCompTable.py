#!/usr/bin/env python
# coding=utf-8

from lxml import etree
import re
import os
import sys
from bs4 import BeautifulSoup
import pyodbc

ScriptPath = os.path.dirname(os.path.realpath(__file__))
fPath = os.path.normpath('C:\Files2013_EDGARFilings\SECEdgar485BPOS\20130401\0000894189-13-001955\cushing-raf_485b.htm')
fSource = r'C:\Files2013_EDGARFilings\SECEdgar485BPOS\20130401\0000894189-13-001955\cushing-raf_485b.htm'

connstr = 'DRIVER={Microsoft Access Driver (*.mdb)};DBQ='
sDB = 'C:\\Files2013_EDGARFilings\\archdb.mdb'
sDBinsert = 'C:\\Files2013_EDGARFilings\\dmcomp.mdb'



valid_chars = '-_., abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

CheckWordsComp01 =['aggregate compensation','trustees']
CheckWordsComp02 =['aggregate compensation','trustee']
CheckWordsComp03 =['aggregatecompensation','trustees']
CheckWordsComp04 =['aggregatecompensation','trustee']
CheckWordsComp05 =['aggregate compensation','directors']
CheckWordsComp06 =['aggregate', 'compensation','trustees','total']

fromDate ='2013-04-18'
toDate ='2013-04-18'

def checkTableExactMatch(lPhrases,argString):
    findcount = -1
    for i, l in enumerate(lPhrases):
        if argString.find(l) > -1:
            findcount = findcount + 1
            #print "found" + str(i) + " " + str(findcount)

    if findcount == i:
        return True
    else:
        return False

def main():
    lRec = []

  # Get Lookup for fieldname
    try:
        conn = pyodbc.connect(connstr + sDB)

        sql = "SELECT Filings.CIK, (Filings.physpath+'\\'+Filings.filename) as filename, Filings.SECDesc, Filings.EffectiveDate,"
        sql = sql + "Filings.accno "
        sql = sql + " FROM Filings WHERE (Filings.SECDesc='485BPOS') AND "
        #sql = sql + "(Filings.EffectiveDate>='2013-03-29') AND (Filings.EffectiveDate<='2013-03-29');"
        #sql = sql + "(Filings.EffectiveDate>='" + fromDate + "') AND (Filings.EffectiveDate<='" + toDate + "');"
        sql = sql + "(Filings.FilingDate>='" + fromDate + "') AND (Filings.FilingDate<='" + toDate + "')"
        sql = sql + " AND FileSize > 100000"
        #print sql

        cursor = conn.cursor()
        cursor.execute(sql)
        rows  = cursor.fetchall()
        if rows != None:
            for r in rows:
                lRec.append(r)
                #print r[0]
    except:
        print "dbCheck Record failure!"
    finally:
        cursor.close()
        conn.close()

    fcount = 0
    rows = []
    tclean = re.compile(r'<.*?>')


    ltest = ['1']
    for lfile in lRec:
    #for l in ltest: # TEST
        fcount = fcount + 1
        stest = r'C:\Files2013_EDGARFilings\SECEdgar485BPOS\20130325\0001435109-13-000109\d30333.htm'
        soup = BeautifulSoup(open(lfile[1]).read())
        #soup = BeautifulSoup(open(stest).read()) # TEST
        print "Processing file: " + lfile[1] # Turn of for TEST

        #
        # First we find the table number, and will use that to save it
        #
        tcnt = 1
        tables= soup.findAll("table")
        for table in tables:
            tcnt = tcnt + 1

            if table.findParent("table") is None:
                rows.append('-------------TABLE-----------------')
                stbl = ''
                tcheck = ''
                for row in table.findAll('tr'):
                    c = ''
                    t = ''

                    for col in row.findAll('td'):
                        c = col.renderContents()
                        #print c
                        c = c.decode("ascii", "ignore").encode("ascii") # down to ascii only
                        #print c
                        c = c.replace("<br>",' ')
                        c = c.replace("<br\/>",' ')
                        c = c.replace("&nbsp;",' ')
                        c = c.replace('\"','')
                        c = tclean.sub('', c.strip()) # remove HTML
                        c = str(''.join(s for s in c if s in valid_chars)) # remove any tabs, etc.
                        c =' '.join(c.split()) # remove multiple spaces
                        t = t + c + '|' # for export to something else
                        tcheck = tcheck + c.lower() + ' ' # to check if table meet criteria
                    stbl = stbl + t + "\n"

                # We now have a table, so check
                #print tcheck

                # DEBUG, if we don't get table matching below print all
                #print stbl

                if checkTableExactMatch(CheckWordsComp01,tcheck) == True:
                    print stbl
                elif checkTableExactMatch(CheckWordsComp02,tcheck) == True:
                    print stbl
                elif checkTableExactMatch(CheckWordsComp03,tcheck) == True:
                    print stbl
                elif checkTableExactMatch(CheckWordsComp04,tcheck) == True:
                    print stbl
                elif checkTableExactMatch(CheckWordsComp05,tcheck) == True:
                    print stbl
                elif checkTableExactMatch(CheckWordsComp06,tcheck) == True:
                    print stbl


if __name__ == '__main__':
    main()

