from bs4 import BeautifulSoup
import lxml
import re

# lxml, html.parser
soup = BeautifulSoup(open(r'C:\Users\user\OneDrive\PythonScripts\XBRL_ParsingExperiments\tmf-20190228.xml'), 'lxml')
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
    #rr:ExpensesOverAssets

    if tag.name == 'rr:managementfeesoverassets':
        #print('MgmtFees: ' + tag.name + 'text ' + tag.text)
        #print(tag.attrs)
        contextref =''
        contextref =tag.attrs.get('contextref')
        print(contextref)
        MemberStart = contextref.find('MemberC')
        print(MemberStart)
        SECSeriesNum = contextref[MemberStart-11:MemberStart-1]
        SECClassNum = contextref[MemberStart+6:MemberStart+16]
        print(SECSeriesNum)
        print(SECClassNum)


    if tag.name == 'rr:expensesoverassets':
        print('ExpensesOverAssets: ' + tag.name + 'text ' + tag.text)
        #print(tag.attrs)
        
        
            

    #print(tag.name)
    #x = x + 1
    #if (x > 10):
    #    exit
    #if tag.name == 'identifier':
    #    print('Identifier: ' + tag.text)