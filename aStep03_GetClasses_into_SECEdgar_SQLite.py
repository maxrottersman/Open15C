#-------------------------------------------------------------------------------
from bs4 import BeautifulSoup
import os
import sys
import re
import sqlite3
from sqlite3 import Error
import requests

ScriptPath = os.path.dirname(os.path.realpath(__file__))
SECIndexesPath = ScriptPath + "\\SECIndexes"

# --------- CONFIG --------------
fromDate = '20190101' # will be greater-than or equl
endDate = '20190105'

dbstr = r'C:\ff_factory2019\pyEDGAR\db\SECedgar.sqlite'
sDB = dbstr #ScriptPath + r'\SECIndexes\edgarfilingsfunds.accdb'
sDBTarget = dbstr #r'C:\ff_Factory2007\NSAR\FRMatch2012.accdb'
# -------------------------------

sURLFile = ''#'c:\\Files2013_EDGAR\\pyEDGAR\\testdocs\\nsarindex3.htm'
lSECFilingsIndexURLs = []
sql=''

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
                lSECFilingsIndexURLs.append(r)
    except:
        print("db error!")
        cursor.close()

    finally:
        pass

def InsertNewFundClasses():
    s =''
    t= ''
    rtext = ''
    CIK = ''
    SeriesName = ''
    SeriesNum =''
    ClassName = ''
    ClassNum =''
    Symbol = ''
    FundName = ''
    flagInClass = False
    cnt = 0

    for indexpath in lSECFilingsIndexURLs:
        cnt = cnt+1
        print(cnt)
        #soup = BeautifulSoup(open(sURLFile).read())
        r = requests.get(indexpath[0])
        soup = BeautifulSoup(r.text)

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

                        print(sql)

                 #   sql = ("insert into CIKseriesclasses(CIK, SeriesNum, SeriesName, ClassNum, ClassName, Symbol) values ('" + CIK + "','" +
                 #   SeriesNum + "','" +
                 #   SeriesName + "','" +
                 #   ClassNum + "','" +
                 #   ClassName + "','" +
                 #   Symbol + "'"+ "')"')
                        
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
                           

                    #cursor.execute("insert into CIKseriesclasses
                    #([CIK], [SeriesNum], [SeriesName], [ClassNum], [ClassName], [Symbol])
                    #values ('" + CIK + "','" + SeriesNum + "','" + SeriesName + "','" +
                    #ClassNum + "','" + ClassName + "','" + Symbol + "'"+ ")" )
                    #conn.commit()

                    #if cnt > 30:
                    #    return main

                flagInClass = False

        except:
            #print "table did not exist"
            print("Error")

def dbtest():
    pass

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
# IT ALL BEGINS ON MAIN
#
if __name__ == '__main__':
     connSQLite = create_connection(dbstr)
     dbLoad_lSECFilingsIndexURLs()
     for l in lSECFilingsIndexURLs:
        print(l)
     InsertNewFundClasses()
     print("Done!")

