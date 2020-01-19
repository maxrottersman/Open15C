from lxml import etree
import os
from os import path
from io import StringIO, BytesIO
import re

import sqlite3
from sqlite3 import Error

fn = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\fmagx.xml'
fn_xslt = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\strip_namespace.xsl'
fn_cleaned = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\fmagx_clean.xml'

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
    if not path.exists(fn_cleaned):
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
    
    tree = etree.parse(fn_cleaned,etree.XMLParser(encoding='ISO-8859-1', ns_clean=True, recover=True))
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
    # 
        if not tag.get("contextRef") is None:
            if str.startswith(tag.get("contextRef"), "S0"):
                saveElem = tag.tag
                saveValue = tag.text
                saveAttrib = tag.get("contextRef")     # 21 for series/class
                saveSeries_Class = tag.get("contextRef")[:21]

                print(saveElem + "|" + saveValue + "|" + saveAttrib + "|" + saveSeries_Class)
   

            
if __name__ == '__main__':
    tree = prepareXML()
    walk485BPOS(tree)
    


