import streamlit as st
from streamlit_modal import Modal
from streamlit_cookies_manager import CookieManager
from streamlit.components.v1 import html
from typing import Literal
import hydralit_components as hc
import pyodbc
import pandas as pd
import numpy as np
import getpass
import time
from datetime import datetime,date
from time import sleep
from configparser import ConfigParser
import logging
from logging.handlers import RotatingFileHandler
import fitz
import xlwings as xw
import openpyxl
import shutil
import psutil
import os
import sys
import base64 
import random
import win32com.client as win32
import tempfile
import re

from .view import appConfig,st_fixed_container
from .log import logIni
from .view import msg_success,msg_error,msg_warning

USERID= getpass.getuser()
DATETIME=datetime.now()

#####################################
#CREATE TABLE

def create_access_table(db,tbl):
    """Create table in the database."""
    cursor = db.cursor()
    #Arrival TIMESTAMP DEFAULT CURRENT_TIMESTAMPCHAR(20),
    # ID INT IDENTITY(1,1) NOT NULL,
    query = f"""
                CREATE TABLE {tbl} (
                    uid VARCHAR(255) NOT NULL,
                    password VARCHAR(255),
                    MMD VARCHAR(255),
                    origin VARCHAR(255),
                    role VARCHAR(255) NOT NULL,
                    status VARCHAR(255) NOT NULL,
                    appVersion VARCHAR(MAX) NOT NULL,
                    CreatedBy VARCHAR(255) NOT NULL,
                    CreatedDate DATETIME NOT NULL,
                    ModifiedBy VARCHAR(255) NOT NULL,
                    ModifiedDate DATETIME NOT NULL,
                )
                """

    cursor.execute(query)
    db.commit()

    st.success(f"{tbl} table created successfully." ,icon="✅")



def create_log_table(db,tbl):
    """Create table in the database."""
    cursor = db.cursor()
    #Arrival TIMESTAMP DEFAULT CURRENT_TIMESTAMPCHAR(20),
    # ID INT IDENTITY(1,1) NOT NULL,
    query = f"""
                CREATE TABLE {tbl} (
                    UID VARCHAR(255) NOT NULL,
                    DateTime DATETIME NOT NULL,
                    Action VARCHAR(MAX) NOT NULL,
                    Remark VARCHAR(MAX),
                    Content VARCHAR(MAX),
                )
                """

    cursor.execute(query)
    db.commit()

    st.success(f"{tbl} table created successfully." ,icon="✅")





def create_bkValidationSourceConfig_table(db,tbl):
    """Create table in the database."""
    cursor = db.cursor()
   
    #Arrival TIMESTAMP DEFAULT CURRENT_TIMESTAMPCHAR(20),
    #BookingCont VARCHAR(255) PRIMARY KEY NOT NULL,

    query = f"""
                CREATE TABLE {tbl} (
                    TempSourceSheetColumn VARCHAR(255) PRIMARY KEY NOT NULL,
                    Template VARCHAR(255) NOT NULL,
                    SourceName VARCHAR(255) NOT NULL,
                    SheetName VARCHAR(255) NOT NULL,
                    ColumnName VARCHAR(255) NOT NULL,
                    CreatedBy VARCHAR(255) NOT NULL,
                    CreatedDate DATETIME NOT NULL,
                    ModifiedBy VARCHAR(255) NOT NULL,
                    ModifiedDate DATETIME NOT NULL
                )
                """

    #FOREIGN KEY (BookingBK) REFERENCES facthbl(Booking)
    cursor.execute(query)
    db.commit()
    st.success(f"{tbl} table created successfully.",icon="✅")




def create_bkValidationSourceRelation_table(db,tbl):
    """Create table in the database."""
    cursor = db.cursor()

    query = f"""
                CREATE TABLE {tbl} (
                    TempSource1Source2 VARCHAR(255) PRIMARY KEY NOT NULL,
                    Template VARCHAR(255) NOT NULL,
                    SourceName1 VARCHAR(255) NOT NULL,
                    PKey1 VARCHAR(255) NOT NULL,
                    FKey1 VARCHAR(255) NOT NULL,
                    SourceName2 VARCHAR(255) NOT NULL,
                    FKey2 VARCHAR(255) NOT NULL,
                    CreatedBy VARCHAR(255) NOT NULL,
                    CreatedDate DATETIME NOT NULL,
                    ModifiedBy VARCHAR(255) NOT NULL,
                    ModifiedDate DATETIME NOT NULL
                )
                """

    #FOREIGN KEY (BookingBK) REFERENCES facthbl(Booking)
    cursor.execute(query)
    db.commit()
    st.success(f"{tbl} table created successfully.",icon="✅")



def create_bkValidationLogic_table(db,tbl):
    """Create table in the database."""
    cursor = db.cursor()

    query = f"""
                CREATE TABLE {tbl} (
                    Template VARCHAR(255) PRIMARY KEY NOT NULL,
                    Logic VARCHAR(MAX) NOT NULL,
                    CreatedBy VARCHAR(255) NOT NULL,
                    CreatedDate DATETIME NOT NULL,
                    ModifiedBy VARCHAR(255) NOT NULL,
                    ModifiedDate DATETIME NOT NULL
                )
                """

    #FOREIGN KEY (BookingBK) REFERENCES facthbl(Booking)
    cursor.execute(query)
    db.commit()
    st.success(f"{tbl} table created successfully.",icon="✅")




def create_dimunit_table(db,tbl):
    """Create table in the database."""
    cursor = db.cursor()
   
    #Arrival TIMESTAMP DEFAULT CURRENT_TIMESTAMPCHAR(20),

    create_dimunit_table_query = f"""
                CREATE TABLE {tbl} (
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
    st.success(f"{tbl} created successfully.",icon="✅")


def create_dimport_table(db,tbl):
    """Create table in the database."""
    cursor = db.cursor()
   
    #Arrival TIMESTAMP DEFAULT CURRENT_TIMESTAMPCHAR(20),

    create_dimport_table_query = f"""
                CREATE TABLE {tbl} (
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
    st.success(f"{tbl} created successfully.",icon="✅")



def create_dimvsl_table(db,tbl):
    """Create table in the database."""
    cursor = db.cursor()
   
    #Arrival TIMESTAMP DEFAULT CURRENT_TIMESTAMPCHAR(20),

    create_dimvsl_table_query = f"""
                CREATE TABLE {tbl} (
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
    st.success(f"{tbl} table created successfully.",icon="✅")



def create_dimcont_table(db,tbl):
    """Create table in the database."""
    cursor = db.cursor()
   
    #Arrival TIMESTAMP DEFAULT CURRENT_TIMESTAMPCHAR(20),

    create_dimcont_table_query = f"""
                CREATE TABLE {tbl} (
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
    st.success(f"{tbl} table created successfully.",icon="✅")



def create_dimfe_table(db,tbl):
    """Create table in the database."""
    cursor = db.cursor()
   
    #Arrival TIMESTAMP DEFAULT CURRENT_TIMESTAMPCHAR(20),

    create_pshed_table_query = f"""
                CREATE TABLE {tbl} (
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
    st.success(f"{tbl} table created successfully.",icon="✅")




def create_bl_table(db,tbl):
    """Create table in the database."""
    cursor = db.cursor()
   
    #Arrival TIMESTAMP DEFAULT CURRENT_TIMESTAMPCHAR(20),

    create_hbl_table_query = f"""
                CREATE TABLE {tbl} (
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
    st.success(f"{tbl} table created successfully.",icon="✅")



def create_cont_table(db,tbl):
    """Create table in the database."""
    cursor = db.cursor()
   
    #Arrival TIMESTAMP DEFAULT CURRENT_TIMESTAMPCHAR(20),
    #BookingCont VARCHAR(255) PRIMARY KEY NOT NULL,

    create_cont_query = f"""
                CREATE TABLE {tbl} (
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
                    EDI VARCHAR(255),
                    Load VARCHAR(255),                
                    CreatedBy VARCHAR(255) NOT NULL,
                    CreatedDate DATETIME NOT NULL,
                    ModifiedBy VARCHAR(255) NOT NULL,
                    ModifiedDate DATETIME NOT NULL
                )
                """

    #FOREIGN KEY (BookingBK) REFERENCES facthbl(Booking)
    cursor.execute(create_cont_query)
    db.commit()
    st.success(f"{tbl} table created successfully.",icon="✅")





######################################
#CONTAINER



def update_user_record(alert,db,DATABASE,tbl, uid, password, MMD, origin, role, status, appVersion):
    """Update a new user record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    query = f"""
    UPDATE {tbl}
    SET uid = ?, password = ?, MMD = ?, origin = ?, role = ?, status = ?, appVersion= ?, ModifiedBy = ?, ModifiedDate = ?, CreatedBy = ?, CreatedDate = ?
    WHERE uid = ?
    """

    data = (str(uid), str(password), str(MMD), str(origin), str(role), str(status), str(appVersion),  USERID,DATETIME,USERID,DATETIME, str(uid))

    try:
        cursor.execute(query, data)
        db.commit()
        time_cm=DATETIME
        # logging.info("%s :: Update Cont %s",USERID,str(Cont) + str(Arrival))
        # remark='; '.join([str(Cont) + str(Arrival), Cont, str(Arrival), Isocode, str(FE)])
        #insert_log(db,None,Cont,None, None, Arrival,None,'Update Cont',remark,'Success')
        mess=f"{str(uid)} record updated successfully."
        msg_success(alert,mess)
        result=True

    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([str(Cont) + str(Arrival), str(Cont), str(Arrival), str(Isocode), str(FE),err])
        #insert_log(db,None,str(Cont),None, None, None, None,'Update Cont',remark,'Error')
        mess=f"{str(uid)} record updated failed. Error: {err}"
        msg_error(alert,mess)
        result=False


    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm



def insert_user_record(alert,db, DATABASE,tbl, uid, password, MMD, origin,role, status, appVersion):
    """Insert a new user record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    query = f"""
    INSERT INTO {tbl} (uid, password, MMD, origin,role, status, appVersion, ModifiedBy, ModifiedDate, CreatedBy, CreatedDate)
    VALUES ( ?, ?, ?, ?, ?, ?, ?, ? , CAST(? AS DATETIME), ?, CAST(? AS DATETIME))
    """

    data  = (str(uid), str(password), str(MMD), str(origin), str(role), str(status), str(appVersion),  USERID,DATETIME,USERID,DATETIME)
    
    try:
        cursor.execute(query, data)
        db.commit()
        time_cm=DATETIME
        # logging.info("%s :: Insert Cont %s",USERID,str(Booking) + str(Cont))
        # remark='; '.join([str(Booking) + str(Cont), str(Cont) + str(Arrival),Cont, str(Arrival) ,Isocode, str(FE)])
        # insert_log(db,str(Booking),str(Cont),None, None, Arrival,None,'Insert Cont',remark,'Success')
        mess=f"{str(uid)} record inserted successfully."
        msg_success(alert,mess)
        result=True
    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([str(Booking) + str(Cont), str(Cont) + str(Arrival),str(Cont), str(Arrival) ,str(Isocode), str(FE),err])
        # insert_log(db,str(Booking),str(Cont),None, None, None,None,'Insert Cont',remark,'Error')
        mess=f"{str(uid)} record inserted failed. Error: {err}"
        msg_error(alert,mess)
        result=False
    
    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm




def update_bkValidationSourceConfig(alert,db, DATABASE,tbl, Template, SourceName, SheetName, ColumnName):
    """Update a new cont record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    query = f"""
    UPDATE {tbl}
    SET Template = ?, SourceName = ?, SheetName = ?, ColumnName = ?, ModifiedBy = ?, ModifiedDate =  CAST(? AS DATETIME)
    WHERE TempSourceSheetColumn = ?
    """

    data = (Template, SourceName,SheetName,ColumnName, USERID,DATETIME, f"{Template}{SourceName}{SheetName}{ColumnName}")

    try:
        cursor.execute(query, data)
        db.commit()
        time_cm=DATETIME
        mess=f"{Template}{SourceName}{SheetName}{ColumnName} record updated successfully."
        msg_success(alert,mess)
        result=True
    except Exception as e:
        db.rollback()
        err=str(e)
        mess=f"{Template}{SourceName}{SheetName}{ColumnName} record updated failed. Error: {err}"
        msg_error(alert,mess)
        result=False
    
    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()
    
    return result,err,time_cm



def insert_bkValidationSourceConfig(alert,db,DATABASE,tbl, Template, SourceName, SheetName, ColumnName):
    """Insert a new cont record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    query = f"""
    INSERT INTO {tbl} (TempSourceSheetColumn, Template, SourceName, SheetName, ColumnName, CreatedBy, CreatedDate, ModifiedBy, ModifiedDate)
    VALUES ( ?, ?, ?, ?, ?, ?, CAST(? AS DATETIME), ?, CAST(? AS DATETIME))
    """

    data = (f"{Template}{SourceName}{SheetName}{ColumnName}",Template, SourceName,SheetName,ColumnName, USERID,DATETIME,USERID,DATETIME)
    
    try:
        cursor.execute(query, data)
        db.commit()
        time_cm=DATETIME
        mess=f"{Template}{SourceName}{SheetName}{ColumnName} record inserted successfully."
        msg_success(alert,mess)
        result=True

    except Exception as e:
        db.rollback()
        err=str(e)
        mess=f"{Template}{SourceName}{SheetName}{ColumnName} record inserted failed. Error: {err}"
        msg_error(alert,mess)
        result=False
    

    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm



def update_bkValidationSourceRelation(alert,db, DATABASE,tbl, Template, SourceName1, PKey1, FKey1, SourceName2, FKey2):
    """Update a new cont record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    query = f"""
    UPDATE {tbl}
    SET Template = ?, SourceName1 = ?, PKey1 = ?, FKey1 = ?, SourceName2 = ?, FKey2 = ?, ModifiedBy = ?, ModifiedDate =  CAST(? AS DATETIME)
    WHERE TempSource1Source2 = ?
    """

    data = (Template, SourceName1,PKey1,FKey1,SourceName2,FKey2,USERID,DATETIME,f"{Template.strip()}{SourceName1.strip()}{SourceName2.strip()}")

    try:
        cursor.execute(query, data)
        db.commit()
        time_cm=DATETIME
        mess=f"{Template}{SourceName1}{SourceName2} record updated successfully."
        msg_success(alert,mess)
        result=True
    except Exception as e:
        db.rollback()
        err=str(e)
        mess=f"{Template}{SourceName1}{SourceName2} record updated failed. Error: {err}"
        msg_error(alert,mess)
        result=False
    
    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()
    
    return result,err,time_cm



def insert_bkValidationSourceRelation(alert,db,DATABASE,tbl, Template, SourceName1, PKey1, FKey1, SourceName2, FKey2):
    """Insert a new cont record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    insert_cont_query = f"""
    INSERT INTO {tbl} (TempSource1Source2,Template, SourceName1, PKey1, FKey1, SourceName2, FKey2, CreatedBy, CreatedDate, ModifiedBy, ModifiedDate)
    VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, CAST(? AS DATETIME), ?, CAST(? AS DATETIME))
    """

    cont_data = (f"{Template.strip()}{SourceName1.strip()}{SourceName2.strip()}",Template, SourceName1, PKey1, FKey1, SourceName2, FKey2, USERID,DATETIME,USERID,DATETIME)
    
    try:
        cursor.execute(insert_cont_query, cont_data)
        db.commit()
        time_cm=DATETIME
        mess=f"{Template}{SourceName1}{SourceName2} record inserted successfully."
        msg_success(alert,mess)
        result=True

    except Exception as e:
        db.rollback()
        err=str(e)
        mess=f"{Template}{SourceName1}{SourceName2} record inserted failed. Error: {err}"
        msg_error(alert,mess)
        result=False
    

    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm



def update_bkValidationLogic(alert,db, DATABASE,tbl, Template, Logic):
    """Update a new cont record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    query = f"""
    UPDATE {tbl}
    SET Template = ?, Logic = ?, ModifiedBy = ?, ModifiedDate =  CAST(? AS DATETIME)
    WHERE Template = ?
    """

    data = (Template, Logic, USERID,DATETIME,Template)

    try:
        cursor.execute(query, data)
        db.commit()
        time_cm=DATETIME
        mess=f"{Template} record updated successfully."
        msg_success(alert,mess)
        result=True
    except Exception as e:
        db.rollback()
        err=str(e)
        mess=f"{Template} record updated failed. Error: {err}"
        msg_error(alert,mess)
        result=False
    
    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()
    
    return result,err,time_cm



def insert_bkValidationLogic(alert,db,DATABASE,tbl, Template, Logic):
    """Insert a new cont record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    query = f"""
    INSERT INTO {tbl} (Template, Logic, CreatedBy, CreatedDate, ModifiedBy, ModifiedDate)
    VALUES ( ?, ?, ?, CAST(? AS DATETIME), ?, CAST(? AS DATETIME))
    """

    data = ( Template, Logic, USERID,DATETIME,USERID,DATETIME)
    
    try:
        cursor.execute(query, data)
        db.commit()
        time_cm=DATETIME
        mess=f"{Template} record inserted successfully."
        msg_success(alert,mess)
        result=True

    except Exception as e:
        db.rollback()
        err=str(e)
        mess=f"{Template} record inserted failed. Error: {err}"
        msg_error(alert,mess)
        result=False
    

    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm





def update_cont_edi(alert,db, DATABASE,tbl, Vessel, Voyage, Arrival, POL, POD, Booking, Cont, Seal):
    """Update a new cont record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    update_cont_query = f"""
    UPDATE {tbl}
    SET VslArrBookingCont = ?, Vessel = ?, Voyage = ?, Arrival = CAST(? AS DATE), POL = ?, POD = ?, Booking = ?, Cont = ?, Seal = ?, EDI = ?, ModifiedBy = ?, ModifiedDate =  CAST(? AS DATETIME)
    WHERE VslArrBookingCont = ?
    """

    cont_data = (str(Vessel) + Arrival.strftime('%Y-%m-%d') + str(Booking) + str(Cont), str(Vessel), str(Voyage), Arrival, str(POL), str(POD), str(Booking), Cont, str(Seal), "Y", USERID,DATETIME,str(Vessel) + Arrival.strftime('%Y-%m-%d') + str(Booking) + str(Cont))

    try:
        cursor.execute(update_cont_query, cont_data)
        db.commit()
        time_cm=DATETIME
        
        # logging.info("%s :: Update Cont EDI %s",USERID,str(Booking) + str(Cont))
        # remark='; '.join([str(Booking) + str(Cont), str(Cont) + str(Arrival), str(Booking), str(Booking), Cont, Seal, str(Arrival)])
        # insert_log(db,str(Booking),Cont,None, None, Arrival,None,'Update Cont', remark,'Success')
        mess=f"{str(Vessel) + Arrival.strftime('%Y-%m-%d') + str(Booking) + str(Cont)} record updated successfully."
        msg_success(alert,mess)
        result=True
    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([str(Booking) + str(Cont), str(Cont) + str(Arrival), str(Booking), str(Booking), str(Cont), str(Seal), str(Arrival),err])
        # insert_log(db,str(Booking),str(Cont),None, None, None, None,'Update Cont',remark,'Error')
        mess=f"{str(Vessel) + Arrival.strftime('%Y-%m-%d') + str(Booking) + str(Cont)} record updated failed. Error: {err}"
        msg_error(alert,mess)
        result=False
    
    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()
    

    return result,err,time_cm



def insert_cont_edi(alert,db,DATABASE,tbl, Vessel, Voyage, Arrival, POL, POD, Booking, Cont, Seal):
    """Insert a new cont record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    # insert_cont_query = """
    # INSERT INTO mtlt_factcont 
    # VALUES ( ?, ? , ?, ?, ?, ?, ?, ?, CAST(? AS DATETIME), ?, CAST(? AS DATETIME))
    # """

    insert_cont_query = f"""
    INSERT INTO {tbl} (VslArrBookingCont, Vessel, Voyage, Arrival, POL, POD ,  Booking, Cont, Seal, EDI, CreatedBy, CreatedDate, ModifiedBy, ModifiedDate)
    VALUES ( ?, ?, ?, CAST(? AS DATE) , ?, ?, ?,  ?, ?, ?, ?, CAST(? AS DATETIME), ?, CAST(? AS DATETIME))
    """

    cont_data = (str(Vessel) + Arrival.strftime('%Y-%m-%d') + str(Booking) + str(Cont), str(Vessel), str(Voyage), Arrival, str(POL), str(POD), str(Booking), Cont, str(Seal), "Y", USERID,DATETIME,USERID,DATETIME)
    
    try:
        cursor.execute(insert_cont_query, cont_data)
        db.commit()
        time_cm=DATETIME
        
        # logging.info("%s :: Insert Cont EDI %s",USERID,str(Booking) + str(Cont))
        # remark='; '.join([str(Booking) + str(Cont), str(Cont) + str(Arrival), str(Booking), Cont, str(Seal), str(Arrival)])
        # insert_log(db,str(Booking),str(Cont),None, None, Arrival, None,'Insert Cont',remark,'Success')
        mess=f"{str(Vessel) + Arrival.strftime('%Y-%m-%d') + str(Booking) + str(Cont)} record inserted successfully."
        msg_success(alert,mess)
        result=True

    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([str(Booking) + str(Cont), str(Cont) + str(Arrival), str(Booking), Cont, str(Seal), str(Arrival),err])
        # insert_log(db,str(Booking),str(Cont),None, None, None, None,'Insert Cont',remark,'Error')
        mess=f"{str(Vessel) + Arrival.strftime('%Y-%m-%d') + str(Booking) + str(Cont)} record inserted failed. Error: {err}"
        msg_error(alert,mess)
        result=False
    

    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm



def update_cont_record(alert,db,DATABASE,tbl, Vessel, Voyage, Arrival, POL, POD, Booking, Cont, Seal, Isocode, FE):
    """Update a new cont record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    update_cont_query = f"""
    UPDATE {tbl}
    SET VslArrBookingCont = ?, Booking = ?, Vessel = ?, Voyage = ?, Arrival = CAST(? AS DATE), POL= ?, POD = ?, Cont = ?, Seal = ?, Isocode = ?, FE = ?, Load = ?, ModifiedBy = ?, ModifiedDate =  CAST(? AS DATETIME)
    WHERE VslArrBookingCont = ?
    """

    cont_data = (str(Vessel) + Arrival.strftime('%Y-%m-%d') + str(Booking) + str(Cont), str(Booking), str(Vessel), str(Voyage), Arrival, str(POL), str(POD), Cont, str(Seal),  Isocode, FE, "Y", USERID,DATETIME, str(Vessel) + Arrival.strftime('%Y-%m-%d') + str(Booking) + str(Cont))

    try:
        cursor.execute(update_cont_query, cont_data)
        db.commit()
        time_cm=DATETIME
        # logging.info("%s :: Update Cont %s",USERID,str(Cont) + str(Arrival))
        # remark='; '.join([str(Cont) + str(Arrival), Cont, str(Arrival), Isocode, str(FE)])
        #insert_log(db,None,Cont,None, None, Arrival,None,'Update Cont',remark,'Success')
        mess=f"{str(Vessel) + Arrival.strftime('%Y-%m-%d') + str(Booking) + str(Cont)} record updated successfully."
        msg_success(alert,mess)
        result=True

    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([str(Cont) + str(Arrival), str(Cont), str(Arrival), str(Isocode), str(FE),err])
        #insert_log(db,None,str(Cont),None, None, None, None,'Update Cont',remark,'Error')
        mess=f"{str(Vessel) + Arrival.strftime('%Y-%m-%d') + str(Booking) + str(Cont)} record updated failed. Error: {err}"
        msg_error(alert,mess)
        result=False


    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm



def insert_cont_record(alert,db,DATABASE, tbl,Vessel, Voyage, Arrival, POL, POD, Booking, Cont, Seal, Isocode, FE):
    """Insert a new cont record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    insert_cont_query = f"""
    INSERT INTO {tbl} (VslArrBookingCont, Booking, Vessel, Voyage, Arrival, POL, POD, Cont, Seal,  Isocode, FE, Load, CreatedBy, CreatedDate, ModifiedBy, ModifiedDate)
    VALUES ( ?, ?, ?, ?,CAST(? AS DATE) , ?, ?, ?, ?, ?, ?, ?, ?, CAST(? AS DATETIME), ?, CAST(? AS DATETIME))
    """

    cont_data = (str(Vessel) + Arrival.strftime('%Y-%m-%d') + str(Booking) + str(Cont), str(Booking), str(Vessel), str(Voyage), str(Arrival), str(POL), str(POD), str(Cont), str(Seal), "Y", Isocode, str(FE), USERID,DATETIME,USERID,DATETIME)
    
    try:
        cursor.execute(insert_cont_query, cont_data)
        db.commit()
        time_cm=DATETIME
        # logging.info("%s :: Insert Cont %s",USERID,str(Booking) + str(Cont))
        # remark='; '.join([str(Booking) + str(Cont), str(Cont) + str(Arrival),Cont, str(Arrival) ,Isocode, str(FE)])
        # insert_log(db,str(Booking),str(Cont),None, None, Arrival,None,'Insert Cont',remark,'Success')
        mess=f"{str(Vessel) + Arrival.strftime('%Y-%m-%d') + str(Booking) + str(Cont)} record inserted successfully."
        msg_success(alert,mess)
        result=True
    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([str(Booking) + str(Cont), str(Cont) + str(Arrival),str(Cont), str(Arrival) ,str(Isocode), str(FE),err])
        # insert_log(db,str(Booking),str(Cont),None, None, None,None,'Insert Cont',remark,'Error')
        mess=f"{str(Vessel) + Arrival.strftime('%Y-%m-%d') + str(Booking) + str(Cont)} record inserted failed. Error: {err}"
        msg_error(alert,mess)
        result=False
    
    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm



def update_cont_load(alert,db, DATABASE,tbl,Vessel, Voyage, Arrival, POL, POD,  Cont, Isocode, FE):
    """Update a new cont record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    update_cont_query = f"""
    UPDATE {tbl}
    SET Vessel = ?, Voyage = ?, Arrival = CAST(? AS DATE), POL =?, POD =?, Cont = ?,  Isocode = ?, FE = ?, Load = ?, ModifiedBy = ?, ModifiedDate =  CAST(? AS DATETIME)
    WHERE VslArrBookingCont LIKE ?
    """

    cont_data = (str(Vessel), str(Voyage), Arrival, str(POL), str(POD), str(Cont), str(Isocode), str(FE), "Y", USERID,DATETIME, str(Vessel) + Arrival.strftime('%Y-%m-%d') + '%' + str(Cont))

    try:
        cursor.execute(update_cont_query, cont_data)
        db.commit()
        time_cm=DATETIME
        # logging.info("%s :: Update Cont %s",USERID,str(Cont) + str(Arrival))
        # remark='; '.join([str(Cont) + str(Arrival), Cont, str(Arrival), Isocode, str(FE)])
        #insert_log(db,None,Cont,None, None, Arrival,None,'Update Cont',remark,'Success')
        mess=f"{str(Vessel) + Arrival.strftime('%Y-%m-%d')+ str(Cont)} record updated successfully."
        msg_success(alert,mess)
        result=True

    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([str(Cont) + str(Arrival), str(Cont), str(Arrival), str(Isocode), str(FE),err])
        #insert_log(db,None,str(Cont),None, None, None, None,'Update Cont',remark,'Error')
        mess=f"{str(Vessel) + Arrival.strftime('%Y-%m-%d') + str(Cont)} record updated failed. Error: {err}"
        msg_error(alert,mess)
        result=False

    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm



def insert_cont_load(alert,db, DATABASE,tbl, Vessel, Voyage, Arrival, POL, POD, Booking, Cont, Isocode, FE):
    """Insert a new cont record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    insert_cont_query = f"""
    INSERT INTO {tbl} (VslArrBookingCont, Vessel, Voyage, Arrival, POL, POD, Booking,  Cont, Isocode, FE, Load, CreatedBy, CreatedDate, ModifiedBy, ModifiedDate)
    VALUES ( ?, ?, ?,  CAST(? AS DATE) , ?, ?, ?, ?, ?, ?, ?, ?, CAST(? AS DATETIME), ?, CAST(? AS DATETIME))
    """

    cont_data = (str(Vessel) + Arrival.strftime('%Y-%m-%d') + str(Booking) + str(Cont), str(Vessel), str(Voyage), Arrival, str(POL), str(POD), str(Booking), str(Cont) , str(Isocode), str(FE), "Y", USERID,DATETIME,USERID,DATETIME)
    
    try:
        cursor.execute(insert_cont_query, cont_data)
        db.commit()
        time_cm=DATETIME
        # logging.info("%s :: Insert Cont %s",USERID,str(Booking) + str(Cont))
        # remark='; '.join([str(Booking) + str(Cont), str(Cont) + str(Arrival),Cont, str(Arrival) ,Isocode, str(FE)])
        # insert_log(db,str(Booking),str(Cont),None, None, Arrival,None,'Insert Cont',remark,'Success')
        mess=f"{str(Vessel) + Arrival.strftime('%Y-%m-%d')+ str(Cont)} record inserted successfully."
        msg_success(alert,mess)
        result=True
    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([str(Booking) + str(Cont), str(Cont) + str(Arrival),str(Cont), str(Arrival) ,str(Isocode), str(FE),err])
        # insert_log(db,str(Booking),str(Cont),None, None, None,None,'Insert Cont',remark,'Error')
        mess=f"{str(Vessel) + Arrival.strftime('%Y-%m-%d')+ str(Cont)} record inserted failed. Error: {err}"
        msg_error(alert,mess)
        result=False
    
    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm



#######################################
#CARGO


def insert_bl_record(alert,db, DATABASE, tbl,Booking, Vessel,Voyage,Arrival,POL,POD,DEL,LINE, Shipper_Name, Shipper_Address,Shipper_Country,Cnee_Name,Cnee_Address,Cnee_Country,Notify_Name,Notify_Address,Notify_Country,Term,Cargo_Type,Movement,Freight,No_Pack,Pack_Unit,Weight,Measurement,Mark,Description):
    """Insert a new BL record into the 'patients' table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME
    
    # Select the database
    cursor.execute(f"USE {DATABASE}")

    insert_bl_query = f"""
    INSERT INTO {tbl} (Booking, Vessel,Voyage,Arrival,POL,POD,DEL,LINE, Shipper_Name, Shipper_Address,Shipper_Country,Cnee_Name,Cnee_Address,Cnee_Country,Notify_Name,Notify_Address,Notify_Country,Term,Cargo_Type,Movement,Freight,No_Pack,Pack_Unit,Weight,Measurement,Mark,Description,CreatedBy,CreatedDate,ModifiedBy,ModifiedDate)
    VALUES ( ?, ?, ?,  CAST(? AS DATE) , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,  CAST(? AS DATETIME) , ?,  CAST(? AS DATETIME) )
    """

    bl_data = (Booking, Vessel,Voyage,Arrival,POL,POD,DEL,LINE, Shipper_Name, Shipper_Address,Shipper_Country,Cnee_Name,Cnee_Address,Cnee_Country,Notify_Name,Notify_Address,Notify_Country,Term,Cargo_Type,Movement,Freight,No_Pack,Pack_Unit,Weight,Measurement,Mark,Description,USERID,DATETIME,USERID,DATETIME)
    
    try:
        cursor.execute(insert_bl_query, bl_data)
        db.commit()
        time_cm=DATETIME
        
        # logging.info("%s :: Insert BK %s",USERID,str(Booking))
        # remark='; '.join([Booking, Vessel,Voyage,str(Arrival),POL,POD,DEL,LINE, Shipper_Name, Shipper_Address,Shipper_Country,Cnee_Name,Cnee_Address,Cnee_Country,Notify_Name,Notify_Address,Notify_Country,Term,Cargo_Type,Movement,Freight,No_Pack,Pack_Unit,Weight,Measurement,Mark,Description])
        # insert_log(db,str(Booking),None,Vessel, Voyage, Arrival,None,'Insert BK',remark,'Success')
        mess=f"{Booking} record inserted successfully."
        msg_success(alert,mess)
        result=True

    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([str(Booking), str(Vessel),str(Voyage),str(Arrival),str(POL),str(POD),str(DEL),str(LINE), str(Shipper_Name), str(Shipper_Address),str(Shipper_Country),str(Cnee_Name),str(Cnee_Address),str(Cnee_Country),str(Notify_Name),str(Notify_Address),str(Notify_Country),str(Term),str(Cargo_Type),str(Movement),str(Freight),str(No_Pack),str(Pack_Unit),str(Weight),str(Measurement),str(Mark),str(Description),err])
        # insert_log(db,str(Booking),None,str(Vessel), str(Voyage), None,None,'Insert BK',remark,'Error')
        mess=f"{Booking} record inserted failed. Error: {err}"
        msg_error(alert,mess)
        result=False

    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm



def update_bl_record(alert,db, DATABASE,tbl, Booking, Vessel,Voyage,Arrival,POL,POD,DEL,LINE, Shipper_Name, Shipper_Address,Shipper_Country,Cnee_Name,Cnee_Address,Cnee_Country,Notify_Name,Notify_Address,Notify_Country,Term,Cargo_Type,Movement,Freight,No_Pack,Pack_Unit,Weight,Measurement,Mark,Description):
    """Insert a new BL record into the 'patients' table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME
    # Select the database
    cursor.execute(f"USE {DATABASE}")

    update_bl_query = f"""
    UPDATE {tbl}
    SET Booking =?, Vessel = ?, Voyage = ?, Arrival =  CAST(? AS DATE), POL = ?, POD = ?, DEL = ?, LINE = ?, Shipper_Name = ?, Shipper_Address = ?, Shipper_Country = ?, Cnee_Name = ?, Cnee_Address = ?, Cnee_Country = ?, Notify_Name = ?, Notify_Address = ?, Notify_Country = ?, Term = ?, Cargo_Type = ?, Movement = ?, Freight = ?, No_Pack = ?, Pack_Unit = ?, Weight = ?, Measurement = ?, Mark = ?, Description = ?, ModifiedBy = ?, ModifiedDate = CAST(? AS DATETIME)
    WHERE Booking = ?
    """

    bl_data = (Booking, Vessel,Voyage,Arrival,POL,POD,DEL,LINE, Shipper_Name, Shipper_Address,Shipper_Country,Cnee_Name,Cnee_Address,Cnee_Country,Notify_Name,Notify_Address,Notify_Country,Term,Cargo_Type,Movement,Freight,No_Pack,Pack_Unit,Weight,Measurement,Mark,Description,USERID,DATETIME,Booking)
    
    try:
        cursor.execute(update_bl_query, bl_data)
        db.commit()
        time_cm=DATETIME
        
        # logging.info("%s :: Update BK %s",USERID,str(Booking))
        # remark='; '.join([str(Booking), Vessel,Voyage,str(Arrival),POL,POD,DEL,LINE, Shipper_Name, Shipper_Address,Shipper_Country,Cnee_Name,Cnee_Address,Cnee_Country,Notify_Name,Notify_Address,Notify_Country,Term,Cargo_Type,Movement,Freight,No_Pack,Pack_Unit,Weight,Measurement,Mark,Description])
        # insert_log(db,str(Booking),None,Vessel, Voyage, Arrival,None,'Update BK',remark,'Success')
        mess=f"{Booking} record updated successfully."
        msg_success(alert,mess)
        result=True
    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([str(Booking), str(Vessel),str(Voyage),str(Arrival),str(POL),str(POD),str(DEL),str(LINE), str(Shipper_Name), str(Shipper_Address),str(Shipper_Country),str(Cnee_Name),str(Cnee_Address),str(Cnee_Country),str(Notify_Name),str(Notify_Address),str(Notify_Country),str(Term),str(Cargo_Type),str(Movement),str(Freight),str(No_Pack),str(Pack_Unit),str(Weight),str(Measurement),str(Mark),str(Description),err])
        # insert_log(db,str(Booking),None,str(Vessel), str(Voyage), None,None,'Update BK',remark,'Error')
        mess=f"{Booking} record updated failed. Error: {err}"
        msg_error(alert,mess)
        result=False

    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm


def insert_dimport_record(alert,db,DATABASE, tbl,code,name,rtcport,dest,transfer,term):
    """Insert a new port record into the table."""
    err=""
    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    insert_dimport_query = f"""
    INSERT INTO {tbl} (Code,Name,RTCPort,DestName,TransferName,Terminal,CreatedBy,CreatedDate,ModifiedBy,ModifiedDate)
    VALUES ( ?, ?, ?, ?, ? , ?, ?, CAST(? AS DATETIME), ?, CAST(? AS DATETIME))
    """

    port_data = (code,name,rtcport,dest,transfer,term,USERID,DATETIME,USERID,DATETIME)
    
    try:
        cursor.execute(insert_dimport_query, port_data)
        db.commit()
        time_cm=DATETIME
        # logging.info("%s :: Insert Port %s",USERID,code)
        # remark='; '.join([code,name,rtcport,dest,transfer])
        # insert_log(db,None,None,None, None, None,code,"Insert Port",remark,"Success")
        mess=f"Port {code} record inserted successfully."
        msg_success(alert,mess)
        result=True
    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([str(code),str(name),str(rtcport),str(dest),str(transfer),err])
        # insert_log(db,None,None,None, None, None,code,"Insert Port",remark,"Error")
        mess=f"Port {code} record inserted failed. Error: {err}"
        msg_error(alert,mess)
        result=False

    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm


def update_dimport_record(alert,db,DATABASE,tbl, code,name,rtcport,dest,transfer,term):
    """Update a new port record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    update_dimport_query = f"""
    UPDATE {tbl}
    SET Code = ?, Name =  ?, RTCPort = ?, DestName = ?, TransferName = ?, Terminal = ?, ModifiedBy = ?, ModifiedDate = CAST(? AS DATETIME)
    WHERE Code = ?
    """

    port_data = (code,name,rtcport,dest,transfer,term,USERID,DATETIME,code)

    try:
        cursor.execute(update_dimport_query, port_data)
        db.commit()
        time_cm=DATETIME
        # logging.info("%s :: Update Port %s",USERID,code)
        # remark='; '.join([str(code),str(name),str(rtcport),str(dest),str(transfer)])
        # insert_log(db,None,None,None, None, None,code,"Update Port",remark,"Success")
        mess=f"Port {code} record updated successfully."
        msg_success(alert,mess)
        result=True
    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([str(code),str(name),str(rtcport),str(dest),str(transfer),err])
        # insert_log(db,None,None,None, None, None,code,"Update Port",remark,"Error")
        mess=f"Port {code} record updated failed. Error: {err}"
        msg_error(alert,mess)
        result=False

    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm


def insert_dimunit_record(alert,db,DATABASE,tbl, code,name,full):
    """Insert a new port record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    insert_dimunit_query = f"""
    INSERT INTO {tbl} (Code,Name,FullPackageName,CreatedBy,CreatedDate,ModifiedBy,ModifiedDate)
    VALUES ( ?, ?, ?, ?, CAST(? AS DATETIME), ?, CAST(? AS DATETIME))
    """

    unit_data = (code,name,full,USERID,DATETIME,USERID,DATETIME)

    try:
        cursor.execute(insert_dimunit_query, unit_data)
        db.commit()
        time_cm=DATETIME
        # logging.info("%s :: Insert Unit %s",USERID,code)
        # remark='; '.join([code,name,full])
        # insert_log(db,None,None,None, None, None,code,"Insert Unit",remark,"Success")
        mess=f"Unit {code} record inserted successfully."
        msg_success(alert,mess)
        result=True
    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([code,name,full,err])
        # insert_log(db,None,None,None, None, None,code,"Insert Unit",remark,"Error")
        mess=f"Unit {code} record inserted failed. Error: {err}"
        msg_error(alert,mess)
        result=False

    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm


def update_dimunit_record(alert,db,DATABASE,tbl, code,name,full):
    """Update a new unit record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    update_dimport_query = f"""
    UPDATE {tbl}
    SET Code = ?, Name =  ?, FullPackageName = ?,  ModifiedBy = ?, ModifiedDate = CAST(? AS DATETIME)
    WHERE Code = ?
    """

    unit_data = (code,name,full,USERID,DATETIME,code)
    
    try:
        cursor.execute(update_dimport_query, unit_data)
        db.commit()
        time_cm=DATETIME
        # logging.info("%s :: Update Unit %s",USERID,code)
        # remark='; '.join([code,name,full])
        # insert_log(db,None,None,None, None, None,code,"Update Unit",remark,"Success")
        mess=f"Unit {code} record updated successfully."
        msg_success(alert,mess)
        result=True
    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([code,name,full,e])
        # insert_log(db,None,None,None, None, None,code,"Update Unit",remark,"Error")
        mess=f"Unit {code} record updated failed. Error: {err}"
        msg_error(alert,mess)
        result=False

    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm


def insert_country_record(alert,db,DATABASE,tbl, code,name):
    """Insert a new country record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    insert_country_query = f"""
    INSERT INTO {tbl} (Code,Name,CreatedBy,CreatedDate,ModifiedBy,ModifiedDate)
    VALUES ( ?, ? , ?, CAST(? AS DATETIME), ?, CAST(? AS DATETIME))
    """

    country_data = (code,name,USERID,DATETIME,USERID,DATETIME)
    
    try:
        cursor.execute(insert_country_query, country_data)
        db.commit()
        time_cm=DATETIME
        # logging.info("%s :: Insert Country %s",USERID,code)
        # remark='; '.join([code,name])
        # insert_log(db,None,None,None, None, None,code,"Insert Country",remark,"Success")
        mess=f"Country {code} record inserted successfully."
        msg_success(alert,mess)
        result=True
    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([code,name,err])
        # insert_log(db,None,None,None, None, None,code,"Insert Country",remark,"Error")
        mess=f"Country {code} record inserted failed. Error: {err}"
        msg_error(alert,mess)
        result=False

    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm


def update_country_record(alert,db, DATABASE,tbl,code,name):
    """Update a new country record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    update_country_query = f"""
    UPDATE {tbl}
    SET Code = ?, Name =  ? , ModifiedBy = ?, ModifiedDate = CAST(? AS DATETIME)
    WHERE Code = ?
    """

    country_data = (code,name,USERID,DATETIME,code)

    try:
        cursor.execute(update_country_query, country_data)
        db.commit()
        time_cm=DATETIME
        # logging.info("%s :: Update Country %s",USERID,code)
        # remark='; '.join([code,name])
        # insert_log(db,None,None,None, None, None,code,"Update Country",remark,"Success")
        mess=f"Country {code} record updated successfully."
        msg_success(alert,mess)
        result=True
    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([code,name,err])
        # insert_log(db,None,None,None, None, None,code,"Update Country",remark,"Error")
        mess=f"Country {code} record updated failed. Error: {err}"
        msg_error(alert,mess)
        result=False

    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm


def insert_dimvsl_record(alert,db,DATABASE, tbl,code,name,calls,nati):
    """Insert a new vessel record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    insert_dimvsl_query = f"""
    INSERT INTO {tbl} (Code,Name,CallSign,Nationality,CreatedBy,CreatedDate,ModifiedBy,ModifiedDate)
    VALUES ( ?, ?, ?, ?, ?, CAST(? AS DATETIME), ?, CAST(? AS DATETIME))
    """

    vsl_data = (code,name,calls,nati,USERID,DATETIME,USERID,DATETIME)
    
    try:
        cursor.execute(insert_dimvsl_query, vsl_data)
        db.commit()
        time_cm=DATETIME
        # logging.info("%s :: Insert vessel %s",USERID,code)
        # remark='; '.join([code,name,calls,nati])
        # insert_log(db,None,None,None, None, None,code,"Insert vessel",remark,"Success")
        mess=f"Vessel {code} record inserted successfully."
        msg_success(alert,mess)
        result=True
    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([code,name,calls,nati,err])
        # insert_log(db,None,None,None, None, None,code,"Insert vessel",remark,"Error")
        mess=f"Vessel {code} record inserted failed. Error: {err}"
        msg_error(alert,mess)
        result=False

    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm


def update_dimvsl_record(alert,db,DATABASE, tbl,code,name,calls,nati):
    """Update a new vessel record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    update_dimvsl_query = f"""
    UPDATE {tbl}
    SET Code = ?, Name =  ?, CallSign = ? ,  Nationality = ? , ModifiedBy = ?, ModifiedDate = CAST(? AS DATETIME)
    WHERE Code = ?
    """

    vsl_data = (code,name,calls,nati,USERID,DATETIME,code)

    try:
        cursor.execute(update_dimvsl_query, vsl_data)
        db.commit()
        time_cm=DATETIME
        # logging.info("%s :: Update Vessel %s",USERID,code)
        # remark='; '.join([code,name,calls,nati])
        # insert_log(db,None,None,None, None, None,code,"Update Vessel",remark,"Success")
        mess=f"Vessel {code} record updated successfully."
        msg_success(alert,mess)
        result=True
    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([code,name,calls,nati,err])
        # insert_log(db,None,None,None, None, None,code,"Update Vessel",remark,"Error")
        mess=f"Vessel {code} record updated failed. Error: {err}"
        msg_error(alert,mess)
        result=False

    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm


def insert_dimcontsize_record(alert,db, DATABASE,tbl,code,size,sizename,typename):
    """Insert a new mtlt_dimcont record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    insert_cont_query = f"""
    INSERT INTO {tbl} (ISOCode,ContainerSize,ContainerSizeName,ContainerTypeName,CreatedBy,CreatedDate,ModifiedBy,ModifiedDate)
    VALUES ( ?, ?, ?, ?, ?, CAST(? AS DATETIME), ?, CAST(? AS DATETIME))
    """

    cont_data = (code,size,sizename,typename,USERID,DATETIME,USERID,DATETIME)

    try:
        cursor.execute(insert_cont_query, cont_data)
        db.commit()
        time_cm=DATETIME
        # logging.info("%s :: Insert Cont Size %s",USERID,code)
        # remark='; '.join([code,size,sizename])
        # insert_log(db,None,None,None, None, None,code,"Insert Cont Size",remark,"Success")
        mess=f"Cont Size {code} record inserted successfully."
        msg_success(alert,mess)
        result=True
    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([code,size,sizename,err])
        # insert_log(db,None,None,None, None, None,code,"Insert Cont Size",remark,"Error")
        mess=f"Cont Size {code} record inserted failed. Error: {err}"
        msg_error(alert,mess)
        result=False

    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm


def update_dimcontsize_record(alert,db, DATABASE, tbl,code,size,sizename,typename):
    """Update a new mtlt_dimcont record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    update_cont_query = f"""
    UPDATE {tbl}
    SET ISOCode = ?, ContainerSize =  ?, ContainerSizeName = ?, ContainerTypeName = ?, ModifiedBy = ?, ModifiedDate = CAST(? AS DATETIME)
    WHERE ISOCode = ?
    """

    cont_data = (code,size,sizename,typename,USERID,DATETIME,code)

    try:
        cursor.execute(update_cont_query, cont_data)
        db.commit()
        time_cm=DATETIME
        # logging.info("%s :: Update Cont Size %s",USERID,code)
        # remark='; '.join([code,size,sizename])
        # insert_log(db,None,None,None, None, None,code,"Update Cont Size",remark,"Success")
        mess=f"Cont Size {code} record updated successfully."
        msg_success(alert,mess)
        result=True
    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([code,size,sizename,err])
        # insert_log(db,None,None,None, None, None,code,"Update Cont Size",remark,"Error")
        mess=f"Cont Size {code} record updated failed. Error: {err}"
        msg_error(alert,mess)
        result=False

    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm


def insert_pshed_record(alert,db,DATABASE, tbl, rtcp,shedno):
    """Insert a new mtlt_dimportshed record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    insert_pshed_query = f"""
    INSERT INTO {tbl} (RTCPort,ShedNo,CreatedBy,CreatedDate,ModifiedBy,ModifiedDate)
    VALUES ( ?, ?, ?, CAST(? AS DATETIME), ?, CAST(? AS DATETIME))
    """

    pshed_data = ( rtcp,shedno,USERID,DATETIME,USERID,DATETIME)
    
    try:
        cursor.execute(insert_pshed_query, pshed_data)
        db.commit()
        time_cm=DATETIME
        # logging.info("%s :: Insert Port Shed %s",USERID,rtcp)
        # remark='; '.join([rtcp,shedno])
        # insert_log(db,None,None,None, None, None, rtcp,"Insert PortShed",remark,"Success")
        mess=f"Port Shed {rtcp} record inserted successfully."
        msg_success(alert,mess)
        result=True
    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([rtcp,shedno,err])
        # insert_log(db,None,None,None, None, None,rtcp, "Insert PortShed",remark,"Error")
        mess=f"Port Shed {rtcp} record inserted failed. Error: {err}"
        msg_error(alert,mess)
        result=False

    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm



def update_pshed_record(alert,db, DATABASE,tbl,rtcp,shedno):
    """Update a new mtlt_dimpshed record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    update_pshed_query = f"""
    UPDATE {tbl}
    SET RTCPort = ?, ShedNo =  ?,  ModifiedBy = ?, ModifiedDate = CAST(? AS DATETIME)
    WHERE RTCPort = ?
    """

    pshed_data = (rtcp,shedno,USERID,DATETIME,rtcp)

    try:
        cursor.execute(update_pshed_query, pshed_data)
        db.commit()
        time_cm=DATETIME
        # logging.info("%s :: Update Port Shed %s",USERID,rtcp)
        # remark='; '.join([rtcp,shedno])
        # insert_log(db,None,None,None, None, None ,rtcp,"Update PortShed",remark,"Success")
        mess=f"Port Shed {rtcp} record updated successfully."
        msg_success(alert,mess)
        result=True
    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([rtcp,shedno,err])
        # insert_log(db,None,None,None, None, None ,rtcp,"Update Port Shed",remark,"Error")
        mess=f"Port Shed {rtcp} record updated failed. Error: {err}"
        msg_error(alert,mess)
        result=False

    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm


def insert_dimfe_record(alert,db,DATABASE,tbl, code,name):
    """Insert a new  record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    insert_dimfe_query = f"""
    INSERT INTO {tbl} (Code,Name,CreatedBy,CreatedDate,ModifiedBy,ModifiedDate)
    VALUES ( ?, ?, ?, CAST(? AS DATETIME), ?, CAST(? AS DATETIME))
    """

    fe_data = (code,str(name),USERID,DATETIME,USERID,DATETIME)

    try:
        cursor.execute(insert_dimfe_query, fe_data)
        db.commit()
        time_cm=DATETIME
        # logging.info("%s :: Insert FE %s",USERID,code)
        # remark='; '.join([code,str(name)])
        # insert_log(db,None,None,None, None, None,code,"Insert FE",remark,"Success")
        mess=f"FE {code} record inserted successfully."
        msg_success(alert,mess)
        result=True
    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([code,str(name),err])
        # insert_log(db,None,None,None, None, None,code,"Insert FE",remark,"Error")
        mess=f"FE {code} record inserted failed. Error: {err}"
        msg_error(alert,mess)
        result=False

    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm


def update_dimfe_record(alert,db,DATABASE,tbl, code,name):
    """Update a new  record into the table."""
    err=""

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    time_cm=DATETIME

    # Select the database
    cursor.execute(f"USE {DATABASE}")

    update_dimfe_query = f"""
    UPDATE {tbl}
    SET Code = ?, Name =  ?,  ModifiedBy = ?, ModifiedDate = CAST(? AS DATETIME)
    WHERE Code = ?
    """

    fe_data = (code,name,USERID,DATETIME,code)
    
    try:
        cursor.execute(update_dimfe_query, fe_data)
        db.commit()
        time_cm=DATETIME
        # logging.info("%s :: Update FE %s",USERID,code)
        # remark='; '.join([code,name])
        # insert_log(db,None,None,None, None, None,code,"Update FE",remark,"Success")
        mess=f"FE {code} record updated successfully."
        msg_success(alert,mess)
        result=True
    except Exception as e:
        db.rollback()
        err=str(e)
        # remark='; '.join([code,name,err])
        # insert_log(db,None,None,None, None, None,code,"Update FE",remark,"Error")
        mess=f"FE {code} record updated failed. Error: {err}"
        msg_error(alert,mess)
        result=False

    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

    return result,err,time_cm



################################
#LOG


def insert_log(db,DATABASE,tbl,Action,Remark,time_cm):

    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    # time_cm=DATETIME
    # Select the database
    cursor.execute(f"USE {DATABASE}")

    insert_log_query = f"""
    INSERT INTO {tbl} 
    VALUES (?, CAST(? AS DATETIME) , ?, ?)
    """

    log_data = (USERID,time_cm, Action, Remark)

    try:
        cursor.execute(insert_log_query, log_data)
        db.commit()
    except Exception as e:
        db.rollback()
        st.write(f"Error: {str(e)}")

    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()
    # st.success(f"log successfully.",icon="✅") 









#################################
#COMMON

def execute_query(db,DATABASE,query):
    # with pyodbc.connect(connection_string) as conn:
    flg_cu=False
    i=0
    while flg_cu==False:
        cursor= db.cursor()
        cursor.execute(f"USE {DATABASE}")
        try:
            i+=1
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            cursor.close()
            flg_cu=True
        except Exception as e:
            cursor.close()
            time.sleep(1)
        
            if i>=10 and flg_cu==False:
                msg_error(False,'Cannot perform select query, please check connection, VPN, Akamai, refresh page and try again: ' + str(e))
                st.stop()
                break

    return results,columns


def delete_record(alert,db,DATABASE,isin,tbl,col,value):
    
    err=""
    cursor = db.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    cursor.execute(f"USE {DATABASE}")
    time_cm=DATETIME


    if isin==True:
        delete_query = f"DELETE FROM {tbl} WHERE {col} IN ({value})"
    else:
        delete_query = f"DELETE FROM {tbl} WHERE {col} = '{value}'"                              
    try:
        cursor.execute(delete_query)
        db.commit()
        time_cm=DATETIME
        mess=f"{value} DELETED successfully."
        msg_success(alert,mess)
        result=True

    except Exception as e:
        db.rollback()
        err=str(e)
        mess=f"{value} DELETED failed. Error: {err}"
        msg_error(alert,mess)
        result=False

    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()
    
    return result,err,time_cm



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


# def reset():
#     st.session_state.submitted = False
#     st.write(st.session_state.submitted)


# def callback():
#     st.session_state.button_clicked = True

def callback():
    st.session_state.running = True





#############################
#MAIN 

# just run when directly run this py file, no run when it is imported in another py file
if __name__ == "__main__":

    # global db
    # db=st.session_state["DB"]
    pass
