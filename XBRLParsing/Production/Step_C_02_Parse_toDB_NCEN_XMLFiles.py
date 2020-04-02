from lxml import etree
import os
from os import path
from io import StringIO, BytesIO
import re
import pandas as pd

import sqlite3
from sqlite3 import Error

from urllib.request import urlopen

fn = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\alger_n_cen.xml'
fn_xslt = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\strip_namespace.xsl'
fn_cleaned = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\tempcleaned.xml'

Folders_NCEN = r'D:\Files2020_Data\Folders_NCEN'

dbstr = r'C:\Files2020_Dev\ByProject\Open15C_Data\SECedgar.sqlite'
dbstr_NCEN = r'C:\Files2020_Dev\ByProject\Open15C_Data\SEC_FlatNCEN.sqlite3'


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
        pass
        #print(e)
 
    return conn

def dbLoad_NCEN_Records(connSQLite, fromDate, toDate):
    
    sql = "Select ID, SECFilingIndexURL, XMLFile, FilingDate FROM EdgarFilings WHERE "
    sql = sql + "(FileType = 'N-CEN' or FileType = 'N-CEN/A') and XMLFile <> '' "
    sql = sql + "and FilingDate >= '" + fromDate +"' and FilingDate <= '" + toDate + "';"
    df = pd.read_sql_query(sql, connSQLite)
    return df    

def prepareXML(XMLPathAndFile):
    #parser = etree.HTMLParser()
    tree = etree.parse(XMLPathAndFile)
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
    
    tree = etree.parse(fn_cleaned)
    root = tree.getroot()
    #print(root.tag)

    return tree

# # ALL TAGS
# for tag in tree.iter():
#     if not len(tag):
#         print(tag.tag," | ",tag.text)

def walkNCEN(tree):
    showTags = False

    for tag in tree.iter():
    #root = etree.Element("managementInvestmentQuestionSeriesInfo")
        # Didn't work because tags with no data/attributs are 0, which the fund sections are
        #if not len(tag):
            if tag.tag == 'managementInvestmentQuestion':
                showTags = True
                # Init vars
                
            if tag.tag == 'attachmentsTab':
                showTags = False

            # if tag.tag == '':
            #     FoundSubTags = True
            #     else:
            #         FoundSubTags = False

            if showTags == True:
                tagparent = tag.getparent()
                tagchildren = tag.getchildren()
                
                #print(tag.getparent())
                #if tag.getparent().tag.tostring().text == 'managementInvestmentQuestion' 
                
                if tagparent.tag == 'managementInvestmentQuestion':
                    if tag.tag == 'mgmtInvFundName':
                        pass
                        #print('*** START FUND SECTION ***')
                    if len(tag.text) > 0 and len(tagchildren) == 0:
                        pass
                        #print(tag.tag.strip(),"|",tag.text.strip()) #,end='')
                        #if tag.tag == 'brokers':

def create_SQLfields():
    
    sqlFields = ( \
    'mgmtInvFundName', \
    'mgmtInvSeriesId', \
    'mgmtInvLei', \
    'isFirstFilingByFund', \
    'numAuthorizedClass', \
    'numAddedClass', \
    'numTerminatedClass', \
    'fundType', \
    'isNonDiversifiedCompany', \
    'isForeignSubsidiary', \
    'isFundSecuritiesLending', \
    'didFundLendSecurities', \
    'paymentToAgentManagerType', \
    'avgPortfolioSecuritiesValue', \
    'netIncomeSecuritiesLending', \
    'relyOnRuleType', \
    'isExpenseLimitationInPlace', \
    'isExpenseReducedOrWaived', \
    'isFeesWaivedRecoupable', \
    'isExpenseWaivedRecoupable', \
    'isTransferAgentHiredOrTerminated', \
    'isPricingServiceHiredOrTerminated', \
    'isCustodianHiredOrTerminated', \
    'isShareholderServiceHiredTerminated', \
    'isAdminHiredOrTerminated', \
    'aggregateCommission', \
    'principalAggregatePurchase', \
    'isBrokerageResearchPayment', \
    'mnthlyAvgNetAssets', \
    'hasLineOfCredit', \
    'isInterfundBorrowing', \
    'isSwingPricing', \
    '')
        
    return sqlFields

def create_dataForfields(FilingDate):    

    dataForFields = [ \
    '', \
    '', \
    '', \
    '', \
    0, \
    0, \
    0, \
    '', \
    '', \
    '', \
    '', \
    '', \
    '', \
    '', \
    '', \
    '', \
    '', \
    '', \
    '', \
    '', \
    '', \
    '', \
    '', \
    '', \
    '', \
    0, \
    0, \
    '', \
    0, \
    '', \
    '', \
    '', \
    FilingDate]

    return dataForFields

def NCEN_to_dataForFields(tree, sqlFields, dataForFields, FilingDate):
    connSQLite = create_connection(dbstr_NCEN)
    showTags = False

    for tag in tree.iter():
    #root = etree.Element("managementInvestmentQuestionSeriesInfo")
        # Didn't work because tags with no data/attributs are 0, which the fund sections are
        #if not len(tag):
            if tag.tag == 'managementInvestmentQuestion':
                showTags = True
                # Init vars
                
            if tag.tag == 'attachmentsTab':
                showTags = False

            # if tag.tag == '':
            #     FoundSubTags = True
            #     else:
            #         FoundSubTags = False

            if showTags == True:
                tagparent = tag.getparent()
                tagchildren = tag.getchildren()
                
                #print(tag.getparent())
                #if tag.getparent().tag.tostring().text == 'managementInvestmentQuestion' 
                
                if tagparent.tag == 'managementInvestmentQuestion':
                    if tag.tag == 'mgmtInvFundName':
                        #print('*** START FUND SECTION ***')
                        dataForFieldsTemp = create_dataForfields(FilingDate) # List for data
                    if len(tag.text) > 0 and len(tagchildren) == 0:
                        for i,f in enumerate(sqlFields):
                            if tag.tag.strip() == f:
                                dataForFieldsTemp[i] = tag.text.strip()

                        #print(tag.tag.strip(),"|",tag.text.strip()) #,end='')
                        #if tag.tag == 'brokers':
                    if tag.tag == 'isSwingPricing' or tag.tag == 'isInterfundBorrowing':
                        #for f in dataForFieldsTemp:
                            #pass
                            # print out values
                            #print(f)
                        # save to database
                        #print(len(dataForFieldsTemp))
                        connSQLite.executemany('INSERT INTO Extract_NCEN VALUES \
                            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', [dataForFieldsTemp])
                        connSQLite.commit()
            
if __name__ == '__main__':
    connSQLite = create_connection(dbstr)
    fromDate = "20190401"
    toDate = "20200331"
    df = dbLoad_NCEN_Records(connSQLite, fromDate, toDate)
    #print(df)

    for index, row in df.iterrows():
        print("Begin Parse " + str(index) + " " + str(row[1]))
         # folder html file for parsing out ACCESSION NUMBER For folder name
        SECFilingIndexURL = str(row[1])
        head, tail = os.path.split(SECFilingIndexURL)
        CreateFolderName = tail.replace('-index.htm','')

        # URL to our XML file
        XMLFileURL = str(row[2])
        head_XML, tail_XML = os.path.split(XMLFileURL)
        XMLlocalFolder = Folders_NCEN + "\\" + str(CreateFolderName) #+ "\\" + tail_XML
        XMLPathAndFile = XMLlocalFolder + r'\\' + tail_XML


        tree = prepareXML(XMLPathAndFile)
        sqlFields = create_SQLfields()
        dataForFields = create_dataForfields(row[2])
        NCEN_to_dataForFields(tree, sqlFields, dataForFields, row[2])


#print(registrantFullName)

# for node in root:
#     print(node.tag)
#     for c in enumerate(node):
#         print(c[1].tag)

## FROM PYTHON DOCS
# # Do this instead
# t = ('RHAT',)
# c.execute('SELECT * FROM stocks WHERE symbol=?', t)
# print c.fetchone()

# # Larger example that inserts many records at a time
# purchases = [('2006-03-28', 'BUY', 'IBM', 1000, 45.00),
#              ('2006-04-05', 'BUY', 'MSFT', 1000, 72.00),
#              ('2006-04-06', 'SELL', 'IBM', 500, 53.00),
#             ]
# c.executemany('INSERT INTO stocks VALUES (?,?,?,?,?)', purchases)

