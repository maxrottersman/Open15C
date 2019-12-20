from lxml import etree
import os
from io import StringIO, BytesIO
import re

fn = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\alger_n_cen.xml'

# Loading XML with Namespace (ns)
tree = etree.parse(fn)
# Mary it to XSLT that will remove ns
xslt = etree.parse(r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\strip_namespace.xsl')

# Apply XSLT
tree_without_namespace = tree.xslt(xslt)

# Now we can built string of clean XML
# UTF-8

CleanXMLDoc = (etree.tostring(tree_without_namespace, pretty_print=True, xml_declaration=True, 
    encoding="UTF-8").decode("UTF-8"))

# Change tree to clean XML
myparser = etree.HTMLParser(encoding="utf-8")
tree = etree.HTML(CleanXMLDoc,myparser)

for e in tree:
    print(e.tag)


