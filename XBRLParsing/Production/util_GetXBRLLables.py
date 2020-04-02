from lxml import etree
import os
from os import path
from io import StringIO, BytesIO
import re
import pandas as pd
import numpy

import sqlite3
from sqlite3 import Error

from urllib.request import urlopen

# See also...
# C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\SQL_Creator.xls

XBRLFolders_485BPOS = r'C:\Files2020_Data\XBRLFolders_485BPOS'
dbstr_filings = r'C:\Files2020_Dev\ByProject\Open15C_Data\SECedgar.sqlite'
dbstr_xbrl = r'C:\Files2020_Dev\ByProject\Open15C_Data\SEC_Flat485BPOS.sqlite3'
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
        #print("connected")
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


def cvs_485BPOS_to_Flat485BPOS(FileName, CIKVal, FolderName):

    # Prepare List of Tuples which we'll SQL Insert many
    DataFiling = []

    try:
        df = pd.read_csv(FileName)

        # # Get unique SeriesNum
        # for i, row in enumerate(df.values):
        #     contextRef = str(row[1])
        #     # FIRST LETS GET SERIES and CLASS NUM IF POSSIBLE
        #     pattern = r'[C]\d{4,9}'
        #     ClassNum = re.search(pattern, contextRef) 
        #     if not ClassNum == None:
        #         # Create table with unique classnums
        #         # We'll then fill, using logic to normalize
        #         # the expense entries, then do a transpose?
        #         dbClassNum = ClassNum[0]
        
        for i, row in enumerate(df.values):
            Label = str(row[0]).strip()
            Label = Label.replace('[', '').replace(']', '')
            Label = Label.replace(',', '')
            lcLabel = Label.lower()
            dbLabel = lcLabel # default
            if 'text' in lcLabel: dbLabel = 'None'
            if 'heading' in lcLabel: dbLabel = 'None'
            if 'name' in lcLabel: dbLabel = 'None'
            #contextRef = str(row[1])
            
            
            # Is line expense or other data we want related?
            Keywords = ['expense','management','fee','annual return']
            if any(word in dbLabel for word in Keywords):
                
                
                if 'operating expenses' in lcLabel and 'after' in lcLabel: dbLabel='NetExp'
                if 'net expenses' in lcLabel': dbLabel='NetExp'
                if lcLabel=='netexp': dbLabel='NetExp'
                
                if ('waiver' in lcLabel or 'reimbursement' in lcLabel) and not 'total' in lcLabel:
                    dbLabel='FeeWaiver'
                
                if lcLabel=='expenses (as a percentage of assets)': dbLabel='TotExp'
                if lcLabel=='totexp': dbLabel='TotExp'

                if 'acquired' in lcLabel: dbLabel='AcquiredFees'
                
                if 'other expenses' in lcLabel: dbLabel='OtherExp'
                if 'miscellaneous' in lcLabel: dbLabel='OtherExp'
                if lcLabel=='otherexp' in lcLabel: dbLabel='OtherExp'
                
                if lcLabel=='distribution and service (12b-1) fees': dbLabel='Dist12b1Fees'
                if lcLabel=='service fee': dbLabel='Dist12b1Fees'
                if '12b-1' in lcLabel: dbLabel='Dist12b1Fees'
                
                if 'management' in lcLabel: dbLabel='MgmtFees'
                if lcLabel=='mgmtfees': dbLabel='MgmtFees'
                if lcLabel=='investment advisory fees': dbLabel='MgmtFees'
                

                if dbLabel != '':
                    #print(dbClassNum +"|"+ dbSeriesNum+"|"+str(dbLabel)+"|"+str(dbValue))
                    dbLabel = dbLabel.replace('(', '').replace(')', '')
                    dbLabel = dbLabel.replace("'", '').replace(',', '')
                    DataTuple = (dbLabel)
                    DataFiling.append(DataTuple) 
                    #DataFiling.append(str(dbLabel)) 
    except:
        pass

    return DataFiling

def SQLInsertFilingsData(dbstr_xbrl, DataFiling):

    connSQLite = create_connection(dbstr_xbrl)
       
    # sql = 'INSERT into [Labels] '
    # sql = sql + '(Label)'
    # sql = sql + " values (?)"

    #print(DataFiling)
    cursor = connSQLite.cursor()
    for idx, val in enumerate(DataFiling):
        sqlins = 'INSERT into [Labels] (Label) VALUES (' + "'" + val + "');"
        cursor.execute(sqlins)
        connSQLite.commit()
        #print(val[0])
    
    connSQLite.close()

    
    
    # try:
    #     #print(sql + '\n')
    #     cursor = connSQLite.cursor()
    #     cursor.executemany(sql, DataFiling.strip(),) #!!!! REMEMBER those brackets or weird number of params
    #     connSQLite.commit()
    #     cursor.close()

    # except: 
    #     print("Failed to insert multiple records into sqlite table")

    # finally:
    #     if (connSQLite):
    #         connSQLite.close()
            #print("The SQLite connection is closed")
        
if __name__ == '__main__':
    connSQLite = create_connection(dbstr_filings)
    fromDate = "20200101"
    toDate = "20200131"
    # ALL
    #fromDate = "20190301"
    #toDate = "20200231"
    df = dbLoad_485BPOS_Records(connSQLite, fromDate, toDate)

    if not df.empty:

        for index, row in df.iterrows():
            if len(str(row[1])) > 20:
                SECFilingIndexURL = str(row[1])
                dbCIKVal=row[3]
                dbFilingDate=str(row[2])
                print(dbFilingDate)
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
                    # We need to change this to build a DataTable we can insert into
                    # A flat expense table.
                    DataFiling = cvs_485BPOS_to_Flat485BPOS(cvsFileAndPath, row[3], CreateZIPFolderName)
                    #df = pd.DataFrame(DataFiling)

                   
                    SQLInsertFilingsData(dbstr_xbrl, DataFiling)

                        
                    #print(getattr(row, 'Index'),col, getattr(row, col))
                    # for col in df_pivot.columns:
                    #     for row in df_pivot.itertuples():
                    #         print(getattr(row, 'Index'),col, getattr(row, col))
                        #print(getattr(row, 'Index'),row)

                    #print(df_pivot)
                    #SQLInsertFilingsData(dbstr_xbrl, DataFiling)
                    # if want to go back
                    #DataFrame2 = list(df.itertuples(index=False))
                    #print(DataFrame2)

                
            
    
    


