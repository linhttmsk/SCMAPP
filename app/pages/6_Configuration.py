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
from datetime import datetime
from configparser import ConfigParser
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import xlwings as xw
import base64 
import random
from src.auth import login,initiateApp
import src.view as vi
from src.log import logIni
import src.query as qr
import src.ulti as ut
import json





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




def main():

    global  time_cm,cookies

    # 0. Configuration
    vi.appConfig("Container List","visible","expanded")

    # 1. Login
    cookies = CookieManager()
    initiateApp(USERID,cookies,APPVERSION)


    # 2. Page Content

    menu = [":blue[*Booking Validation Source Config*]",":blue[*Booking Validation Source Relation*]", ":blue[*Booking Validation Logic*]"]
    options = st.sidebar.radio("Select an Option :dart:",menu)

    if options==":blue[*Booking Validation Source Config*]":
        
        tab1,tab2=st.tabs([":clipboard: Source Config","📑 Batch Upload"])

        with tab1:

            with st.expander(":mag_right: *Search Panel*",expanded=True):
                s2_col1,s2_col2,s2_col3,s2_col4=st.columns([1,1,1,1])
                s_col1,s_col2,s_col3,s_col4,s_col5=st.columns([1,1,0.5,0.5,2])

                search_pop=s_col1.popover("📑Search Mode",use_container_width=True)
                menu_search_sc = ["Wildcard","Multiple","Show all"]
                search_opt = search_pop.radio(" ",menu_search_sc,horizontal=True,label_visibility='collapsed')
                
                bt_search_sc=s_col3.button(":mag_right:",key="bt_search_sc",use_container_width=True)
                bt_clear_sc=s_col4.button("❌",key="bt_clear_sc",use_container_width=True)

            if "search_sc" not in st.session_state:
                st.session_state.search_sc=""
            if "clear_sc" not in st.session_state:
                st.session_state.clear_sc=False
            if "template" not in st.session_state:
                st.session_state.template=""
            if "source" not in st.session_state:
                st.session_state.source=""
            if "sheet" not in st.session_state:
                st.session_state.sheet=""
            
            if "sc_out" not in st.session_state:
                st.session_state.sc_out=""

            if "sc_col" not in st.session_state:
                st.session_state.sc_col=""

            if "keyi" not in st.session_state:
                st.session_state.keyi=0

            results=None
            query=None

            if search_opt== "Show all":
                s_col2.button(":blue[✅ Show all]",disabled=True,use_container_width=True)
                if bt_search_sc:
                    st.session_state.search_sc="Show all"
                    st.session_state.clear_sc=False
                    st.session_state.sc_out=False

                if bt_clear_sc:
                    st.session_state.clear_sc=True
                    st.session_state.search_sc=""
                    st.session_state.sc_out=False

                if st.session_state.search_sc=="Show all":
                    query = f"SELECT * FROM scm_{st.session_state.origin}_bkValidationSourceConfig"

            elif search_opt== "Multiple":
                s_col2.button(":blue[✅ Multiple]",disabled=True,use_container_width=True)
                

                if bt_search_sc:
                    st.session_state.search_sc="Multiple"
                    st.session_state.clear_sc=False
                    st.session_state.sc_out=False

                if bt_clear_sc:
                    st.session_state.clear_sc=True
                    st.session_state.keyi+=1
                    st.session_state.search_sc=""
                    st.session_state.sc_out=False
                    
                if st.session_state.clear_sc==True:
                    search_temp=s2_col1.text_input("Template",key="search_tempsc_m"+ str(st.session_state.keyi),value='')
                    st.session_state.template=search_temp
                    search_source=s2_col2.text_input("Source",key="search_sourcesc_m"+ str(st.session_state.keyi),value='')
                    st.session_state.source=search_source
                    search_sheet=s2_col3.text_input("Sheet",key="search_sheetsc_m"+ str(st.session_state.keyi),value='')
                    st.session_state.sheet=search_sheet
                    
                else:
                    search_temp=s2_col1.text_input("Template",key="search_tempsc_m",value=st.session_state.template)
                    search_source=s2_col2.text_input("Source",key="search_sourcesc_m",value=st.session_state.source)
                    search_sheet=s2_col3.text_input("Sheet",key="search_sheetsc_m",value=st.session_state.sheet)

                if st.session_state.search_sc=="Multiple":
                    # Split the string into a list of values
                    search_temp = search_temp.split(',')
                    search_source = search_source.split(',')
                    search_sheet = search_sheet.split(',')
                    
                    # Enclose each value with single quotes
                    search_temp = ",".join(f"'{value.strip()}'" for value in search_temp)
                    search_source = ",".join(f"'{value.strip()}'" for value in search_source)
                    search_sheet = ",".join(f"'{value.strip()}'" for value in search_sheet)
                    
                    query = f"SELECT * FROM scm_{st.session_state.origin}_bkValidationSourceConfig WHERE"

                    if search_temp!="''":
                        query = f"{query} AND Template IN ({search_temp})"
                    if search_source!="''":
                        query = f"{query} AND SourceName IN ({search_source})"
                    if search_sheet!="''":
                        query = f"{query} AND SheetName IN ({search_sheet})"
                        

            else:
                s_col2.button(":blue[✅ Wildcard]",disabled=True,use_container_width=True)


                if bt_search_sc:
                    st.session_state.search_sc="Wildcard"
                    st.session_state.clear_sc=False
                    st.session_state.sc_out=False

                if bt_clear_sc:
                    st.session_state.clear_sc=True
                    st.session_state.keyi+=1
                    st.session_state.search_sc=""
                    st.session_state.sc_out=False
                    
                if st.session_state.clear_sc==True:
                    search_temp=s2_col1.text_input("Template",key="search_tempsc_w"+ str(st.session_state.keyi),value='')
                    st.session_state.template=search_temp
                    search_source=s2_col2.text_input("SourceName",key="search_sourcesc_w"+ str(st.session_state.keyi),value='')
                    st.session_state.source=search_source
                    search_sheet=s2_col3.text_input("SheetName",key="search_sheetsc_w"+ str(st.session_state.keyi),value='')
                    st.session_state.sheet=search_sheet
                    
                else:
                    search_temp=s2_col1.text_input("Template",key="search_tempsc_w",value=st.session_state.template)
                    search_source=s2_col2.text_input("SourceName",key="search_sourcesc_w",value=st.session_state.source)
                    search_sheet=s2_col3.text_input("SheetName",key="search_sheetsc_w",value=st.session_state.sheet)


                if st.session_state.search_sc=="Wildcard":
                    query = f"SELECT * FROM scm_{st.session_state.origin}_bkValidationSourceConfig WHERE"

                    if search_temp!="":
                        query = f"{query} AND Template LIKE '%{search_temp}%'"
                    if search_source!="":
                        query = f"{query} AND SourceName LIKE '%{search_source}%'"
                    if search_sheet!="":
                        query = f"{query} AND SheetName LIKE '%{search_sheet}%'"
                                        

            if query and not query.endswith('WHERE'):
                if st.session_state.sc_out==False:
                    query=query.replace("WHERE AND","WHERE")
                    if st.session_state.isDev:
                        st.write(query)     
                    results,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,query)
                    st.session_state.sc_out=results
                    st.session_state.sc_col=columns

                    
                if not st.session_state.sc_out:
                    st.info("No records found",icon='ℹ')
                else:
                    st.info(f"**[   :red[{len(st.session_state.sc_col)}]   ]**  Records found. Please select at least 1 record",icon='⭐') 
                    # Create a DataFrame with the results and column name
                    df = pd.DataFrame.from_records(st.session_state.sc_out, columns=st.session_state.sc_col)

                    selected_rows=0
                    with st.expander(":bookmark_tabs: *Table Result*",expanded=True):
                        ecol1,ecol2,ecol3,ecol5=st.columns([0.7,1,1,1])
                        select_all = ecol1.checkbox('Select All')
                        if select_all:
                            tbl=st.dataframe(df,height=300)
                            selected_rows=df
                            idx=df.index
                        
                        else:      
                            selected_rows,idx = vi.dataframe_with_selections(df)
                        # st.write(len(results), "Records found")
                            

                    if len(selected_rows)==1:
                        ecol2.write(f":blue[📌 **[ :red[1] ]** *record selected*]")  
                        form_exp=st.expander(":book: *Source Config Form*",expanded=True)
                        #clear_on_submit=False
                        fr1=form_exp.form("sourceconfig")
                        fr1_cont1=fr1.container()
                        fr1_cont2=fr1.container()
                        
                        # if "button_clicked" not in st.session_state:
                        #     st.session_state.button_clicked = False

                        fr1_cont1_col1, fr1_cont1_col2 ,fr1_cont1_col3,fr1_cont1_col4= fr1_cont1.columns([1,1,1.2,1.2])
                        submit_new=fr1_cont1_col1.form_submit_button("✔️Submit New",use_container_width=True)
                        submit_edit=fr1_cont1_col2.form_submit_button("✔️Submit Edit",use_container_width=True)
                        
                        
                        fr1_cont2_col1,fr1_cont2_col2,fr1_cont2_col3=fr1_cont2.columns(3)

                        idv=fr1_cont2_col1.text_input("Template",key = "temp_e",value=selected_rows['Template'][idx[0]])
                        source=fr1_cont2_col2.text_input("SourceName",key = "source_e",value=selected_rows['SourceName'][idx[0]])  
                        sheet=fr1_cont2_col3.text_input("SheetName",key = "sheet_e",value=selected_rows['SheetName'][idx[0]])  
                        column=fr1_cont2_col3.text_input("ColumnName",key = "column_e",value=selected_rows['ColumnName'][idx[0]])  
                        # submit new
                        if submit_new:
                            st.toast("Submitting new ...",icon='🎈')
                            if idv:

                                select_query = f"""
                                SELECT * FROM scm_{st.session_state.origin}_bkValidationSourceConfig WHERE TempSourceSheetColumn= '{idv}{source}{sheet}{column}'
                                """
                                existing_sc,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,select_query)
                                
                                if existing_sc:
                                    mess="Combination already exist"
                                    vi.msg_error(True,mess)
                                    
                                else:  
                                    flg,e,time_cm=qr.insert_bkValidationSourceConfig(True,st.session_state.DB,st.session_state.DATABASE,f'scm_{st.session_state.origin}_bkValidationSourceConfig' , idv, source,sheet,column)
                                    if flg==True:
                                        # # Lists of keys and values
                                        # keys = ['id', 'name','full']
                                        # values = [code, name,full]
                                        # # Create a dictionary using zip
                                        # dictionary = dict(zip(keys, values))
                                        st.session_state.sc_out=False
                                        logging.info("%s :: Insert Source Config %s",USERID, f"{idv}{source}{sheet}{column} Inserted successfully ^^")
                                        qr.insert_log(st.session_state.DB,st.session_state.DATABASE,f'scm_{st.session_state.origin}_factlog', "Insert Source Config", f"{idv}{source}{sheet}{column} Inserted successfully ^^",time_cm)

                            else:
                                mess="Template is blank"
                                vi.msg_error(True,mess)

                                    
                        # submit edit
                        if submit_edit:
                            st.toast("Submitting edit ...",icon='🎈')
                            select_query = f"""
                            SELECT * FROM scm_{st.session_state.origin}_bkValidationSourceConfig WHERE TempSourceSheetColumn = '{idv}{source}{sheet}{column}'
                            """
                            existing_sc,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,select_query)
                            
                            if not existing_sc:
                                mess="Combination is not existing"
                                vi.msg_error(True,mess)
                                
                            else:  
                                flg,e,time_cm=qr.update_bkValidationSourceConfig(True,st.session_state.DB,st.session_state.DATABASE,f'scm_{st.session_state.origin}_kValidationSourceConfig' ,idv, source, sheet,column)
                                if flg==True:
                                    # # Lists of keys and values
                                    # keys = ['code', 'name', 'full']
                                    # values = [code, name, full]

                                    # # Create a dictionary using zip
                                    # dictionary = dict(zip(keys, values))
                                    st.session_state.sc_out=False
                                    logging.info("%s :: Update Source Config %s",USERID, f"{idv}{source}{sheet}{column} Updated successfully ^^")
                                    qr.insert_log(st.session_state.DB,st.session_state.DATABASE,f'scm_{st.session_state.origin}_factlog', "Update Source Config", f"{idv}{source}{sheet}{column} Updated successfully ^^",time_cm)



                    
                        if "del_yes" not in st.session_state:
                            st.session_state.del_yes=False


                        delete_sc=fr1_cont1_col3.popover("❌ Delete Record",use_container_width=True)
                        del_yes = delete_sc.form_submit_button("✅ Confirm",type="primary",use_container_width=True)
                        del_no = delete_sc.form_submit_button("❌ Cancel",use_container_width=True)
                        
                        if del_yes:
                            st.toast("Deletting ...", icon='🎈')
                            st.session_state.del_yes=True

                            
                        if del_no:
                            st.toast("Cancelling ...", icon='🎈')
                            mess="Cancelled Delete"
                            vi.msg_success(True,mess)

                        
                        if st.session_state.del_yes==True:
                            st.session_state.del_yes=False
                            for index, row in selected_rows.iterrows():
                            
                                if row['Code']:
                        
                                    flg,e,time_cm=qr.delete_record(True,st.session_state.DB,st.session_state.DATABASE,False,f"scm_{st.session_state.origin}_bkValidatorSourceConfig","TempSourceSheetColumn",f"{idv}{source}{sheet}{column}")
                                    
                                    if flg==True:
                                        st.session_state.sc_out=False
                                        logging.info("%s :: Delete Source Config %s",USERID, f"{idv}{source}{sheet}{column} Deleted successfully ^^")
                                        qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_factlog', "Delete Source Config", f"{code} Deleted successfully ^^",time_cm)
                        

                    elif len(selected_rows)>1:
                        ecol2.write(f":blue[📌 **[ :red[{len(selected_rows)}] ]** *records selected*]")  


                        if "del_yes" not in st.session_state:
                            st.session_state.del_yes=False

                        delete_sc=ecol5.popover("❌ Delete Records",use_container_width=True)
                        del_yes = delete_sc.button("✅ Confirm",type="primary",use_container_width=True)
                        del_no = delete_sc.button("❌ Cancel",use_container_width=True)
                        
                        if del_yes:
                            st.toast("Deletting ...", icon='🎈')
                            st.session_state.del_yes=True
                            
                        if del_no:
                            st.toast("Cancelling ...", icon='🎈')
                            mess="Cancelled Delete"
                            vi.msg_success(True,mess)

                        if st.session_state.del_yes==True:
                            st.session_state.del_yes=False

                            flg=False
                            code_list=[]
                            code_str=''

                            for index, row in selected_rows.iterrows():
                                
                                if row['TempSourceSheetColumn']:
                                    code= row['TempSourceSheetColumn']
                                    code_list.append(code)
                                    #coonvert list to string with ' begin and end of each item
                                    code_str = ', '.join([f"'{item}'" for item in code_list])

                            flg,e,time_cm=qr.delete_record(False,st.session_state.DB,st.session_state.DATABASE,True,f"scm_{st.session_state.origin}_bkValidatorSourceConfig","TempSourceSheetColumn",code_str)

                            
                            if flg==True:
                                st.session_state.sc_out=False
                                mess=f"{len(selected_rows)} records deleted successfully!!!"
                                code_list=str(list(selected_rows['TempSourceSheetColumn']))
                                logging.info("%s :: Deleted Multiple Source Config %s",USERID,mess)
                                qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_factlog', "Deleted Multiple Source Config", mess ,time_cm)
                                vi.msg_success(True,mess)

                                            
                            else:
                                mess=f"Failed!!! Error: {e}" 
                                code_list=str(list(selected_rows['TempSourceSheetColumn']))
                                logging.info("%s :: Deleted Multiple Source Config  %s",USERID,mess)
                                qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_factlog',"Deleted Multiple Source Config", mess,time_cm)
                                vi.msg_error(True,mess)




        with tab2:

            with st.expander(":hand: *Command Button*",expanded=True):
                conttb1,conttb2=st.columns([1,4])
                submit_sc=conttb1.button("✔️Submit Table",key="submit_nsc",use_container_width=True)
            
            if "sct_col" not in st.session_state:
                st.session_state.sct_col=False
            

            if st.session_state.sct_col==False:
                #query cont
                query_sc = f"SELECT * FROM scm_{st.session_state.origin}_bkValidationSourceConfig WHERE TempSourceSheetColumn='123'"

                results,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,query_sc)
                columns=columns[1:-4]
                st.session_state.sct_col=columns



            if st.session_state.sct_col:
                with st.expander(":book: *Table Input*",expanded=True):
                    # df=pd.DataFrame.from_records(results_cont, columns=columns_cont,)
                    edited_df = st.data_editor(pd.DataFrame.from_records("", columns=st.session_state.sct_col),num_rows="dynamic")
        

                if submit_sc:
                    st.toast("Submitting ...",icon='🎈')
                    if edited_df["Template"].count()>0:
                        # statusbar
                        progress_text = "Operation in progress. Please wait."
                        my_bar = st.progress(0, text=progress_text)
                        percent_complete=0
                        flg=False
                        ok_flg=False
                        err_flg=False
                        rc_fail=0
                        rc_ok=0

                        sc_err={}


                        for index, row in edited_df.iterrows():
                        
                            # st.write(index)
                            # st.write(row['Booking'])
                            if row['Template']:  
                                select_query = f"""
                                SELECT * FROM scm_{st.session_state.origin}_bkValidationSourceConfig WHERE TempSourceSheetColumn = '{row['Template']}{row['SourceName']}{row['SheetName']}{row['ColumnName']}'
                                """ 
                                existing,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,select_query)
                                if existing:
                                    
                                    flg,e,time_cm=   qr.update_bkValidationSourceConfig(False,st.session_state.DB, st.session_state.DATABASE,f'scm_{st.session_state.origin}_bkValidationSourceConfig' ,row["Template"], row["SourceName"], row["SheetName"],row["ColumnName"])
                                    
                                    if flg==True:
                                        ok_flg=True
                                        rc_ok+=1
                                    else:
                                        err_flg=True
                                        sc_err[f"{row['Template']}{row['SourceName']}{row['SheetName']}{row['ColumnName']}"]=e
                                        rc_fail+=1
                                        
                                else:
                                    
                                    flg,e,time_cm= qr.insert_bkValidationSourceConfig(False,st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_bkValidationSourceConfig', row["Template"], row["SourceName"], row["SheetName"],row["ColumnName"])
                                    if flg==True:
                                        ok_flg=True
                                        rc_ok+=1
                                    else:
                                        err_flg=True
                                        sc_err[f"{row['Template']}{row['SourceName']}{row['SheetName']}{row['ColumnName']}"]=e
                                        rc_fail+=1
                                        
                            # time.sleep(0.01)
                            prop=1/len(edited_df)* 100
                            percent_complete+=prop
                            my_bar.progress(int(percent_complete), text=f"*{progress_text}>> exported :red[**{rc_ok}/{len(edited_df)}**] records <<>>  :blue[**{row['Template']}{row['SourceName']}{row['SheetName']}{row['ColumnName']}**] <<*")

                        
                        if ok_flg==True and err_flg!=True and rc_fail==0:
                            mess=f"Imported successfully!!! {rc_ok} records"
                            
                            logging.info("%s :: Upload Source Config Table %s",USERID,mess)
                            qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_factlog', "Upload Source Config Table", mess,time_cm)
                            vi.msg_success(True,mess)
                            

                        elif rc_ok==0:
                            mess="No records imported"
                            logging.info("%s :: Upload Source Config Table %s",USERID,mess)
                            qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_factlog', "Upload Source Config Table", mess,time_cm)
                            vi.msg_error(True,mess)
                                            
                        else:
                            mess=f"Imported {rc_ok} records. Failed import for {rc_fail} records: {sc_err}"
                            logging.info("%s :: Upload Source Config Table %s",USERID,mess)
                            qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_factlog', "Upload Source Config Table", mess,time_cm)
                            vi.msg_error(True,mess)
                        

                    else:
                        st.warning('Please input data',icon="⚠️") 




    elif options==":blue[*Booking Validation Source Relation*]":
        
        tab1,tab2=st.tabs([":clipboard: Source Relation","📑 Batch Upload"])

        with tab1:

            with st.expander(":mag_right: *Search Panel*",expanded=True):
                s2_col1,s2_col2,s2_col3,s2_col4=st.columns([1,1,1,1])
                s_col1,s_col2,s_col3,s_col4,s_col5=st.columns([1,1,0.5,0.5,2])

                search_pop=s_col1.popover("📑Search Mode",use_container_width=True)
                menu_search_sr = ["Wildcard","Multiple","Show all"]
                search_opt = search_pop.radio(" ",menu_search_sr,horizontal=True,label_visibility='collapsed')
                
                bt_search_sr=s_col3.button(":mag_right:",key="bt_search_sr",use_container_width=True)
                bt_clear_sr=s_col4.button("❌",key="bt_clear_sr",use_container_width=True)

            if "search_sr" not in st.session_state:
                st.session_state.search_sr=""
            if "clear_sr" not in st.session_state:
                st.session_state.clear_sr=False
            if "template" not in st.session_state:
                st.session_state.template=""
            if "source" not in st.session_state:
                st.session_state.source=""
            
            if "sr_out" not in st.session_state:
                st.session_state.sr_out=""

            if "sr_col" not in st.session_state:
                st.session_state.sr_col=""

            if "keyi" not in st.session_state:
                st.session_state.keyi=0

            results=None
            query=None


            if search_opt== "Show all":
                s_col2.button(":blue[✅ Show all]",disabled=True,use_container_width=True)
                if bt_search_sr:
                    st.session_state.search_sr="Show all"
                    st.session_state.clear_sr=False
                    st.session_state.sr_out=False

                if bt_clear_sr:
                    st.session_state.clear_sr=True
                    st.session_state.search_sr=""
                    st.session_state.sr_out=False

                if st.session_state.search_sr=="Show all":
                    query = f"SELECT * FROM scm_{st.session_state.origin}_bkValidationSourceRelation"

            elif search_opt== "Multiple":
                s_col2.button(":blue[✅ Multiple]",disabled=True,use_container_width=True)
                

                if bt_search_sr:
                    st.session_state.search_sr="Multiple"
                    st.session_state.clear_sr=False
                    st.session_state.sr_out=False

                if bt_clear_sr:
                    st.session_state.clear_sr=True
                    st.session_state.keyi+=1
                    st.session_state.search_sr=""
                    st.session_state.sr_out=False
                    
                if st.session_state.clear_sr==True:
                    search_temp=s2_col1.text_input("Template",key="search_tempsr_m"+ str(st.session_state.keyi),value='')
                    st.session_state.template=search_temp
                    search_source=s2_col2.text_input("Source1",key="search_sourcesr_m"+ str(st.session_state.keyi),value='')
                    st.session_state.source=search_source
                    
                else:
                    search_temp=s2_col1.text_input("Template",key="search_tempsr_m",value=st.session_state.template)
                    search_source=s2_col2.text_input("Source1",key="search_sourcesr_m",value=st.session_state.source)
                    
                if st.session_state.search_sr=="Multiple":
                    # Split the string into a list of values
                    search_temp = search_temp.split(',')
                    search_source = search_source.split(',')
                    
                    # Enclose each value with single quotes
                    search_temp = ",".join(f"'{value.strip()}'" for value in search_temp)
                    search_source = ",".join(f"'{value.strip()}'" for value in search_source)
                        
                    query = f"SELECT * FROM scm_{st.session_state.origin}_bkValidationSourceRelation WHERE"

                    if search_temp!="''":
                        query = f"{query} AND Template IN ({search_temp})"
                    if search_source!="''":
                        query = f"{query} AND SourceName1 IN ({search_source})"
                        

            else:
                s_col2.button(":blue[✅ Wildcard]",disabled=True,use_container_width=True)
                

                if bt_search_sr:
                    st.session_state.search_sr="Wildcard"
                    st.session_state.clear_sr=False
                    st.session_state.sc_out=False

                if bt_clear_sr:
                    st.session_state.clear_sr=True
                    st.session_state.keyi+=1
                    st.session_state.search_sr=""
                    st.session_state.sc_out=False
                    
                if st.session_state.clear_sr==True:
                    search_temp=s2_col1.text_input("Template",key="search_tempsr_w"+ str(st.session_state.keyi),value='')
                    st.session_state.template=search_temp
                    search_source=s2_col2.text_input("SourceName1",key="search_sourcesr_w"+ str(st.session_state.keyi),value='')
                    st.session_state.source=search_source
                    
                else:
                    search_temp=s2_col1.text_input("Template",key="search_tempsr_w",value=st.session_state.template)
                    search_source=s2_col2.text_input("SourceName1",key="search_sourcesr_w",value=st.session_state.source)
                    

                if st.session_state.search_sr=="Wildcard":
                    query = f"SELECT * FROM scm_{st.session_state.origin}_bkValidationSourceRelation WHERE"

                    if search_temp!="":
                        query = f"{query} AND Template LIKE '%{search_temp}%'"
                    if search_source!="":
                        query = f"{query} AND SourceName1 LIKE '%{search_source}%'"
                                        

            if query and not query.endswith("WHERE"):
                if st.session_state.sr_out==False:
                    query=query.replace("WHERE AND","WHERE")
                    if st.session_state.isDev:
                        st.write(query)    
                    results,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,query)
                    st.session_state.sr_out=results
                    st.session_state.sr_col=columns

                    
                if not st.session_state.sr_out:
                    st.info("No records found",icon='ℹ')
                else:
                    st.info(f"**[   :red[{len(st.session_state.sr_out)}]   ]**  Records found. Please select at least 1 record",icon='⭐') 
                    # Create a DataFrame with the results and column name
                    df = pd.DataFrame.from_records(st.session_state.sr_out, columns=st.session_state.sr_col)

                    selected_rows=0
                    with st.expander(":bookmark_tabs: *Table Result*",expanded=True):
                        ecol1,ecol2,ecol3,ecol5=st.columns([0.7,1,1,1])
                        select_all = ecol1.checkbox('Select All')
                        if select_all:
                            tbl=st.dataframe(df,height=300)
                            selected_rows=df
                            idx=df.index
                        
                        else:      
                            selected_rows,idx = vi.dataframe_with_selections(df)
                        # st.write(len(results), "Records found")
                            

                    if len(selected_rows)==1:
                        ecol2.write(f":blue[📌 **[ :red[1] ]** *record selected*]")  
                        form_exp=st.expander(":book: *Source Config Form*",expanded=True)
                        #clear_on_submit=False
                        fr1=form_exp.form("sourceconfig")
                        fr1_cont1=fr1.container()
                        fr1_cont2=fr1.container()
                        
                        # if "button_clicked" not in st.session_state:
                        #     st.session_state.button_clicked = False

                        fr1_cont1_col1, fr1_cont1_col2 ,fr1_cont1_col3,fr1_cont1_col4= fr1_cont1.columns([1,1,1.2,1.2])
                        submit_new=fr1_cont1_col1.form_submit_button("✔️Submit New",use_container_width=True)
                        submit_edit=fr1_cont1_col2.form_submit_button("✔️Submit Edit",use_container_width=True)
                        
                        
                        fr1_cont2_col1,fr1_cont2_col2,fr1_cont2_col3=fr1_cont2.columns(3)

                        idv=fr1_cont2_col1.text_input("Template",key = "temp_e",value=selected_rows['Template'][idx[0]])
                        source1=fr1_cont2_col2.text_input("SourceName1",key = "source1_e",value=selected_rows['SourceName1'][idx[0]])  
                        pkey1=fr1_cont2_col3.text_input("PKey1",key = "pkey1_e",value=selected_rows['PKey1'][idx[0]])  
                        fkey1=fr1_cont2_col1.text_input("FKey1",key = "fkey1_e",value=selected_rows['FKey1'][idx[0]])
                        source2=fr1_cont2_col2.text_input("SourceName2",key = "source2_e",value=selected_rows['SourceName2'][idx[0]])  
                        fkey2=fr1_cont2_col3.text_input("FKey2",key = "fkey2_e",value=selected_rows['FKey2'][idx[0]])

                        # submit new
                        if submit_new:
                            st.toast("Submitting new ...",icon='🎈')
                            if idv:

                                select_query = f"""
                                SELECT * FROM scm_{st.session_state.origin}_bkValidationSourceRelation WHERE TempSource1Source2= '{idv}{source1}{source2}'
                                """
                                existing_sr,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,select_query)
                                
                                if existing_sr:
                                    mess="Combination already exist"
                                    vi.msg_error(True,mess)
                                    
                                else:  
                                    flg,e,time_cm=qr.insert_bkValidationSourceRelation(True,st.session_state.DB,st.session_state.DATABASE,f'scm_{st.session_state.origin}_bkValidationSourceRelation' , idv, source1,pkey1,fkey1,source1,fkey2)
                                    if flg==True:
                                        # # Lists of keys and values
                                        # keys = ['id', 'name','full']
                                        # values = [code, name,full]
                                        # # Create a dictionary using zip
                                        # dictionary = dict(zip(keys, values))
                                        st.session_state.sr_out=False
                                        logging.info("%s :: Insert Source Relation %s",USERID, f"{idv}{source1}{source2} Inserted successfully ^^")
                                        qr.insert_log(st.session_state.DB,st.session_state.DATABASE,f'scm_{st.session_state.origin}_factlog', "Insert Source Relation", f"{idv}{source1}{source2} Inserted successfully ^^",time_cm)

                            else:
                                mess="Template is blank"
                                vi.msg_error(True,mess)

                                    
                        # submit edit
                        if submit_edit:
                            st.toast("Submitting edit ...",icon='🎈')
                            select_query = f"""
                            SELECT * FROM scm_{st.session_state.origin}_bkValidationSourceRelation WHERE TempSource1Source2 = '{idv}{source1}{source2}'
                            """
                            existing_sr,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,select_query)
                            
                            if not existing_sr:
                                mess="Combination is not existing"
                                vi.msg_error(True,mess)
                                
                            else:  
                                flg,e,time_cm=qr.update_bkValidationSourceRelation(True,st.session_state.DB,st.session_state.DATABASE,f'scm_{st.session_state.origin}_bkValidationSourceRelation' ,idv, source1, pkey1,fkey1,source2,fkey2)
                                if flg==True:
                                    # # Lists of keys and values
                                    # keys = ['code', 'name', 'full']
                                    # values = [code, name, full]

                                    # # Create a dictionary using zip
                                    # dictionary = dict(zip(keys, values))
                                    st.session_state.sr_out=False
                                    logging.info("%s :: Update Source Relation %s",USERID, f"{idv}{source1}{source2} Updated successfully ^^")
                                    qr.insert_log(st.session_state.DB,st.session_state.DATABASE,f'scm_{st.session_state.origin}_factlog', "Update Source Relation", f"{idv}{source1}{source2} Updated successfully ^^",time_cm)



                    
                        if "del_yes" not in st.session_state:
                            st.session_state.del_yes=False


                        delete_sr=fr1_cont1_col3.popover("❌ Delete Record",use_container_width=True)
                        del_yes = delete_sr.form_submit_button("✅ Confirm",type="primary",use_container_width=True)
                        del_no = delete_sr.form_submit_button("❌ Cancel",use_container_width=True)
                        
                        if del_yes:
                            st.toast("Deletting ...", icon='🎈')
                            st.session_state.del_yes=True

                            
                        if del_no:
                            st.toast("Cancelling ...", icon='🎈')
                            mess="Cancelled Delete"
                            vi.msg_success(True,mess)

                        
                        if st.session_state.del_yes==True:
                            st.session_state.del_yes=False
                            for index, row in selected_rows.iterrows():
                            
                                if row['TempSource1Source2']:
                        
                                    flg,e,time_cm=qr.delete_record(True,st.session_state.DB,st.session_state.DATABASE,False,f"scm_{st.session_state.origin}_bkValidationSourceRelation","TempSource1Source2",f"{idv}{source1}{source2}")
                                    
                                    if flg==True:
                                        st.session_state.sr_out=False
                                        logging.info("%s :: Delete Source Relation %s",USERID, f"{idv}{source1}{source2} Deleted successfully ^^")
                                        qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_factlog', "Delete Source Config", f"{idv}{source1}{source2} Deleted successfully ^^",time_cm)
                        

                    elif len(selected_rows)>1:
                        ecol2.write(f":blue[📌 **[ :red[{len(selected_rows)}] ]** *records selected*]")  


                        if "del_yes" not in st.session_state:
                            st.session_state.del_yes=False

                        delete_sr=ecol5.popover("❌ Delete Records",use_container_width=True)
                        del_yes = delete_sr.button("✅ Confirm",type="primary",use_container_width=True)
                        del_no = delete_sr.button("❌ Cancel",use_container_width=True)
                        
                        if del_yes:
                            st.toast("Deletting ...", icon='🎈')
                            st.session_state.del_yes=True
                            
                        if del_no:
                            st.toast("Cancelling ...", icon='🎈')
                            mess="Cancelled Delete"
                            vi.msg_success(True,mess)

                        if st.session_state.del_yes==True:
                            st.session_state.del_yes=False

                            flg=False
                            code_list=[]
                            code_str=''

                            for index, row in selected_rows.iterrows():
                                
                                if row['TempSource1Source2']:
                                    code= row['TempSource1Source2']
                                    code_list.append(code)
                                    #coonvert list to string with ' begin and end of each item
                                    code_str = ', '.join([f"'{item}'" for item in code_list])

                            flg,e,time_cm=qr.delete_record(False,st.session_state.DB,st.session_state.DATABASE,True,f"scm_{st.session_state.origin}_bkValidatorSourceRelation","TempSource1Source2",code_str)

                            
                            if flg==True:
                                st.session_state.sc_out=False
                                mess=f"{len(selected_rows)} records deleted successfully!!!"
                                code_list=str(list(selected_rows['TempSource1Source2']))
                                logging.info("%s :: Deleted Multiple Source Relation %s",USERID,mess)
                                qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_factlog', "Deleted Multiple Source Relation", mess ,time_cm)
                                vi.msg_success(True,mess)

                                            
                            else:
                                mess=f"Failed!!! Error: {e}" 
                                code_list=str(list(selected_rows['TempSourceSheetColumn']))
                                logging.info("%s :: Deleted Multiple Source Relation  %s",USERID,mess)
                                qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_factlog',"Deleted Multiple Source Relation", mess,time_cm)
                                vi.msg_error(True,mess)



        


        with tab2:

            with st.expander(":hand: *Command Button*",expanded=True):
                conttb1,conttb2=st.columns([1,4])
                submit_sr=conttb1.button("✔️Submit Table",key="submit_nsr",use_container_width=True)
            
            if "srt_col" not in st.session_state:
                st.session_state.srt_col=False
            

            if st.session_state.srt_col==False:
                #query cont
                query_sr = f"SELECT * FROM scm_{st.session_state.origin}_bkValidationSourceRelation WHERE TempSource1Source2='123'"

                results,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,query_sr)
                columns=columns[1:-4]
                st.session_state.srt_col=columns



            if st.session_state.srt_col:
                with st.expander(":book: *Table Input*",expanded=True):
                    # df=pd.DataFrame.from_records(results_cont, columns=columns_cont,)
                    edited_df = st.data_editor(pd.DataFrame.from_records("", columns=st.session_state.srt_col),num_rows="dynamic")
        

                if submit_sr:
                    st.toast("Submitting ...",icon='🎈')
                    if edited_df["Template"].count()>0:
                        # statusbar
                        progress_text = "Operation in progress. Please wait."
                        my_bar = st.progress(0, text=progress_text)
                        percent_complete=0
                        flg=False
                        ok_flg=False
                        err_flg=False
                        rc_fail=0
                        rc_ok=0

                        sc_err={}


                        for index, row in edited_df.iterrows():
                        
                            # st.write(index)
                            # st.write(row['Booking'])
                            if row['Template']:  
                                select_query = f"""
                                SELECT * FROM scm_{st.session_state.origin}_bkValidationSourceRelation WHERE TempSource1Source2 = '{row['Template']}{row['SourceName1']}{row['SourceName2']}'
                                """ 
                                existing,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,select_query)
                                if existing:
                                    
                                    flg,e,time_cm=   qr.update_bkValidationSourceRelation(False,st.session_state.DB, st.session_state.DATABASE,f'scm_{st.session_state.origin}_bkValidationSourceRelation' ,row["Template"], row["SourceName1"], row["PKey1"], row["FKey1"], row["SourceName2"], row["PKey2"])
                                    
                                    if flg==True:
                                        ok_flg=True
                                        rc_ok+=1
                                    else:
                                        err_flg=True
                                        sc_err[f"{row['Template']}{row['SourceName1']}{row['SourceName2']}"]=e
                                        rc_fail+=1
                                        
                                else:
                                    
                                    flg,e,time_cm= qr.insert_bkValidationSourceRelation(False,st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_bkValidationSourceRelation', row["Template"], row["SourceName1"], row["PKey1"], row["FKey1"], row["SourceName2"], row["FKey2"])
                                    if flg==True:
                                        ok_flg=True
                                        rc_ok+=1
                                    else:
                                        err_flg=True
                                        sc_err[f"{row['Template']}{row['SourceName1']}{row['SourceName2']}"]=e
                                        rc_fail+=1
                                        
                            # time.sleep(0.01)
                            prop=1/len(edited_df)* 100
                            percent_complete+=prop
                            my_bar.progress(int(percent_complete), text=f"*{progress_text}>> exported :red[**{rc_ok}/{len(edited_df)}**] records <<>>  :blue[**{row['Template']}{row['SourceName1']}{row['SourceName2']}**] <<*")

                        
                        if ok_flg==True and err_flg!=True and rc_fail==0:
                            mess=f"Imported successfully!!! {rc_ok} records"
                            
                            logging.info("%s :: Upload Source Config Table %s",USERID,mess)
                            qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_factlog', "Upload Source Relation Table", mess,time_cm)
                            vi.msg_success(True,mess)
                            

                        elif rc_ok==0:
                            mess="No records imported"
                            logging.info("%s :: Upload Source Config Table %s",USERID,mess)
                            qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_factlog', "Upload Source Relation Table", mess,time_cm)
                            vi.msg_error(True,mess)
                                            
                        else:
                            mess=f"Imported {rc_ok} records. Failed import for {rc_fail} records: {sc_err}"
                            logging.info("%s :: Upload Source Config Table %s",USERID,mess)
                            qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_factlog', "Upload Source Relation Table", mess,time_cm)
                            vi.msg_error(True,mess)
                        

                    else:
                        st.warning('Please input data',icon="⚠️") 

    


    elif options==":blue[*Booking Validation Logic*]":
        
        tab1,tab2=st.tabs([":clipboard: Source Logic","📑 Batch Upload"])

        with tab1:

            with st.expander(":mag_right: *Search Panel*",expanded=True):
                s2_col1,s2_col2,s2_col3,s2_col4=st.columns([1,1,1,1])
                s_col1,s_col2,s_col3,s_col4,s_col5=st.columns([1,1,0.5,0.5,2])

                search_pop=s_col1.popover("📑Search Mode",use_container_width=True)
                menu_search_lg = ["Wildcard","Multiple","Show all"]
                search_opt = search_pop.radio(" ",menu_search_lg,horizontal=True,label_visibility='collapsed')
                
                bt_search_lg=s_col3.button(":mag_right:",key="bt_search_lg",use_container_width=True)
                bt_clear_lg=s_col4.button("❌",key="bt_clear_lg",use_container_width=True)

            if "search_lg" not in st.session_state:
                st.session_state.search_lg=""
            if "clear_lg" not in st.session_state:
                st.session_state.clear_lg=False
            if "template" not in st.session_state:
                st.session_state.template=""
            
            if "lg_out" not in st.session_state:
                st.session_state.lg_out=""

            if "lg_col" not in st.session_state:
                st.session_state.lg_col=""

            if "keyi" not in st.session_state:
                st.session_state.keyi=0

            results=None
            query=None

            if search_opt== "Show all":
                s_col2.button(":blue[✅ Show all]",disabled=True,use_container_width=True)
                if bt_search_lg:
                    st.session_state.search_lg="Show all"
                    st.session_state.clear_lg=False
                    st.session_state.lg_out=False

                if bt_clear_lg:
                    st.session_state.clear_lg=True
                    st.session_state.search_lg=""
                    st.session_state.lg_out=False

                if st.session_state.search_lg=="Show all":
                    query = f"SELECT * FROM scm_{st.session_state.origin}_bkValidationLogic"

            elif search_opt== "Multiple":
                s_col2.button(":blue[✅ Multiple]",disabled=True,use_container_width=True)

                if bt_search_lg:
                    st.session_state.search_lg="Multiple"
                    st.session_state.clear_lg=False
                    st.session_state.lg_out=False

                if bt_clear_lg:
                    st.session_state.clear_lg=True
                    st.session_state.keyi+=1
                    st.session_state.search_lg=""
                    st.session_state.lg_out=False
                    
                if st.session_state.clear_lg==True:
                    search_temp=s2_col1.text_input("Template",key="search_templg_m"+ str(st.session_state.keyi),value='')
                    st.session_state.template=search_temp

                else:
                    search_temp=s2_col1.text_input("Template",key="search_templg_m",value=st.session_state.template)
                    
                if st.session_state.search_sc=="Multiple":
                    # Split the string into a list of values
                    search_temp = search_temp.split(',')

                    
                    # Enclose each value with single quotes
                    search_temp = ",".join(f"'{value.strip()}'" for value in search_temp)

                    
                    query = f"SELECT * FROM scm_{st.session_state.origin}_bkValidationLogic WHERE"

                    if search_temp!="''":
                        query = f"{query} AND Template IN ({search_temp})"
                        

            else:
                s_col2.button(":blue[✅ Wildcard]",disabled=True,use_container_width=True)

                if bt_search_lg:
                    st.session_state.search_lg="Wildcard"
                    st.session_state.clear_lg=False
                    st.session_state.lg_out=False

                if bt_clear_lg:
                    st.session_state.clear_lg=True
                    st.session_state.keyi+=1
                    st.session_state.search_lg=""
                    st.session_state.lg_out=False
                    
                if st.session_state.clear_lg==True:
                    search_temp=s2_col1.text_input("Template",key="search_templg_w"+ str(st.session_state.keyi),value='')
                    st.session_state.template=search_temp
                    
                else:
                    search_temp=s2_col1.text_input("Template",key="search_templg_w",value=st.session_state.template)
                    

                if st.session_state.search_lg=="Wildcard":
                    query = f"SELECT * FROM scm_{st.session_state.origin}_bkValidationSourceRelation WHERE"

                    if search_temp!="":
                        query = f"{query} AND Template LIKE '%{search_temp}%'"
                                        

            if query and not query.endswith("WHERE"):
                if st.session_state.lg_out==False:
                    query=query.replace("WHERE AND","WHERE")
                    if st.session_state.isDev:
                        st.write(query)     
                    results,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,query)
                    st.session_state.lg_out=results
                    st.session_state.lg_col=columns

                    
                if not st.session_state.lg_out:
                    st.info("No records found",icon='ℹ')
                else:
                    st.info(f"**[   :red[{len(st.session_state.lg_out)}]   ]**  Records found. Please select at least 1 record",icon='⭐') 
                    # Create a DataFrame with the results and column name
                    df = pd.DataFrame.from_records(st.session_state.lg_out, columns=st.session_state.lg_col)


                    selected_rows=0
                    with st.expander(":bookmark_tabs: *Table Result*",expanded=True):
                        ecol1,ecol2,ecol3,ecol5=st.columns([0.7,1,1,1])
                        select_all = ecol1.checkbox('Select All')
                        if select_all:
                            tbl=st.dataframe(df,height=300)
                            selected_rows=df
                            idx=df.index
                        
                        else:      
                            selected_rows,idx = vi.dataframe_with_selections(df)
                        # st.write(len(results), "Records found")
                            

                    ##
                    # Tạo dataframe mới từ cột `Logic`
                    # Xử lý JSON và tạo dataframe mới
                    rows = []
                    for index, row in df.iterrows():
                        vjson=json.loads(row["Logic"])
                        logic=vjson["Logic"]
                        for item in logic:
                            #st.write(row)
                            title = item["title"]
                            logic_str = ut.process_logic(item["str"])
                            
                            # Tạo mỗi dòng dữ liệu
                            #"Logic": json.dumps(vjson["Logic"]),
                            row = {
                                "Template": vjson["Template"],
                                
                                "Title": title,
                                "LogicStr": logic_str,
                                "CreatedBy": row["CreatedBy"],
                                "CreatedDate":row["CreatedDate"],
                                "ModifiedBy": row["ModifiedBy"],
                                "ModifiedDate": row["ModifiedDate"],
                                
                            }
                            rows.append(row)

                    # Tạo DataFrame từ danh sách các dòng
                    df2 = pd.DataFrame(rows)
                    #st.dataframe(df2)

                    selected_rows2=0
                    with st.expander(":bookmark_tabs: *Table Result*",expanded=True):
                        ecol21,ecol22,ecol23,ecol25=st.columns([0.7,1,1,1])
                        select_all2 = ecol21.checkbox('Select All2')
                        if select_all2:
                            tbl=st.dataframe(df2,height=300)
                            selected_rows2=df2
                            idx2=df.index
                        
                        else:      
                            selected_rows2,idx2 = vi.dataframe_with_selections(df2)
                            

                    ##



                    if len(selected_rows)==1:
                        ecol2.write(f":blue[📌 **[ :red[1] ]** *record selected*]")  
                        form_exp=st.expander(":book: *Logic Form*",expanded=True)
                        #clear_on_submit=False
                        fr1=form_exp.form("logic")
                        fr1_cont1=fr1.container()
                        fr1_cont2=fr1.container()
                        
                        # if "button_clicked" not in st.session_state:
                        #     st.session_state.button_clicked = False

                        fr1_cont1_col1, fr1_cont1_col2 ,fr1_cont1_col3,fr1_cont1_col4= fr1_cont1.columns([1,1,1.2,1.2])
                        submit_new=fr1_cont1_col1.form_submit_button("✔️Submit New",use_container_width=True)
                        submit_edit=fr1_cont1_col2.form_submit_button("✔️Submit Edit",use_container_width=True)
                        
                        
                        fr1_cont2_col1,fr1_cont2_col2=fr1_cont2.columns([1,5])

                        idv=fr1_cont2_col1.text_input("Template",key = "temp_e",value=selected_rows['Template'][idx[0]])
                        logic=fr1_cont2_col2.text_area("Logic",key = "logic_e",value=selected_rows['Logic'][idx[0]],height=500)  
                        
                        # submit new
                        if submit_new:
                            st.toast("Submitting new ...",icon='🎈')
                            if idv:

                                select_query = f"""
                                SELECT * FROM scm_{st.session_state.origin}_bkValidationLogic WHERE Template= '{idv}'
                                """
                                existing_lg,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,select_query)
                                
                                if existing_lg:
                                    mess="Combination already exist"
                                    vi.msg_error(True,mess)
                                    
                                else:  
                                    flg,e,time_cm=qr.insert_bkValidationLogic(True,st.session_state.DB,st.session_state.DATABASE,f'scm_{st.session_state.origin}_bkValidationLogic' , idv, logic)
                                    if flg==True:
                                        # # Lists of keys and values
                                        # keys = ['id', 'name','full']
                                        # values = [code, name,full]
                                        # # Create a dictionary using zip
                                        # dictionary = dict(zip(keys, values))
                                        st.session_state.lg_out=False
                                        logging.info("%s :: Insert Logic %s",USERID, f"{idv}{source}{sheet}{column} Inserted successfully ^^")
                                        qr.insert_log(st.session_state.DB,st.session_state.DATABASE,f'scm_{st.session_state.origin}_factlog', "Insert Logic", f"{idv} Inserted successfully ^^",time_cm)

                            else:
                                mess="Template is blank"
                                vi.msg_error(True,mess)

                                    
                        # submit edit
                        if submit_edit:
                            st.toast("Submitting edit ...",icon='🎈')
                            select_query = f"""
                            SELECT * FROM scm_{st.session_state.origin}_bkValidationLogic WHERE Template = '{idv}'
                            """
                            existing_lg,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,select_query)
                            
                            if not existing_lg:
                                mess="Combination is not existing"
                                vi.msg_error(True,mess)
                                
                            else:  
                                flg,e,time_cm=qr.update_bkValidationLogic(True,st.session_state.DB,st.session_state.DATABASE,f'scm_{st.session_state.origin}_bkValidationLogic' ,idv, logic)
                                if flg==True:
                                    # # Lists of keys and values
                                    # keys = ['code', 'name', 'full']
                                    # values = [code, name, full]

                                    # # Create a dictionary using zip
                                    # dictionary = dict(zip(keys, values))
                                    st.session_state.lg_out=False
                                    logging.info("%s :: Update Logic %s",USERID, f"{idv} Updated successfully ^^")
                                    qr.insert_log(st.session_state.DB,st.session_state.DATABASE,f'scm_{st.session_state.origin}_factlog', "Update Logic", f"{idv} Updated successfully ^^",time_cm)



                    
                        if "del_yes" not in st.session_state:
                            st.session_state.del_yes=False


                        delete_lg=fr1_cont1_col3.popover("❌ Delete Record",use_container_width=True)
                        del_yes = delete_lg.form_submit_button("✅ Confirm",type="primary",use_container_width=True)
                        del_no = delete_lg.form_submit_button("❌ Cancel",use_container_width=True)
                        
                        if del_yes:
                            st.toast("Deletting ...", icon='🎈')
                            st.session_state.del_yes=True

                            
                        if del_no:
                            st.toast("Cancelling ...", icon='🎈')
                            mess="Cancelled Delete"
                            vi.msg_success(True,mess)

                        
                        if st.session_state.del_yes==True:
                            st.session_state.del_yes=False
                            for index, row in selected_rows.iterrows():
                            
                                if row['Template']:
                        
                                    flg,e,time_cm=qr.delete_record(True,st.session_state.DB,st.session_state.DATABASE,False,f"scm_{st.session_state.origin}_bkValidatorLogic","Template",f"{idv}")
                                    
                                    if flg==True:
                                        st.session_state.lg_out=False
                                        logging.info("%s :: Delete Logic %s",USERID, f"{idv} Deleted successfully ^^")
                                        qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_factlog', "Delete Logic", f"{code} Deleted successfully ^^",time_cm)
                        

                    elif len(selected_rows)>1:
                        ecol2.write(f":blue[📌 **[ :red[{len(selected_rows)}] ]** *records selected*]")  


                        if "del_yes" not in st.session_state:
                            st.session_state.del_yes=False

                        delete_lg=ecol5.popover("❌ Delete Records",use_container_width=True)
                        del_yes = delete_lg.button("✅ Confirm",type="primary",use_container_width=True)
                        del_no = delete_lg.button("❌ Cancel",use_container_width=True)
                        
                        if del_yes:
                            st.toast("Deletting ...", icon='🎈')
                            st.session_state.del_yes=True
                            
                        if del_no:
                            st.toast("Cancelling ...", icon='🎈')
                            mess="Cancelled Delete"
                            vi.msg_success(True,mess)

                        if st.session_state.del_yes==True:
                            st.session_state.del_yes=False

                            flg=False
                            code_list=[]
                            code_str=''

                            for index, row in selected_rows.iterrows():
                                
                                if row['Template']:
                                    code= row['Template']
                                    code_list.append(code)
                                    #coonvert list to string with ' begin and end of each item
                                    code_str = ', '.join([f"'{item}'" for item in code_list])

                            flg,e,time_cm=qr.delete_record(False,st.session_state.DB,st.session_state.DATABASE,True,f"scm_{st.session_state.origin}_bkValidatorLogic","Template",code_str)

                            
                            if flg==True:
                                st.session_state.lg_out=False
                                mess=f"{len(selected_rows)} records deleted successfully!!!"
                                # code_list=str(list(selected_rows['TempSourceSheetColumn']))
                                logging.info("%s :: Deleted Multiple Logic %s",USERID,mess)
                                qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_factlog', "Deleted Multiple Logic", mess ,time_cm)
                                vi.msg_success(True,mess)

                                            
                            else:
                                mess=f"Failed!!! Error: {e}" 
                                code_list=str(list(selected_rows['Template']))
                                logging.info("%s :: Deleted Multiple Logic  %s",USERID,mess)
                                qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_factlog',"Deleted Multiple Logic", mess,time_cm)
                                vi.msg_error(True,mess)


                    
                    # if len(selected_rows2)==1:
                    #     ecol22.write(f":blue[📌 **[ :red[1] ]** *record selected*]")  
                    #     form_exp2=st.expander(":book: *Logic Form2*",expanded=True)
                    #     #clear_on_submit=False
                    #     fr21=form_exp2.form("logic2")
                    #     fr21_cont1=fr21.container()
                    #     fr21_cont2=fr21.container()
                        
                    #     # if "button_clicked" not in st.session_state:
                    #     #     st.session_state.button_clicked = False

                    #     fr1_cont1_col21, fr1_cont1_col22 ,fr1_cont1_col23,fr1_cont1_col24= fr21_cont1.columns([1,1,1.2,1.2])
                    #     submit_new2=fr1_cont1_col21.form_submit_button("✔️Submit New",use_container_width=True)
                    #     submit_edit2=fr1_cont1_col22.form_submit_button("✔️Submit Edit",use_container_width=True)
                        
                        
                    #     fr1_cont2_col21,fr1_cont2_col22,fr1_cont2_col23=fr21_cont2.columns([1,2,4])

                    #     idv2=fr1_cont2_col21.text_input("Template",key = "temp_e2",value=selected_rows2['Template'][idx2[0]])
                    #     title2=fr1_cont2_col22.text_area("Title",key = "logic_e2",value=selected_rows2['Title'][idx2[0]],height=500) 
                    #     logic2=fr1_cont2_col23.text_area("Logic",key = "logic_e2",value=selected_rows2['LogicStr'][idx2[0]],height=500) 
                        
                    #     # submit new
                    #     if submit_new2:
                    #         st.toast("Submitting new ...",icon='🎈')
                    #         if idv2:

                    #             select_query = f"""
                    #             SELECT * FROM scm_{st.session_state.origin}_bkValidationLogic WHERE Template= '{idv2}'
                    #             """
                    #             existing_lg2,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,select_query)
                                
                    #             if existing_lg2:
                    #                 mess="Combination already exist"
                    #                 vi.msg_error(True,mess)
                                    
                    #             else:  
                    #                 flg,e,time_cm=qr.insert_bkValidationLogic(True,st.session_state.DB,st.session_state.DATABASE,f'scm_{st.session_state.origin}_bkValidationLogic' , idv2, logic2)
                    #                 if flg==True:
                    #                     # # Lists of keys and values
                    #                     # keys = ['id', 'name','full']
                    #                     # values = [code, name,full]
                    #                     # # Create a dictionary using zip
                    #                     # dictionary = dict(zip(keys, values))
                    #                     st.session_state.lg_out=False
                    #                     logging.info("%s :: Insert Logic %s",USERID, f"{idv2} Inserted successfully ^^")
                    #                     qr.insert_log(st.session_state.DB,st.session_state.DATABASE,f'scm_{st.session_state.origin}_factlog', "Insert Logic", f"{idv2} Inserted successfully ^^",time_cm)

                    #         else:
                    #             mess="Template is blank"
                    #             vi.msg_error(True,mess)

                                    
                    #     # submit edit
                    #     if submit_edit2:
                    #         st.toast("Submitting edit ...",icon='🎈')
                    #         select_query = f"""
                    #         SELECT * FROM scm_{st.session_state.origin}_bkValidationLogic WHERE Template = '{idv2}'
                    #         """
                    #         existing_lg2,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,select_query)
                            
                    #         if not existing_lg2:
                    #             mess="Combination is not existing"
                    #             vi.msg_error(True,mess)
                                
                    #         else:  
                    #             flg,e,time_cm=qr.update_bkValidationLogic(True,st.session_state.DB,st.session_state.DATABASE,f'scm_{st.session_state.origin}_bkValidationLogic' ,idv2, logic2)
                    #             if flg==True:
                    #                 # # Lists of keys and values
                    #                 # keys = ['code', 'name', 'full']
                    #                 # values = [code, name, full]

                    #                 # # Create a dictionary using zip
                    #                 # dictionary = dict(zip(keys, values))
                    #                 st.session_state.lg_out=False
                    #                 logging.info("%s :: Update Logic %s",USERID, f"{idv2} Updated successfully ^^")
                    #                 qr.insert_log(st.session_state.DB,st.session_state.DATABASE,f'scm_{st.session_state.origin}_factlog', "Update Logic", f"{idv2} Updated successfully ^^",time_cm)



                    
                    #     if "del_yes" not in st.session_state:
                    #         st.session_state.del_yes=False


                    #     delete_lg2=fr1_cont1_col3.popover("❌ Delete Record",use_container_width=True)
                    #     del_yes2 = delete_lg.form_submit_button("✅ Confirm",type="primary",use_container_width=True)
                    #     del_no2 = delete_lg.form_submit_button("❌ Cancel",use_container_width=True)
                        
                    #     if del_yes2:
                    #         st.toast("Deletting ...", icon='🎈')
                    #         st.session_state.del_yes=True

                            
                    #     if del_no2:
                    #         st.toast("Cancelling ...", icon='🎈')
                    #         mess="Cancelled Delete"
                    #         vi.msg_success(True,mess)

                        
                    #     if st.session_state.del_yes==True:
                    #         st.session_state.del_yes=False
                    #         for index, row in selected_rows.iterrows():
                            
                    #             if row['Template']:
                        
                    #                 flg,e,time_cm=qr.delete_record(True,st.session_state.DB,st.session_state.DATABASE,False,f"scm_{st.session_state.origin}_bkValidatorLogic","Template",f"{idv2}")
                                    
                    #                 if flg==True:
                    #                     st.session_state.lg_out=False
                    #                     logging.info("%s :: Delete Logic %s",USERID, f"{idv2} Deleted successfully ^^")
                    #                     qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_factlog', "Delete Logic", f"{idv2} Deleted successfully ^^",time_cm)
                        

                    # elif len(selected_rows2)>1:
                    #     ecol2.write(f":blue[📌 **[ :red[{len(selected_rows)}] ]** *records selected*]")  


                    #     if "del_yes" not in st.session_state:
                    #         st.session_state.del_yes=False

                    #     delete_lg=ecol5.popover("❌ Delete Records",use_container_width=True)
                    #     del_yes = delete_lg.button("✅ Confirm",type="primary",use_container_width=True)
                    #     del_no = delete_lg.button("❌ Cancel",use_container_width=True)
                        
                    #     if del_yes:
                    #         st.toast("Deletting ...", icon='🎈')
                    #         st.session_state.del_yes=True
                            
                    #     if del_no:
                    #         st.toast("Cancelling ...", icon='🎈')
                    #         mess="Cancelled Delete"
                    #         vi.msg_success(True,mess)

                    #     if st.session_state.del_yes==True:
                    #         st.session_state.del_yes=False

                    #         flg=False
                    #         code_list=[]
                    #         code_str=''

                    #         for index, row in selected_rows.iterrows():
                                
                    #             if row['Template']:
                    #                 code= row['Template']
                    #                 code_list.append(code)
                    #                 #coonvert list to string with ' begin and end of each item
                    #                 code_str = ', '.join([f"'{item}'" for item in code_list])

                    #         flg,e,time_cm=qr.delete_record(False,st.session_state.DB,st.session_state.DATABASE,True,f"scm_{st.session_state.origin}_bkValidatorLogic","Template",code_str)

                            
                    #         if flg==True:
                    #             st.session_state.lg_out=False
                    #             mess=f"{len(selected_rows)} records deleted successfully!!!"
                    #             # code_list=str(list(selected_rows['TempSourceSheetColumn']))
                    #             logging.info("%s :: Deleted Multiple Logic %s",USERID,mess)
                    #             qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_factlog', "Deleted Multiple Logic", mess ,time_cm)
                    #             vi.msg_success(True,mess)

                                            
                    #         else:
                    #             mess=f"Failed!!! Error: {e}" 
                    #             code_list=str(list(selected_rows['Template']))
                    #             logging.info("%s :: Deleted Multiple Logic  %s",USERID,mess)
                    #             qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_factlog',"Deleted Multiple Logic", mess,time_cm)
                    #             vi.msg_error(True,mess)



        


        with tab2:

            with st.expander(":hand: *Command Button*",expanded=True):
                conttb1,conttb2=st.columns([1,4])
                submit_lg=conttb1.button("✔️Submit Table",key="submit_nsc",use_container_width=True)
            
            if "lgt_col" not in st.session_state:
                st.session_state.lgt_col=False
            

            if st.session_state.lgt_col==False:
                #query cont
                query_lg = f"SELECT * FROM scm_{st.session_state.origin}_bkValidationLogic WHERE Template='123'"

                results,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,query_lg)
                columns=columns[:-4]
                st.session_state.lgt_col=columns



            if st.session_state.lgt_col:
                with st.expander(":book: *Table Input*",expanded=True):
                    # df=pd.DataFrame.from_records(results_cont, columns=columns_cont,)
                    edited_df = st.data_editor(pd.DataFrame.from_records("", columns=st.session_state.lgt_col),num_rows="dynamic")
        

                if submit_lg:
                    st.toast("Submitting  ...",icon='🎈')
                    if edited_df["Template"].count()>0:
                        # statusbar
                        progress_text = "Operation in progress. Please wait."
                        my_bar = st.progress(0, text=progress_text)
                        percent_complete=0
                        flg=False
                        ok_flg=False
                        err_flg=False
                        rc_fail=0
                        rc_ok=0

                        sc_err={}


                        for index, row in edited_df.iterrows():
                        
                            # st.write(index)
                            # st.write(row['Booking'])
                            if row['Template']:  
                                select_query = f"""
                                SELECT * FROM scm_{st.session_state.origin}_bkValidationLogic WHERE Template = '{row['Template']}'
                                """ 
                                existing,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,select_query)
                                if existing:
                                    
                                    flg,e,time_cm=   qr.update_bkValidationLogic(False,st.session_state.DB, st.session_state.DATABASE,f'scm_{st.session_state.origin}_bkValidationLogic' ,row["Template"],row["Logic"])
                                    
                                    if flg==True:
                                        ok_flg=True
                                        rc_ok+=1
                                    else:
                                        err_flg=True
                                        sc_err[f"{row['Template']}"]=e
                                        rc_fail+=1
                                        
                                else:
                                    
                                    flg,e,time_cm= qr.insert_bkValidationLogic(False,st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_bkValidationLogic', row["Template"],row["Logic"])
                                    if flg==True:
                                        ok_flg=True
                                        rc_ok+=1
                                    else:
                                        err_flg=True
                                        sc_err[f"{row['Template']}"]=e
                                        rc_fail+=1
                                        

                            # time.sleep(0.01)
                            prop=1/len(edited_df)* 100
                            percent_complete+=prop
                            my_bar.progress(int(percent_complete), text=f"*{progress_text}>> exported :red[**{rc_ok}/{len(edited_df)}**] records <<>>  :blue[**{row['Template']}**] <<*")

                        
                        if ok_flg==True and err_flg!=True and rc_fail==0:
                            mess=f"Imported successfully!!! {rc_ok} records"
                            logging.info("%s :: Upload Logic Table %s",USERID,mess)
                            qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_factlog', "Upload Logic Table", mess,time_cm)
                            vi.msg_success(True,mess)
                            

                        elif rc_ok==0:
                            mess="No records imported"
                            logging.info("%s :: Upload Logic Table %s",USERID,mess)
                            qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_factlog', "Upload Logic Table", mess,time_cm)
                            vi.msg_error(True,mess)
                                            
                        else:
                            mess=f"Imported {rc_ok} records. Failed import for {rc_fail} records: {sc_err}"
                            logging.info("%s :: Upload Logic Table %s",USERID,mess)
                            qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'scm_{st.session_state.origin}_factlog', "Upload Logic Table", mess,time_cm)
                            vi.msg_error(True,mess)
                        

                    else:
                        st.warning('Please input data',icon="⚠️") 

        


if __name__ == "__main__":
    
    main()