import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["streamlit","streamlit_modal","streamlit_cookies_manager","streamlit.components.v1","pyodbc","hydralit_components","pymupdf","xlwings"], "excludes": [""]}

# GUI applications require a different base on Windows (the default is for a
# Setting base to None will use the default, which shows console.
#base = "Win32GUI"
base = None

setup(  name = "MIMS",
        version = "1.0",
        description = "MIMS manifest app",
        options = {"build_exe": build_exe_options},
        executables = [Executable("MIMS.py", base=base,icon = 'sun.ico')])