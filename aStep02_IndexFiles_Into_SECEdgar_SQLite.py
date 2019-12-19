# Created:     22/02/2013
# Copyright:   (c) Max Rottersman 2013
# Licence:     <your licence>
# PARSES EDGAR INDEX FILE AND COPIES 485BPOS ENTERIES WITH NEW FILENAMES TO USE FOR PROSPECTUSES
# INTO listmaster.YYYYDDYY.txt

import csv
import os
from os import listdir
import sys
import string
import re

import sqlite3
from sqlite3 import Error

dbstr = r'C:\ff_factory2019\pyEDGAR\db\SECedgar.sqlite'

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

ScriptPath = os.path.dirname(os.path.realpath(__file__))
SECIndexesPath = ScriptPath + "\\SECIndexes"

# --------- CONFIG --------------
fromDate = '20190101' # will be greater-than or equl
endDate = '20190105'
# 48BPOS, NSAR and N1A
FileTypeFunds = [r'485bpos' ,r'485bpos/a',r'485apos',r'485apos/a',r'nsar-a',r'nsar-a/a', r'nsar-b',r'nsar-b/a',r'n-1a',r'n-1a/a',r'n-cen']
# -------------------------------
valid_chars = '-_., abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

sfilename = 'master.20130215.idx'
EDGAR485BPOSListfilename = 'List20130215.txt'
SECIndexesPath = ScriptPath + "\\SECIndexes"
filenamewithpath = SECIndexesPath + "\\aLatestIndexes.txt"

def getIndexFiles():
     # Read in current index list from aLatestIndex.txt
    global EDGARindexfiles
    
    #with open(SECIndexesPath + "\\aLatestIndexes.txt") as f:
    #    EDGARindexfiles = f.readlines()
    # USE read files method
    #print(SECIndexesPath)
    EDGARindexfiles = [file for file in listdir(SECIndexesPath) if file.endswith('.idx')]
    #print(EDGARindexfiles)

def get_EDGAR_Fund_Records_From_CSV_file(filename, separator):
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

                        # CIK, name, form, date, file
                        yield line[0] , line[1], line[2], line[3], line[4], nurl


#
#  CALL MAIN
#
if __name__ == '__main__':

    getIndexFiles()
    #exit
    connSQLite = create_connection(dbstr)

    global newfilename 
    global oldfilename 
    
    newfilename = ''
    oldfilename = ''
    # master.20190103.idx # maybe, for testing
    for fn in EDGARindexfiles:
        fn = fn.rstrip('\n')
        yyyymmdd = fn.replace('master.','')
        yyyymmdd = yyyymmdd.replace('.idx','')

        #print(yyyymmdd)
        flagRecordExists = True

        # # First check if days filings in database
        # # DO LATER
        try:
            sqlcheck = "Select FilingDate FROM EdgarFilings where [FilingDate] ='" + yyyymmdd + "' LIMIT 1" 
            cursorcheck = connSQLite.cursor()
            cursorcheck.execute(sqlcheck)
            exist = cursorcheck.fetchone()
            
            if exist is None:
                flagRecordExists = False
            else:
                flagRecordExists = True
                
        except:
                print("dbCheck Record failure!")
        finally:
                cursorcheck.close()
                #cursorcheck.close()
                #conncheck.close()

        # If we date process rante
        if (yyyymmdd >= fromDate and yyyymmdd <= endDate) and flagRecordExists == False:

            if os.path.isfile(SECIndexesPath + "\\" + fn):
                #print yyyymmdd
                #print fn
                #print(SECIndexesPath + "\\" +fn)
                #exit
                fcnt = 1
                for pair in get_EDGAR_Fund_Records_From_CSV_file(SECIndexesPath + "\\" +fn, '|'):
                    #print pair # or could be pair[1]
                    regname = pair[1]
                    regname = str(''.join(s for s in regname if s in valid_chars)) # remove any tabs, etc.
                    #regname = regname.encode('ascii', 'ignore')
                    #regname = regname.translate(None, "',!.;&//()")
                    # thare are dups in SEC data, so check for it and don't write
                    newfilename = regname + "__" + pair[3] + "__" + pair[0] + "__" + str(fcnt).zfill(3) + ".htm"

                    # Write to file method
                    if (newfilename != oldfilename):
                        recstring = regname+"|"+pair[3]+"|"+pair[0] + "|" +pair[5] + "|" + newfilename + "\n"
                        #f.write(regname+"|"+pair[3]+"|"+pair[0] + "|" +pair[5] + "|" + newfilename + "\n")
                        print(pair[2] + '|' + regname+"|"+pair[3]+"|"+pair[0] + "|" +pair[5])
                        sql = 'INSERT into EdgarFilings '
                        sql = sql + '([RegName],[FilingDate],[Filetype],[CIK],[SECFilingIndexURL],[MasterFileURL],[MasterFileDate]) VALUES '
                        sql = sql + "('" + regname + "',"
                        sql = sql + "'" + pair[3] + "',"
                        sql = sql + "'" + pair[2] + "',"
                        sql = sql + "" + pair[0] + ","
                        sql = sql + "'" + pair[5] + "',"
                        sql = sql + "'" + '' + "',"
                        sql = sql + "'" + '' + "')"

                        try:
                            print(sql + '\n')
                            cursor = connSQLite.cursor()
                            cursor.execute(sql)
                            connSQLite.commit()
                            cursor.close()
                            #cursor.execute(sql)
                            #conn.commit()

                        except:
                            pass
                            #cursor.close()
                            #conn.close()

                        finally:
                            pass

                    oldfilename = newfilename
                    #sys.exit()
                
                fcnt += 1
            
                    

    