from lxml import etree
import os
from os import path
from io import StringIO, BytesIO
import re
import pandas as pd

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
            contextRef = str(row[1])
            unitRef = str(row[2])
            Dec = str(row[3])
            # ignore Prec and Lang
            Value = row[6].strip()
            chkValue = Value.replace('.','',1)
            dbValue = ''

            # if 'Expenses (as a percentage of Assets)'.strip() == Label:
            #         dbLabel='TotExp'
            #         x = chkValue.isdigit()
                                        
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
            Keywords = ['expense','management','fee','annual return']
            dbLabel =''
            dbValue = 0
            if any(word in Label.lower() for word in Keywords) and chkValue.isdigit() == True:
               
                dbValue = float(Value)
                if Label=='Acquired Fund Fees and Expenses': dbLabel='AcquiredFees'
                if Label=='Other Expenses (as a percentage of Assets):': dbLabel='OtherExp'
                if Label=='Other expenses': dbLabel='OtherExp'
                if Label=='Distribution and Service (12b-1) Fees': dbLabel='Dist12b1Fees'
                if Label=='Management Fees (as a percentage of Assets)': dbLabel='MgmtFees'
                if Label=='Fee Waiver or Reimbursement': dbLabel='FeeWaiver'
                if Label=='Total annual fund operating expenses': dbLabel='TotExp'
                if Label=='Expenses (as a percentage of Assets)': dbLabel='TotExp'
                if Label=='Net Expenses (as a percentage of Assets)': dbLabel='NetExp'
                if Label=='Total annual fund operating expenses after expense reimbursement': dbLabel='NetExp'

            if dbLabel != '':
                #print(dbClassNum +"|"+ dbSeriesNum+"|"+str(dbLabel)+"|"+str(dbValue))
                DataTuple = (dbClassNum, dbSeriesNum, dbLabel, dbValue)
                DataFiling = []
                DataFiling.append(DataTuple) 
    except:
        pass

    return DataFiling

def SQLInsertFilingsData(dbstr_xbrl, DataFiling):

    connSQLite = create_connection(dbstr_xbrl)
       
    sql = 'INSERT into Flat_485BPOS'
    sql = sql + '(CIKVal,FilingDate,SeriesNum,ClassNum,AcquiredFees,Dist12b1Fees,MgmtFees,OtherExp,TotExp,FeeWaiver,NetExp)'
    sql = sql + " values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    
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
    fromDate = "20200226"
    toDate = "20200227"
    df = dbLoad_485BPOS_Records(connSQLite, fromDate, toDate)

    if not df.empty:

        for index, row in df.iterrows():
            if len(str(row[1])) > 20:
                SECFilingIndexURL = str(row[1])
                dbCIKVal=row[3]
                dbFilingDate=str(row[2])
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
                    df = pd.DataFrame(DataFiling)
                    df.columns = ['ClassNum','SeriesNum','Label','dbValue']
                    #print(df)
                    df_pivot = df.pivot(index='ClassNum',columns='Label',values='dbValue')


                    for row in df_pivot.itertuples():
                        
                        dbSeriesNum=''
                        dbClassNum=''
                        dbAcquiredFees=0
                        dbDist12b1Fees=0
                        dbMgmtFees=0
                        dbOtherExp=0
                        dbTotExp=0
                        dbFeeWaiver=0
                        dbNetExp=0

                        dbClassNum = getattr(row, 'Index')
                        if 'AcquiredFees' in df_pivot : dbAcquiredFees = getattr(row, 'AcquiredFees')
                        if 'OtherExp'  in df_pivot : dbOtherExp = getattr(row, 'OtherExp')
                        if 'NetExp'  in df_pivot : dbNetExp = getattr(row, 'NetExp')
                        if 'TotExp'  in df_pivot : dbTotExp = getattr(row, 'TotExp')
                        if 'Dist12b1Fees'  in df_pivot : dbDist12b1Fees = getattr(row, 'Dist12b1Fees')
                        if 'MgmtFees'  in df_pivot : dbMgmtFees = getattr(row, 'MgmtFees')
                        if 'FeeWaiver'  in df_pivot : dbFeeWaiver = getattr(row, 'FeeWaiver')

                        # print(dbClassNum, dbAcquiredFees)
                        # print(dbClassNum, dbOtherExp)
                        # print(dbClassNum, dbNetExp)
                        # print(dbClassNum, dbTotExp)
                        # print(dbClassNum, dbDist12b1Fees)
                        # print(dbClassNum, dbMgmtFees)
                        # print(dbClassNum, dbFeeWaiver)

                        DataFilingSQLInsert = []
                        DataTuple = (dbCIKVal,dbFilingDate,dbSeriesNum,dbClassNum,dbAcquiredFees,dbDist12b1Fees,dbMgmtFees,dbOtherExp,dbTotExp,dbFeeWaiver,dbNetExp)
                        DataFilingSQLInsert.append(DataTuple) 

                        SQLInsertFilingsData(dbstr_xbrl, DataFilingSQLInsert)

                        
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

                
            
    
    


