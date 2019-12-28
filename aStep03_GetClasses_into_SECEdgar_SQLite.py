#-------------------------------------------------------------------------------
from bs4 import BeautifulSoup
import os
import sys
import re

from pathlib import Path

import sqlite3
from sqlite3 import Error
import requests


# --------- CONFIG --------------
ScriptPath = Path.cwd() # new way of getting script folder in both win/linux
ScriptPathParent = Path.cwd().resolve().parent # Parent
DataPath = ScriptPathParent / 'Open15C_Data'
SECIndexesPath = DataPath / 'SEC_IndexFiles' # / adds right in all os
DataPathSQLiteDB = DataPath / 'SECedgar.sqlite'

fromDate = '20190101' # will be greater-than or equl
endDate = '20190131'
# -------------------------------

sURLFile = ''#'c:\\Files2013_EDGAR\\pyEDGAR\\testdocs\\nsarindex3.htm'
lSECFilingsIndexURLs = [] # make this global
sql=''

#
# Create CONNECTION to SQLite Database
#
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("connected")
    except Error as e:
        print(e)
 
    return conn
#
# Get files to go mine
#
def dbLoad_lSECFilingsIndexURLs():
    
    try:
        sql = 'Select SECFilingIndexURL FROM EdgarFilings WHERE '
        sql = sql + "FilingDate >= '" + fromDate + "' AND "
        sql = sql + "FilingDate <= '" + endDate + "';"
        print(sql)
        cursor = connSQLite.cursor()
        cursor.execute(sql)
        rows  = cursor.fetchall()
        if rows != None:
            for r in rows:
                lSECFilingsIndexURLs.append(r) #global from up top
    except:
        print("db error!")
        cursor.close()

    finally:
        pass

def InsertNewFundClasses():
    s =''
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
        print(cnt)
        #soup = BeautifulSoup(open(sURLFile).read())
        r = requests.get(indexpath[0])
        soup = BeautifulSoup(r.text,features="html.parser")

        # Get filing dates
        DateAdd = soup.find(text="Filing Date").findNext('div').contents[0]
        if DateAdd =='': DateAdd='20991231'

        table = soup("table", {'class' : 'tableSeries' })

        s = str(indexpath)
        start = s.find('/data/') + 6
        end = s.find('/', start)
        #print indexpath
        #print s[start:end]
        CIK = s[start:end]
        SeriesName =''
        try:
            rows = table[0].findAll('tr')
            RowType = "HEADER"
            for tr in rows:
                cols = tr.findAll('td')
                rtext =''
                flagInClass = False
                for i, c in enumerate(cols):
                    #print c.text
                    s = c.text.strip()

                    if i == 0:
                        if s.find('Series') > -1:
                            SeriesNum = s.replace('Series','').strip()
                            RowType = "SERIES"
                        if s.find('Contract') > -1:
                            RowType = "CLASS"
                            ClassNum = s.replace('Class/Contract','').strip()
                        if s == '':
                            RowType = "HEADER"
                            flagInClass = False
                            SeriesName = ''
                            SeriesNum = ''
                            ClassName = ''
                            ClassNum = ''
                            Symbol = ''

                    if i==1:
                       pass

                    if i==2:
                        if SeriesNum != '' and ClassNum == '':
                            SeriesName = s

                        if ClassNum != '':
                            ClassName = s
                            # We we have a class we'll write record
                            flagInClass = True

                    if i==3:
                        if s != 'Ticker Symbol':
                            Symbol = s


                #print rtext
                if flagInClass == True and RowType != "HEADER":
                    #print CIK + '|' + SeriesNum + '|' + SeriesName + '|' + ClassNum + '|' + ClassName + '|' + Symbol
                    if CIK == '':
                        CIK = "NA"
                    SeriesName = SeriesName.replace("'","")
                    SeriesName = SeriesName.replace("(","")
                    SeriesName = SeriesName.replace(")","")
                    SeriesName = SeriesName.replace(",","")

                    ClassName = ClassName.replace("'","")
                    ClassName = ClassName.replace("(","")
                    ClassName = ClassName.replace(")","")
                    ClassName = ClassName.replace(",","")

                    # First check if fund class already in database
                    flagRecordExists = False
                    try:
                        # First check existance
                        sqlcheck = "Select ClassNum FROM SECMasterClass where [ClassNum] ='" + ClassNum + "'"
                        #print sqlcheck
                        cursorcheck = connSQLite.cursor()
                        cursorcheck.execute(sqlcheck)
                        row  = cursorcheck.execute(sqlcheck).fetchone()
                        if row != None:
                            flagRecordExists = True
                            print("Series: " + SeriesName + " class: " + ClassNum + " already exists")
                    except:
                            flagRecordExists = False
                            print("dbCheck Record failure!")
                    finally:
                            cursorcheck.close()

                    if flagRecordExists == False:
                        sql = ("INSERT into SECMasterClass (CIK, SeriesNum, SeriesName, ClassNum, ClassName, Symbol, DateAdd) values ('" + CIK + "','" +
                        SeriesNum + "','" +
                        SeriesName + "','" +
                        ClassNum + "','" +
                        ClassName + "','" +
                        Symbol + "','" +
                        DateAdd + "'" + ")")

                        #print(sql)
                        
                        try:
                            cursor = connSQLite.cursor()
                            cursor.execute(sql)
                            connSQLite.commit()
                            cursor.close()

                        except:
                            print("db insert error")
                            cursor.close()
                            

                        finally:
                            cursor.close()

                    #if cnt > 30:
                    #    return main

                flagInClass = False

        except:
            #print "table did not exist"
            print("Error")

def dbtest():
    pass



#
# IT ALL BEGINS ON MAIN
#
if __name__ == '__main__':
     connSQLite = create_connection(DataPathSQLiteDB)
     # will use data range from top
     dbLoad_lSECFilingsIndexURLs()
     # print them out
     for l in lSECFilingsIndexURLs:
        print(l)
    # go through each one, download, parse, write to db
     InsertNewFundClasses()
     print("Done!")

