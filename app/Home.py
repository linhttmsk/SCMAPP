import streamlit as st
from streamlit_cookies_manager import CookieManager
from streamlit.components.v1 import html
import hydralit_components as hc
from typing import Literal
from configparser import ConfigParser
import logging
from logging.handlers import RotatingFileHandler
import requests
import json
import pyodbc
import base64 
import http.client as httplib
from PIL import Image
import getpass
import time
from datetime import datetime
import random
import os
import sys
from src.auth import login,logout,initiateApp
from src.view import appConfig,st_fixed_container


USERID= getpass.getuser()
DATETIME=datetime.now()
DATETIMEFORMAT="%d/%m/%Y %H:%M:%S"
DATETIMEFM = datetime.now().strftime(DATETIMEFORMAT)

# Get the absolute path of the current script file
script_path = sys.argv[0]
absolute_path = os.path.abspath(script_path)
folder_path0 = os.path.dirname(absolute_path)
folder_path = os.path.dirname(folder_path0)

# Read config file and get info
inifile = os.path.join(folder_path0 + r'\\.streamlit', 'config.ini')
parser = ConfigParser()
parser.read(inifile)# Read config file and get info
APPID=parser.get('APP','appid')
APPVERSION=parser.get('APP','appversion')





# App
def main():

    # 0. Configuration
    appConfig("Import Manifest Application " + APPVERSION,"hidden","collapsed")   

    # 1. Login
    cookies = CookieManager()
    initiateApp(USERID,cookies,APPVERSION)
            
    # 2. Page Content
    if st.session_state.LOG:
        st.success(f"*Welcome*! :blue[**{USERID}**] (*Origin*: :blue[**{st.session_state.origin}**], *Role*: :blue[**{st.session_state.role}**]) *SignedIn*: :blue[**{DATETIMEFM}**]",icon='✅')
        expand=st.status("*🔗 Quick link*",expanded=True)
        with expand:

            col1,col2,col3=expand.columns([2.5,1,2.5])

            col1.markdown("<h6 style='text-align: center; color: grey;'>📜 Function</h6>", unsafe_allow_html=True)

            col1.markdown("""<a style='display: block; text-align: center;' href="Booking_Validation" target="_blank">Booking Validation</a>""", unsafe_allow_html=True)
            col1.markdown("""<a style='display: block; text-align: center;' href="Destination_Planning" target="_blank">Destination Planning</a>""", unsafe_allow_html=True)
            col1.markdown("""<a style='display: block; text-align: center;' href="CFS_Container" target="_blank">CFS Container</a>""", unsafe_allow_html=True)
            col1.markdown("""<a style='display: block; text-align: center;' href="Allocation" target="_blank">Allocation</a>""", unsafe_allow_html=True)
            col1.markdown("""<a style='display: block; text-align: center;' href="Report" target="_blank">Report</a>""", unsafe_allow_html=True)
            col1.markdown("""<a style='display: block; text-align: center;' href="Configuration" target="_blank">Configuration</a>""", unsafe_allow_html=True)

            if st.session_state.isDev:
                col1.markdown("""<a style='display: block; text-align: center;' href="devtest" target="_blank">devtest</a>""", unsafe_allow_html=True)

            col2.markdown("<h6 style='text-align: center; color: grey;'>📑 Documentation</h6>", unsafe_allow_html=True)
            
            col2.markdown("""<a style='display: block; text-align: center;' href="https://teamsite.maerskgroup.com/:b:/t/Automationshare/EUV4bdQnYuRNhKABYO1ma5cBzkbhkbEJ_DddedVbDjcikw?e=RKKV7k" target="_blank">Guideline</a>""", unsafe_allow_html=True)
            
            col3.markdown("<h6 style='text-align: center; color: grey;'>👩‍🚀 Account</h6>", unsafe_allow_html=True)

            col3.markdown("""<a style='display: block; text-align: center;' href="https://forms.office.com/e/A4czSt88k7" target="_blank">Reset Password</a>""", unsafe_allow_html=True)

            scol1,scol2,scol3=col3.columns([1,1.5,1])
            btlogout=scol2.button(":arrow_left: LogOut",use_container_width=True)

            
            if btlogout:
                logout(cookies)
        
        st.toast(f'Hi {USERID}, Signed in', icon='🎈')
        
        #st.balloons()
        



    
if __name__ == "__main__":

    
    main()
    

