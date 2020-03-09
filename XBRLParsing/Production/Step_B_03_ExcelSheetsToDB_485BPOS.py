from lxml import etree
import os
from os import path
from io import StringIO, BytesIO
import re
import pandas as pd

import sqlite3
from sqlite3 import Error

from urllib.request import urlopen

XBRLFolders_485BPOS = r'C:\Files2020_Data\XBRLFolders_485BPOS'
dbstr_filings = r'C:\Files2020_Dev\ByProject\Open15C_Data\SECedgar.sqlite'
dbstr_xbrl = r'C:\Files2020_Dev\ByProject\Open15C_Data\SEC_XBRL.sqlite3'

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
    
    sql = "Select ID, SECFilingIndexURL, FilingDate, CAST(CIK as NUMERIC) as CIKVal, XMLFile FROM EdgarFilings WHERE "
    sql = sql + "(FileType = '485BPOS' or FileType = '485BPOS/A') and XMLFile <> '' "
    sql = sql + "and FilingDate >= '" + fromDate +"' and FilingDate <= '" + toDate + "';"
    df = pd.read_sql_query(sql, connSQLite)
    return df  


# # ALL TAGS
# for tag in tree.iter():
#     if not len(tag):
#         print(tag.tag," | ",tag.text)


def cvs_485BPOS_to_db(FileName, CIKVal, FolderName):

    # Prepare List of Tuples which we'll SQL Insert many
    DataFiling = []

    try:
        df = pd.read_csv(FileName)
        
        for i, row in enumerate(df.values):
            Label = str(row[0])
            contextRef = str(row[1])
            unitRef = str(row[2])
            Dec = str(row[3])
            # ignore Prec and Lang
            Value = str(row[6])
            dbValue = ''
            if len(Value) < 80:
                dbValue = Value
                            
            # FIRST LETS GET SERIES and CLASS NUM IF POSSIBLE
            pattern = r'[S]\d{4,9}'
            SeriesNum = re.search(pattern, contextRef) 
            pattern = r'[C]\d{4,9}'
            ClassNum = re.search(pattern, contextRef) 
            #print(row[1])
            dbSeriesNum = ''
            dbClassNum = ''
            if not SeriesNum == None:
                dbSeriesNum = SeriesNum[0]
            if not ClassNum == None:
                dbClassNum = ClassNum[0]

            # Is line expense or other data we want related?
            Keywords = ['expense','management','fee','annual return','central index key','symbol']
            dbLabel =''
            if any(word in Label.lower() for word in Keywords):
                dbLabel = Label

            if dbLabel != '':
                #print(dbLabel+'|'+dbSeriesNum+'|'+dbClassNum+'|'+dbValue)
                DataTuple = (CIKVal, FolderName, contextRef, dbLabel,dbSeriesNum,dbClassNum, Dec, unitRef, dbValue)
                DataFiling.append(DataTuple) 
    except:
        pass

    return DataFiling

def SQLInsertFilingsData(dbstr_xbrl, DataFiling):

    connSQLite = create_connection(dbstr_xbrl)
       
    sql = 'INSERT into Extract_XBRL_485BPOS'
    sql = sql + '(CIKVal,FolderName,contextRef,[Label],Series,Class,Dec,unitRef,[Value])'
    sql = sql + " values (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    
    try:
        #print(sql + '\n')
        cursor = connSQLite.cursor()
        cursor.executemany(sql, DataFiling) #!!!! REMEMBER those brackets or weird number of params
        connSQLite.commit()
        cursor.close()

    except: 
        print("Failed to insert multiple records into sqlite table")

    finally:
        if (connSQLite):
            connSQLite.close()
            #print("The SQLite connection is closed")


        
if __name__ == '__main__':
    connSQLite = create_connection(dbstr_filings)
    fromDate = "20190301"
    toDate = "20200231"
    df = dbLoad_485BPOS_Records(connSQLite, fromDate, toDate)

    if not df.empty:

        for index, row in df.iterrows():
            if len(str(row[1])) > 20:
                SECFilingIndexURL = str(row[1])
                head, tail = os.path.split(SECFilingIndexURL)
                if len(tail) > 3:
                    # We used name of folder for cvs files
                    CreateZIPFolderName = tail.replace('-index.htm','')
                    # so what is it?
                    cvsFile = CreateZIPFolderName + '.csv'
                    # And where did we put it?
                    ZIPUnzipFolder = XBRLFolders_485BPOS + '\\' + CreateZIPFolderName
                    # Altogether now
                    cvsFileAndPath = ZIPUnzipFolder + '\\' + cvsFile

                    print("To db " + str(index) + ' ' + cvsFileAndPath)
                    # File to import, CIKVal and Folder
                    DataFiling = cvs_485BPOS_to_db(cvsFileAndPath, row[3], CreateZIPFolderName)
                    SQLInsertFilingsData(dbstr_xbrl, DataFiling)

                
            
    
    


