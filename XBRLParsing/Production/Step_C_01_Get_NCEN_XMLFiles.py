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

Folders_NCEN = r'D:\Files2020_Data\Folders_NCEN'
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
    
    sql = "Select ID, SECFilingIndexURL, XMLFile, FilingDate, CAST(CIK as NUMERIC) as CIKVal FROM EdgarFilings WHERE "
    sql = sql + "(FileType = 'N-CEN' or FileType = 'N-CEN/A') and XMLFile <> '' "
    sql = sql + "and FilingDate >= '" + fromDate +"' and FilingDate <= '" + toDate + "';"
    #print(sql)
    df = pd.read_sql_query(sql, connSQLite)
    return df  

        
if __name__ == '__main__':
    connSQLite = create_connection(dbstr)
    #fromDate = "20200201"
    #toDate = "20200204"
    fromDate = "20190401"
    toDate = "20190431"
    df = dbLoad_485BPOS_Records(connSQLite, fromDate, toDate)

    for index, row in df.iterrows():
        if len(str(row[1])) > 20:
            # folder html file for parsing out ACCESSION NUMBER For folder name
            SECFilingIndexURL = str(row[1])
            # URL to our XML file
            XMLFileURL = str(row[2])

            head, tail = os.path.split(SECFilingIndexURL)
            if len(tail) > 3:
                # Zip file name same as HTML
                CreateFolderName = tail.replace('-index.htm','')

                head_XML, tail_XML = os.path.split(XMLFileURL)
                
                XMLlocalFolder = Folders_NCEN + "\\" + str(CreateFolderName) #+ "\\" + tail_XML
                print(XMLlocalFolder)
                
                print("Begin download " + str(index) + " " + XMLFileURL + " " + str(row[2])  + " " + str(row[3]))
                print(XMLFileURL + " | "+ XMLlocalFolder)

                if not os.path.exists(XMLlocalFolder):
                    os.makedirs(XMLlocalFolder)
                
                # Download XML file
                urllib.request.urlretrieve(XMLFileURL,XMLlocalFolder + r'\\' + tail_XML)

              
    
    


