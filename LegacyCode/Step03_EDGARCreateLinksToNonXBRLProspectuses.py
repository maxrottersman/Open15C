# Created:     26/02/2013
# Copyright:   (c) Max Rottersman 2013
# Licence:     <your licence>
# DOWNLOAD PROSPECTUS IF NOT XBRL

import requests
import re
from BeautifulSoup import BeautifulSoup
import os
import sys
import glob
import bleach


URLnormal = 'http://www.sec.gov/Archives/edgar/data/838802/000111183013000177/0001111830-13-000177-index.htm'
URLXBRL = 'http://www.sec.gov/Archives/edgar/data/917713//000119312513062155/0001193125-13-062155-index.htm'
EDGAR485BPOSList = 'c:\\Files2013_WebDev\\pyEDGAR\SECIndexes\\485bpos_List20130215.txt'

ScriptPath = os.path.dirname(os.path.realpath(__file__))
SECIndexesPath = ScriptPath + "\\SECIndexes"
SECEdgar485BPOSPath = ScriptPath + "\\SECEdgar485BPOS"

pre = 'http://www.sec.gov/'

sURLFile = ''
sURLFile = SECEdgar485BPOSPath + '\\aURLs.htm'

# LOCAL
#TargetURLdb = 'http://localhost:50768/NetCompSystem/xam/FilingsProspectusesAdd.aspx'
# REMOTE
TargetURLdb = 'http://mpidb.com/xam/FilingsProspectusesAdd.aspx'


# -----------------------
# TestExtract
# -----------------------
def testmain():
    gfl = [] # good file list
    fl = glob.glob(SECIndexesPath + "\\listmaster*.txt")
    for j in fl:
        x1 = j.split('.')
        ############ NOT ALL
        if x1[1] >= '20130601':
            gfl.append(x1[1])

    for fn in gfl:
        file = open(SECIndexesPath + '\\listmaster.'+fn+'.txt', 'r')
        table = [row.strip().split('|') for row in file]
        file.close()

        for myrow in table:
            filename = myrow[4]
            r = requests.get(myrow[3])

            soup = BeautifulSoup(r.text)

            divaccession = soup.find("div", {'id' : 'secNum' })
            if divaccession != None:
                secacckey = ''
                secacckey = divaccession.renderContents()
                secacckey = bleach.clean(secacckey, tags=[], strip=True).strip()
                secacckey = secacckey.replace('SEC Accession No. ','').strip()

                print secacckey

        sys.exit()

# -----------------------
# MAIN
# -----------------------

def main():
    pass

    # Open LINKs page for WRITING LINKS
 #   fURLFile = open(sURLFile,'w')
 #   fURLFile.write("<html><body>" + os.linesep)
 #   fURLFile.write("<table><tr><td>Filing</td><td>Update Database</td>" + os.linesep)

    gfl = [] # good file list
    # Get listmaster file list from folder
    fl = glob.glob(SECIndexesPath + "\\listmaster*.txt")
    #print "\n".join(fl)
    for j in fl:
        x1 = j.split('.')
        ############ NOT ALL
        if x1[1] > '20130328':
            #print x1[1] # date YYYYMMDD
            gfl.append(x1[1])

    for fn in gfl:

        file = open(SECIndexesPath + '\\listmaster.'+fn+'.txt', 'r')
        table = [row.strip().split('|') for row in file]
        file.close()

#        icnt = 1
        for myrow in table:

            filename = myrow[4]


            r = requests.get(myrow[3])

            #
            # Into SOUP!
            #
            soup = BeautifulSoup(r.text)

            table = soup("table", {'class' : 'tableFile' })
            rows = table[0].findAll('tr', limit=2)
            for tr in rows:
                    cols = tr.findAll('td')

            # Get Accession No.
            divaccession = soup.find("div", {'id' : 'secNum' })
            if divaccession != None:
                secacckey = ''
                secacckey = divaccession.renderContents()
                secacckey = bleach.clean(secacckey, tags=[], strip=True).strip()
                secacckey = secacckey.replace('SEC Accession No. ','').strip()

            # Company Name
            if len(cols) > 0:
                    pass
                    #print cols[1].text

                # URL
            s = str(cols[2:3]).strip('[]')
            match = re.search(r'href=[\'"]?([^\'" >]+)', s)
            if match:
                    #print pre + match.group(0)[7:]
                    URLnormal = pre + match.group(0)[7:]

                # print r.headers
                    if 'XBRL INSTANCE' in r.text:
                        pass
                        #print "FOUND XBRL"
                    else:
                        pass
              #          print "NORMAL filing: " + myrow[3]

                # Normal File DOES NOT WORK FOR ALL
                #<td class="CIKname">CIK <a href="/cgi-bin/browse-edgar?action=getcompany&CIK=0001217286">0001217286</a></td>
                #<td class="CIKname">&nbsp;</td>
                        #CIK = soup.find("td",{'class':'CIKname'})
                        #atag = CIK.findNext('a')
                        #print 'dbCIK|'+atag.contents[0]
                        #sCIK = ''
                        #sCIK = atag.contents[0]

                 #<div class="infoHead">Effectiveness Date</div>
                 #<div class="info">2013-01-07</div>
                        sEffectivenessDate = ''
                        sEffectivenessDate = soup.find(text="Effectiveness Date").findNext('div').contents[0]
                        sEffectivenessDate = sEffectivenessDate.replace('-','')
                        #print 'dbEffectivenessDate|' + sEffectivenessDate

                        sFiling = ''
                        el = soup.find("table",{'summary':'Document Format Files'}).find('td',{'scope':'row'})
                        el = el.findNext('td') # Reg name
                        sRegName = ''
                        if el.length > 0:
                            sRegName = el.contents[0]
                        el = el.findNext('td')
                        el = el.findNext('a') # Main filing URL
                        s = str(el)
                        start = s.find('/Archives') #+ 3
                        end = s.find('>', start)
                        sURL = s[start:end-1]
                        el = el.findNext('td') # File Size
                        el = el.findNext('td')
                        filesize = el.contents[0]

              #          print 'dbFiling|' + s[start:end-1]+ '|' + filesize

#<span class="companyName">
                        el = soup.find("span",{'class':'companyName'})
                        if sRegName == '':
                            sRegName = el.contents[0]
                        sRegName = sRegName.replace(' (Filer)','').strip()

 #<span class="companyName">FIRST TRUST COMBINED SERIES 297 (Filer)
                        #<acronym title="Central Index Key">CIK</acronym>: <a href="/cgi-bin/browse-edgar?CIK=0001471540&amp;action=getcompany">0001471540 (see all company filings)</a></span>
                        sCIK = ''
                        el = el.findNext('a')
                        sCIK = str(el.contents[0])
                        sCIK = sCIK.replace(' (see all company filings)','')
               #         print "sCIK is: " + sCIK

                        # For URL links file
               #        print pre + s[start:end-1]
               #         print filesize
               #         print sRegName
               #         print sCIK
               #         print sEffectivenessDate.replace('-','')

                        # -----------------
                        # Write to database
                        # -----------------
                        # Filing|EffectiveDate|Size|CIK|Regname
                        # http://localhost:50768/NetCompSystem/Editor/TrusteeSectionsAdd2013.aspx
                        sParam = ''
                        sParam = pre + sURL + '|' + sEffectivenessDate + '|' + filesize + '|' + sCIK + '|' + sRegName + "|" + secacckey
                        payload = {'d': sParam}
                        webpost = requests.get(TargetURLdb, params=payload)
                        print TargetURLdb + sParam
                        #print webpost.url
                       # sys.exit()

                        # Convert with 000s commas
                        filesize = format(int(filesize), ",d")
 #                       fURLFile.write('<tr><td>')
                        #fURLFile.write('Filing page:' + myrow[3] + "</br>" + os.linesep)


#                        fURLFile.write('<a href="' + pre + sURL + '">'+sRegName + ' Size: ' + filesize + "</a></br>" + os.linesep)
#                        fURLFile.write('</td><td>')
#                        fURLFile.write('<a href="' + TargetURL + '?CIK=' + sCIK)
#                        fURLFile.write('&effectivedate=' + sEffectivenessDate)
#                        fURLFile.write('&regname=' + sRegName)
#                        fURLFile.write('&URLSource=' + pre + sURL)
#                        fURLFile.write('">Update ' +sCIK+"</a></td>")
#                        fURLFile.write('<td>' +sEffectivenessDate+"</td>")
#                        fURLFile.write("</tr>" + os.linesep)




                        rows = soup.findAll("tr")

                        for myrow in rows:
                                    delimstr = ''

                                    for td in myrow.findAll("td"):
                                        delimstr =  delimstr + "|" + td.text


                                    if delimstr.find('Class') > 0 or delimstr.find('Series') > 0 or delimstr.find('485BPOS') > 0: #1==1: #
                                            #nothing
                                        pass
                                    else:
                                        delimstr = ''

                                    if delimstr.find('Class') > 0:
                                        delimstr = 'dbClass' + delimstr

                                    if delimstr.find('Series') > 0:
                                        delimstr = 'dbSeries' + delimstr

                                    if delimstr.find('485BPOS') > 0:
                                        delimstr = 'dbFile' + delimstr


                                    if delimstr != '':
                                        pass
                                   #     print delimstr

       #     icnt += 1
 #   fURLFile.write("</table></html></body>" + os.linesep)
 #   fURLFile.close()
  #          if icnt > 15:
  #              sys.exit()

if __name__ == '__main__':
    #testmain()
    main()

