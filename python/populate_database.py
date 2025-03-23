import create_table as ct
import urllib.request
import gzip
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET
import psycopg2
import sys
import re
import gc
import secrets

# Connect to MariaDB Platform
try:
    conn = psycopg2.connect(
        user=secrets.user,
        password=secrets.password,
        host=secrets.host,
        database=secrets.database
    )
except psycopg2.Error as e:
    print(f"Error connecting to PostgreSQL Platform: {e}")
    sys.exit(1)
# Get Cursor
cur = conn.cursor()

f = open("/home/jan/itercount.txt", "r")
start = int(f.read())
f.close()

for i in range(start, 500):
    f = open("/home/jan/itercount.txt", "w")
    f.write(str(i))
    f.close()
    gc.collect()
    ct.create_table(f"pubmed23n{i:0>4}", cur)
    conn.commit() 

cur.execute("show tables;")
tabsOrNone = [re.search(".*pubmed23n[0-9]{4}$", tab[0]) for tab in cur]
tabs = [x.group() for x in tabsOrNone if x is not None]
cur.execute("show tables;")
abstractssOrNone = [re.search(".*pubmed23n[0-9]{4}_abstract*", tab[0]) for tab in cur]
abstracts = [x.group() for x in abstractssOrNone if x is not None]

sql_call = "CREATE TABLE pubmed AS "
for t in tabs:
    if t is not tabs[0]:
        sql_call = sql_call + " UNION "
    sql_call = sql_call + "SELECT * FROM " + t 
sql_call = sql_call + ";"

try:
    cur.execute(f"DROP TABLE IF EXISTS pubmed;")
    cur.execute(sql_call)
except mariadb.Error as e: 
    print(f"Error: {e}")

sql_call = "CREATE TABLE pubmed_abstract AS "
for t in abstracts:
    if t is not abstracts[0]:
        sql_call = sql_call + " UNION "
    sql_call = sql_call + "SELECT * FROM " + t 
sql_call = sql_call + ";"

try:
    cur.execute(f"DROP TABLE IF EXISTS pubmed_abstract;")
    cur.execute(sql_call)
    cur.execute("create index PMID on pubmed_abstract(PMID);")
except mariadb.Error as e: 
    print(f"Error: {e}")

conn.commit() 
conn.close()
