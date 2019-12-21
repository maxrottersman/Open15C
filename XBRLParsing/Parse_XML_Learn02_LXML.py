from lxml import etree
import os
from os import path
from io import StringIO, BytesIO
import re

fn = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\alger_n_cen.xml'
fn_xslt = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\strip_namespace.xsl'
fn_cleaned = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\alger_n_cen_clean.xml'

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

# # ALL TAGS
# for tag in tree.iter():
#     if not len(tag):
#         print(tag.tag," | ",tag.text)


showTags = False

for tag in tree.iter():
#root = etree.Element("managementInvestmentQuestionSeriesInfo")
    # Didn't work because tags with no data/attributs are 0, which the fund sections are
    #if not len(tag):
        if tag.tag == 'managementInvestmentQuestion':
            showTags = True
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
            
#print(registrantFullName)

# for node in root:
#     print(node.tag)
#     for c in enumerate(node):
#         print(c[1].tag)

