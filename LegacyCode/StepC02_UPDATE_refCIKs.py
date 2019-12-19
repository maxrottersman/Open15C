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

ScriptPath = os.path.dirname(os.path.realpath(__file__))
SECIndexesPath = ScriptPath + "\\SECIndexes"

# --------- CONFIG --------------
fromDate = '20130601' # will be greater-than or equl
endDate = '20131001'
connstr = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};Provider=Microsoft.ACE.OLEDB.12.0;DBQ='
sDBTarget = r'C:\ff_Factory2007\NSAR\FRMatch2012.accdb'
# -------------------------------

URLnormal = 'http://www.sec.gov/Archives/edgar/data/838802/000111183013000177/0001111830-13-000177-index.htm'

valid_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
URLCikPage = 'http://www.sec.gov/cgi-bin/browse-edgar'
# ?action=getcompany&CIK=0000061397&type=485&dateb=&count=100&scd=filings
lSECCIKs = []

def MineCIKInfo():

    cnt = 0
    for l in lSECCIKs:
        cnt = cnt + 1

        s_FilingDateFirst = ''
        s_FilingDateLast = ''
        s_alladdress = ''
        s_businessaddress = ''
        s_fye = ''
        s_identInfo = ''
        s_locstate = ''
        s_mailaddress = ''
        s_registrant = ''

        cikstr = l[0]
        cikstr10 = cikstr.zfill(10)
        payload = {'action':'getcompany','CIK':cikstr10,'type':'485','datab':'','count':'100','scd':'filings'}
        r = requests.get(URLCikPage, params=payload)
        chks = ''
        chks = r.text
        if chks != '' and chks.find('No matching CIK') < 1:

            #print r.text
            #
            # Into SOUP!
            #
            soup = BeautifulSoup(r.text)

            # Get identInfo
            identInfo = soup.find("p", {'class' : 'identInfo' })
            s_identInfo = identInfo.renderContents()
            s_identInfo = bleach.clean(s_identInfo, tags=[], strip=True).strip()
            #print "s_identInfo:" + s_identInfo

            s_locstate = s_identInfo[s_identInfo.find('State location')+16:s_identInfo.find('State location')+16+2]
            #print "s_locstate:" + s_locstate

            s_fye = s_identInfo[s_identInfo.find('Fiscal Year End')+17:s_identInfo.find('Fiscal Year End')+17+4]
            #print "s_fye:" + s_fye

            # Get companyName
            registrant = soup.find("span", {'class' : 'companyName' })
            s_registrant = registrant.renderContents()
            s_registrant = bleach.clean(s_registrant, tags=[], strip=True).strip()
            s_registrant = s_registrant[0:s_registrant.find('CIK#')]
            s_registrant = str(''.join(s for s in s_registrant if s in valid_chars))
            #print "s_registrant:" + s_registrant

            # Get addresses
            s_alladdress = ''
            alladdress = soup.findAll("div",{'class': 'mailer'})
            for mys in alladdress:
                s_alladdress = s_alladdress + ' ' + mys.renderContents()
            s_alladdress = bleach.clean(s_alladdress, tags=[], strip=True).strip()

            # Mailing
            s_mailaddress = s_alladdress[16:s_alladdress.find('Business Address')]
            s_mailaddress =' '.join(s_mailaddress.split())
            s_mailaddress = str(''.join(s for s in s_mailaddress if s in valid_chars))
            #print 's_mailaddress:'+ s_mailaddress
            # Business
            s_businessaddress = s_alladdress[s_alladdress.find('Business Address')+16:]
            s_businessaddress =' '.join(s_businessaddress.split())
            s_businessaddress = str(''.join(s for s in s_businessaddress if s in valid_chars))
            #print 's_businessaddress:'+ s_businessaddress

            # Now find more recent and oldest prospectus filings
            # Tables with files
            table = soup("table", {'class' : 'tableFile2' })
            rows = table[0].findAll('tr')
            filelist = []

            # Go through FILE LIST in index and put in filelist[]
            rcount = 0
            for rnum, tr in enumerate(rows):
                cstr = ''
                cols = tr.findAll('td')
                for cnum, td in enumerate(cols):
                    # First row, latest filings
                    if rnum == 1:
                        # 4th column is filindg date
                        if cnum ==3:
                            s_FilingDateLast = td.text

                    # Last Row, earliest filing date
                    if rnum == rcount:
                         # 4th column is filindg date
                        if cnum ==3:
                            s_FilingDateFirst = td.text
                rcount = rcount + 1

            #print 's_FilingDateLast:' + s_FilingDateLast
            #print 's_FilingDateFirst:' + s_FilingDateFirst

            sql = "UPDATE refCIKs SET [LocState] = '" + s_locstate + "', "
            sql = sql + "[Registrant]='" + s_registrant + "',"
            sql = sql + "[fye]='" + s_fye + "',"
            sql = sql + "[MailAddress]='" + s_mailaddress + "',"
            sql = sql + "[BusinessAddress]='" + s_businessaddress + "',"
            sql = sql + "[FileDateLast]='" + s_FilingDateLast + "',"
            sql = sql + "[FileDateFirst]='" + s_FilingDateFirst + "'"
            sql = sql + " WHERE CIK=" + str(cikstr).strip()

            print cnt
            conn = pyodbc.connect(connstr + sDBTarget)
            cursor = conn.cursor()
            try:
                cursor.execute(sql)
                conn.commit()

            except:
                print "db update error"
                cursor.close()
                conn.close()

            finally:
                cursor.close()
                conn.close()

        if cnt > 100000:
            sys.exit()


def dbLoad_lSECCIKs():
    conn = pyodbc.connect(connstr + sDBTarget)
    cursor = conn.cursor()
    try:
        sql = 'Select trim(str([CIK])) as CIKstr FROM refCIKs Where IsNull([Registrant]) ORDER BY CIK Asc;'
        cursor.execute(sql)
        rows  = cursor.fetchall()
        if rows != None:
            for r in rows:
                lSECCIKs.append(r)
    except:
        print "db error!"
        cursor.close()
        conn.close()

    finally:
        conn.close()


if __name__ == '__main__':
    dbLoad_lSECCIKs()
    MineCIKInfo()

# INSERT INTO [Filings] ([AcceptedDate], [accno], [accno_filename], [accnosecurl], [archpath], [CIK], [EffectiveDate], [FieldAttributes], [FieldName], [FieldSize], [FieldType], [filename], [FileSize], [FilingDate], [FldDescription], [FormType], [Object], [physpath], [SECDesc], ) VALUES ('s_AcceptedDate', 's_accno', 's_accno_filename', 's_accnosecurl', 's_archpath', i_CIK, 's_EffectiveDate', i_FieldAttributes, 's_FieldName', i_FieldSize, 's_FieldType', 's_filename', i_FileSize, 's_FilingDate', 's_FldDescription', 's_FormType', 's_Object', 's_physpath', 's_SECDesc', );

