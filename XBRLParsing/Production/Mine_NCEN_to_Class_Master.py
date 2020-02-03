from lxml import etree
import os
from os import path
from io import StringIO, BytesIO
import re

import sqlite3
from sqlite3 import Error

fn = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\alger_n_cen.xml'
fn_xslt = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\strip_namespace.xsl'
fn_cleaned = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\alger_n_cen_clean.xml'

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

def prepareXML():
    # ONLY IF WE HAVE NOT ARLEADY PROCESSED
    if path.exists(fn_cleaned):
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
    
    tree = etree.parse(fn_cleaned)
    root = tree.getroot()
    print(root.tag)

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
                        print('*** START FUND SECTION ***')
                    if len(tag.text) > 0 and len(tagchildren) == 0:
                        print(tag.tag.strip(),"|",tag.text.strip()) #,end='')
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

def create_dataForfields():    

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
    0]

    return dataForFields

def NCEN_to_dataForFields(tree, sqlFields, dataForFields):
    connSQLite = create_connection(dbstr)
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
                        print('*** START FUND SECTION ***')
                        dataForFieldsTemp = create_dataForfields() # List for data
                    if len(tag.text) > 0 and len(tagchildren) == 0:
                        for i,f in enumerate(sqlFields):
                            if tag.tag.strip() == f:
                                dataForFieldsTemp[i] = tag.text.strip()

                        #print(tag.tag.strip(),"|",tag.text.strip()) #,end='')
                        #if tag.tag == 'brokers':
                    if tag.tag == 'isSwingPricing':
                        for f in dataForFieldsTemp:
                            pass
                            # print out values
                            #print(f)
                        # save to database
                        print(len(dataForFieldsTemp))
                        connSQLite.executemany('INSERT INTO Extract_NCEN VALUES \
                            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', [dataForFieldsTemp])
                        connSQLite.commit()
            
if __name__ == '__main__':
    tree = prepareXML()
    #walkNCEN(tree)
    sqlFields = create_SQLfields()
    #print(SQLFields[3])
    dataForFields = create_dataForfields()
    #dataForFields[3] = "max"
    #print(dataForFields[3])
    NCEN_to_dataForFields(tree, sqlFields, dataForFields)


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

