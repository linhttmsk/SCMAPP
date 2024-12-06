import streamlit as st
import pyodbc
import getpass
import time
from configparser import ConfigParser
import logging
from logging.handlers import RotatingFileHandler
import os
# from src.query import execute_query


# SERVER =parser.get('SQL','server')
# DATABASE =parser.get('SQL','database')
# USERNAME =parser.get('SQL','username')
# PASSWORD =parser.get('SQL','password')
DRIVER="{ODBC Driver 18 for SQL Server}"
VERISON="1.0.0"

# # local server
# server = 'MMD5CG2101V26\SQLEXPRESS'
# database = 'MIMS'
# username = 'CRB\TLT023'
# # password = 'GkDbBgJzLUPWnxuFpiXhqAm580'
# driver = '{ODBC Driver 18 for SQL Server}'
# # Trusted_Connection=yes;


# # Azure server
# server = 'adsosqlausql01.crb.apmoller.net'
# database = 'MEKAUTO'
# username = 'MEKMIMS'
# password = 'mekci123#'
# # username = 'testLT'
# # password = 'testingLT'
# driver = '{ODBC Driver 18 for SQL Server}'


# connection_string = f"DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};USERUID={USERNAME};PWD={PASSWORD};Encrypt=yes;TrustServerCertificate=yes;Trusted_Connection=no;MultipleActiveResultSets=True"
# connection_string=f"DRIVER={DRIVER};Server={SERVER};Initial Catalog={DATABASE};Persist Security Info=False;User ID={USERNAME};Password={PASSWORD};Integrated Security=SSPI;MultipleActiveResultSets=True;Encrypt=Yes;TrustServerCertificate=Yes;Connection Timeout=30;"
# connection_string = f"DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};USERUID={USERNAME};Encrypt=no;TrustServerCertificate=yes;Integrated_Security=yes;Trusted_Connection=yes;"
# connection_string = f"DRIVER={DRIVER};SERVER=tcp:{SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};PersistSecurityInfo=False;MultipleActiveResultSets=False;Encrypt=yes;TrustServerCertificate=yes;"
# Server=tcp:{server_name}.database.windows.net,1433;Initial Catalog={database_name};Persist Security Info=False;User ID={your_username};Password={your_password};MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;

def get_credential(USERID,password):
    SERVER, DATABASE, USERNAME, PASSWORD=["","","",""]

    
    inter_on=is_cnx_active('www.google.com')

    if inter_on==False:
        st.error('Please check your connection',icon="🚨")
    else:
        
        # Set request body
        req_body = {
            'UID': USERID,
            'key': password
        }

        # Assign request URL to variable
        req_url = "https://prod-148.westeurope.logic.azure.com:443/workflows/a09d050d0f9b4d19a066837e0c57b7be/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=74QnpWC9MpN1oesa9ubqJ_uZHFbH-Ievpge4oxSkYvM"


        # Send HTTP request
        try:
            response = requests.post(req_url, json=req_body, headers={"Content-Type": "application/json"})
            # Extract values from the response
            result = response.text
            # st.write(result)

            if response.status_code == 200:
                try:
                    # Parse the JSON string
                    data = json.loads(result)

                    # Extract values
                    SERVER = data.get("server")
                    DATABASE = data.get("database")
                    USERNAME = data.get("user")
                    PASSWORD = data.get("pw")

                
                except json.JSONDecodeError as e:
                    st.error(f"Error decoding JSON: {e}")
                        
            else:
                st.error(f"No access!!! {response.status_code}  {response.text}",icon= "🚨")

        except Exception as e:
            st.error(f"No access!!! If you would like to use VPN, please perform your first log in via LAN network.",icon= "🚨")
        
    return SERVER, DATABASE, USERNAME, PASSWORD


def create_connection():
    global connection_string

    credential=cookies["key_vault"].split("|")
    SERVER=credential[1]
    DATABASE=credential[2]
    USERNAME=credential[3]
    PASSWORD=credential[4]

    base64_bytes = SERVER.encode("ascii") 

    sample_string_bytes = base64.b64decode(base64_bytes) 
    SERVER = sample_string_bytes.decode("ascii") 

    base64_bytes = DATABASE.encode("ascii") 

    sample_string_bytes = base64.b64decode(base64_bytes) 
    DATABASE = sample_string_bytes.decode("ascii") 

    base64_bytes = USERNAME.encode("ascii") 

    sample_string_bytes = base64.b64decode(base64_bytes) 
    USERNAME = sample_string_bytes.decode("ascii") 

    base64_bytes = PASSWORD.encode("ascii") 

    sample_string_bytes = base64.b64decode(base64_bytes) 
    PASSWORD = sample_string_bytes.decode("ascii") 
    
    db=None
    
    connection_string = f"DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};\
        Encrypt=yes;MultipleActiveResultSets=yes;TrustServerCertificate=yes;Trusted_Connection=no;MARS_Connection=Yes;"
    db=pyodbc.connect(connection_string)

    return db,DATABASE


# Function to execute SQL queries
def execute_query(query):
    with pyodbc.connect(connection_string) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
    return results,columns


def create_Appversion_table(db):
    """Create table in the database."""
    cursor = db.cursor()
   
    #Arrival TIMESTAMP DEFAULT CURRENT_TIMESTAMPCHAR(20),

    query = """
                CREATE TABLE dimAppversion (
                    AppID VARCHAR(255) PRIMARY KEY NOT NULL,
                    Version VARCHAR(255) NOT NULL,
                    Owner VARCHAR(255),
                )
                """

    cursor.execute(query)
    db.commit()
    st.success("dimAppversion created successfully.",icon="✅")


def checkVersion(AppID,version):
    isApp=False
    query=f"SELECT * FROM dimAppversion WHERE AppID = '{AppID}'"
    results,columns=execute_query(query)
    if results:
        for row in results:
            if row[1]==version:
                isApp=True

    return isApp

def create_log_table(db):
    """Create table in the database."""
    cursor = db.cursor()
   
    #Arrival TIMESTAMP DEFAULT CURRENT_TIMESTAMPCHAR(20),
    # ID INT IDENTITY(1,1) NOT NULL,
    create_log_table_query = """
                CREATE TABLE mims_factlog (
                    UID VARCHAR(255) NOT NULL,
                    DateTime DATETIME NOT NULL,
                    Booking VARCHAR(MAX),
                    Cont VARCHAR(MAX),
                    Vessel VARCHAR(MAX),
                    Voyage VARCHAR(MAX),
                    Arrival VARCHAR(MAX),
                    Code VARCHAR(MAX),
                    Action VARCHAR(MAX) NOT NULL,
                    Remark VARCHAR(MAX),
                )
                """

    cursor.execute(create_log_table_query)
    db.commit()

    st.success("factlog table created successfully." ,icon="✅")



def create_dimunit_table(db):
    """Create table in the database."""
    cursor = db.cursor()
   
    #Arrival TIMESTAMP DEFAULT CURRENT_TIMESTAMPCHAR(20),

    create_dimunit_table_query = """
                CREATE TABLE mims_dimunit (
                    Code VARCHAR(255) PRIMARY KEY NOT NULL,
                    Name VARCHAR(255) NOT NULL,
                    FullPackageName VARCHAR(255) NOT NULL,
                    CreatedBy VARCHAR(255) NOT NULL,
                    CreatedDate DATETIME NOT NULL,
                    ModifiedBy VARCHAR(255) NOT NULL,
                    ModifiedDate DATETIME NOT NULL,
                )
                """

    cursor.execute(create_dimunit_table_query)
    db.commit()
    st.success("mims_dimunit created successfully.",icon="✅")


def create_dimport_table(db):
    """Create table in the database."""
    cursor = db.cursor()
   
    #Arrival TIMESTAMP DEFAULT CURRENT_TIMESTAMPCHAR(20),

    create_dimport_table_query = """
                CREATE TABLE mims_dimport (
                    Code VARCHAR(255) PRIMARY KEY NOT NULL,
                    Name VARCHAR(255) NOT NULL,
                    RTCPort VARCHAR(255),
                    DestName VARCHAR(255),
                    TransferName VARCHAR(255),
                    Terminal VARCHAR(255),
                    CreatedBy VARCHAR(255) NOT NULL,
                    CreatedDate DATETIME NOT NULL,
                    ModifiedBy VARCHAR(255) NOT NULL,
                    ModifiedDate DATETIME NOT NULL,
                )
                """

    cursor.execute(create_dimport_table_query)
    db.commit()
    st.success("mims_dimport created successfully.",icon="✅")



def create_dimvsl_table(db):
    """Create table in the database."""
    cursor = db.cursor()
   
    #Arrival TIMESTAMP DEFAULT CURRENT_TIMESTAMPCHAR(20),

    create_dimvsl_table_query = """
                CREATE TABLE mims_dimvsl (
                    Code VARCHAR(255) PRIMARY KEY NOT NULL,
                    Name VARCHAR(255) NOT NULL,
                    CallSign VARCHAR(255) NOT NULL,
                    Nationality VARCHAR(255),
                    CreatedBy VARCHAR(255) NOT NULL,
                    CreatedDate DATETIME NOT NULL,
                    ModifiedBy VARCHAR(255) NOT NULL,
                    ModifiedDate DATETIME NOT NULL,
                )
                """

    cursor.execute(create_dimvsl_table_query)
    db.commit()
    st.success("mims_dimvsl table created successfully.",icon="✅")



def create_dimcont_table(db):
    """Create table in the database."""
    cursor = db.cursor()
   
    #Arrival TIMESTAMP DEFAULT CURRENT_TIMESTAMPCHAR(20),

    create_dimcont_table_query = """
                CREATE TABLE mims_dimcont (
                    ISOCode VARCHAR(255) PRIMARY KEY NOT NULL,
                    ContainerSize VARCHAR(255) NOT NULL,
                    ContainerSizeName VARCHAR(255) NOT NULL,
                    ContainerTypeName VARCHAR(255) NOT NULL,
                    CreatedBy VARCHAR(255) NOT NULL,
                    CreatedDate DATETIME NOT NULL,
                    ModifiedBy VARCHAR(255) NOT NULL,
                    ModifiedDate DATETIME NOT NULL,
                )
                """

    cursor.execute(create_dimcont_table_query)
    db.commit()
    st.success("mims_dimcont table created successfully.",icon="✅")



def create_dimfe_table(db):
    """Create table in the database."""
    cursor = db.cursor()
   
    #Arrival TIMESTAMP DEFAULT CURRENT_TIMESTAMPCHAR(20),

    create_pshed_table_query = """
                CREATE TABLE mims_dimfe (
                    Code VARCHAR(255) PRIMARY KEY NOT NULL,
                    Name VARCHAR(255) NOT NULL,
                    CreatedBy VARCHAR(255) NOT NULL,
                    CreatedDate DATETIME NOT NULL,
                    ModifiedBy VARCHAR(255) NOT NULL,
                    ModifiedDate DATETIME NOT NULL,
                )
                """

    cursor.execute(create_pshed_table_query)
    db.commit()
    st.success("mims_dimfe table created successfully.",icon="✅")




def create_bl_table(db):
    """Create table in the database."""
    cursor = db.cursor()
   
    #Arrival TIMESTAMP DEFAULT CURRENT_TIMESTAMPCHAR(20),

    create_hbl_table_query = """
                CREATE TABLE mims_facthbl (
                    Booking VARCHAR(255) PRIMARY KEY NOT NULL,
                    Vessel VARCHAR(255) NOT NULL,
                    Voyage VARCHAR(255) NOT NULL,
                    Arrival DATE NOT NULL,
                    POL VARCHAR(255) NOT NULL,
                    POD VARCHAR(255) NOT NULL,
                    DEL VARCHAR(255),
                    LINE VARCHAR(255),
                    Shipper_Name VARCHAR(255),
                    Shipper_Address VARCHAR(MAX),
                    Shipper_Country VARCHAR(255),
                    Cnee_Name VARCHAR(255),
                    Cnee_Address VARCHAR(MAX),
                    Cnee_Country VARCHAR(255),
                    Notify_Name VARCHAR(255),
                    Notify_Address VARCHAR(MAX),
                    Notify_Country VARCHAR(255),
                    Term VARCHAR(255),
                    Cargo_Type VARCHAR(255),
                    Movement VARCHAR(255),
                    Freight VARCHAR(255),
                    No_Pack DECIMAL,
                    Pack_Unit VARCHAR(255),
                    Weight DECIMAL(18,3),
                    Measurement DECIMAL(18,3),
                    Mark VARCHAR(MAX),
                    Description VARCHAR(MAX),
                    CreatedBy VARCHAR(255) NOT NULL,
                    CreatedDate DATETIME NOT NULL,
                    ModifiedBy VARCHAR(255) NOT NULL,
                    ModifiedDate DATETIME NOT NULL
                )
                """

    cursor.execute(create_hbl_table_query)
    db.commit()
    st.success("mims_facthbl table created successfully.",icon="✅")



def create_cont_table(db):
    """Create table in the database."""
    cursor = db.cursor()
   
    #Arrival TIMESTAMP DEFAULT CURRENT_TIMESTAMPCHAR(20),
    #BookingCont VARCHAR(255) PRIMARY KEY NOT NULL,

    create_cont_query = """
                CREATE TABLE mims_factcont (
                    VslArrBookingCont VARCHAR(255) PRIMARY KEY NOT NULL,
                    Booking VARCHAR(255) NOT NULL,
                    Vessel VARCHAR(255) NOT NULL,
                    Voyage VARCHAR(255) NOT NULL,
                    Arrival DATE NOT NULL,
                    POL VARCHAR(255) NOT NULL,
                    POD VARCHAR(255) NOT NULL,
                    Cont VARCHAR(255) NOT NULL,
                    Seal VARCHAR(255),
                    Isocode VARCHAR(255),
                    FE VARCHAR(255),                
                    CreatedBy VARCHAR(255) NOT NULL,
                    CreatedDate DATETIME NOT NULL,
                    ModifiedBy VARCHAR(255) NOT NULL,
                    ModifiedDate DATETIME NOT NULL
                )
                """

    #FOREIGN KEY (BookingBK) REFERENCES facthbl(Booking)
    cursor.execute(create_cont_query)
    db.commit()
    st.success("mims_factcont table created successfully.",icon="✅")


def reset():
    st.session_state.submitted = False
    st.write(st.session_state.submitted)


def callback():
    st.session_state.button_clicked = True


def delete_record(db,tbl,col,value):
    cursor = db.cursor()
    delete_query = f"DELETE FROM {tbl} WHERE {col} = ?"
                                                
    delete_data=(value)
    cursor.execute(delete_query,delete_data)
    db.commit()
    st.success(f"{value} DELETED successfully.",icon="✅")
    

def delete_table(db,tbl):
    cursor = db.cursor()
    drop_table_query=f"""
                DELETE FROM {tbl}
                """
    cursor.execute(drop_table_query)
    db.commit()
    st.success(f"{tbl} Table DELETED successfully.",icon="✅")


def drop_table(db,tbl):
    cursor = db.cursor()
    drop_table_query=f"""
                DROP TABLE {tbl}
                """
    cursor.execute(drop_table_query)
    db.commit()
    st.success(f"{tbl} table DROPPED successfully.",icon="✅")


global db
db=st.session_state["DB"]

# drop_table(db,'mims_factlog')
# drop_table(db,'mims_factcont')
# drop_table(db,'mims_facthbl')
# drop_table(db,'mims_dimport')
# drop_table(db,'mims_dimunit')
# drop_table(db,'mims_dimcont')
# drop_table(db,'mims_dimvsl')
# drop_table(db,'mims_dimterm')
# drop_table(db,'mims_dimfe')

# delete_table(db,'mims_factlog')
# delete_table(db,'mims_factcont')
# delete_table(db,'mims_facthbl')
# delete_table(db,'mims_dimunit')
# delete_table(db,'mims_dimcont')
# delete_table(db,'mims_dimvsl')
# delete_table(db,'mims_dimterm')
# delete_table(db,'mims_dimfe')
# delete_table(db,'mims_dimport')

# create_log_table(db)
# create_bl_table(db)
# create_cont_table(db)
# create_dimunit_table(db)
# create_dimport_table(db)
# create_dimfe_table(db)
# create_dimvsl_table(db)
# create_contsize_table(db)
# create_dimterm_table(db)
# create_dimcont_table(db)

# import os
# import win32com.client as win32
# bt=st.button('email')
# if bt:
#     olApp=win32.Dispatch('Outlook.Application')
#     olNS=olApp.GetNameSpace('MAPI')
#     mailItem=olApp.CreateItem(0)
#     mailItem.Subject='Dummy'
#     mailItem.BodyFormat=1
#     mailItem.Body='Hello World'
#     mailItem.To='linh.t@lns.maersk.com'
#     mailItem.Attachments.Add(r'C:\Users\TLT023\OneDrive - Maersk Group\Documents\TOOL\CI\Ticket\1022 MIMIS\28 Aug\MIMS Document.pdf')
#     mailItem.Display()


# import base64 

# test='10.18.148.20,1433'
# sample_string = test
# sample_string_bytes = sample_string.encode("ascii") 

# base64_bytes = base64.b64encode(sample_string_bytes) 
# encode_str = base64_bytes.decode("ascii")

# print(encode_str)

create_Appversion_table()
isApp=checkVersion("MIMS",VERSION)
st.write(isApp)




















































