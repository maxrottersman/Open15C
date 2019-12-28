# Created:     22/02/2013
# Copyright:   (c) Max Rottersman 2013
# Licence:     <your licence>
# PARSES EDGAR INDEX FILE AND COPIES 485BPOS ENTERIES WITH NEW FILENAMES TO USE FOR PROSPECTUSES
# INTO listmaster.YYYYDDYY.txt

import csv
import os
#from os import listdir
import sys
import string
import re
from pathlib import Path

import sqlite3
from sqlite3 import Error

ScriptPath = Path.cwd() # new way of getting script folder in both win/linux
ScriptPathParent = Path.cwd().resolve().parent # Parent
DataPath = ScriptPathParent / 'Open15C_Data'
SECIndexesPath = DataPath / 'SEC_IndexFiles' # / adds right in all os
DataPathSQLiteDB = DataPath / 'SECedgar.sqlite'
#print(SECIndexesPath)
#exit()

# --------- CONFIG --------------
fromDate = '20190101' # will be greater-than or equl
endDate = '20190105'
# 48BPOS, NSAR and N1A
FileTypeFunds = [r'485bpos' ,r'485bpos/a',r'485apos',r'485apos/a',r'nsar-a',r'nsar-a/a', r'nsar-b',r'nsar-b/a',r'n-1a',r'n-1a/a',r'n-cen']
# -------------------------------
valid_chars = '-_., abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
sfilename = 'master.20130215.idx'

#
# Get Index files in our daily download from SEC folder
# Returns: List of all *.idx file names with path
#
def getIndexFiles():

    #p = Path(SECIndexesPath).glob('*.idx')
    #EDGARindexfiles =  [fn.stem for fn in p] # stem for only filename
    
    p = Path(SECIndexesPath).glob('*.idx')
    EDGARindexfilesWithPath =  [fn for fn in p] # stem for only filename
    #print(EDGARindexfilesWithPath)

    return EDGARindexfilesWithPath


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


def get_EDGAR_Fund_Records_From_CSV_file(filename, separator):
    DataItems = ['','','','','','','']
    DataFiling = []
    with open(filename, 'r') as file_obj:
        for line in csv.reader(file_obj,
              delimiter=separator): # Strips whitespace after delimiter.
              # Your custom delimiter.
              #, skipinitialspace=True
            if line: # Make sure there's at least one entry.
                if len(line) > 3:
                    filetype = str(line[2]).strip().lower()
                    #print filetype
                    # make sure in fund type list like 485BPOS, NSAR-A or B, N1A, etc.
                    if any(filetype == chks for chks in FileTypeFunds):
                        fn = os.path.basename(line[4]) # Gets trailing filename
                        path = str(line[4]).replace(fn,'')
                        fnnum = re.sub("\D", "", fn) # removes dashes (-) in string, making numeric only
                        nurl = "http://www.sec.gov/Archives/" + path + "" + fnnum + "/" + fn.replace('.txt','-index.htm')

                         #print pair # or could be pair[1]
                        regname = line[1]
                        regname = str(''.join(s for s in regname if s in valid_chars)) # remove any tabs, etc.
                        #newfilename = regname + "__" + d[3] + "__" + d[0] + "__" + str(fcnt).zfill(3) + ".htm"

                        # Write to file method
                        #if (newfilename != oldfilename):
                        #    recstring = regname+"|"+d[3]+"|"+d[0] + "|" +d[5] + "|" + newfilename + "\n"
                            #print(pair[2] + '|' + regname+"|"+pair[3]+"|"+pair[0] + "|" +pair[5])

                        #recordList = [regname,d[3],d[2],d[0],d[5],'','']
                        print(line)
                        # CIK, name, form, date, file
                        DataTuple = (regname, line[3],line[2],line[0],nurl,line[4],'')

                        DataFiling.append(DataTuple) # append was just pointer to list

                        #yield line[0] , line[1], line[2], line[3], line[4], nurl
    return DataFiling

#
# Insert into SQL db
#
def SQLInsertFilingsData(DataPathSQLiteDB, connSQLite, DataFiling):

    #tuple_recs = tuple(DataFiling)

    connSQLite = create_connection(DataPathSQLiteDB)

    print(DataPathSQLiteDB)
    #exit()
       
    sql = 'INSERT into EdgarFilings'
    sql = sql + '(RegName,FilingDate,Filetype,CIK,SECFilingIndexURL,MasterFileURL,MasterFileDate)'
    sql = sql + " values (?, ?, ?, ?, ?, ?, ?)"
    #sql = sql + "('" + regname + "',"
    #sql = sql + "'" + pair[3] + "',"
    #sql = sql + "'" + pair[2] + "',"
    #sql = sql + "" + pair[0] + ","
    #sql = sql + "'" + pair[5] + "',"
    #sql = sql + "'" + '' + "',"
    #sql = sql + "'" + '' + "')"

    try:
        print(sql + '\n')
        cursor = connSQLite.cursor()
        cursor.executemany(sql, DataFiling) #!!!! REMEMBER those brackets or weird number of params
        connSQLite.commit()
        cursor.close()
        #cursor.execute(sql)
        #conn.commit()
       

    except: 
        pass
        print("Failed to insert multiple records into sqlite table")

    finally:
        if (connSQLite):
            connSQLite.close()
            print("The SQLite connection is closed")

#sys.exit()


#
#  CALL MAIN
#
if __name__ == '__main__':

    EDGARindexfilesWithPath = getIndexFiles()
    
    print(EDGARindexfilesWithPath)
    
    for fn in EDGARindexfilesWithPath:
        str_fn_withpath = str(fn)
        str_fn = str(Path(fn).name)
        #print(fn)
        #print(str_fn)
        #exit()
        # GET DATE ONLY
        str_fn = str_fn.rstrip('\n')
        yyyymmdd = str_fn.replace('master.','')
        yyyymmdd = yyyymmdd.replace('.idx','')
        #print(yyyymmdd)

        flagRecordExists = True

        # # First check if days filings in database
        # # DO LATER
        
        connSQLite = create_connection(DataPathSQLiteDB)
        try:
            sqlcheck = "Select FilingDate FROM EdgarFilings where [FilingDate] ='" + yyyymmdd + "' LIMIT 1" 
            cursorcheck = connSQLite.cursor()
            cursorcheck.execute(sqlcheck)
            exist = cursorcheck.fetchone()
            cursorcheck.close()
            
            if exist is None:
                flagRecordExists = False
                print('This date NOT in EdgarFilings')
            else:
                flagRecordExists = True
                print('This date in EdgarFilings')
                
        except:
            print("dbCheck Record failure!")
        finally:
            pass

        # have we checked for records
        #exit()
                
                
        # If we date process rante
        if (yyyymmdd >= fromDate and yyyymmdd <= endDate) and flagRecordExists == False:
            DataFiling = get_EDGAR_Fund_Records_From_CSV_file(str_fn_withpath, "|")
            print(DataFiling)
            SQLInsertFilingsData(DataPathSQLiteDB, connSQLite, DataFiling)


        
        
                    

    