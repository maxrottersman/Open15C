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
    
    sql = "Select ID, SECFilingIndexURL, FilingDate, CAST(CIK as NUMERIC) as CIKVal, XMLFile FROM EdgarFilings WHERE "
    sql = sql + "(FileType = '485BPOS' or FileType = '485BPOS/A') and XMLFile <> '' "
    sql = sql + "and FilingDate >= '" + fromDate +"' and FilingDate <= '" + toDate + "';"
    df = pd.read_sql_query(sql, connSQLite)
    return df  


# # ALL TAGS
# for tag in tree.iter():
#     if not len(tag):
#         print(tag.tag," | ",tag.text)

def walk485BPOS(FilingDate, FileName, CIKVal, tree, GetFieldsList):
    connSQLite = create_connection(dbstr)

    # List of data we'll add to SQL TABLE
    # Series, Class, XMLFieldName, StringValue, FilingDate, FileName, CIKVal
    dataForFields = [ \
    '', \
    '', \
    '', \
    '', \
    '', \
    '', \
    0]

    for tag in tree.iter():

    # tag is the element name
    # tag.get("attribute name")
    # tag.keys() returns list of attributes
    # tag.items() returns name, value pair
    # 
        for r in GetFieldsList:
            if str(tag.tag).lower() == r.lower():
                SECClass = ''
                SECSeries = ''
                saveElem = ''
                saveValue = ''
                
                ElemFirstAttribute = str(tag.items()[0][1])
                if len(ElemFirstAttribute) >= 12:
                    #print(ElemFirstAttribute)
                    try:
                        SECClass = str(re.findall(r'C\d{9}',ElemFirstAttribute)[0]) # Works
                    except IndexError:
                        SECClass = ''

                    try:
                        SECSeries = str(re.findall(r'S\d{9}',ElemFirstAttribute)[0]) # Works
                    except IndexError:
                        SECSeries = ''
                    
                    try:
                        saveElem = str(tag.tag)
                    except:
                        pass

                    try:
                        saveValue = str(tag.text)
                    except:
                        pass
                    
                    try:
                        print(SECSeries + "|" + SECClass + "|" + saveElem + "|" + saveValue +  "\r")
                    except:
                        pass

                dataForFields[0] = SECSeries # Series
                dataForFields[1] = SECClass # Class
                dataForFields[2] = saveElem # XMLFieldName
                dataForFields[3] = saveValue # StringValue
                dataForFields[4] = FilingDate # FilingDate
                dataForFields[5] = FileName # FilingValue
                dataForFields[6] = CIKVal # FilingValue

                if len(saveElem) > 9:
                    connSQLite.executemany('INSERT INTO Extract_485BPOS VALUES \
                            (?,?,?,?,?,?,?)', [dataForFields])
                    connSQLite.commit()

def cvs_485BPOS_to_db(FileName):

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
            print(dbLabel+'|'+dbSeriesNum+'|'+dbSeriesNum+'|'+dbValue)


        
if __name__ == '__main__':
    connSQLite = create_connection(dbstr)
    fromDate = "20200228"
    toDate = "20200231"
    df = dbLoad_485BPOS_Records(connSQLite, fromDate, toDate)

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

                print("To db " + cvsFileAndPath)
                cvs_485BPOS_to_db(cvsFileAndPath)
                break
            
    
    


