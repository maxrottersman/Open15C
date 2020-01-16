#-------------------------------------------------------------------------------

from pathlib import Path

import sqlite3
from sqlite3 import Error
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --------- CONFIG --------------
ScriptPath = Path.cwd() # new way of getting script folder in both win/linux
ScriptPathParent = Path.cwd().resolve().parent # Parent
DataPath = ScriptPathParent / 'Open15C_Data'
SECIndexesPath = DataPath / 'SEC_IndexFiles' # / adds right in all os
DataPathSQLiteDB = DataPath / 'SECedgar.sqlite'
db_uri = r'sqlite:///' + str(DataPathSQLiteDB)
print(db_uri)
# -------------------------------

db_sqlalchemy = create_engine(db_uri)
con = db_sqlalchemy.connect()
res = con.execute("Select * from SECMasterClass where [Symbol] <> ''")


df_fromsql = pd.read_sql_table("SECMasterClass",con=db_sqlalchemy)


# Get TABLE NAMES: db_sqlalchemy.table_names()

# Get TABLE COLUMNS. If we want metadata from tables do following:
#metadata = MetaData(db_sqlalchemy)
#t = Table("SECMasterClass", metadata, autoload=True)
#columns = [m.key for m in t.columns]
# or with more meta: print(repr(metadata.tables['SECMasterClass']))

#
# IT ALL BEGINS ON MAIN
#
if __name__ == '__main__':
    print(df_fromsql.head())
