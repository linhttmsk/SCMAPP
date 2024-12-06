import streamlit as st
from streamlit_modal import Modal
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
import pandas as pd



global db,SERVER, DATABASE, USERNAME, PASSWORD,cookies


# Get the absolute path of the current script file
script_path = sys.argv[0]
absolute_path = os.path.abspath(script_path)
folder_path0 = os.path.dirname(absolute_path)
folder_path = os.path.dirname(folder_path0)


USERID= getpass.getuser()
DATETIME=datetime.now()
DATETIMEFORMAT="%d/%m/%Y %H:%M:%S"
DATETIMEFM = datetime.now().strftime(DATETIMEFORMAT)



def appConfig(title,isSidebar,sidebarState):

    # #hide sidebar
    # st.set_option("client.showSidebarNavigation",False)

    # set page configure to customize hambger menu, default wide mode,
    st.set_page_config(
        page_title= title,
        page_icon="🌞",
        layout="wide",
        initial_sidebar_state= sidebarState,
        menu_items={
            'Report a bug':'https://forms.office.com/e/1YeG32yGVH',
            'About': 
            '''
            
            # Developed by MEK CI Automation
            ### Thanks🌞
            

            -------

            '''
        }
    )
    

    html(f"""<script>
        var decoration = window.parent.document.querySelectorAll('[data-testid="stDecoration"]')[0];
        decoration.style.height = "3.7rem";
        decoration.style.right = "250px";
        decoration.style.left = "250px";

        // Adjust text decorations
        decoration.innerText = "{title}";
        decoration.style.fontWeight = "bold";
        decoration.style.fontSize = "1.5rem";
        decoration.style.display = "flex";
        decoration.style.justifyContent = "center";
        decoration.style.alignItems = "center";
        decoration.style.color = "#EBF4F6";
        decoration.style.background = "#496989";
      

        var header = window.parent.document.querySelectorAll('[data-testid="stHeader"]')[0];
        header.style.height = "3.7rem";

        // Adjust text header
        
        header.style.background = "#496989";
        </script>
    """, width=0, height=0)

    
    # header.style.fontSize = "1.5rem";
    # header.style.display = "flex";
    # header.style.justifyContent = "center";
    # header.style.alignItems = "center";
    #header.style.color = "darkblue";

    
    side_bg_ext='png'
    side_bg= os.path.join(folder_path0 + r'\img', 'maersk.png')

    # style
    common_style=f"""
                    <style>
                    .block-container {{
                        padding-top: 0rem;
                        padding-bottom: 1rem;
                        padding-left: 1.2rem;
                        padding-right: 1rem;
                    }}
                    [data-testid="stDeployButton"] {{
                        display: none;  
                    }}
                    [data-testid="stAppDeployButton"] {{
                        display: none;  
                    }}
                    [data-testid="stSidebar"]{{
                    visibility: {isSidebar};
                    }}
                    [data-testid="baseButton-headerNoPadding"]{{
                    visibility: {isSidebar};
                    }}
                    [data-testid="stBaseButton-headerNoPadding"]{{
                    visibility: {isSidebar};
                    }}
                    [data-testid="baseButton-primary"]{{
                        display: inline-block;
                        padding: 5px 20px;
                        background-color: #58A399;’
                        color: #C5DFF8;
                        text-align: center;
                        text-decoration: none;
                        font-size: 16px; 
                        border-radius: 8px;’
                    }}
                    [data-testid="baseButton-secondary"]{{
                            display: inline-block;
                            padding: 5px 20px;
                            background-color: #5DEBD7;’
                            color:Blue;
                            text-align: center;
                            text-decoration: none;
                            font-size: 13px; 
                            border-radius: 8px;’
                    }}
                    [data-testid="baseButton-secondaryFormSubmit"]{{
                            display: inline-block;
                            padding: 5px 20px;
                            background-color: #5DEBD7;’
                            color: #C5DFF8;
                            text-align: center;
                            text-decoration: none;
                            font-size: 16px; 
                            border-radius: 8px;’
                    }}
                    [data-testid="stBaseButton-primary"]{{
                        display: inline-block;
                        padding: 5px 20px;
                        background-color: #58A399;’
                        color: #C5DFF8;
                        text-align: center;
                        text-decoration: none;
                        font-size: 16px; 
                        border-radius: 8px;’
                    }}
                    [data-testid="stBaseButton-secondary"]{{
                            display: inline-block;
                            padding: 5px 20px;
                            background-color: #5DEBD7;’
                            color:Blue;
                            text-align: center;
                            text-decoration: none;
                            font-size: 13px; 
                            border-radius: 8px;’
                    }}
                    [data-testid="stBaseButton-secondaryFormSubmit"]{{
                            display: inline-block;
                            padding: 5px 20px;
                            background-color: #5DEBD7;’
                            color: #C5DFF8;
                            text-align: center;
                            text-decoration: none;
                            font-size: 16px; 
                            border-radius: 8px;’
                    }}
                    
                    [data-testid="stPopoverButton"]{{
                            background-color: #A8CD9F;’
                    }}
                    [data-testid="stExpander"]{{
                            background-color: #EBF4F627;’
                    }}
                    [data-testid="stSidebarHeader"] {{
                        background-image: url(data:image/{side_bg_ext};base64,{base64.b64encode(open(side_bg, "rb").read()).decode()});
                        background-repeat: no-repeat;
                        padding-top: 0px;
                        background-position: 0px 0px;
                       
                    }}
                   
                    </style>        
                """
    st.markdown(common_style,unsafe_allow_html=True)
    

    
    # .stSidebar {display:none;}
    # .stSidebarCollapsedControl {display:none;}
    #.stDeployButton {display:none;}
    ##MainMenu {visibility: hidden;} 

                # [data-testid="stExpander"]{{
                #         background-color: #58A39940;’
                # }}

    # sidebar_style="""
    #             <style>
    #             [data-testid="stSidebar"]{
    #             visibility: visible;
    #             }
    #             [data-testid="baseButton-headerNoPadding"]{
    #             visibility: visible;
    #             }
    #             </style>            
    #          """
    # st.markdown(sidebar_style,unsafe_allow_html=True)





    

def st_fixed_container(
    *,
    height: int | None = None,
    border: bool | None = None,
    mode: Literal["fixed", "sticky"] = "fixed",
    position: Literal["top", "bottom"] = "top",
    margin: str | None = None,
    transparent: bool = True,
    ):
    global counter
    # fixed container
    FIXED_CONTAINER_CSS = """
    :root {{
        --background-color: #ffffff; /* Default background color */
    }}
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div.fixed-container-{id}):not(:has(div.not-fixed-container)) {{
        position: {mode};
        width: inherit;
        background-color: inherit;
        {position}: {margin};
        z-index: 999;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div.fixed-container-{id}):not(:has(div.not-fixed-container)) div[data-testid="stVerticalBlock"]:has(div.fixed-container-{id}):not(:has(div.not-fixed-container)) > div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: transparent;
        width: 100%;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div.fixed-container-{id}):not(:has(div.not-fixed-container)) div[data-testid="stVerticalBlock"]:has(div.fixed-container-{id}):not(:has(div.not-fixed-container)) > div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: var(--background-color);
    }}
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div.fixed-container-{id}):not(:has(div.not-fixed-container)) div[data-testid="stVerticalBlock"]:has(div.fixed-container-{id}):not(:has(div.not-fixed-container)) > div[data-testid="element-container"] {{
        display: none;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div.not-fixed-container):not(:has(div[class^='fixed-container-'])) {{
        display: none;
    }}
    """.strip()

    FIXED_CONTAINER_JS = """
    const root = parent.document.querySelector('.stApp');
    let lastBackgroundColor = null;
    function updateContainerBackground(currentBackground) {
        parent.document.documentElement.style.setProperty('--background-color', currentBackground);
        ;
    }
    function checkForBackgroundColorChange() {
        const style = window.getComputedStyle(root);
        const currentBackgroundColor = style.backgroundColor;
        if (currentBackgroundColor !== lastBackgroundColor) {
            lastBackgroundColor = currentBackgroundColor; // Update the last known value
            updateContainerBackground(lastBackgroundColor);
        }
    }
    const observerCallback = (mutationsList, observer) => {
        for(let mutation of mutationsList) {
            if (mutation.type === 'attributes' && (mutation.attributeName === 'class' || mutation.attributeName === 'style')) {
                checkForBackgroundColorChange();
            }
        }
    };
    const main = () => {
        checkForBackgroundColorChange();
        const observer = new MutationObserver(observerCallback);
        observer.observe(root, { attributes: true, childList: false, subtree: false });
    }
    // main();
    document.addEventListener("DOMContentLoaded", main);
    """.strip()


    MARGINS = {
        "top": "2.875rem",
        "bottom": "0",
    }


    counter = 0


    if margin is None:
        margin = MARGINS[position]
    

    fixed_container = st.container()
    non_fixed_container = st.container()
    css = FIXED_CONTAINER_CSS.format(
        mode=mode,
        position=position,
        margin=margin,
        id=counter,
    )
    with fixed_container:
        html(f"<script>{FIXED_CONTAINER_JS}</script>", scrolling=True, height=0)
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='fixed-container-{counter}'></div>",
            unsafe_allow_html=True,
        )
    with non_fixed_container:
        st.markdown(
            f"<div class='not-fixed-container'></div>",
            unsafe_allow_html=True,
        )
    counter += 1

    parent_container = fixed_container if transparent else fixed_container.container()
    return parent_container.container(height=height, border=border)




# def add_logo():
#     side_bg_ext='png'
#     side_bg= os.path.join(folder_path0 + r'\img', 'maersk.png')
#     st.markdown(
#         f"""
#         <style>
#             [data-testid="stHeader"] {{
#                 background-image: url(data:image/{side_bg_ext};base64,{base64.b64encode(open(side_bg, "rb").read()).decode()});
#                 background-repeat: no-repeat;
#                 padding-top: 0px;
#                 background-position: 0px 0px;
#             }}
#         </style>
       
#         """,
#         unsafe_allow_html=True,
#     )
    
# <div>
#     [data-testid="stHeader"] {{
#         }}
#     <h1 style='text-align: center; color: #365486;'>🌞  SCM Planning Application</h1>
# </div>





def dataframe_with_selections(df,myHeight):
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Select", False)
    edited_df = st.data_editor(
        df_with_selections,
        hide_index=False,
        column_config={"Select": st.column_config.CheckboxColumn(required=True)},
        disabled=df.columns,
        height=myHeight
        # num_rows="dynamic"
    )
    
    # Filter the dataframe using the temporary column
    selected_rows = edited_df[edited_df["Select"]]
    return selected_rows.drop("Select", axis=1),selected_rows.index





# def find_start_row_index(df,file):
#     if file=="xlsx":
#         # Function to find the row index where the first column starts with "Container"
#         for i, value in enumerate(df.iloc[: 0]):
#             if str(value).startswith("Container"):
#                 return i
#     elif file=="csv":
#         for i, value in enumerate(df.iloc[:, 0]):
#             if str(value).startswith("Container"):
#                 return i
#     else:
#         return None

def find_start_row_index(df,file):
    # st.write(df.iloc[: 0])
    for i, value in enumerate(df.iloc[: 0]):
        # st.write(value)
        if not str(value).startswith('Unnamed') and not str(value).startswith('nan'):
            return i
        break
    else:
        return None 




def msg_success(alert,mess):
    if alert==True:
        
        modal = Modal(key="success",title="🎊 Success",padding=5,max_width=700)
        with modal.container():
            exp=st.expander("*Bravo*",expanded=True)
            alert=exp.success(mess, icon="✅")
            # time.sleep(3)
            # modal.close()                     
    else:
        st.success(mess,icon="✅") 




def msg_error(alert,mess):
    if alert==True:
        modal = Modal(key="error",title="🚨 Error",padding=5,max_width=700)
        with modal.container():
            exp=st.expander("*Something went wrong*",expanded=True)
            alert=exp.error(mess, icon="❌")
            # time.sleep(3)
            # modal.close()                     
    else:
        st.error(mess,icon="🚨") 




def msg_warning(alert,mess):
    if alert==True:
        modal = Modal(key="warning",title="⚠️ Warning",padding=5,max_width=700)
        with modal.container():
            exp=st.expander("*Be carefull*",expanded=True)
            alert=exp.warning(mess, icon="⚠️")
            # time.sleep(3)
            # modal.close()                     
    else:
        st.warning(mess,icon="⚠️") 



if __name__ == "__main__":

    pass