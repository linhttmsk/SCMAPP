import streamlit as st
# from streamlit_modal import Modal
from streamlit_cookies_manager import CookieManager
from streamlit.components.v1 import html
# from typing import Literal
# import hydralit_components as hc
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
# import fitz
import xlwings as xw
import openpyxl
import shutil
import psutil
import os
import sys
# import base64 
# import random
# import win32com.client as win32
# import tempfile
import re
from src.auth import login,checkAppVersion
import src.view as vi
from src.log import logIni
import src.query as qr



#utcnow()
USERID= getpass.getuser()
DATETIME=datetime.now()
DATETIMEFORMAT="%d/%m/%Y %H:%M:%S"
DATETIMEFM = datetime.now().strftime(DATETIMEFORMAT)


# Get the absolute path of the current script file
script_path = sys.argv[0]
absolute_path = os.path.abspath(script_path)
folder_path0 = os.path.dirname(absolute_path)
folder_path = os.path.dirname(folder_path0)
     

# logging
logging=logIni(folder_path0)



# Read config file and get info
inifile = os.path.join(folder_path0 + r'\\.streamlit', 'config.ini')
parser = ConfigParser()
parser.read(inifile)

APPID=parser.get('APP','appid')
APPVERSION=parser.get('APP','appversion')

# TEMP_PDF=folder_path + parser.get('PATH','temp_pdf')
# TEMP_XLSM=folder_path + parser.get('PATH','temp_xlsm')
# OUTPUT=parser.get('PATH','output')
# DRIVER=parser.get('SQL','driver')

# #party
# SHIP_NAME=parser.get('PARTY','shipname')
# SHIP_ADD=f"{parser.get('PARTY','shipadd1')}\n{parser.get('PARTY','shipadd2')}\n{parser.get('PARTY','shipadd3')}"
# CNOR_NAME=parser.get('PARTY','cnorname')
# CNOR_ADD=f"{parser.get('PARTY','cnoradd1')}\n{parser.get('PARTY','cnoradd2')}\n{parser.get('PARTY','cnoradd3')}"

# NOTI_NAME_E=parser.get('PARTY','notiname_e')
# NOTI_ADD_E=f"{parser.get('PARTY','notiadd1_e')}\n{parser.get('PARTY','notiadd2_e')}\n{parser.get('PARTY','notiadd3_e')}"

# CNEE_NAME_E=parser.get('PARTY','cneename_e')
# CNEE_ADD_E=f"{parser.get('PARTY','cneeadd1_e')}\n{parser.get('PARTY','cneeadd2_e')}\n{parser.get('PARTY','cneeadd3_e')}"

# # cont
# # CONTTYPE=parser.get('DEFAULT','conttype')
# CARGOTYPE=parser.get('DEFAULT','cargotype')
# CONTOWNER=parser.get('DEFAULT','contowner')
# VANNING=parser.get('DEFAULT','vanning')

# PACKU_E=parser.get('DEFAULT','packu_e')
# GW_E=float(parser.get('DEFAULT','gw_e'))
# GWU=parser.get('DEFAULT','gwu')
# MEASURE_E=float(parser.get('DEFAULT','measure_e'))
# MEASUREU=parser.get('DEFAULT','measureu')
# MARK_E=parser.get('DEFAULT','mark_e')
# DESCRIPT_E=parser.get('DEFAULT','descript_e')




# Streamlit app
def main():

    global time_cm,cookies

    # 0. Configuration
    vi.appConfig("Destination Planning","visible","expanded")

    # 1. Login
    cookies = CookieManager()
    initiateApp(USERID,cookies,APPVERSION)
 
    # 2. Page Content
    st.write('not available')

if __name__ == "__main__":

    main()