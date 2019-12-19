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

connstr = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};Provider=Microsoft.ACE.OLEDB.12.0;DBQ='
sDB = r'C:\ff_Factory2007\NSAR\FRMatch2012.accdb'
# -------------------------------

sURLFile = ''#'c:\\Files2013_EDGAR\\pyEDGAR\\testdocs\\nsarindex3.htm'
lSECFilingsIndexURLs = []
sql=''
URLpre = 'http://www.sec.gov/cgi-bin/series?company=&sc=companyseries&ticker=&CIK='
URLsuffix = '&type=N-PX'

#<b class="blue">ROWCX</b></td></tr>

def dbLoad_SECMasterClass():
    conn = pyodbc.connect(connstr + sDB)
    cursor = conn.cursor()
    cnt = 0
    try:

        sql = r'SELECT [SECMasterClass].[ClassNum] FROM [SECMasterClass] '
        sql += r"WHERE IsNull([SECMasterClass].[Symbol])=True OR [SECMasterClass].[Symbol] = '';"

        print sql
        cursor.execute(sql)
        rows  = cursor.fetchall()
        if rows != None:
            for r in rows:
                cnt = cnt + 1
                URLstr = URLpre + str(r[0]) + URLsuffix
                #print URLstr
                #lSECFilingsIndexURLs.append(URLstr)

                rstr = requests.get(URLstr)
                soup = BeautifulSoup(rstr.text)
                symbolstr = soup.find("b", {'class' : 'blue' })
                if symbolstr != None:
                    s_ticker = symbolstr.renderContents()
                    #print symbolstr.renderContents()
                    Update_SECMasterClass(r[0], s_ticker)

                #if cnt > 300:
                #    break

    except:
        print "db error!"
        cursor.close()
        conn.close()


    finally:
        pass
        #conn.close()

def Update_SECMasterClass(s_classnum, s_ticker):
    sqlupdate = "UPDATE SECMasterClass SET [Symbol] = '" + s_ticker + "' "
    sqlupdate = sqlupdate + " WHERE [ClassNum]= '" + s_classnum + "'"

    conn = pyodbc.connect(connstr + sDB)
    cursor = conn.cursor()
    try:
        print sqlupdate
        cursor.execute(sqlupdate)
        conn.commit()
    except:
        print "db update error"
        cursor.close()
        conn.close()
    finally:
        cursor.close()
        conn.close()


def dbtest():
    pass

if __name__ == '__main__':
     dbLoad_SECMasterClass()
     print "Done!"

