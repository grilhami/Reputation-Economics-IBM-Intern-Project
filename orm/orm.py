# You HAVE to use Python 3.5.x or else the IBM_DB library won't work!
import ibm_db
conn = ibm_db.connect("DATABASE=BLUDB;HOSTNAME=dashdb-txn-sbox-yp-dal09-03.services.dal.bluemix.net;PORT=50000;PROTOCOL=TCPIP;UID=ffz03558;PWD=6s50g+3tr7slj5cb;", "", "")
from datetime import date

# Function to include
kode = input("Kode Perusahaan: ")
nama = input("Company Name: ")
cxo = input("CXO: ")
fpath = input("Full Path: ")
ppath = input("Partial Path: ")
social = input("Social Media: ")
date = str(date.today())

#sql = "INSERT INTO FFZ03558.SOURCE VALUES(" + kode + "," + nama + "," + cxo + "," + fpath + "," + ppath + "," + social + ")"
sql = "INSERT INTO FFZ03558.SOURCE VALUES(?, ?, ?, ?, ?, ?, ?)"
prep_stmt = ibm_db.prepare(conn, sql)
ibm_db.bind_param(prep_stmt, 1, kode)
ibm_db.bind_param(prep_stmt, 2, nama)
ibm_db.bind_param(prep_stmt, 3, cxo)
ibm_db.bind_param(prep_stmt, 4, fpath)
ibm_db.bind_param(prep_stmt, 5, ppath)
ibm_db.bind_param(prep_stmt, 6, social)
ibm_db.bind_param(prep_stmt, 7, date)
ibm_db.execute(prep_stmt)

# SELECT Statement
# sql = "SELECT * FROM FFZ03558.SOURCE"
# stmt = ibm_db.exec_immediate(conn, sql)

# tuple = ibm_db.fetch_tuple(stmt)
# while tuple != False:
#    print("The ID is: ", tuple[0])
#    print("The name is: ", tuple[1])
#    tuple = ibm_db.fetch_tuple(stmt)