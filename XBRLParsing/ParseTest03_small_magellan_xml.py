from bs4 import BeautifulSoup
import lxml
import re

# lxml, html.parser
soup = BeautifulSoup(open(r'C:\Users\user\OneDrive\PythonScripts\XBRL_ParsingExperiments\fmagx.xml'), 'lxml')
tag_list = soup.find_all()
# re.compile("^r") # tags that begin with r
print(len(tag_list))
x = 1

# for item in soup.select("[contextref^='Duration']"):
#     print(item.tag)
#     x = x + 1
#     if (x > 10):
#         exit

for tag in tag_list:

    # if tag.name == 'rr:ExpensesOverAssets':
    #     print('MgmtFees: ' + tag.name + 'text ' + tag.text)

    print(tag.name + ' |  ' + tag.text + '\n')  

    if tag.name == 'rr:managementfeesoverassets':
        print('MgmtFees: ' + tag.name + 'text ' + tag.text)    

    #print(tag.name)
    #x = x + 1
    #if (x > 10):
    #    exit
    #if tag.name == 'identifier':
    #    print('Identifier: ' + tag.text)