# You HAVE to use Python 3.5.x or else the IBM_DB library won't work!
# Libraries:
# - pip install ibm_db
# - pip install PrettyTable

import ibm_db
conn = ibm_db.connect("DATABASE=BLUDB;HOSTNAME=dashdb-txn-sbox-yp-dal09-03.services.dal.bluemix.net;PORT=50000;PROTOCOL=TCPIP;UID=ffz03558;PWD=6s50g+3tr7slj5cb;", "", "")
from datetime import date
from prettytable import PrettyTable

##### Function to store company data to the database.
#        Arguments:
#        company_name (str): Name of company
#        cxo_name (str): name of cxo
#        path_to_parsed_pdf (str): path to the parsed pdf file stored in IBM COS
#        path_to_youtube_transcript (str): path to the youtube transcript file stored in IBM COS
#        links (list): list of all news urls
#        saved_date (datetime): date of when object is stored
#        Return: None
##### End of function description.

def insert_to_db(
                company_name,
                cxo_name,
                path_to_parsed_pdf,
                path_to_youtube_transcript,
                links,
                saved_date
                ):

    sql = "INSERT INTO FFZ03558.SOURCE VALUES(?, ?, ?, ?, ?, ?)"
    prep_stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(prep_stmt, 1, company_name)
    ibm_db.bind_param(prep_stmt, 2, cxo_name)
    ibm_db.bind_param(prep_stmt, 3, path_to_parsed_pdf)
    ibm_db.bind_param(prep_stmt, 4, path_to_youtube_transcript)
    ibm_db.bind_param(prep_stmt, 5, links)
    ibm_db.bind_param(prep_stmt, 6, saved_date)
    ibm_db.execute(prep_stmt)

##### Utility to test the function.
# insert_to_db("Glue Tester", "Mr. Smith John", "Path Here", "Path Here", "https://google.com", "2020-01-17")
# print("Successfully inserted!")
##### End of utility.

def get_analysis_data():
    """
        Getting the analysis ready data
    """

    # TODO: Implement code below
    sql = "SELECT * FROM FFZ03558.SOURCE"
    stmt = ibm_db.exec_immediate(conn, sql)
    tabel = PrettyTable()
    tabel.field_names = ["Name", "CXO", "Path (PDF)", "Path (YouTube)", "Links", "Save Date"]   

    tuple = ibm_db.fetch_tuple(stmt)
    while tuple != False:
        tabel.add_row([tuple[0], tuple[1], tuple[2], tuple[3], tuple[4], tuple[5]])
        tuple = ibm_db.fetch_tuple(stmt)

    print(tabel)

##### SELECT Statement to call all the data inside the database.
# get_analysis_data()
##### End of SELECT Statement.
