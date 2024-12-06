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
import json
from src.auth import login,logout,initiateApp
import src.view as vi
from src.log import logIni
import src.query as qr
import src.ulti as ut
# from src.gcss import getGcssContbl



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


TEMP_PDF=folder_path + parser.get('PATH','temp_pdf')
TEMP_XLSM=folder_path + parser.get('PATH','temp_xlsm')
OUTPUT=parser.get('PATH','output')
DRIVER=parser.get('SQL','driver')

#party
SHIP_NAME=parser.get('PARTY','shipname')
SHIP_ADD=f"{parser.get('PARTY','shipadd1')}\n{parser.get('PARTY','shipadd2')}\n{parser.get('PARTY','shipadd3')}"
CNOR_NAME=parser.get('PARTY','cnorname')
CNOR_ADD=f"{parser.get('PARTY','cnoradd1')}\n{parser.get('PARTY','cnoradd2')}\n{parser.get('PARTY','cnoradd3')}"

NOTI_NAME_E=parser.get('PARTY','notiname_e')
NOTI_ADD_E=f"{parser.get('PARTY','notiadd1_e')}\n{parser.get('PARTY','notiadd2_e')}\n{parser.get('PARTY','notiadd3_e')}"

CNEE_NAME_E=parser.get('PARTY','cneename_e')
CNEE_ADD_E=f"{parser.get('PARTY','cneeadd1_e')}\n{parser.get('PARTY','cneeadd2_e')}\n{parser.get('PARTY','cneeadd3_e')}"

# cont
# CONTTYPE=parser.get('DEFAULT','conttype')
CARGOTYPE=parser.get('DEFAULT','cargotype')
CONTOWNER=parser.get('DEFAULT','contowner')
VANNING=parser.get('DEFAULT','vanning')

PACKU_E=parser.get('DEFAULT','packu_e')
GW_E=float(parser.get('DEFAULT','gw_e'))
GWU=parser.get('DEFAULT','gwu')
MEASURE_E=float(parser.get('DEFAULT','measure_e'))
MEASUREU=parser.get('DEFAULT','measureu')
MARK_E=parser.get('DEFAULT','mark_e')
DESCRIPT_E=parser.get('DEFAULT','descript_e')




# Streamlit app
def main():

    global time_cm,cookies

    # 0. Configuration
    vi.appConfig("Booking Validation","visible","expanded")

    # 1. Login
    cookies = CookieManager()
    initiateApp(USERID,cookies,APPVERSION)
 
    # 2. Page Content
    menu = [":blue[*Upload & Check*]",":blue[*Batch Upload*]",":blue[*Search Data*]"] #,"HBL Data","EDI File Upload","Import Enter Files","Batch Upload"]
    options = st.sidebar.radio("Select an Option :dart:",menu)
    
    

    if options== ":blue[*Upload & Check*]":
        with st.expander(":hand: *Command Button*",expanded=True):
            cont0_col1,cont0_col2,cont0_col3=st.columns([1,1,3])

            check_bt=cont0_col2.button("⬇️Cross Check",use_container_width=True)
            viewdt_bt=cont0_col1.button("👀View data",use_container_width=True)
        
        upload_exp= st.expander(":cloud: *File Upload*",expanded=True)
        cont1=upload_exp.container()
        con1_col1,con1_col2=cont1.columns([1,5])
        
        # template select
        if 'template' not in st.session_state:
            st.session_state.template=''

        if st.session_state.template=='':

            select_query = f"""
            SELECT DISTINCT(Template) FROM scm_{st.session_state.origin}_bkValidationSourceConfig
            """
            temp_record,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,select_query)

            # Get unique values from the specified column using a set
            unique_temp = set(row[0] for row in temp_record)

            # If you want to convert the set back to a list, you can do so
            temp_list = list(unique_temp)
            # temp_list = list(temp_record)

            st.session_state.template=temp_list

        input_template=con1_col1.selectbox(":red[*]Template",st.session_state.template)


        # retrieve source
        if 'sheet' not in st.session_state:
            st.session_state.sheet=''


        if st.session_state.sheet=='':

            select_query = f"""
            SELECT DISTINCT SourceName,SheetName FROM scm_{st.session_state.origin}_bkValidationSourceConfig WHERE Template='{input_template}'
            """
            source_record,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,select_query)
            
            #st.session_state.sourceconfig=source_record

            # Get unique values from the specified column using a set
            unique_temp = set(row[1] for row in source_record)

            # If you want to convert the set back to a list, you can do so
            sheet_list = list(unique_temp)

            st.session_state.sheet=sheet_list

        

        if "files" not in st.session_state:
            st.session_state.files={}

        for sheet in st.session_state.sheet:
            uploaded_files = con1_col2.file_uploader(label=f":red[*]Upload {sheet}",label_visibility='visible', accept_multiple_files=False, type=["xlsx","xlsm"])
            if uploaded_files:
                st.session_state.files[sheet] = uploaded_files



        # process
        if st.session_state.files!={}:
            # st.write(st.session_state.files)
            extract={}
            file_flg=False

            for sheet,uploaded_file in st.session_state.files.items():
                file_extension = uploaded_file.name.split('.')[-1]

                if file_extension.startswith("xls"):
                    try:
                        # df = pd.read_excel(uploaded_file, engine='openpyxl',converters={'Bookno':str,'Discharge': str,'Container':str,'Isocode':str,'F/E': str})
                        df = pd.read_excel(uploaded_file, engine='openpyxl',sheet_name = sheet)
                        start_row_index = vi.find_start_row_index(df,"xlsx")
                    except Exception as e:
                        st.error(f"Error reading file: {e}",icon="🚨")
                        st.stop()
                    # st.write(start_row_index)
                    if start_row_index is not None:
                        # Use the identified row as header and slice the DataFrame from that row onwards
                        sliced_df = df.iloc[start_row_index:].reset_index(drop=True)
                        extract[sheet]=sliced_df
                        file_flg=True
                        # sliced_df.columns = sliced_df.iloc[0]  # Set the first row as the header
                        # sliced_df = sliced_df.iloc[1:]  # Exclude the row used as header
                        # st.write("DataFrame with 'Container' row as header:")

                    else:
                        st.error(f"No header found in first row: {sheet}",icon="🚨")
                        # file_flg=False
                        st.stop()
                else:
                    st.warning("Unsupported file type. Please upload an XLSX (.xlsx) file.")


            
            if file_flg==True:
                
                if viewdt_bt:
                    st.toast("Viewing data ...",icon='🎈')
                    for sheet,sliced_df in extract.items():
                        st.write(sheet,sliced_df)
                

                if check_bt:
                    st.toast("Checking ...",icon='🎈')

                    if 'logic' not in st.session_state:
                        st.session_state.logic=''


                    if st.session_state.logic=='':

                        select_query = f"""
                        SELECT DISTINCT(Logic) FROM scm_{st.session_state.origin}_bkValidationLogic WHERE Template='{input_template}'
                        """
                        logic_record,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,select_query)
                        
                        # st.write(logic_record[0][0])
                        st.session_state.logic=json.loads(logic_record[0][0])


                    if st.session_state.isDev:
                        st.write(':green[*Logic*]',st.session_state.logic)

                    if st.session_state.logic:
                        # Merge data
                        # Rename foreign key columns to a common key for merging and add sheet names to other columns
                        renamed_dfs = []
                        for sheet, sliced_df in extract.items():

                            select_query = f"""
                            SELECT DISTINCT(FKey1) FROM scm_{st.session_state.origin}_bkValidationSourceRelation WHERE TempSource1Source2 LIKE '{input_template}{sheet}%'
                            """
                            fkey_record,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,select_query)
                            
                            #st.write(select_query)
                            if fkey_record:
                                foreign_key = fkey_record[0][0].replace("\n", "").strip()
                                # st.write(fkey_record[0])
                            else:
                                select_query = f"""
                                SELECT DISTINCT(FKey2) FROM scm_{st.session_state.origin}_bkValidationSourceRelation WHERE TempSource1Source2 LIKE '{input_template}%{sheet}'
                                """
                                fkey_record2,columns2 = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,select_query)
                                
                                if fkey_record2:
                                    foreign_key = fkey_record2[0][0].replace("\n", "").strip()
                                    # st.write(fkey_record2[0])
                                else:
                                    st.error("Cannot found FKey",icon="🚨")
                                    st.stop()

                            # st.write(foreign_key)
                            # Rename the foreign key column to a common name ('ID') for merging
                            renamed_df = sliced_df.rename(columns={foreign_key: 'ID'})
                            
                            # Rename other columns to include the sheet name for uniqueness
                            renamed_df = renamed_df.rename(columns={col: f"{sheet}.{col}" if col != 'ID' else 'ID' for col in renamed_df.columns})
                            
                            renamed_dfs.append(renamed_df)


                        #Merge all DataFrames on the common foreign key ('ID')
                        merged_df = renamed_dfs[0]

                        for next_df in renamed_dfs[1:]:
                            merged_df = pd.merge(merged_df, next_df, on='ID', how='outer')  # Use 'outer' for a full join
                        
                        # st.write(renamed_dfs[0])
                        # st.write(renamed_dfs[1])
                        # merged_df = pd.merge(renamed_dfs[0], renamed_dfs[1], on='ID', how='outer')  # Use 'outer' for a full join
                        

                        merged_df= merged_df.rename(columns={col: col[:-2] if col.endswith('_y') else col for col in merged_df.columns})

                        df = pd.DataFrame(merged_df)

                        if st.session_state.isDev:
                            st.write(':green[*Merged Data*]',df)

                        
                        result_dict = {}
                        error_log = {}

                        for logic in st.session_state.logic["Logic"]:
                            title = logic["title"]
                            logic_str = logic["str"]

                            try:
                                result = ut.eval_logic(df, logic_str)
                                result = [str(item) for item in result]
                                result_dict[title] = result
                            except Exception as e:
                                st.error(f"Error evaluating logic '{title}': {e}")
                                result_dict[title] = pd.Series([False] * len(df), index=df.index)
                                error_log[title] = str(e)

                        if result_dict:
                            #st.dataframe(result_dict)
                            addFinal=ut.add_final_check_column(result_dict)
                            # st.dataframe(addFinal)
                            addFinal = pd.concat([df["ID"], addFinal], axis=1)
                            finalFalse = addFinal[addFinal['Final_Check'] == 'False']
                            st.write(':red[*Final Check (False)*]',finalFalse)
                        if error_log:
                            st.write(':red[*Error*]',error_log)


                            

                    

    if options== ":blue[*Batch Upload*]":

        cont1=st.expander(":hand: *Command Button*",expanded=True)
        conttb1,conttb2=cont1.columns([1,4])
        submit_bl=conttb1.button("✔️Submit Table ",key="submit_nbl",use_container_width=True)
        
        st.info('Arrival: M/D/YYYY',icon='ℹ️')
        if "blcol" not in st.session_state:
            st.session_state["blcol"]=False

        if st.session_state["blcol"]==False:
            query_bl = f"SELECT * FROM mtlt_{st.session_state.origin}_facthbl WHERE Booking='123'"
            results,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,query_bl)
            columns=columns[:-4]
            st.session_state["blcol"]=columns

        
        if st.session_state["blcol"]!=False:
            with st.expander(":bookmark_tabs: *Input Table*",expanded=True):
                edited_df = st.data_editor(pd.DataFrame.from_records("", columns=st.session_state["blcol"]),num_rows="dynamic")
        

            if submit_bl:
                st.toast(f'Submitting new Booking ...', icon='🎈')
                if edited_df["Booking"].count()>0:
                    
                    # statusbar
                    progress_text = "Operation in progress. Please wait."
                    
                    my_bar = st.progress(0, text=progress_text)
                    percent_complete=0
                    flg=False
                    ok_flg=False
                    err_flg=False
                    rc_fail=0
                    rc_ok=0

                    bl_err={}

                    vsl_dict={}
                    voy_dict={}
                    arr_dict={}
                    
                    #loop record
                    
                    for index, row in edited_df.iterrows():
                    
                        # st.write(index)
                        # st.write(row['Booking'])
                        if row['Booking']: 
                            
                            
                            
                            select_query = f"""
                            SELECT * FROM mtlt_{st.session_state.origin}_facthbl WHERE Booking = '{row['Booking']}'
                            """ 
                            existing,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,select_query)

                            if existing:
                                
                                flg,e,time_cm= qr.update_bl_record(False,st.session_state.DB, st.session_state.DATABASE,f'mtlt_{st.session_state.origin}_facthbl',row["Booking"], row["Vessel"], row["Voyage"], datetime.strptime(str(row['Arrival']),'%m/%d/%Y'), row["POL"], row["POD"], row["DEL"], row["LINE"], row["Shipper_Name"], row["Shipper_Address"], row["Shipper_Country"], row["Cnee_Name"], row["Cnee_Address"], row["Cnee_Country"], row["Notify_Name"], row["Notify_Address"], row["Notify_Country"], row["Term"], row["Cargo_Type"], row["Movement"], row["Freight"], row["No_Pack"], row["Pack_Unit"], row["Weight"], row["Measurement"], row["Mark"], row["Description"])
                                
                                if flg==True:
                                    ok_flg=True
                                    rc_ok+=1
                                else:
                                    err_flg=True
                                    bl_err[row["Booking"]]=e
                                    rc_fail+=1
                                    
                            else:
                                
                                flg,e,time_cm= qr.insert_bl_record(False,st.session_state.DB,st.session_state.DATABASE,f'mtlt_{st.session_state.origin}_facthbl', row["Booking"], row["Vessel"], row["Voyage"], datetime.strptime(str(row['Arrival']),'%m/%d/%Y'), row["POL"], row["POD"], row["DEL"], row["LINE"], row["Shipper_Name"], row["Shipper_Address"], row["Shipper_Country"], row["Cnee_Name"], row["Cnee_Address"], row["Cnee_Country"], row["Notify_Name"], row["Notify_Address"], row["Notify_Country"], row["Term"], row["Cargo_Type"], row["Movement"], row["Freight"], row["No_Pack"], row["Pack_Unit"], row["Weight"], row["Measurement"], row["Mark"], row["Description"])
                                if flg==True:
                                    ok_flg=True
                                    rc_ok+=1
                                else:
                                    err_flg=True
                                    bl_err[row["Booking"]]=e
                                    rc_fail+=1

                            vsl_dict[row['Booking']]=str(row['Vessel'])
                            voy_dict[row['Booking']]=str(row['Voyage'])
                            arr_dict[row['Booking']]=str(row['Arrival'])
                            

                        prop=1/len(edited_df)* 100
                        percent_complete+=prop
                        my_bar.progress(int(percent_complete), text=f"*{progress_text}>> imported :red[**{rc_ok}/{len(edited_df)}**] records <<>>  :blue[**{row['Booking']}**] <<*")

                    # cnf final
                    if ok_flg==True and err_flg!=True and rc_fail==0:
                        mess=f"Imported successfully!!! {rc_ok} records"
                        logging.info("%s :: Upload BK Table %s",USERID,mess)
                        qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'mtlt_{st.session_state.origin}_factlog', str(list(edited_df['Booking'])), None, str(vsl_dict), str(voy_dict), str(arr_dict), None, "Upload BK Table", mess + '|' + edited_df.to_json(orient='records', lines=True),time_cm)
                        vi.msg_success(True,mess)

                    elif rc_ok==0:
                        mess="No records imported"
                        logging.info("%s :: Upload BK Table %s",USERID,mess)
                        qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'mtlt_{st.session_state.origin}_factlog', str(list(edited_df['Booking'])), None, str(vsl_dict), str(voy_dict), str(arr_dict), None, "Upload BK Table", mess+ '|' + edited_df.to_json(orient='records', lines=True),time_cm)
                        vi.msg_error(True,mess)

                    else:
                        mess=f"Imported {rc_ok}/{len(edited_df)} records. Failed import for {rc_fail} records: {bl_err}"
                        logging.info("%s :: Upload BK Table %s",USERID,mess)
                        qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'mtlt_{st.session_state.origin}_factlog', str(list(edited_df['Booking'])), None, str(vsl_dict), str(voy_dict), str(arr_dict), None, "Upload BK Table", mess+ '|' + edited_df.to_json(orient='records', lines=True),time_cm)
                        vi.msg_error(True,mess)

                else:
                    st.warning('Please input data',icon="⚠️") 


    if options== ":blue[*Search Data*]":
        
        
            
        with st.expander(":mag_right: *Search Panel*",expanded=True):

            s2_col1,s2_col2,s2_col3,s2_col4,s2_col5,s2_col6,s2_col7,=st.columns([1,1,1,1,1,1,1])
            s_col1,s_col2,s_col3,s_col4,s_col5,s_col6=st.columns([1,1,0.5,0.5,0.5,1.5])
            
            search_pop=s_col1.popover("🎯Search Mode",use_container_width=True)
            menu_search = ["Wildcard","Multiple","Arrival Date","Vessel List","Show all"]
            search_opt = search_pop.radio(" ", menu_search,horizontal=False,label_visibility='collapsed')

            search_bt_bk=s_col3.button(":mag_right:",key="search_bt_bk",use_container_width=True)
            new_bl=s_col4.button("➕",use_container_width=True)
            clear_bt_bk=s_col5.button("❌",key="clear_bt_bk",use_container_width=True)
            
        
        if "search_cargo" not in st.session_state:
            st.session_state.search_cargo=""
        if "clear_bl" not in st.session_state:
            st.session_state.clear_bl=False
        if "vsl" not in st.session_state:
            st.session_state.vsl=""
        if "voy" not in st.session_state:
            st.session_state.voy=""
        if "bk" not in st.session_state:
            st.session_state.bk=""
        if "pod" not in st.session_state:
            st.session_state.pod=""
        if "pol" not in st.session_state:
            st.session_state.pol=""
        if "sp" not in st.session_state:
            st.session_state.sp=""
        if "cn" not in st.session_state:
            st.session_state.cn=""
        if "arr" not in st.session_state:
            st.session_state.arr=date.today()
        if "keyi" not in st.session_state:
            st.session_state.keyi=0
        if "cargo_out" not in st.session_state:
            st.session_state.cargo_out=False
        if "cargo_col" not in st.session_state:
            st.session_state.cargo_col=False
        if "vslbl_out" not in st.session_state:
            st.session_state.vslbl_out=False
        if "vslbl_col" not in st.session_state:
            st.session_state.vslbl_col=False
        if "newbl" not in st.session_state:
            st.session_state.newbl=False
        

        query=None

        
        if search_opt== "Show all":

            s_col2.button(":blue[✅ Show all]",disabled=True,use_container_width=True)

            # new_bl=s_col3.button("➕",use_container_width=True)
            # clear_bt_bk=s_col4.button("❌",key="clear_bt_bk",use_container_width=True)
            # st.session_state.newbl=False

            if search_bt_bk:
                st.session_state.search_cargo="Show all"
                st.session_state.clear_bl=False
                st.session_state.newbl=False
                st.session_state.cargo_out=False

            if clear_bt_bk:
                st.session_state.search_cargo=""
                st.session_state.newbl=False
                st.session_state.cargo_out=False
            
            if new_bl:
                st.session_state.newbl=True
                st.session_state.search_cargo=""
                st.session_state.cargo_out=False
            
            if st.session_state.search_cargo=="Show all": 

                query = f"SELECT * FROM mtlt_{st.session_state.origin}_facthbl"
                
        elif search_opt== "Vessel List":
            
            s_col2.button(":blue[✅ Vessel List]",disabled=True,use_container_width=True)
            
            # search_bt_bk=s_col3.button(":mag_right:",key="search_bt_bk",use_container_width=True)
            # new_bl=s_col4.button("➕",use_container_width=True)
            # clear_bt_bk=s_col5.button("❌",key="clear_bt_bk",use_container_width=True)
            

            if search_bt_bk:
                st.session_state.search_cargo="Vessel List"
                st.session_state.clear_bl=False
                st.session_state.newbl=False
                st.session_state.cargo_out=False
                st.session_state.vslbl_out=False

            if clear_bt_bk:
                st.session_state.clear_bl=True
                st.session_state.keyi+=1
                st.session_state.search_cargo=""
                st.session_state.newbl=False
                st.session_state.cargo_out=False
                st.session_state.vslbl_out=False
            
            if new_bl:
                st.session_state.newbl=True
                st.session_state.clear_bl=True
                st.session_state.search_cargo=""
                st.session_state.cargo_out=False
                st.session_state.vslbl_out=False

                
            if st.session_state.clear_bl==True:
                search_vsl=s2_col1.text_input("Vessel",key="search_vsl_v"+ str(st.session_state.keyi),value='')
                search_voy=s2_col2.text_input("Voyage", key="search_voy_v"+ str(st.session_state.keyi),value='')
                st.session_state.vsl=search_vsl
                st.session_state.voy=search_voy
            else:
                search_vsl=s2_col1.text_input("Vessel",key="search_vsl_v",value=st.session_state.vsl)
                search_voy=s2_col2.text_input("Voyage", key="search_voy_v",value=st.session_state.voy)

            #search_arr=s_col4.date_input("Arrival",key="search_arr")

            query_vsl=None
            results_vsl=None

            if st.session_state.search_cargo=="Vessel List":
                if str(search_vsl) + str(search_voy) !="":
                    query_vsl= f"SELECT DISTINCT Vessel, Voyage, Arrival FROM mtlt_{st.session_state.origin}_facthbl WHERE"
                    if search_vsl!="":
                        query_vsl= query_vsl + f" Vessel LIKE '%{search_vsl}%'"
                    if search_voy!="":
                        query_vsl= query_vsl + f" Voyage LIKE '%{search_voy}%'"
                
                if query_vsl:
                    if st.session_state.vslbl_out==False:
                        results_vsl,columns_vsl = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,query_vsl)
                        st.session_state.vslbl_out=results_vsl
                        st.session_state.vslbl_col=columns_vsl

                    if not st.session_state.vslbl_out:
                        st.info("No records found",icon='ℹ')
                    else:
                        st.info(f"**[   :red[{len(st.session_state.vslbl_out)}]   ]**  Records found. Please select at least 1 record",icon='⭐')   
                        df_vsl = pd.DataFrame.from_records(st.session_state.vslbl_out, columns=st.session_state.vslbl_col)

                        vsl_selected_rows=0
                        with st.expander(":ship: *Vessel List* ",expanded=True):
                            vcol1,vcol2,vcol3,vcol4=st.columns([1.3,1.7,2,2])
                            select_all_vsl = vcol1.checkbox('Select All Vessel')
                            if select_all_vsl:
                                tbl_vsl=st.dataframe(df_vsl,height=300)
                                vsl_selected_rows=df_vsl
                                vsl_idx=df_vsl.index
                            else:        
                                vsl_selected_rows,vsl_idx = vi.dataframe_with_selections(df_vsl)
                            # st.write(len(results_vsl), "Records found")

                        if len(vsl_selected_rows)>=1:
                            vcol2.write(f":blue[📌 **[ :red[{len(vsl_selected_rows)}] ]** *records selected*]")
                            search_bk=s2_col3.text_input("Booking",key="search_bk_v")
                            search_pod=s2_col4.text_input("POD",key="search_pod_v")
                            search_pol=s2_col5.text_input("POL",key="search_pol_v")
                            search_sp=s2_col6.text_input("Shipper",key="search_sp_v")
                            search_cn=s2_col7.text_input("Cnee",key="search_cn_v")

                            vsl_str=''
                            vsl_list=[]
                            voy_str=''
                            voy_list=[]
                            arr_str=''
                            arr_list=[]
                            for rowi_vsl in vsl_idx:
                                vsl_list.append(vsl_selected_rows["Vessel"][rowi_vsl])
                                voy_list.append(vsl_selected_rows["Voyage"][rowi_vsl])
                                arr_list.append(str(vsl_selected_rows["Arrival"][rowi_vsl]))
                            #coonvert list to string with ' begin and end of each item
                            vsl_str = ', '.join([f"'{item}'" for item in vsl_list])
                            voy_str = ', '.join([f"'{item}'" for item in voy_list])
                            arr_str = ', '.join([f"'{item}'" for item in arr_list])

                            query = f"SELECT * FROM mtlt_{st.session_state.origin}_facthbl WHERE Vessel IN ({vsl_str}) AND Voyage IN ({voy_str}) AND Arrival IN ({arr_str})"
                                
                            if search_bk!="":
                                query = query + f" AND Booking LIKE '%{search_bk}%'"
                            if search_pod!="":
                                query = query + f" AND POD LIKE '%{search_pod}%'"
                            if search_pol!="":
                                query = query + f" AND POL LIKE '%{search_pol}%'"
                            if search_sp!="":
                                query = query + f" AND Shipper_Name LIKE '%{search_sp}%'"
                            if search_cn!="":
                                query = query + f" AND Cnee_Name LIKE '%{search_cn}%'"
                            


        elif search_opt== "Multiple":

            s_col2.button(":blue[✅ Multiple]",disabled=True,use_container_width=True)
            
            # search_bt_bk=s_col3.button(":mag_right:",key="search_bt_bk",use_container_width=True)
            # new_bl=s_col4.button("➕",use_container_width=True)
            # clear_bt_bk=s_col5.button("❌",key="clear_bt_bk",use_container_width=True)

            if search_bt_bk:
                st.session_state.search_cargo="Multiple"
                st.session_state.clear_bl=False
                st.session_state.newbl=False
                st.session_state.cargo_out=False

            if clear_bt_bk:
                st.session_state.clear_bl=True
                st.session_state.keyi+=1
                st.session_state.search_cargo=""
                st.session_state.newbl=False
                st.session_state.cargo_out=False
            
            if new_bl:
                st.session_state.newbl=True
                st.session_state.clear_bl=True
                st.session_state.search_cargo=""
                st.session_state.cargo_out=False


            if st.session_state.clear_bl==True:
                search_bk=s2_col3.text_input("Booking", key="search_bk_m" + str(st.session_state.keyi),value='')
                search_vsl=s2_col1.text_input("Vessel",key="search_vsl_m"+ str(st.session_state.keyi),value='')
                search_voy=s2_col2.text_input("Voyage", key="search_voy_m"+ str(st.session_state.keyi),value='')
                search_pod=s2_col4.text_input("POD", key="search_pod_m"+ str(st.session_state.keyi),value='')
                search_pol=s2_col5.text_input("POL", key="search_pol_m"+ str(st.session_state.keyi),value='')

                st.session_state.bk=search_bk
                st.session_state.vsl=search_vsl
                st.session_state.voy=search_voy
                st.session_state.pod=search_pod
                st.session_state.pol=search_pol
            else:
                search_bk=s2_col3.text_input("Booking",key="search_bk_m",value=st.session_state.bk)
                search_vsl=s2_col1.text_input("Vessel",key="search_vsl_m",value=st.session_state.vsl)
                search_voy=s2_col2.text_input("Voyage", key="search_voy_m",value=st.session_state.voy)
                search_pod=s2_col4.text_input("POD", key="search_pod_m",value=st.session_state.pod)
                search_pol=s2_col5.text_input("POL", key="search_pol_m",value=st.session_state.pol)

            # search_arr=s_col5.date_input("Arrival",key="search_arr")

            if st.session_state.search_cargo=="Multiple":  
                # Split the string into a list of values
                search_bk = search_bk.split(',')
                search_vsl = search_vsl.split(',')
                search_voy = search_voy.split(',')
                search_pod = search_voy.split(',')
                search_pol = search_voy.split(',')


                # Enclose each value with single quotes
                search_bk = ",".join(f"'{value.strip()}'" for value in search_bk)
                search_vsl = ",".join(f"'{value.strip()}'" for value in search_vsl)
                search_voy = ",".join(f"'{value.strip()}'" for value in search_voy)
                search_pod = ",".join(f"'{value.strip()}'" for value in search_pod)
                search_pol = ",".join(f"'{value.strip()}'" for value in search_pol)

                # st.write(search_bk)
                # st.write(search_vsl)

                
                if (str(search_bk)+ str(search_vsl)+ str(search_voy)+ str(search_pod)+ str(search_pol)).replace("'","")!="":
                    query = f"SELECT * FROM mtlt_{st.session_state.origin}_facthbl WHERE"
                if search_bk!="''":
                    query = query + f" AND Booking IN ({search_bk})"
                if search_vsl!="''":
                    query = query + f" AND Vessel IN ({search_vsl})"
                if search_voy!="''":
                    query = query + f" AND Voyage IN ({search_voy})"
                if search_pod!="''":
                    query = query + f" AND POD IN ({search_pod})"
                if search_pol!="''":
                    query = query + f" AND POL IN ({search_pol})"
                
                query=query.replace("WHERE AND", "WHERE")
        
        

        elif search_opt== "Arrival Date":

            s_col2.button(":blue[✅ Arrival Date]",disabled=True,use_container_width=True)
            
            # search_bt_bk=s_col3.button(":mag_right:",key="search_bt_bk",use_container_width=True)
            # new_bl=s_col4.button("➕",use_container_width=True)
            # clear_bt_bk=s_col5.button("❌",key="clear_bt_bk",use_container_width=True)

            if search_bt_bk:
                st.session_state.search_cargo="Arrival Date"
                st.session_state.clear_bl=False
                st.session_state.newbl=False
                st.session_state.cargo_out=False

            if clear_bt_bk:
                st.session_state.clear_bl=True
                st.session_state.keyi+=1
                st.session_state.search_cargo=""
                st.session_state.newbl=False
                st.session_state.cargo_out=False
            
            if new_bl:
                st.session_state.newbl=True
                st.session_state.clear_bl=True
                st.session_state.search_cargo=""
                st.session_state.cargo_out=False
            
            # st.write(st.session_state.arr)
            if st.session_state.clear_bl==True:
                search_vsl=s2_col2.text_input("Vessel",key="search_vsl_a" + str(st.session_state.keyi),value='')
                search_voy=s2_col3.text_input("Voyage", key="search_voy_a" + str(st.session_state.keyi),value='')
                search_bk=s2_col4.text_input("Booking", key="search_bk_a" + str(st.session_state.keyi),value='')
                search_arr=s2_col1.date_input("Arrival",key="search_arr_a" + str(st.session_state.keyi),value=date.today())
                search_pod=s2_col5.text_input("POD",key="search_pod_a" + str(st.session_state.keyi),value='')
                search_pol=s2_col6.text_input("POL",key="search_pol_a" + str(st.session_state.keyi),value='')
                search_sp=s2_col7.text_input("Shipper",key="search_sp_a" + str(st.session_state.keyi),value='')
                search_cn=s2_col8.text_input("Cnee",key="search_cn_a" + str(st.session_state.keyi),value='')

                st.session_state.vsl=search_vsl
                st.session_state.voy=search_voy
                st.session_state.bk=search_bk
                st.session_state.arr=search_arr
                st.session_state.pod=search_pod
                st.session_state.pol=search_pol
                st.session_state.sp=search_sp
                st.session_state.cn=search_cn
            else:
                
                search_vsl=s2_col2.text_input("Vessel",key="search_vsl_a",value=st.session_state.vsl)
                search_voy=s2_col3.text_input("Voyage", key="search_voy_a",value=st.session_state.voy)
                search_bk=s2_col4.text_input("Booking", key="search_bk_a",value=st.session_state.bk)
                search_arr=s2_col1.date_input("Arrival", key="search_arr_a",value=st.session_state.arr)
                search_sp=s2_col5.text_input("POD",key="search_pod_a",value=st.session_state.pod)
                search_cn=s2_col6.text_input("POL",key="search_pol_a",value=st.session_state.pol)
                search_sp=s2_col7.text_input("Shipper",key="search_sp_a",value=st.session_state.sp)
                search_cn=s2_col8.text_input("Cnee",key="search_cn_a",value=st.session_state.cn)


            if st.session_state.search_cargo=="Arrival Date":
                
                
                query = f"SELECT * FROM mtlt_{st.session_state.origin}_facthbl WHERE Arrival LIKE '{search_arr}'"
                if search_bk!="":
                    query = query + f" AND Booking LIKE '%{search_bk}%'"
                if search_vsl!="":
                    query = query + f" AND Vessel LIKE '%{search_vsl}%'"
                if search_voy!="":
                    query = query + f" AND Voyage LIKE '%{search_voy}%'"
                if search_pod!="":
                    query = query + f" AND POD LIKE '%{search_pod}%'"
                if search_pol!="":
                    query = query + f" AND POL LIKE '%{search_pol}%'"
                if search_sp!="":
                    query = query + f" AND Shipper_Name LIKE '%{search_sp}%'"
                if search_cn!="":
                    query = query + f" AND Cnee_Name LIKE '%{search_cn}%'"


        else:
    
            s_col2.button(":blue[✅ Wildcard]",disabled=True,use_container_width=True)
            
            # search_bt_bk=s_col3.button(":mag_right:",key="search_bt_bk",use_container_width=True)
            # new_bl=s_col4.button("➕",use_container_width=True)
            # clear_bt_bk=s_col5.button("❌",key="clear_bt_bk",use_container_width=True)

            if search_bt_bk:
                st.session_state.search_cargo="Wildcard"
                st.session_state.clear_bl=False
                st.session_state.newbl=False
                st.session_state.cargo_out=False


            if clear_bt_bk:
                st.session_state.clear_bl=True
                st.session_state.keyi+=1
                st.session_state.search_cargo=""
                st.session_state.newbl=False
                st.session_state.cargo_out=False
            
            if new_bl:
                st.session_state.newbl=True
                st.session_state.clear_bl=True
                st.session_state.search_cargo=""
                st.session_state.cargo_out=False
            

            if st.session_state.clear_bl==True:
                
                search_vsl=s2_col1.text_input("Vessel",key="search_vsl_w" + str(st.session_state.keyi),value='')
                search_voy=s2_col2.text_input("Voyage", key="search_voy_w0" + str(st.session_state.keyi),value='')
                search_bk=s2_col3.text_input("Booking", key="search_bk_w0" + str(st.session_state.keyi),value='')
                search_pod=s2_col4.text_input("POD", key="search_pod_w0" + str(st.session_state.keyi),value='')
                search_pol=s2_col5.text_input("POL", key="search_pol_w0" + str(st.session_state.keyi),value='')
                search_sp=s2_col6.text_input("Shipper", key="search_sp_w0" + str(st.session_state.keyi),value='')
                search_cn=s2_col7.text_input("Cnee", key="search_cn_w0" + str(st.session_state.keyi),value='')
                
                st.session_state.vsl=search_vsl
                st.session_state.voy=search_voy
                st.session_state.bk=search_bk
                st.session_state.pod=search_pod
                st.session_state.pol=search_pol
                st.session_state.sp=search_sp
                st.session_state.cn=search_cn
                
            else:
                search_vsl=s2_col1.text_input("Vessel",key="search_vsl_w",value=st.session_state.vsl)
                search_voy=s2_col2.text_input("Voyage", key="search_voy_w",value=st.session_state.voy)
                search_bk=s2_col3.text_input("Booking", key="search_bk_w",value=st.session_state.bk)
                search_pod=s2_col4.text_input("POD", key="search_pod_w0" ,value=st.session_state.pod)
                search_pol=s2_col5.text_input("POL", key="search_pol_w0" ,value=st.session_state.pol)
                search_sp=s2_col6.text_input("Shipper", key="search_sp_w0",value=st.session_state.sp)
                search_cn=s2_col7.text_input("Cnee", key="search_cn_w0" ,value=st.session_state.cn)


            # search_arr=s_col5.date_input("Arrival",key="search_arr")

            if st.session_state.search_cargo=="Wildcard":
                
                if str(search_bk) + str(search_vsl) + str(search_voy) + str(search_sp) + str(search_cn) + str(search_pod) + str(search_pol) != "":
                    query = f"SELECT * FROM mtlt_{st.session_state.origin}_facthbl WHERE"
                if search_bk!="":
                    query = query + f" AND Booking LIKE '%{search_bk}%'"
                if search_vsl!="":
                    query = query + f" AND Vessel LIKE '%{search_vsl}%'"
                if search_voy!="":
                    query = query + f" AND Voyage LIKE '%{search_voy}%'"
                if search_sp!="":
                    query = query + f" AND Shipper_Name LIKE '%{search_sp}%'"
                if search_cn!="":
                    query = query + f" AND Cnee_Name LIKE '%{search_cn}%'"
                if search_pod!="":
                    query = query + f" AND POD LIKE '%{search_pod}%'"
                if search_pol!="":
                    query = query + f" AND POL LIKE '%{search_pol}%'"
                
                query = query.replace("WHERE AND", "WHERE")



        if query:
            if st.session_state.isDev:
                st.write(query)
            
            if st.session_state.cargo_out==False:
                results,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,query)
                st.session_state.cargo_out=results
                st.session_state["cargo_col"]=columns
            
            
            if not st.session_state.cargo_out:
                st.info("No records found",icon='ℹ')
            else:

                st.info(f"**[   :red[{len(st.session_state['cargo_out'])}]   ]**  Records found. Please select at least 1 record",icon='⭐')   
                # Create a DataFrame with the results and column names
                df = pd.DataFrame.from_records(st.session_state.cargo_out, columns=st.session_state["cargo_col"])

                selected_rows=0
                with st.expander(":bookmark_tabs: *Table Result* ",expanded=True):
                    ecol1,ecol2,ecol3,ecol5=st.columns([1,1,1,1])
                    
                    select_all = ecol1.checkbox('Select All Booking')
                    if select_all:
                        tbl=st.dataframe(df,height=300)
                        selected_rows=df
                        idx=df.index
                        
                    else:         
                        selected_rows,idx = vi.dataframe_with_selections(df)

                    # st.write(len(results), "Records found")                                  

        
                if len(selected_rows)==1:
                    
                    ecol2.write(":blue[📌 **[ :red[1] ]** *record selected*]") 
                    #clear_on_submit=False
                    exp_form=st.expander(":bookmark_tabs: Booking Form",expanded=True)
                    fr1=exp_form.form("entry")
                    fr1_cont1=fr1.container()
                    fr1_cont2=fr1.container()
                            

                    fr1_cont1_col1, fr1_cont1_col2 ,fr1_cont1_col3,fr1_cont1_col4= fr1_cont1.columns([1,1,1.2,1.2])
                    submit_new=fr1_cont1_col1.form_submit_button("✔️Submit New",use_container_width=True)
                    submit_edit=fr1_cont1_col2.form_submit_button("✔️Submit Edit",use_container_width=True)
                    
                    
                    
                    fr1_cont2_col1,fr1_cont2_col2,fr1_cont2_col3=fr1_cont2.columns(3)

                    Booking = fr1_cont2_col1.text_input(":red[*]Booking",key = "bk_e",value=selected_rows['Booking'][idx[0]])  
                    Vessel = fr1_cont2_col1.text_input(":red[*]Vessel",key = "vsl_e",value=selected_rows['Vessel'][idx[0]])
                    Voyage = fr1_cont2_col1.text_input(":red[*]Voyage",key = "voy_e",value=selected_rows['Voyage'][idx[0]])
                    Arrival = fr1_cont2_col1.date_input(":red[*]Arrival",key = "arr_e",value=selected_rows['Arrival'][idx[0]])
                    POL = fr1_cont2_col1.text_input(":red[*]POL",key= "pol_e",value=selected_rows['POL'][idx[0]])
                    POD = fr1_cont2_col1.text_input(":red[*]POD",key= "pod_e",value=selected_rows['POD'][idx[0]])
                    DEL = fr1_cont2_col1.text_input("DEL",key= "del_e",value=selected_rows['DEL'][idx[0]])
                    LINE = fr1_cont2_col1.text_input("LINE",key= "line_e",value=selected_rows['LINE'][idx[0]])
                    Term  = fr1_cont2_col1.text_input("Term",key= "term_e",value=selected_rows['Term'][idx[0]])
                    Cargo_Type = fr1_cont2_col1.text_input("Cargo Type",key= "cargo_e",value=selected_rows['Cargo_Type'][idx[0]])
                    Movement = fr1_cont2_col1.text_input("Movement",key= "move_e",value=selected_rows['Movement'][idx[0]])
                    Freight = fr1_cont2_col2.text_input("Freight",key= "freight_e",value=selected_rows['Freight'][idx[0]])
                    No_Pack = fr1_cont2_col2.text_input(":red[*]No Pack",key= "nopack_e",value=selected_rows['No_Pack'][idx[0]])
                    Pack_Unit = fr1_cont2_col2.text_input(":red[*]Pack Unit",key= "packunit_e",value=selected_rows['Pack_Unit'][idx[0]])
                    Weight = fr1_cont2_col2.text_input(":red[*]Weight",key= "weight_e",value=selected_rows['Weight'][idx[0]])
                    Measurement  = fr1_cont2_col2.text_input(":red[*]Measurement",key= "measure_e",value=selected_rows['Measurement'][idx[0]])

                    Mark  = fr1_cont2_col2.text_area("Mark",key= "mark_e",value=selected_rows['Mark'][idx[0]],height=170)
                    Description  = fr1_cont2_col2.text_area("Description",key= "descr_e",value=selected_rows['Description'][idx[0]],height=250)
                    
                    Shipper_Name = fr1_cont2_col3.text_input(":red[*]Shipper Name",key= "shippername_e",value=selected_rows['Shipper_Name'][idx[0]])
                    Shipper_Address = fr1_cont2_col3.text_area(":red[*]Shipper Address",key= "shipperadd_e",value=selected_rows['Shipper_Address'][idx[0]])
                    Shipper_Country = fr1_cont2_col3.text_input("Shipper Country Code",key= "shippercountry_e",value=selected_rows['Shipper_Country'][idx[0]])
                    Cnee_Name = fr1_cont2_col3.text_input(":red[*]Cnee Name",key= "cneename_e",value=selected_rows['Cnee_Name'][idx[0]])
                    Cnee_Address = fr1_cont2_col3.text_area(":red[*]Cnee Address",key= "cneeadd_e",value=selected_rows['Cnee_Address'][idx[0]])
                    Cnee_Country = fr1_cont2_col3.text_input("Cnee Country Code",key= "cneecountry_e",value=selected_rows['Cnee_Country'][idx[0]])
                    Notify_Name = fr1_cont2_col3.text_input(":red[*]Notify Name",key= "notifyname_e",value=selected_rows['Notify_Name'][idx[0]])
                    Notify_Address = fr1_cont2_col3.text_area("Notify Address",key= "notifyadd_e",value=selected_rows['Notify_Address'][idx[0]])
                    Notify_Country = fr1_cont2_col3.text_input("Notify Country Code",key= "notifycountry_e",value=selected_rows['Notify_Country'][idx[0]])
                    

                        
                    # submit new
                    if submit_new:
                        
                        if Booking and Vessel and Voyage and Arrival and POL and POD and No_Pack and Pack_Unit and Weight and Measurement and Shipper_Name and Shipper_Address and Cnee_Name and Notify_Name:
                    
                            st.toast(f'Submitting new booking...', icon='🎈')
                        
                            # cursor = db.cursor()

                            select_query = f"""
                            SELECT * FROM mtlt_{st.session_state.origin}_facthbl WHERE Booking= '{Booking}'
                            """
                            existing_bk,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,select_query)
                            
                            if existing_bk:
                                mess="Booking number already exist"
                                vi.msg_error(True,mess)
                                    
                            else:
                            
                                flg,e,time_cm=qr.insert_bl_record(True,st.session_state.DB,st.session_state.DATABASE,f'mtlt_{st.session_state.origin}_facthbl', Booking, Vessel, Voyage, Arrival,POL,POD,DEL,LINE, Shipper_Name, Shipper_Address,Shipper_Country,Cnee_Name,Cnee_Address,Cnee_Country,Notify_Name,Notify_Address,Notify_Country,Term,Cargo_Type,Movement,Freight,No_Pack,Pack_Unit,Weight,Measurement,Mark,Description)
                                if flg==True:
                                    # Lists of keys and values
                                    keys = ['Booking', 'Vessel','Voyage','Arrival','POL','POD','DEL','LINE', 'Shipper_Name', 'Shipper_Address','Shipper_Country','Cnee_Name','Cnee_Address','Cnee_Country','Notify_Name','Notify_Address','Notify_Country','Term','Cargo_Type','Movement','Freight','No_Pack','Pack_Unit','Weight','Measurement','Mark','Description']
                                    values = [Booking, Vessel,Voyage,Arrival,POL,POD,DEL,LINE, Shipper_Name, Shipper_Address,Shipper_Country,Cnee_Name,Cnee_Address,Cnee_Country,Notify_Name,Notify_Address,Notify_Country,Term,Cargo_Type,Movement,Freight,No_Pack,Pack_Unit,Weight,Measurement,Mark,Description]

                                    # Create a dictionary using zip
                                    dictionary = dict(zip(keys, values))
                                    st.session_state.cargo_out=False
                                    logging.info("%s :: Insert Booking %s",USERID,Booking)
                                    qr.insert_log(st.session_state.DB,st.session_state.DATABASE,f'mtlt_{st.session_state.origin}_factlog', Booking, None, Vessel, Voyage, Arrival, None, "Insert Booking", f"{Booking} Insert successfully|{str(dictionary)}",time_cm)

                        else:
                            mess="Missing data"
                            vi.msg_error(True,mess)
                    
                            
                    # submit edit
                    if submit_edit:
                        
                        if Booking and Vessel and Voyage and Arrival and POL and POD and No_Pack and Pack_Unit and Weight and Measurement and Shipper_Name and Shipper_Address and Cnee_Name  and Notify_Name:
                    
                            st.toast(f'Editting Booking ...', icon='🎈')
                            select_query = f"""
                            SELECT * FROM mtlt_{st.session_state.origin}_facthbl WHERE Booking= '{Booking}'
                            """
                            existing_bk,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,select_query)

                            if existing_bk:

                                flg,e,time_cm=qr.update_bl_record(True,st.session_state.DB,st.session_state.DATABASE,f'mtlt_{st.session_state.origin}_facthbl', Booking, Vessel,Voyage,Arrival,POL,POD,DEL,LINE, Shipper_Name, Shipper_Address,Shipper_Country,Cnee_Name,Cnee_Address,Cnee_Country,Notify_Name,Notify_Address,Notify_Country,Term,Cargo_Type,Movement,Freight,No_Pack,Pack_Unit,Weight,Measurement,Mark,Description)
                                
                                if flg==True:
                                    # Lists of keys and values
                                    keys = ['Booking', 'Vessel','Voyage','Arrival','POL','POD','DEL','LINE', 'Shipper_Name', 'Shipper_Address','Shipper_Country','Cnee_Name','Cnee_Address','Cnee_Country','Notify_Name','Notify_Address','Notify_Country','Term','Cargo_Type','Movement','Freight','No_Pack','Pack_Unit','Weight','Measurement','Mark','Description']
                                    values = [Booking, Vessel,Voyage,Arrival,POL,POD,DEL,LINE, Shipper_Name, Shipper_Address,Shipper_Country,Cnee_Name,Cnee_Address,Cnee_Country,Notify_Name,Notify_Address,Notify_Country,Term,Cargo_Type,Movement,Freight,No_Pack,Pack_Unit,Weight,Measurement,Mark,Description]

                                    # Create a dictionary using zip
                                    dictionary = dict(zip(keys, values))
                                    
                                    st.session_state.cargo_out=False
                                    logging.info("%s :: Update Booking %s",USERID,Booking)
                                    qr.insert_log(st.session_state.DB,st.session_state.DATABASE,f'mtlt_{st.session_state.origin}_factlog', Booking, None, Vessel, Voyage, Arrival, None, "Update Booking", f"{Booking} Update successfully|{str(dictionary)}",time_cm)
                                    
                            else:
                                mess="Booking number is not existing"
                                vi.msg_error(True,mess)

                        else:
                            mess="Missing data"
                            vi.msg_error(True,mess)


                    # if "del_bl" not in st.session_state:
                    #     st.session_state["del_bl"]=False


                    if "del_yes" not in st.session_state:
                        st.session_state["del_yes"]=False

                    # if delete_bl:
                    #     st.toast(f'Delete Booking', icon='🎈')
                    #     st.session_state["del_bl"]=True

                
                    # if st.session_state["del_bl"]==True:
                    delete_bl=fr1_cont1_col3.popover("❌ Delete Record",use_container_width=True)  
                    # del_cnf = fr1_cont1_col4.container(border=1)
                    # del_cnf.write("Are you sure you wish to delete?")
                    # colf1,colf2=del_cnf.columns([1,1])
                    del_yes = delete_bl.form_submit_button("✅ Confirm",type="primary",use_container_width=True)
                    del_no = delete_bl.form_submit_button("❌ Cancel",use_container_width=True)
                    
                    if del_yes:
                        
                        # fr1_cont1_col5.info("Deleting...")
                        st.toast(f'Deletting Booking ...', icon='🎈')
                        st.session_state["del_yes"]=True
                        # st.session_state["del_bl"]=False
                        
                    if del_no:
                        # fr1_cont1_col5.info("Cancelling...")
                        st.toast(f'Cancelling...', icon='🎈')
                        # st.session_state["del_bl"]=False
                        mess="Cancelled Delete"
                        vi.msg_success(True,mess)
                                    

                        
                    if st.session_state["del_yes"]==True:
                        
                        st.session_state["del_yes"]=False
                        
                        for index, row in selected_rows.iterrows():
                            # some case missing bk (1-Oct-24)
                            #if row['Booking']:
                            flg,e,time_cm=qr.delete_record(False,st.session_state.DB,st.session_state.DATABASE,False,f"mtlt_{st.session_state.origin}_facthbl","Booking",row['Booking'])
                                # flg_cont,e_cont,time_cm=delete_record(False,st.session_state.DB,False,"mtlt_{st.session_state.origin}_factcont","Booking",row['Booking'])
                            
                            
                            if flg==True:
                                st.session_state.cargo_out=False
                                mess=f"{row['Booking']} records deleted successfully"
                                logging.info("%s :: Deleted Booking %s",USERID,mess)
                                qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'mtlt_{st.session_state.origin}_factlog',str(row['Booking']), None, str(row['Vessel']), str(row['Voyage']), str(row['Arrival']), None, "Deleted Booking", mess + '|' + selected_rows.to_json(orient='records', lines=True),time_cm)
                                vi.msg_success(True,mess)
                            else:
                                mess=f"Failed!!!Error: {e}"
                                logging.info("%s :: Deleted Booking %s",USERID,mess)
                                qr.insert_log(st.session_state.DB,st.session_state.DATABASE,  f'mtlt_{st.session_state.origin}_factlog',str(row['Booking']), None, str(row['Vessel']), str(row['Voyage']), str(row['Arrival']), None, "Deleted Booking", mess + '|' + selected_rows.to_json(orient='records', lines=True),time_cm)
                                vi.msg_error(True,mess)
                                



                elif len(selected_rows)>1:
                    ecol2.write(f":blue[📌 **[ :red[{len(selected_rows)}] ]** *records selected*]")
                    
                    # if "del_bl" not in st.session_state:
                    #     st.session_state["del_bl"]=False

                
                    if "del_yes" not in st.session_state:
                        st.session_state["del_yes"]=False

                    # if delete_bl:
                    #     st.toast(f'Delete Booking', icon='🎈')
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
                        st.toast(f'Deleting Booking ...', icon='🎈')
                        st.session_state["del_yes"]=True
                        # st.session_state["del_bl"]=False
                        
                    if del_no:
                        # ecol4.info("Cancelling...")
                        st.toast(f'Cancelling...', icon='🎈')
                        # st.session_state["del_bl"]=False
                        mess="Cancelled Delete"
                        vi.msg_success(True,mess)

                        
                    if st.session_state["del_yes"]==True:
                        st.session_state["del_yes"]=False
                    

                        bk_list=[]
                        vsl_dict={}
                        voy_dict={}
                        arr_dict={}

                        bk_str=''
                        flg=False
                    
                        for index, row in selected_rows.iterrows():
                            # some case missing bk (1-Oct-24)
                            #if row['Booking']:
                            bk= row['Booking']
                            vsl_dict[bk]=row['Vessel']
                            voy_dict[bk]=row['Voyage']
                            arr_dict[bk]=row['Arrival']
                            
                            bk_list.append(bk)
                            bk_str = ', '.join([f"'{item}'" for item in bk_list])
                        

                        flg,e,time_cm=qr.delete_record(False,st.session_state.DB,st.session_state.DATABASE,True,f"mtlt_{st.session_state.origin}_facthbl","Booking",bk_str)
                        time.sleep(1)

                        # final cnf
                        if flg==True:
                            st.session_state.cargo_out=False
                            mess=f"{len(selected_rows)} records deleted successfully!!!"
                            logging.info("%s :: Delete Multiple Booking %s",USERID,mess)
                            qr.insert_log(st.session_state.DB,st.session_state.DATABASE,  f'mtlt_{st.session_state.origin}_factlog',str(bk_list), None, str(vsl_dict), str(voy_dict), str(arr_dict), None, "Delete Multiple Booking", mess + '|' + selected_rows.to_json(orient='records', lines=True),time_cm)
                            vi.msg_success(True,mess)

                        else:
                            mess=f"Failed!!! Error: {e}"
                            logging.info("%s :: Delete Multiple Booking %s",USERID,mess)
                            qr.insert_log(st.session_state.DB,st.session_state.DATABASE, f'mtlt_{st.session_state.origin}_factlog', str(bk_list), None, str(vsl_dict), str(voy_dict), str(arr_dict), None, "Delete Multiple Booking", mess+ '|' + selected_rows.to_json(orient='records', lines=True),time_cm)
                            vi.msg_error(True,mess)



        if st.session_state.newbl==True:
            form_exp=st.expander(":book: *Input Form*",expanded=True)
            fr1=form_exp.form("newbhl")
            #clear_on_submit=True)

            with fr1:
                fr1_col1,fr1_col2,fr1_col3=fr1.columns([1,1,4])
                
                # reset_form=fr1_col2.form_submit_button("Reset Form",use_container_width=True)
                submit_hbl=fr1_col1.form_submit_button("✔️Submit Form",use_container_width=True)

                fr1_cont2=fr1.container()
                
                fr1_cont2_col1,fr1_cont2_col2,fr1_cont2_col3=fr1_cont2.columns(3)
                

                Booking = fr1_cont2_col1.text_input(":red[*]Booking",key = "Booking")
                Vessel = fr1_cont2_col1.text_input(":red[*]Vessel",key = "Vessel")
                Voyage = fr1_cont2_col1.text_input(":red[*]Voyage",key = "Voyage")
                Arrival = fr1_cont2_col1.date_input(":red[*]Arrival",key = "Arrival")
                POL = fr1_cont2_col1.text_input(":red[*]POL",key= "POL")
                POD = fr1_cont2_col1.text_input(":red[*]POD",key= "POD")
                DEL = fr1_cont2_col1.text_input("DEL",key= "DEL")
                LINE = fr1_cont2_col1.text_input("LINE",key= "LINE")
                Term  = fr1_cont2_col1.text_input("Term",key= "Term")
                Cargo_Type = fr1_cont2_col1.text_input("Cargo Type",key= "Cargo_Type")
                Movement = fr1_cont2_col2.text_input("Movement",key= "Movement")
                Freight = fr1_cont2_col2.text_input("Freight",key= "Freight")
                No_Pack = fr1_cont2_col2.text_input(":red[*]No Pack",key= "No_Pack")
                Pack_Unit = fr1_cont2_col2.text_input(":red[*]Pack Unit",key= "Pack_Unit")
                Weight = fr1_cont2_col2.text_input(":red[*]Weight",key= "Weight")
                Measurement  = fr1_cont2_col2.text_input(":red[*]Measurement",key= "Measurement")

                Mark  = fr1_cont2_col2.text_area("Mark",key= "Mark")
                Description  = fr1_cont2_col2.text_area("Description",key= "Description")

                Shipper_Name = fr1_cont2_col3.text_input(":red[*]Shipper Name",key= "Shipper_Name")
                Shipper_Address = fr1_cont2_col3.text_area(":red[*]Shipper Address",key= "Shipper_Address")
                Shipper_Country = fr1_cont2_col3.text_input("Shipper Country Code",key= "Shipper_Country")
                Cnee_Name = fr1_cont2_col3.text_input(":red[*]Cnee Name",key= "Cnee_Name")
                Cnee_Address = fr1_cont2_col3.text_area(":red[*]Cnee Address",key= "Cnee_Address")
                Cnee_Country = fr1_cont2_col3.text_input("Cnee Country Code",key= "Cnee_Country")
                Notify_Name = fr1_cont2_col3.text_input(":red[*]Notify Name",key= "Notify_Name")
                Notify_Address = fr1_cont2_col3.text_area("Notify Address",key= "Notify_Address")
                Notify_Country = fr1_cont2_col3.text_input("Notify Country Code",key= "Notify_Country")
                


            if submit_hbl:
                st.toast(f'Submitting new Booking ...', icon='🎈')
                if Booking and Vessel and Voyage and Arrival and POL and POD and No_Pack and Pack_Unit and Weight and Measurement and Shipper_Name and Shipper_Address and Cnee_Name and Notify_Name:

                    select_query = f"""
                    SELECT * FROM mtlt_{st.session_state.origin}_facthbl WHERE Booking= '{Booking}'
                    """
                    existing_bk,columns = qr.execute_query(st.session_state.DB,st.session_state.DATABASE,select_query)

                    if existing_bk:
                        mess="Booking number already exist"
                        vi.msg_error(True,mess)
                    
                    else:
                        
                        flg,e,time_cm=qr.insert_bl_record(True,st.session_state.DB,st.session_state.DATABASE,f'mtlt_{st.session_state.origin}_facthbl', Booking, Vessel,Voyage,Arrival,POL,POD,DEL,LINE, Shipper_Name, Shipper_Address,Shipper_Country,Cnee_Name,Cnee_Address,Cnee_Country,Notify_Name,Notify_Address,Notify_Country,Term,Cargo_Type,Movement,Freight,No_Pack,Pack_Unit,Weight,Measurement,Mark,Description)
                        if flg==True:
                            # Lists of keys and values
                            keys = ['Booking', 'Vessel','Voyage','Arrival','POL','POD','DEL','LINE', 'Shipper_Name', 'Shipper_Address','Shipper_Country','Cnee_Name','Cnee_Address','Cnee_Country','Notify_Name','Notify_Address','Notify_Country','Term','Cargo_Type','Movement','Freight','No_Pack','Pack_Unit','Weight','Measurement','Mark','Description']
                            values = [Booking, Vessel,Voyage,Arrival,POL,POD,DEL,LINE, Shipper_Name, Shipper_Address,Shipper_Country,Cnee_Name,Cnee_Address,Cnee_Country,Notify_Name,Notify_Address,Notify_Country,Term,Cargo_Type,Movement,Freight,No_Pack,Pack_Unit,Weight,Measurement,Mark,Description]

                            # Create a dictionary using zip
                            dictionary = dict(zip(keys, values))
                            
                            logging.info("%s :: Insert Booking %s",USERID,Booking)
                            qr.insert_log(st.session_state.DB,st.session_state.DATABASE,  f'mtlt_{st.session_state.origin}_factlog',Booking, None, Vessel, Voyage, Arrival, None, "Insert Booking", f"{Booking} Inserted successfully|{str(dictionary)}",time_cm)
                
                else:
                    mess="Missing data"
                    vi.msg_error(True,mess)
                                    







if __name__ == "__main__":

    main()