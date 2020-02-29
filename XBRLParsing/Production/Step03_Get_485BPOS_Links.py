
from bs4 import BeautifulSoup
from urllib.request import urlopen
import sqlite3
from sqlite3 import Error
import pandas as pd

# For testing
url = 'https://www.sec.gov/Archives/edgar/data/1111178/000111117819000001/0001111178-19-000001-index.htm'
url = 'https://www.sec.gov/Archives/edgar/data/1141819/000089418919000011/0000894189-19-000011-index.htm' #48bpos

lSECFilingsIndexURLs = [] # make this global

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
# Get records
#
def dbLoad_lSECFilingsIndexURLs(connSQLite):
    
    sql = "Select ID, SECFilingIndexURL FROM EdgarFilings WHERE "
    sql = sql + "FileType like '485BPOS%';"
    df = pd.read_sql_query(sql, connSQLite)
    return df    

# Retrieve all of the anchor tags
def get_XML_url(url):
    html = urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    tags = soup('a')
    XMLfile = ''
    for tag in tags:
        # If .xml in both url AND file name
        if ".xml".lower() in tag.get('href',None).lower() and ".html".lower() not in str(tag).lower():
            # not if xml link files
            if not any(x in str(tag).lower() for x in ('_def','_lab','_cal','_pre')):
                #print('TAG:', tag)
                #print('URL:', tag.get('href', None))
                XMLfile = tag.get('href',None)
                #print('Contents:', tag.contents[0])
                #print('Attrs:', tag.attrs)
    return XMLfile

if __name__ == '__main__':
    dbstr = r'C:\Files2020_Dev\ByProject\Open15C_Data\SECedgar.sqlite'
    connSQLite = create_connection(dbstr)
    df = dbLoad_lSECFilingsIndexURLs(connSQLite)
    cnt = 1
    for index, row in df.iterrows():
        #print(row[0])
        #print(row[1])
        XMLFile = 'http://www.sec.gov' + get_XML_url(row[1])
        sql = """UPDATE EdgarFilings SET XMLFile = ? WHERE ID = ?"""
        data = (XMLFile, row[0])
        cursor = connSQLite.cursor()
        cursor.execute(sql,data)
        connSQLite.commit()
        cursor.close()

        cnt += 1
        print(cnt)
        #if cnt > 3:
        #    break
    #print(df.head())
     
    # Get file links from Edgar_filings into List
    # Go through list and get XML_url
        # need to add ID to table...
        # then insert into table
    