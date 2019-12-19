from bs4 import BeautifulSoup
import lxml
import re
import xml.etree.ElementTree as ET 

# lxml, html.parser
#soup = BeautifulSoup(open(r'C:\Users\user\OneDrive\PythonScripts\XBRL_ParsingExperiments\tmf-20190228.xml'), 'lxml')
#tag_list = soup.find_all()
 # create element tree object 
tree = ET.parse(open(r'C:\Users\user\OneDrive\PythonScripts\XBRL_ParsingExperiments\tmf-20190228.xml')) 
# get root element 
root = tree.getroot() 
# create empty list for news items 
    # iterate news items 
i = 1
for item in root.findall(): 
    i = i + 1
        
print(i)