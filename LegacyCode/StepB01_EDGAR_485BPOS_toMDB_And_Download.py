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
import pyodbc

# -------------------------------
fromDate = '20130430' # will be greater-than or equl
endDate = '20130530'
# --------- CONFIG --------------
FileSizeMinForDownload = 10
# -------------------------------

URLnormal = ''#'http://www.sec.gov/Archives/edgar/data/838802/000111183013000177/0001111830-13-000177-index.htm'
URLXBRL = ''#'http://www.sec.gov/Archives/edgar/data/917713//000119312513062155/0001193125-13-062155-index.htm'
EDGAR485BPOSList = ''#'c:\\Files2013_WebDev\\pyEDGAR\SECIndexes\\485bpos_List20130215.txt'

sMDF = 'C:\\Files2013_EDGARFilings\\archdb.mdb'

ScriptPath = os.path.dirname(os.path.realpath(__file__))
SECIndexesPath = ScriptPath + "\\SECIndexes"
SECEdgar485BPOSPath = ScriptPath + "\\SECEdgar485BPOS"
# Change to hardcode local separate path
SECEdgar485BPOSPath = 'C:\\Files2013_EDGARFilings\\SECEdgar485BPOS'
DownloadPath = 'C:\\Files2013_EDGARFilings\\SECEdgar485BPOS'

valid_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

pre = 'http://www.sec.gov/'

def main():
    SECPath =''
    SECYYYYMMDD = ''
    PhysYYYYMMDD =''
    PhysYYYYMMDDaccno = ''

    s_accnosecurl = ''
    s_physpath = ''
    s_archpath =''
    s_filename =''
    s_accno = ''
    i_CIK = ''
    s_FormType = ''
    s_SECDesc = ''
    i_FileSize = ''
    s_FilingDate = ''
    s_AcceptedDate = ''
    s_accno_filename = ''


    gfl = [] # good filing list
    # Get listmaster file list from folder
    fl = glob.glob(SECIndexesPath + "\\listmaster*.txt")
    for j in fl:
        x1 = j.split('.') # get date of index
        if (x1[1] >= fromDate) and (x1[1] <= endDate):
            #print x1[1] # date YYYYMMDD
            gfl.append(x1[1])

    for fn in gfl:

        # Create YYYYMMDD path which will hold this day's filings
        PhysYYYYMMDD = DownloadPath + "\\" + fn # YYYYMMDD folder
        if not os.path.exists(PhysYYYYMMDD):
            os.makedirs(PhysYYYYMMDD)

        # Create table of files (prospectuses)
        file = open(SECIndexesPath + '\\listmaster.'+fn+'.txt', 'r')
        table = [row.strip().split('|') for row in file]
        file.close()

        #sys.exit()

        icnt = 1
        for myrow in table:

            filename = myrow[4]

            r = requests.get(myrow[3])
            # s_accnosecurl, SEC index file listing prospectus contents
            s_accnosecurl = myrow[3]
            # Get root of path where files will be
            SECPath = s_accnosecurl[0:s_accnosecurl.rfind('/')]
            s_archpath = SECPath # same for now

            #
            # Into SOUP!
            #
            soup = BeautifulSoup(r.text)

            # Get Accession No.
            divaccession = soup.find("div", {'id' : 'secNum' })
            if divaccession != None:
                s_accno = ''
                s_accno = divaccession.renderContents()
                s_accno = bleach.clean(s_accno, tags=[], strip=True).strip()
                s_accno = s_accno.replace('SEC Accession No. ','').strip()

            # This filings file to be put in Accession path
            PhysYYYYMMDDaccno = PhysYYYYMMDD + '\\' + s_accno
            # Create if necessary
            if not os.path.exists(PhysYYYYMMDDaccno):
                os.makedirs(PhysYYYYMMDDaccno)


            # Tables with files
            table = soup("table", {'class' : 'tableFile' })
            rows = table[0].findAll('tr')
            filelist = []

            # Go through FILE LIST in index and put in filelist[]
            for tr in rows:
                cstr = ''
                cols = tr.findAll('td')
                for index, s in enumerate(cols):
                    # Don't want first number, position in table
                    if index > 0:
                        cstr = cstr + '|' + s.text

                # Don't want complete submittion file
                if cstr.find('Complete sub') < 0:
                    # Ignore empties
                    if cstr.strip() != '':
                        filelist.append(cstr.strip())

     #<div class="infoHead">Effectiveness Date</div>
     #<div class="info">2013-01-07</div>
            s_EffectiveDate =  soup.find(text="Effectiveness Date").findNext('div').contents[0]
            s_AcceptedDate = soup.find(text="Accepted").findNext('div').contents[0]
            s_FilingDate = soup.find(text="Filing Date").findNext('div').contents[0]

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
            s_FileSize = el.contents[0]
            i_FileSize = s_FileSize

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
            i_CIK = sCIK


            # Put all files in table
            for l in filelist:
                lsplit = l.split('|')
                #sql = "INSERT INTO [Filings] ([AcceptedDate], [accno], [accno_filename], [accnosecurl], [archpath], [CIK], [EffectiveDate], [filename], [FileSize], [FilingDate], [FormType], [physpath], [SECDesc]) VALUES ('s_AcceptedDate', 's_accno', 's_accno_filename', 's_accnosecurl', 's_archpath', i_CIK, 's_EffectiveDate', 's_filename', i_FileSize, 's_FilingDate', 's_FormType', 's_physpath', 's_SECDesc');"
                sql = "INSERT INTO [Filings] ([AcceptedDate], [accno], [accno_filename], [accnosecurl], [archpath], [CIK], [EffectiveDate], [filename], [FileSize], [FilingDate], [FormType], [physpath], [SECDesc]) VALUES "

                #([AcceptedDate], [accno], [accno_filename], [accnosecurl],
                # [archpath], [CIK], [EffectiveDate], [filename], [FileSize],
                #[FilingDate], [FormType], [physpath], [SECDesc])

                cleanfilename = ''.join(c for c in lsplit[2] if c in valid_chars)

                sstr = '('
                sstr = sstr + "'" + s_AcceptedDate + "',"
                sstr = sstr + "'" + s_accno + "',"
                sstr = sstr + "'" + s_accno + '__' + lsplit[2] + "',"
                sstr = sstr + "'" + s_accnosecurl + "',"
                sstr = sstr + "'" + s_archpath + "',"
                sstr = sstr + "" + i_CIK + ","
                sstr = sstr + "'" + s_EffectiveDate + "',"
                sstr = sstr + "'" + cleanfilename + "',"
                sstr = sstr + "" + lsplit[4] + ","
                sstr = sstr + "'" + s_FilingDate + "',"
                sstr = sstr + "'" + lsplit[3] + "',"
                sstr = sstr + "'" + PhysYYYYMMDDaccno + "',"
                sstr = sstr + "'" + lsplit[1] + "'"
                sstr = sstr + ")"

                sql = sql + sstr + ";"

                #print sql

                # Put in Database?
                flagRecordExists = False

                try:
                    conncheck = pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb)};DBQ='+sMDF)
                    # First check existance
                    sqlcheck = "Select accno_filename FROM Filings where [accno_filename] ='" + s_accno + "__" + lsplit[2] + "'"
                    #print sqlcheck
                    cursorcheck = conncheck.cursor()
                    cursorcheck.execute(sqlcheck)
                    row  = cursorcheck.execute(sqlcheck).fetchone()
                    if row != None:
                        flagRecordExists = True
                except:
                        flagRecordExists = False
                        print "dbCheck Record failure!"
                finally:
                    cursorcheck.close()
                    conncheck.close()

                try:
                    if flagRecordExists == False:
                        conn = pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb)};DBQ='+sMDF)
                        cursorinsert = conn.cursor()
                        cursorinsert.execute(sql)
                        conn.commit()
                except:
                    print "dbInsert failure!"
                finally:
                    if flagRecordExists == False:
                        cursorinsert.close()
                        conn.close()

                if flagRecordExists == False:
                    print "Downloading: " + SECPath + '/' + lsplit[2]
                    r = requests.get(SECPath + '/' + lsplit[2])
                    print "Saving to: " + PhysYYYYMMDDaccno +"\\" + lsplit[2]
                    with open(PhysYYYYMMDDaccno +"\\" + cleanfilename, "w") as code:
                        code.write(r.content)

    #sys.exit()

    print "DONE"
    icnt += 1

  #          if icnt > 15:
  #              sys.exit()

if __name__ == '__main__':
    main()

# INSERT INTO [Filings] ([AcceptedDate], [accno], [accno_filename], [accnosecurl], [archpath], [CIK], [EffectiveDate], [FieldAttributes], [FieldName], [FieldSize], [FieldType], [filename], [FileSize], [FilingDate], [FldDescription], [FormType], [Object], [physpath], [SECDesc], ) VALUES ('s_AcceptedDate', 's_accno', 's_accno_filename', 's_accnosecurl', 's_archpath', i_CIK, 's_EffectiveDate', i_FieldAttributes, 's_FieldName', i_FieldSize, 's_FieldType', 's_filename', i_FileSize, 's_FilingDate', 's_FldDescription', 's_FormType', 's_Object', 's_physpath', 's_SECDesc', );

