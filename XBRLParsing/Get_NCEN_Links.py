
from bs4 import BeautifulSoup
from urllib.request import urlopen
import sqlite3
from sqlite3 import Error

url = 'https://www.sec.gov/Archives/edgar/data/1111178/000111117819000001/0001111178-19-000001-index.htm'
url = 'https://www.sec.gov/Archives/edgar/data/1141819/000089418919000011/0000894189-19-000011-index.htm' #48bpos


soup = BeautifulSoup(html, 'html.parser')

dbstr = r'C:\Files2020_Dev\ByProject\Open15C_DataOnly\SECedgar.sqlite'

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

# Retrieve all of the anchor tags
def get_XML_url(url):
    html = urlopen(url).read()
    tags = soup('a')
    for tag in tags:
        # If .xml in both url AND file name
        if ".xml".lower() in tag.get('href',None).lower() and ".html".lower() not in str(tag).lower():
            # not if xml link files
            if not any(x in str(tag).lower() for x in ('_def','_lab','_cal','_pre')):
                #print('TAG:', tag)
                print('URL:', tag.get('href', None))
                #print('Contents:', tag.contents[0])
                #print('Attrs:', tag.attrs)
    return tag.get('href', None)

if __name__ == '__main__':
    # Get file links from Edgar_filings into List
    # Go through list and get XML_url
        # need to add ID to table...
        # then insert into table
    pass