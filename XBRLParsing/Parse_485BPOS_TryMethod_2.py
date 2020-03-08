from lxml import etree
import os
from os import path
from io import StringIO, BytesIO
import re

import sqlite3
from sqlite3 import Error

# TESTING
#fn = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\fmagx.xml'
#fn = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\ftetfiv-20181231.xml'
fn = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\mmsf-20190201.xml'
fn_xslt = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\strip_namespace.xsl'
#fn_cleaned = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\fmagx_clean.xml'
fn_cleaned = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\fn_cleaned.xml'

dbstr = r'C:\Files2020_Dev\ByProject\Open15C_DataOnly\sqlite\SECedgar.sqlite'

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

def prepareXML():
    # ONLY IF WE HAVE NOT ARLEADY PROCESSED
    # _cleaned
    if path.exists(fn):
        # Loading XML with Namespace (ns)
        tree = etree.parse(fn)
        # Mary it to XSLT that will remove ns
        xslt = etree.parse(fn_xslt)

        # Apply XSLT
        tree_without_namespace = tree.xslt(xslt)

        # Now we can built string of clean XML
        # UTF-8

        CleanXMLDoc = (etree.tostring(tree_without_namespace, pretty_print=True, xml_declaration=True, 
            encoding="UTF-8").decode("UTF-8"))

        # OUTPUT RESULT TREE TO FILE
        with open(fn_cleaned, 'w') as f:
            f.write(CleanXMLDoc)
    
    #tree = etree.parse(fn_cleaned,etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))
    tree = etree.parse(fn_cleaned,etree.XMLParser(encoding='ISO-8859-1', ns_clean=True, recover=True))
    #magical_parser = etree.XMLParser(encoding='utf-8', recover=True)
    #tree = etree.parse(fn_cleaned,magical_parser)
    #root = tree.getroot()
    #print(root.tag)

    return tree

# # ALL TAGS
# for tag in tree.iter():
#     if not len(tag):
#         print(tag.tag," | ",tag.text)

def walk485BPOS(tree):

    for tag in tree.iter():

    # tag is the element name
    # tag.get("attribute name")
    # tag.keys() returns list of attributes
    # tag.items() returns name, value pair
    # str(tag.keys()) returns attribute keys
    # str(tag.items()) key/values of attributes
    # str(tag.items()[0][1]) First value of attributes
    # 
        #print(str(tag.tag))
        if str(tag.tag).lower() == 'ManagementFeesOverAssets'.lower():
            saveAttrib = ''
            saveSeries_Class = ''
            SECClass = ''
            SECSeries = ''
            
            ElemFirstAttribute = str(tag.items()[0][1])
            SECClass = str(re.findall(r'C\d{9}',ElemFirstAttribute)[0]) # Works
            SECSeries = str(re.findall(r'S\d{9}',ElemFirstAttribute)[0]) # Works
            
            saveElem = tag.tag
            saveValue = tag.text
            #saveAttrib = tag.get("contextRef")     # 21 for series/class
            #saveSeries_Class = tag.get("contextRef")[:21]
            #prefix = saveSeries_Class.split("_")[0]
            #suffix = saveSeries_Class.split("_")[1]
            # Don't need this data now: "|" + saveAttrib +
            print(SECSeries + "|" + SECClass + "|" + saveElem + "|" + saveValue +  "\r")

            
if __name__ == '__main__':
    tree = prepareXML()
    walk485BPOS(tree)
    

