import streamlit as st
from streamlit_cookies_manager import CookieManager
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
# import random
import os
import sys
from .query import execute_query
from .log import logIni


script_path = sys.argv[0]
absolute_path = os.path.abspath(script_path)
folder_path0 = os.path.dirname(absolute_path)
folder_path = os.path.dirname(folder_path0)

inifile = os.path.join(folder_path0 + r'\\.streamlit', 'config.ini')
parser = ConfigParser()
parser.read(inifile)
DRIVER=parser.get('SQL','driver')
APPID=parser.get('APP','appid')
APPVERSION=parser.get('APP','appversion')

# SERVER1=parser.get('SQL1','server')
# DATABASE1=parser.get('SQL1','database')
# USERNAME1=parser.get('SQL1','uid')
# PASSWORD1=parser.get('SQL1','pw')

# USERID= getpass.getuser()
DATETIME=datetime.now()
DATETIMEFORMAT="%d/%m/%Y %H:%M:%S"
DATETIMEFM = datetime.now().strftime(DATETIMEFORMAT)


# logging
logging=logIni(folder_path0)






def checkAppVersion(db,USERID,version):
    if 'isDev' not in st.session_state:
        st.session_state.isDev=''
    # if 'isSU' not in st.session_state:
    #     st.session_state.isSU=''
    if 'isUser' not in st.session_state:
        st.session_state.isUser=''
    if 'role' not in st.session_state:
        st.session_state.role=''
    if 'origin' not in st.session_state:
        st.session_state.origin=''
    if 'LOG' not in st.session_state:
        st.session_state.LOG=''

    query=f"SELECT * FROM scm_dimaccess WHERE uid = '{USERID}'"
    results,columns=execute_query(db,st.session_state.DATABASE,query)
    if results:
        for row in results:
            if row[5].lower()!='granted':
                st.error(f"Unauthorized",icon='🚨')
                break
            if row[6]==version:
                st.session_state.LOG=True
                st.session_state.role=row[4]
                st.session_state.origin=row[3]

                if st.session_state.role.lower()=='dev':
                    st.session_state.isDev=True
                elif st.session_state.role.lower()=='user':
                    st.session_state.isUser=True
                # elif st.session_state.role.lower()=='su':
                #     st.session_state.isSU=True
            
                st.sidebar.success(f"Welcome! :blue[**{USERID}**] > :blue[**{st.session_state.origin}**] > :blue[**{st.session_state.role}**]",icon='✅')
            else:
                st.error(f"Wrong AppVersion, please upgrade your app to Verison {row[5]}",icon='🚨')
            break




def checkAppVerisonAll(db,user,version):
    if 'role' not in st.session_state:
        st.session_state.role=''
    if st.session_state.role=='':
            
        try:
            #db1,DATABASE1=connectSQLAccess(USERID)
            checkAppVersion(db,user,version)
            
        except Exception as e:
            logging.info("%s :: AppVerison & Account Validation failed!!! Error: %s", user,str(e))
            st.error(f'{user} AppVerison & Account Validation failed !!! Error: {e}', icon="🚨")
            st.stop()
    else:
        st.sidebar.success(f"Welcome! :blue[**{user}**] > :blue[**{st.session_state.origin}**] > :blue[**{st.session_state.role}**]",icon='✅')  




# def connectSQLAccess(USERID):
    
#     connection_string = (
#     f"Driver={DRIVER};"
#     f"Server=tcp:{SERVER1},1433;"
#     f"Database={DATABASE1};"
#     f"Uid={USERNAME1};"
#     f"Pwd={PASSWORD1};"
#     f"Encrypt=yes;"
#     f"TrustServerCertificate=no;"
#     f"Connection Timeout=30;"
#     )

#     db1=None
#     connection_string = f"DRIVER={DRIVER};SERVER={SERVER1};DATABASE={DATABASE1};UID={USERNAME1};PWD={PASSWORD1};\
#         Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
#     db1=pyodbc.connect(connection_string)
 
#     return db1,DATABASE1



def login(USERID,cookies): 
    
    if 'LOG' not in st.session_state:
        st.session_state.LOG=''
    # st.write(st.session_state.LOG)
    if st.session_state.LOG=='':
        
        
        # Get cookies
        if not cookies.ready():
            st.info('🌐 loading cookies...')
            st.stop()

        
        # if 'log' not in st.session_state:
        #     st.session_state['log']=False


        if "log_bt" not in cookies or "my_mekscm" not in cookies or ("log_bt" in cookies and cookies["log_bt"]!='mekscm'):
            col1,col2,col3=st.columns([1,1,1])
            
            log_exp=col2.status(":rainbow[***WELCOME***]",expanded=True)
            
            with log_exp:
                account=log_exp.text_input("😉 Account",USERID,disabled=True)
                password=log_exp.text_input("🗝️ Password", type="password")
                
                log_bt=log_exp.button(":arrow_right: Click to Login",use_container_width=True)

                bt_col1, bt_col2,bt_col3=log_exp.columns([1,0.1,1])
                bt_col1.markdown("""<a style='display: block; text-align: center;' href="https://forms.office.com/e/A4czSt88k7" target="_blank">SignIn or Reset Password</a>""", unsafe_allow_html=True)

                bt_col3.markdown("""<a style='display: block; text-align: center;' href="https://teamsite.maerskgroup.com/:b:/t/Automationshare/EUV4bdQnYuRNhKABYO1ma5cBzkbhkbEJ_DddedVbDjcikw?e=RKKV7k" target="_blank">Click here for Guideline</a>""", unsafe_allow_html=True)

                if log_bt:
                    # if not cookies_log not in cookies:
                    
                    # st.session_state['log']=True
                    cookies["log_bt"]='ok'
                    cookies.save()

                
        if "log_bt" in cookies:
        

            if "DATABASE" not in st.session_state or "LOG" not in st.session_state or "DB" not in st.session_state:
                st.session_state.DATABASE=""
                st.session_state.LOG=""
                st.session_state.DB=""

            if "my_mekscm" not in cookies or not cookies["my_mekscm"]:
                try:
                    if not password:
                        st.warning("Missing password",icon="⚠️")
                        st.session_state.DATABASE=""
                        st.session_state.LOG=""
                        st.session_state.DB=""
            
                    else:
                
                        SERVER, DATABASE, USERNAME, PASSWORD=get_credential(USERID,password)
            
                        if SERVER and DATABASE and USERNAME and  PASSWORD:
                            sample_string = USERID
                            sample_string_bytes = sample_string.encode("ascii") 
                            
                            base64_bytes = base64.b64encode(sample_string_bytes) 
                            encode_str = base64_bytes.decode("ascii")

                            sample_string = DATETIMEFM
                            sample_string_bytes = sample_string.encode("ascii") 
                            
                            base64_bytes = base64.b64encode(sample_string_bytes) 
                            datelog = base64_bytes.decode("ascii")

                            sample_string = encode_str + datelog + "(@|" + SERVER + "|&" + datelog + encode_str + "#|" + DATABASE  + "|" + encode_str + "|" + USERNAME + "|" + datelog +  "|" + PASSWORD + "|" + datelog
                            sample_string_bytes = sample_string.encode("ascii") 
                            
                            base64_bytes = base64.b64encode(sample_string_bytes) 
                            cooki_str = base64_bytes.decode("ascii")


                            cookies["my_mekscm"]=cooki_str
                            cookies.update()
                            
           
                            logflag,db,DATABASE=login_check(USERID,cookies)
                            
                            st.session_state.DATABASE=DATABASE
                            st.session_state.LOG=logflag
                            st.session_state.DB=db

                            st.rerun()
                            
                except Exception as e:  
                    st.error(f'Error: {e}',icon= "🚨")
        
            
            elif st.session_state.LOG=="" or st.session_state.DATABASE=="" or cookies["log_bt"]=='ok':

                logflag,db,DATABASE=login_check(USERID,cookies)

                st.session_state.DATABASE=DATABASE
                st.session_state.LOG=logflag
                st.session_state.DB=db

                #st.rerun()

        

    # if st.session_state.LOG==True and st.session_state.DB!='' and st.session_state.DATABASE!='':
    #     try:
    #         #db1,DATABASE1=connectSQLAccess(USERID)
    #         checkAppVersion(db,USERID,APPVERSION)
    #     except Exception as e:
    #         logging.info("%s :: Login failed!!! Error: %s", USERID,str(e))
    #         st.error(f'{USERID} Login failed !!! Error: {e}', icon="🚨")

    # st.write(logflag,db,DATABASE,cookies )
    #return logflag,db,DATABASE,cookies,role    
        




def is_cnx_active(url):
    
    conn = httplib.HTTPConnection(url, timeout=10)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False 



@st.cache_data
def get_credential(USERID,password):
    SERVER, DATABASE, USERNAME, PASSWORD=["","","",""]

    inter_on=is_cnx_active('www.google.com')

    if inter_on==False:
        st.error('Please check your connection',icon="🚨")
    else:
        
        # Set request body
        req_body = {
            'appid': APPID,
            'command': 'sql',
            'uid': USERID,
            'key': password
        }

        # Assign request URL to variable
        req_url = "https://prod-01.westeurope.logic.azure.com:443/workflows/ce52a236e4124f2290e70232269809ce/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=JssMVF202heo5bx_niPaD8PSeNJeO8025LVG7-UIRMM"
                

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




@st.cache_resource
def create_connection(USERID,cooki_str):

    # cooki_str=cookies["my_mekscm"]
    base64_bytes = cooki_str.encode("ascii")

    sample_string_bytes = base64.b64decode(base64_bytes) 
    cooki_str = sample_string_bytes.decode("ascii")

    credential=cooki_str.split("|")

    cooki_uid=credential[4]
    base64_bytes = cooki_uid.encode("ascii") 

    sample_string_bytes = base64.b64decode(base64_bytes) 
    cooki_uid = sample_string_bytes.decode("ascii") 

    if cooki_uid==USERID:
        SERVER=credential[1]
        DATABASE=credential[3]
        USERNAME=credential[5]
        PASSWORD=credential[7]
    else:
        SERVER=''
        DATABASE=''
        USERNAME=''
        PASSWORD=''

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
        Encrypt=yes;MultipleActiveResultSets=yes;TrustServerCertificate=yes;Trusted_Connection=no;MARS_Connection=Yes;Connection Timeout=50;ConnectRetryInterval=10;"
    
    #MultipleActiveResultSets=yes;
    # SERVER='tcp:meksql.database.windows.net,1433'
    # DATABASE='mekciautodb'
    # USERNAME='mekcisql'
    # PASSWORD='Maersk171216*'
    # db=None
    
    # connection_string = f"DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};\
    #     Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

    db=pyodbc.connect(connection_string)

    # db.setencoding(encoding='utf-8', ctype=pyodbc.SQL_CHAR)
    # db.setdecoding(pyodbc.SQL_CHAR,encoding='utf-8', ctype=pyodbc.SQL_CHAR)

    return db,DATABASE



def login_check(USERID,cookies):
    try:
        cooki_str=cookies["my_mekscm"]
        db,DATABASE=create_connection(USERID,cooki_str)
        flag=True
        cookies["log_bt"]='mekscm'
        cookies.update()
        # welcome_list = ["Nice day,", "Blessed day,", "Wonderful day,", "Beautifull day,","Enjoy your day,"]
        # welcome_sent=random.choice(welcome_list)
        # st.sidebar.success(f"""{welcome_sent} {USERID}""",icon="✅")
        alert = st.success(f"Login successfull!!! Welcome {USERID} to Manifest Application") # Display the alert
        logging.info("%s :: Login successfull!!! Welcome %s to %s database", USERID,USERID,DATABASE)
        time.sleep(1) # Wait for 3 seconds
        alert.empty() # Clear the alert
    
    except Exception as e:
        logging.info("%s :: Login failed!!! Error: %s", USERID,str(e))
        st.error(f'{USERID} Login failed !!! Error: {e}', icon="🚨")
        st.stop()
    return flag,db,DATABASE




def logout(cookies):
    
    
    cookies["my_mekscm"]=None
    cookies["log_bt"]=None
    cookies.update()
    
    
    st.session_state.LOG=''
    st.cache_resource.clear()
    st.cache_data.clear()
    # logflag=False
    
    
    time.sleep(1)
    st.rerun()
    return False




def initiateApp(user,cookies,version):
    with hc.HyLoader('',hc.Loaders.pretty_loaders,index=[1]):
        login(user,cookies)  

    #st.spinner(text="Running, your change can stop the process...")
    if st.session_state.LOG==True and st.session_state.DB and st.session_state.DATABASE:
        checkAppVerisonAll(st.session_state.DB,user,version)


        if st.session_state.LOG==True and st.session_state.DB and st.session_state.DATABASE and st.session_state.role.lower()!='':
            
            #st.sidebar.write('_______________________')
            
            #st.sidebar.page_link('1_Home.py', label='Home')
            st.sidebar.page_link('pages/1_Booking Validation.py', label='🚢 Booking Validation')
            st.sidebar.page_link('pages/2_Destination Planning.py', label='🚚 Destination Planning')
            st.sidebar.page_link('pages/3_CFS Container.py', label='▶️ CFS Container')
            st.sidebar.page_link('pages/4_Allocation.py', label='📚 Allocation')
            st.sidebar.page_link('pages/5_Report.py', label='📝 Report')
            st.sidebar.page_link('pages/6_Configuration.py', label='⚙ Configuration')
            st.sidebar.page_link('pages/devtest.py', label='❗Dev Test')

            st.sidebar.write('_______________________')