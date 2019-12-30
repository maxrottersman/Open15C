import mysql.connector
from mysql.connector import errorcode

hostname = '34.73.201.162'
username = 'maxsql'
password = 'sql321'
database = 'SECFunds'

query = ("SELECT mgmtInvFundName FROM Extract_NCEN")
         #"WHERE hire_date BETWEEN %s AND %s")

try:
    cnx = mysql.connector.connect(user='maxsql',
                                database='SECFunds',
                                host='34.73.201.162',
                                password='sql321')
    cursor = cnx.cursor()
    cursor.execute(query) #, (hire_start, hire_end))
    for (mgmtInvFundName) in cursor:
        print(mgmtInvFundName)

   
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:
    cnx.close()