#-------------------------------------------------------------------------------
from bs4 import BeautifulSoup
import os
import sys
import re
import pyodbc
import requests

ScriptPath = os.path.dirname(os.path.realpath(__file__))
SECIndexesPath = ScriptPath + "\\SECIndexes"

# --------- CONFIG --------------
fromDate = '20130423' # will be greater-than or equl
endDate = '20131231'
DateAdd = "2013-05-19"

connstr = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};Provider=Microsoft.ACE.OLEDB.12.0;DBQ='
sDB = r'C:\ff_Factory2007\NSAR\FRMatch2012.accdb'
# -------------------------------

global shttp
shttp = r'http://www.sec.gov/cgi-bin/browse-edgar?scd=series&action=getcompany&CIK='

sURLFile = ''#'c:\\Files2013_EDGAR\\pyEDGAR\\testdocs\\nsarindex3.htm'
lSECFilingsIndexURLs = []
lCIKs = []
sql=''


def dbLoad_lSECFilingsIndexURLs():
    conn = pyodbc.connect(connstr + sDB)
    cursor = conn.cursor()
    try:
        sql = 'Select str([CIK]) as CIKstr FROM [refCIKs]'
        print sql
        cursor.execute(sql)
        rows  = cursor.fetchall()
        if rows != None:
            for r in rows:
                lSECFilingsIndexURLs.append(r[0].strip())

    except:
        print "db error!"
        cursor.close()
        conn.close()

    finally:
        pass
        #conn.close()

def InsertNewFundClasses():
    s =''
    t= ''
    rtext = ''

    global CIK
    global SeriesName
    global SeriesNum
    global ClassName
    global ClassNum
    global Symbol

    CIK = ''
    SeriesName = ''
    SeriesNum =''
    ClassName = ''
    ClassNum =''
    Symbol = ''

    flagInClass = False
    cnt = 0

    for indexpath in lSECFilingsIndexURLs:
        cnt = cnt+1
        print cnt

        #if cnt > 10:
        #    break

        #soup = BeautifulSoup(open(sURLFile).read())
        print "indexpath: " + indexpath

        CIK = indexpath

        r = requests.get(shttp + indexpath)
        soup = BeautifulSoup(r.text)

        table = soup("table")

        try:
            rows = table[3].findAll('tr')
            for tr in rows:

                ClassName = ''
                ClassNum = ''


                cols = tr.findAll('td')
                rtext =''
                flagInClass = False

                for i, c in enumerate(cols):
                    #print c.text
                    s = c.text.strip()
                    html = str(c.renderContents())
                    #print str(i) + '|' + html + '|' + s

                    if i == 1:
                        if html.find('class="hot"') > -1:
                            SeriesNum = s
                            RowType = "SERIES"



                    if i==2:
                        if html.find('CIK=S00') > -1:
                            SeriesName = s

                        if html.find('CIK=C00') > -1:
                            ClassNum = s

                    if i==3:
                        if s != '':
                            ClassName = s

                    if i==4:
                        if s != '':
                            Symbol = s

                if ClassNum != '':
                    #print CIK + '|' + SeriesName + '|' + SeriesNum + '|' + ClassName + '|' + ClassNum + '|' + Symbol + '|' + DateAdd
                    dbInsert()

        except:
            pass




def dbtest():
    pass

def dbInsert():

    #print "In dbInsert and ClassNum = " + ClassNum
    flagRecordExists = False

    try:
        conncheck = pyodbc.connect(connstr + sDB)
        # First check existance
        sqlcheck = "Select ClassNum FROM SECMasterClass where [ClassNum] ='" + ClassNum + "'"
        #print sqlcheck
        cursorcheck = conncheck.cursor()
        cursorcheck.execute(sqlcheck)
        row  = cursorcheck.execute(sqlcheck).fetchone()
        if row != None:
            flagRecordExists = True
            #print "Series: " + SeriesName + " class: " + ClassNum + " already exists"
    except:
            flagRecordExists = False
            print "dbCheck Record failure!"
    finally:
            cursorcheck.close()
            conncheck.close()

    if flagRecordExists == False:
        sql = ("INSERT into SECMasterClass (CIK, SeriesNum, SeriesName, ClassNum, ClassName, Symbol, DateAdd) values ('" + CIK + "','" +
        SeriesNum + "','" +
        SeriesName + "','" +
        ClassNum + "','" +
        ClassName + "','" +
        Symbol + "','" +
        DateAdd + "'" + ")")

        print sql

        conn = pyodbc.connect(connstr + sDB)
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            conn.commit()

        except:
            print "db insert error"
            cursor.close()
            conn.close()

        finally:
            cursor.close()
            conn.close()

            return


if __name__ == '__main__':
     dbLoad_lSECFilingsIndexURLs()
     for l in lSECFilingsIndexURLs:
        pass
        #print l
     InsertNewFundClasses()
     print "Done!"

