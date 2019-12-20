from bs4 import BeautifulSoup
import re

fn = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\alger_n_cen.xml'
fn_xsl = r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\strip_namespace.xsl'

soup = BeautifulSoup(open(r'C:\Files2020_Dev\ByProject\Open15c\XBRLParsing\alger_n_cen.xml'), 'lxml')


for paragraph in soup.find_all('fileNumberInfo'):
    print(paragraph.string)
    print(str(paragraph.text))

