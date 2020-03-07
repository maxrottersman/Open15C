from lxml import etree
import os
from os import path
from io import StringIO, BytesIO
import re
import pandas as pd

import sqlite3
from sqlite3 import Error

#from urllib.request import urlopen
import urllib
from zipfile import ZipFile

XBRLZipFiles_485BPOS = r'C:\Files2020_Data\XBRLZipFiles_485BPOS'
XBRLFolders_485BPOS = r'C:\Files2020_Data\XBRLFolders_485BPOS'
dbstr = r'C:\Files2020_Dev\ByProject\Open15C_Data\SECedgar.sqlite'

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

def dbLoad_485BPOS_Records(connSQLite, fromDate, toDate):
    
    sql = "Select ID, SECFilingIndexURL, FilingDate, CAST(CIK as NUMERIC) as CIKVal FROM EdgarFilings WHERE "
    sql = sql + "(FileType = '485BPOS' or FileType = '485BPOS/A') and XMLFile <> '' "
    sql = sql + "and FilingDate >= '" + fromDate +"' and FilingDate <= '" + toDate + "';"
    df = pd.read_sql_query(sql, connSQLite)
    return df  

        
if __name__ == '__main__':
    connSQLite = create_connection(dbstr)
    fromDate = "20200101"
    toDate = "20200231"
    df = dbLoad_485BPOS_Records(connSQLite, fromDate, toDate)

    for index, row in df.iterrows():
        if len(str(row[1])) > 20:
            SECFilingIndexURL = str(row[1])
            head, tail = os.path.split(SECFilingIndexURL)
            if len(tail) > 3:
                # Zip file name same as HTML
                CreateZIPFolderName = tail.replace('-index.htm','')
                zipfile = tail.replace('-index.htm','-xbrl.zip')
                # URL to get zip file
                ZIPurl = head + r'/' + zipfile
                # Construct local folder to save zip file
                ZIPlocal = XBRLZipFiles_485BPOS + r'\\' + str(zipfile)
                # Construct local folder to UNZIP file into
                ZIPUnzipFolder = XBRLFolders_485BPOS + r'\\' + CreateZIPFolderName
                
                print("Begin download " + str(index) + " " + ZIPurl + " " + str(row[2])  + " " + str(row[3]))
                
                # Download ZIP file
                urllib.request.urlretrieve(ZIPurl,ZIPlocal)

                # UNZIP into folder
                with ZipFile(ZIPlocal,'r') as zipObj:
                    zipObj.extractall(ZIPUnzipFolder)

    
    


