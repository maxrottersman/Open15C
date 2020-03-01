from lxml import etree
import os
from os import path
from io import StringIO, BytesIO
import re
import pandas as pd

import sqlite3
from sqlite3 import Error

from urllib.request import urlopen

fn = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\fmagx.xml'
fn_xslt = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\strip_namespace.xsl'
fn_cleaned = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\fmagx_clean.xml'

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
    
    sql = "Select ID, XMLFile, FilingDate FROM EdgarFilings WHERE "
    sql = sql + "(FileType = '485BPOS' or FileType = '485BPOS/A') and XMLFile <> '' "
    sql = sql + "and FilingDate >= '" + fromDate +"' and FilingDate <= '" + toDate + "';"
    df = pd.read_sql_query(sql, connSQLite)
    return df  

def create_GetFieldsList():
    
    GetFieldsList = set([ \
    'annualreturn2009', \
    'annualreturn2010', \
    'annualreturn2011', \
    'annualreturn2012', \
    'annualreturn2013', \
    'annualreturn2014', \
    'annualreturn2015', \
    'annualreturn2016', \
    'annualreturn2017', \
    'annualreturn2018', \
    'averageannualreturnyear01', \
    'averageannualreturnyear01', \
    'averageannualreturnyear05', \
    'averageannualreturnyear05', \
    'averageannualreturnyear10', \
    'averageannualreturnyear10', \
    'distributionandservice12b1feesoverassets', \
    'expensesoverassets', \
    'managementfeesoverassets', \
    'otherexpensesoverassets', \
    'portfolioturnoverrate', \
    'shareholderfeeother', \
    '9z'])
       
    return GetFieldsList

def prepareXML(url):

    with urlopen(url) as f:
        tree = etree.parse(f)

        # Mary it to XSLT that will remove ns
        xslt = etree.parse(fn_xslt)

        # Apply XSLT
        tree_without_namespace = tree.xslt(xslt)

        # Now we can built string of clean XML
        # UTF-8

        CleanXMLDoc = (etree.tostring(tree_without_namespace, pretty_print=True, xml_declaration=True, 
            encoding="UTF-8").decode("UTF-8"))

        # OUTPUT RESULT TREE TO FILE
        with open(fn_cleaned, 'w', encoding="utf-8") as f:
            f.write(CleanXMLDoc)
    
    tree = etree.parse(fn_cleaned,etree.XMLParser(encoding='ISO-8859-1', ns_clean=True, recover=True))
    #root = tree.getroot()
    #print(root.tag)

    return tree

# # ALL TAGS
# for tag in tree.iter():
#     if not len(tag):
#         print(tag.tag," | ",tag.text)

def walk485BPOS(FilingDate, FileName, tree, GetFieldsList):
    connSQLite = create_connection(dbstr)

    # List of data we'll add to SQL TABLE
    # Series, Class, XMLFieldName, StringValue, FilingDate, FileName
    dataForFields = [ \
    '', \
    '', \
    '', \
    '', \
    '', \
    '']

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

                if len(saveElem) > 9:
                    connSQLite.executemany('INSERT INTO Extract_485BPOS VALUES \
                            (?,?,?,?,?,?)', [dataForFields])
                    connSQLite.commit()
        
if __name__ == '__main__':
    connSQLite = create_connection(dbstr)
    fromDate = "20190101"
    toDate = "20190131"
    df = dbLoad_485BPOS_Records(connSQLite, fromDate, toDate)

    GetFieldsList = create_GetFieldsList()

    for index, row in df.iterrows():
        if len(str(row[1])) > 20:
            print("Begin Parse " + str(index) + " " + str(row[1]) + " " + str(row[2]))
            tree = prepareXML(row[1])
            #NCEN_to_dataForFields(tree, sqlFields, dataForFields, row[2])
            walk485BPOS(row[2], row[1], tree, GetFieldsList)

    
    


