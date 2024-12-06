import streamlit as st
# from streamlit_modal import Modal
from streamlit_cookies_manager import CookieManager
from streamlit.components.v1 import html
# from typing import Literal
# import hydralit_components as hc
# import pyodbc
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
# import xlwings as xw
# import openpyxl
# import shutil
# import psutil
import os
import sys
# import base64 
# import random
# import win32com.client as win32
# import tempfile
# import re
from src.auth import login,initiateApp
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



global  time_cm,cookies

# 0. Configuration
vi.appConfig("Dev Test","visible","expanded")

# 1. Login
cookies = CookieManager()
initiateApp(USERID,cookies,APPVERSION)


if st.session_state.isDev:

    ### TEST

    #qr.create_access_table(st.session_state.DB,'mtlt_dimaccess')
    #qr.drop_table(st.session_state.DB,"mtlt_dimaccess")
    # qr.drop_table(st.session_state.DB,'mtlt_factlog')
    # qr.drop_table(st.session_state.DB,f'mtlt_{st.session_state.origin}_factcont')
    # qr.drop_table(st.session_state.DB,f'mtlt_{st.session_state.origin}_factcontload')
    # qr.drop_table(st.session_state.DB,f'mtlt_{st.session_state.origin}_factcontgcss')
    # qr.drop_table(st.session_state.DB,f'mtlt_{st.session_state.origin}_factenter')
    # qr.drop_table(st.session_state.DB,f'mtlt_{st.session_state.origin}_facthbl')
    #qr.drop_table(st.session_state.DB,f'mtlt_{st.session_state.origin}_dimport')
    #qr.drop_table(st.session_state.DB,f'mtlt_TH_dimenterstatus')
    # qr.drop_table(st.session_state.DB,'mtlt_dimunit')
    # qr.drop_table(st.session_state.DB,'mtlt_dimcont')
    # qr.drop_table(st.session_state.DB,'mtlt_dimvsl')
    # qr.drop_table(st.session_state.DB,'mtlt_dimfe')
    # qr.drop_table(st.session_state.DB,'mtlt_dimaccess')

    # qr.delete_table(st.session_state.DB,'mtlt_factlog')
    # qr.delete_table(st.session_state.DB,'mtlt_factcont')
    # qr.delete_table(st.session_state.DB,'mtlt_facthbl')
    # qr.delete_table(st.session_state.DB,'mtlt_dimunit')
    # qr.delete_table(st.session_state.DB,'mtlt_dimcont')
    # qr.delete_table(st.session_state.DB,'mtlt_dimvsl')
    # qr.delete_table(st.session_state.DB,'mtlt_dimterm')
    # qr.delete_table(st.session_state.DB,'mtlt_dimfe')
    # qr.delete_table(st.session_state.DB,'mtlt_dimport')

    # qr.create_log_table(st.session_state.DB,f'mtlt_{st.session_state.origin}_factlog')
    # qr.create_bl_table(st.session_state.DB,f'mtlt_{st.session_state.origin}_facthbl')
    # qr.create_enter_table(st.session_state.DB,f'mtlt_{st.session_state.origin}_factenter')
    # qr.create_cont_table(st.session_state.DB,f'mtlt_{st.session_state.origin}_factcont')
    # qr.create_contload_table(st.session_state.DB,f'mtlt_{st.session_state.origin}_factcontload')
    # qr.create_contgcss_table(st.session_state.DB,f'mtlt_{st.session_state.origin}_factcontgcss')
    # qr.create_dimenterstatus_table(st.session_state.DB,f'mtlt_{st.session_state.origin}_dimenterstatus')
    # qr.create_dimunit_table(st.session_state.DB,f'mtlt_{st.session_state.origin}_dimunit')
    # qr.create_dimport_table(st.session_state.DB,f'mtlt_{st.session_state.origin}_dimport')
    # qr.create_dimfe_table(st.session_state.DB,f'mtlt_{st.session_state.origin}_dimfe')
    # qr.create_dimvsl_table(st.session_state.DB,f'mtlt_{st.session_state.origin}_dimvsl')
    # qr.create_dimcont_table(st.session_state.DB,f'mtlt_{st.session_state.origin}_dimcont')

  

    tab1,tab2=st.tabs(['➕ User Moification','👥 User Management'])
    with tab1:
        # batch upload users
        cont1=st.expander(":hand: *Command Button*",expanded=True)
        conttb1,conttb2=cont1.columns([1,4])
        submit_user=conttb1.button("✔️Submit",key="submit_nu",use_container_width=True)
        
        if "userCol" not in st.session_state:
            st.session_state.userCol=False

        if st.session_state.userCol==False:
            query = "SELECT * FROM mtlt_dimaccess WHERE uid='123'"
            results,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,query)
            # columns=columns[:-4]
            st.session_state.userCol=columns

        
        if st.session_state.userCol!=False:
            with st.expander(":bookmark_tabs: *Input Table*",expanded=True):
                edited_df = st.data_editor(pd.DataFrame.from_records("", columns=st.session_state.userCol[:-4]),num_rows="dynamic")
        

            if submit_user:
                st.toast(f'Submitting new User ...', icon='🎈')
                if edited_df["uid"].count()>0:
                    
                    # statusbar
                    progress_text = "Operation in progress. Please wait."
                    
                    my_bar = st.progress(0, text=progress_text)
                    percent_complete=0
                    flg=False
                    ok_flg=False
                    err_flg=False
                    rc_fail=0
                    rc_ok=0

                    user_err={}


                    
                    #loop record
                    
                    for index, row in edited_df.iterrows():
                    
                        # st.write(index)
                        # st.write(row['BL'])
                        if row['uid']: 
                            
                            
                            
                            select_query = f"""
                            SELECT * FROM mtlt_dimaccess WHERE uid = '{row['uid']}'
                            """ 
                            existing,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,select_query)

                            if existing:
                                
                                flg,e,time_cm= qr.update_user_record(False,st.session_state.DB, st.session_state.DATABASE,'scm_dimaccess', row["uid"], row["password"], row["MMD"], row["origin"],row["role"], row["status"], row["appVersion"])
                                
                                if flg==True:
                                    ok_flg=True
                                    rc_ok+=1
                                else:
                                    err_flg=True
                                    user_err[row["uid"]]=e
                                    rc_fail+=1
                                    
                            else:
                                
                                flg,e,time_cm= qr.insert_user_record(False,st.session_state.DB, st.session_state.DATABASE,'scm_dimaccess', row["uid"], row["password"], row["MMD"], row["origin"],row["role"], row["status"], row["appVersion"])
                                if flg==True:
                                    ok_flg=True
                                    rc_ok+=1
                                else:
                                    err_flg=True
                                    user_err[row["uid"]]=e
                                    rc_fail+=1


                        prop=1/len(edited_df)* 100
                        percent_complete+=prop
                        my_bar.progress(int(percent_complete), text=f"*{progress_text}>> imported :red[**{rc_ok}/{len(edited_df)}**] records <<>>  :blue[**{row['uid']}**] <<*")

                    # cnf final
                    # if ok_flg==True and err_flg!=True and rc_fail==0:
                    #     mess=f"Imported successfully!!! {rc_ok} records"
                    #     logging.info("%s :: Upload User Table %s",USERID,mess)
                    #     insert_log(db1,None , None, None, None, None, str(list(edited_df['uid'])), "Upload bl Table", mess,time_cm)
                    #     vi.msg_success(True,mess)

                    # elif rc_ok==0:
                    #     mess="No records imported"
                    #     logging.info("%s :: Upload User Table %s",USERID,mess)
                    #     insert_log(db1,None , None, None, None, None, str(list(edited_df['uid'])), "Upload bl Table", mess,time_cm)
                    #     msg_error(True,mess)

                    # else:
                    #     mess=f"Imported {rc_ok}/{len(edited_df)} records. Failed import for {rc_fail} records: {bl_err}"
                    #     logging.info("%s :: Upload User Table %s",USERID,mess)
                    #     insert_log(db1,None , None, None, None, None, str(list(edited_df['uid'])), "Upload bl Table", mess,time_cm)
                    #     msg_error(True,mess)

                else:
                    st.warning('Please input data',icon="⚠️") 


    with tab2:
        
        if 'userOut' not in st.session_state:
            st.session_state.userOut=False
        if 'userCol' not in st.session_state:
            st.session_state.userCol=False


        query = f"SELECT * FROM scm_dimaccess"

        if st.session_state.isDev:
            st.write(query)
        
        if st.session_state.userOut==False:
            results,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,query)
            st.session_state.userOut=results
            st.session_state.userCol=columns
        
        
        if not st.session_state.userOut:
            st.info("No records found",icon='ℹ')
        else:

            st.info(f"**[   :red[{len(st.session_state.userOut)}]   ]**  Records found. Please select at least 1 record",icon='⭐')   
            # Create a DataFrame with the results and column names
            df = pd.DataFrame.from_records(st.session_state.userOut, columns=st.session_state.userCol)
            # table=st.dataframe(df,height=500)

            selected_rows=0
            with st.expander(":bookmark_tabs: *Table Result* ",expanded=True):
                ecol1,ecol2,ecol3,ecol5=st.columns([1,1,1,1])
                
                select_all = ecol1.checkbox('Select All')
                if select_all:
                    tbl=st.dataframe(df,height=300)
                    selected_rows=df
                    idx=df.index
                    
                else:         
                    selected_rows,idx = vi.dataframe_with_selections(df,300)

            
            if len(selected_rows)>=1:
                    ecol2.write(f":blue[📌 **[ :red[{len(selected_rows)}] ]** *records selected*]")
                    
                    # if "del_bl" not in st.session_state:
                    #     st.session_state["del_bl"]=False

                
                    if "del_yes" not in st.session_state:
                        st.session_state.del_yes=False

                    # if delete_bl:
                    #     st.toast(f'Delete BL', icon='🎈')
                    #     st.session_state["del_bl"]=True

                        
                    # if st.session_state["del_bl"]==True:
                    delete_bl=ecol5.popover("❌ Delete Records",use_container_width=True)

                    # del_cnf = ecol4.container(border=1)
                    # del_cnf.write("Are you sure you wish to delete?")
                    # colf1,colf2=del_cnf.columns([1,1])
                    del_yes = delete_bl.button("✅ Confirm",type="primary",use_container_width=True)
                    del_no = delete_bl.button("❌ Cancel",use_container_width=True)
                
                    if del_yes:
                        
                        # ecol4.info("Deleting...")
                        st.toast(f'Deleting BL ...', icon='🎈')
                        st.session_state.del_yes=True
                        # st.session_state["del_bl"]=False
                        
                    if del_no:
                        # ecol4.info("Cancelling...")
                        st.toast(f'Cancelling...', icon='🎈')
                        # st.session_state["del_bl"]=False
                        mess="Cancelled Delete"
                        vi.msg_success(True,mess)

                        
                    if st.session_state.del_yes==True:
                        st.session_state.del_yes=False
                    

                        uid_list=[]
                        
                        uid_str=''
                        flg=False
                    
                        for index, row in selected_rows.iterrows():
                            # some case missing bl (1-Oct-24)
                            #if row['BL']:
                            uid= row['uid']
                            
                            uid_list.append(uid)
                            uid_str = ', '.join([f"'{item}'" for item in uid_list])
                        

                        flg,e,time_cm=qr.delete_record(False,st.session_state.DB,st.session_state.DATABASE,True,f"scm_dimaccess","uid",uid_str)
                        time.sleep(1)

                        # final cnf
                        if flg==True:
                            st.session_state.userOut=False
                            mess=f"{len(selected_rows)} records deleted successfully!!!"
                            logging.info("%s :: Delete Multiple User %s",USERID,mess)
                            st.success(mess)
                            # qr.insert_log(st.session_state.DB,st.session_state.DATABASE,  f'mtlt_{st.session_state.origin}_factlog',str(bl_list), None, str(vsl_dict), str(voy_dict), str(arr_dict), None, "Delete Multiple BL", mess + '|' + selected_rows.to_json(orient='records', lines=True),time_cm)
                            #vi.msg_success(True,mess)

                        else:
                            mess=f"Failed!!! Error: {e}"
                            logging.info("%s :: Delete Multiple User %s",USERID,mess)
                            st.error(mess)
                            #qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'mtlt_{st.session_state.origin}_factlog', str(bl_list), None, str(vsl_dict), str(voy_dict), str(arr_dict), None, "Delete Multiple BL", mess+ '|' + selected_rows.to_json(orient='records', lines=True),time_cm)
                            #vi.msg_error(True,mess)


        



else:
    st.warning('You dont have permisson for this page',icon="⚠️")

