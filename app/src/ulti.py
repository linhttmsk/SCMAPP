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
import json





def process_logic(logic):
    if isinstance(logic, list):
        if logic[0] in ["and", "or", "not", ">", "<", "=", "+", "-", "*", "/"]:  # Các toán tử
            # Đối với toán tử, thực hiện phép toán cho các đối số
            return f"({process_logic(logic[1])} {logic[0]} {process_logic(logic[2])})"
        elif logic[0] in ["left", "mid"]:  # Các hàm xử lý chuỗi như left, mid
            return f"{logic[0]}({', '.join([process_logic(item) for item in logic[1:]])})"
        else:
            # Đối với các mảng khác, nối các phần tử với dấu phẩy
            return f"({', '.join([process_logic(item) for item in logic])})"
    else:
        return str(logic)





def add_final_check_column(result_dict):
    """
    Thêm cột 'Final_Check' vào DataFrame.
    Nếu có bất kỳ giá trị False trong dòng thì 'Final_Check' là False, ngược lại là True.
    Các cột còn lại sẽ trả về giá trị 'True' hoặc 'False' dưới dạng văn bản, 
    nhưng không thay đổi các chuỗi như 'False[...]'.
    """
    # Nếu result_dict là dict, chuyển đổi thành DataFrame
    if isinstance(result_dict, dict):
        result_dict = pd.DataFrame(result_dict)

    # Hàm để kiểm tra các giá trị có chuỗi dạng 'False[...]' và giữ nguyên chuỗi đó
    def check_boolean(value):
        # Kiểm tra nếu là chuỗi False[...] (không thay đổi chuỗi này)
        if isinstance(value, str) and value.startswith('False[') and value.endswith(']'):
            return value  # Giữ nguyên chuỗi 'False[...]' mà không thay đổi
        # Nếu là kiểu boolean, trả về chính nó (True/False)
        if isinstance(value, bool):
            return value
        return True  # Ngược lại trả về True (các giá trị khác đều coi là True)

    # Áp dụng hàm kiểm tra cho tất cả các giá trị trong DataFrame
    result_dict = result_dict.map(check_boolean)

    # Thêm cột Final_Check dựa trên việc kiểm tra các giá trị trong mỗi dòng
    result_dict["Final_Check"] = result_dict.apply(lambda row: 'True' if all(v == True for v in row) else 'False', axis=1)

    # Chuyển các giá trị boolean còn lại thành 'True' hoặc 'False' dưới dạng văn bản,
    # nhưng không thay đổi các chuỗi như 'False[...]'
    for column in result_dict.columns:
        if column != "Final_Check":
            result_dict[column] = result_dict[column].apply(lambda x: 
                                                           x if isinstance(x, str) and x.startswith('False[') else ('True' if x is True else 'False'))

    return result_dict





def get_operand(operand, df):
    """
    Resolve the operand:
    - If it's a column name, extract it.
    - If it's a nested list, evaluate recursively.
    - Handle TODAY and other scalar values.
    """
    if isinstance(operand, list):
        return eval_logic(df, operand)  # Recursive call for nested operand
    elif isinstance(operand, str):
        if operand == "TODAY":
            return pd.Timestamp.now().normalize()  # Today's date
        elif operand in df.columns:
            return df[operand]  # Extract column
        elif "." in operand and operand in df.columns:
            return df[operand]  # Handle dotted column names
        try:
            return float(operand)  # Convert to number if possible
        except ValueError:
            return operand  # Treat as scalar string
    elif isinstance(operand, (int, float)):
        return operand  # Return scalar number
    else:
        raise ValueError(f"Unsupported operand type: {type(operand)}")



def eval_logic(df, logic):
    """
    Evaluate a logic expression on the DataFrame.
    """
    operator = logic[0]
    operand1 = get_operand(logic[1], df)
    operand2 = get_operand(logic[2], df) if len(logic) > 2 else None

    # Ensure operand1 and operand2 are Series when needed
    if isinstance(operand1, pd.Series) and not isinstance(operand2, pd.Series):
        operand2 = pd.Series([operand2] * len(operand1), index=operand1.index)

    # Handle False by adding [False['a','b']]
    def handle_false(operand1, operator,operand2):
        if isinstance(operand1, pd.Series) and isinstance(operand2, pd.Series):
            return pd.Series([f"False[{operand1.iloc[i]},{operator}, {operand2.iloc[i]}]" if not result else result 
                              for i, result in enumerate(operand1 == operand2)])
        return operand1  # Return the original operand if not Series

    # Perform the logic evaluation
    if operator == ">":
        if isinstance(operand1, pd.Series) and pd.api.types.is_datetime64_any_dtype(operand1):
            if isinstance(operand2, (int, float)):  # Check for scalar number in operand2
                operand2 = operand1 + pd.to_timedelta(operand2, unit="D")
        result = operand1 > operand2
        if isinstance(result, pd.Series):
            return result.where(result, handle_false(operand1,">", operand2))
        return result

    elif operator == "<":
        if isinstance(operand1, pd.Series) and pd.api.types.is_datetime64_any_dtype(operand1):
            if isinstance(operand2, (int, float)):  # Check for scalar number in operand2
                operand2 = operand1 + pd.to_timedelta(operand2, unit="D")
        result = operand1 < operand2
        if isinstance(result, pd.Series):
            return result.where(result, handle_false(operand1,"<", operand2))
        return result

    elif operator == "=":
        result = operand1 == operand2
        if isinstance(result, pd.Series):
            return result.where(result, handle_false(operand1,"=", operand2))
        return result

    elif operator == "!=":
        result = operand1 != operand2
        if isinstance(result, pd.Series):
            return result.where(result, handle_false(operand1,"!=", operand2))
        return result

    elif operator == "+":
        if isinstance(operand1, pd.Timestamp) and isinstance(operand2, (int, float)):
            result = operand1 + pd.Timedelta(days=operand2)
        else:
            result = operand1 + operand2
        if isinstance(result, pd.Series):
            return result.where(result, handle_false(operand1,"+", operand2))
        return result

    elif operator == "if":
        condition = eval_logic(df, logic[1])
        true_value = get_operand(logic[2], df)
        false_value = get_operand(logic[3], df)
        if isinstance(condition, pd.Series):
            result = true_value.where(condition, false_value)
            return result.where(result, handle_false(true_value,"if", false_value))
        return true_value if condition else false_value

    elif operator == "or":
      # Nếu cả operand1 và operand2 đều là chuỗi
      if isinstance(operand1, str) and isinstance(operand2, str):
          result = bool(operand1) or bool(operand2)
      # Nếu operand1 và operand2 là Series
      elif isinstance(operand1, pd.Series) and isinstance(operand2, pd.Series):
          result = operand1.astype(bool) | operand2.astype(bool)
      # Nếu operand1 là Series
      elif isinstance(operand1, pd.Series):
          operand2 = pd.Series([bool(operand2)] * len(operand1), index=operand1.index)
          result = operand1.astype(bool) | operand2
      # Nếu operand2 là Series
      elif isinstance(operand2, pd.Series):
          operand1 = pd.Series([bool(operand1)] * len(operand2), index=operand2.index)
          result = operand1 | operand2.astype(bool)
      else:
          # Với các kiểu dữ liệu khác
          result = bool(operand1) or bool(operand2)

      # Trả về kết quả
      if isinstance(result, pd.Series):
          return result.where(result, handle_false(operand1,"or", operand2))
      return result

    elif operator == "and":
      # Nếu operand1 và operand2 là Series
      if isinstance(operand1, pd.Series) and isinstance(operand2, pd.Series):
          # Chuyển đổi cả hai thành Boolean trước khi áp dụng toán tử &
          result = operand1.astype(bool) & operand2.astype(bool)
      # Nếu operand1 là Series
      elif isinstance(operand1, pd.Series):
          operand2 = pd.Series([bool(operand2)] * len(operand1), index=operand1.index)
          result = operand1.astype(bool) & operand2
      # Nếu operand2 là Series
      elif isinstance(operand2, pd.Series):
          operand1 = pd.Series([bool(operand1)] * len(operand2), index=operand2.index)
          result = operand1 & operand2.astype(bool)
      else:
          # Với các kiểu dữ liệu khác
          result = bool(operand1) and bool(operand2)

      # Trả về kết quả
      if isinstance(result, pd.Series):
          # Đảm bảo điều kiện trong `where` là Boolean
          return result.where(result.astype(bool), handle_false(operand1,"and", operand2))
      return result


    elif operator == "left":
        if not isinstance(operand1, pd.Series):
            operand1 = pd.Series([operand1] * len(df))
        operand1 = operand1.astype(str)  # Ensure string type
        result = operand1.str[:logic[2]]
        if isinstance(result, pd.Series):
            return result.where(result, handle_false(operand1,"left", result))
        return result

    elif operator == "mid":
        if not isinstance(operand1, pd.Series):
            operand1 = pd.Series([operand1] * len(df))
        operand1 = operand1.astype(str)
        start, length = logic[2], logic[3]
        result = operand1.str[start:start + length]
        if isinstance(result, pd.Series):
            return result.where(result, handle_false(operand1,"mid", result))
        return result

    elif operator == "right":
        if not isinstance(operand1, pd.Series):
            operand1 = pd.Series([operand1] * len(df))
        operand1 = operand1.astype(str)
        result = operand1.str[-logic[2]:]
        if isinstance(result, pd.Series):
            return result.where(result, handle_false(operand1,"right", result))
        return result

    else:
        raise ValueError(f"Unsupported operator: {operator}")





# def eval_logic(df, logic):
#     """
#     Evaluate a logic expression on the DataFrame.
#     """
#     operator = logic[0]
#     operand1 = get_operand(logic[1], df)
#     operand2 = get_operand(logic[2], df) if len(logic) > 2 else None

#     # Ensure operand1 and operand2 are Series when needed
#     if isinstance(operand1, pd.Series) and not isinstance(operand2, pd.Series):
#         operand2 = pd.Series([operand2] * len(operand1), index=operand1.index)

#     if operator == ">":
#         # Handle Timestamp comparison with int/float
#         if isinstance(operand1, pd.Series) and pd.api.types.is_datetime64_any_dtype(operand1):
#             if isinstance(operand2.iloc[0], (int, float)):  # Check for scalar number in operand2
#                 operand2 = operand1 + pd.to_timedelta(operand2, unit="D")
#         return operand1 > operand2
#     elif operator == "<":
#         # Handle Timestamp comparison with int/float
#         if isinstance(operand1, pd.Series) and pd.api.types.is_datetime64_any_dtype(operand1):
#           if isinstance(operand2.iloc[0], (int, float)):  # Check for scalar number in operand2
#             operand2 = operand1 + pd.to_timedelta(operand2, unit="D")
#         return operand1 < operand2
#     elif operator == "=":
#       return operand1 == operand2
#     elif operator == "!=":
#       return operand1 != operand2
#     elif operator == "+":
#         if isinstance(operand1, pd.Timestamp) and isinstance(operand2, (int, float)):
#           return operand1 + pd.Timedelta(days=operand2)
#         return operand1 + operand2
#     elif operator == "if":
#         condition = eval_logic(df, logic[1])
#         true_value = get_operand(logic[2], df)
#         false_value = get_operand(logic[3], df)
#         if isinstance(condition, pd.Series):
#           return true_value.where(condition, false_value)
#         return true_value if condition else false_value
#     elif operator == "or":
#       return operand1 | operand2
#     elif operator == "and":
#       return operand1 & operand2
#     elif operator == "left":
#         if not isinstance(operand1, pd.Series):
#             operand1 = pd.Series([operand1] * len(df))
#         operand1 = operand1.astype(str)  # Ensure string type
#         return operand1.str[:logic[2]]
#     elif operator == "mid":
#         if not isinstance(operand1, pd.Series):
#             operand1 = pd.Series([operand1] * len(df))
#         operand1 = operand1.astype(str)
#         start, length = logic[2], logic[3]
#         return operand1.str[start:start + length]
#     elif operator == "right":
#         if not isinstance(operand1, pd.Series):
#             operand1 = pd.Series([operand1] * len(df))
#         operand1 = operand1.astype(str)
#         return operand1.str[-logic[2]:]
#     else:
#         raise ValueError(f"Unsupported operator: {operator}")







# def eval(df,args):
#   operator = args[0]
#   if operator=="or":
#     return eval(args[2]) or eval(args[1])
#   elif operator=="and":
#     return eval(args[2]) and eval(args[1])
#   elif operator=="mid":
#     return eval(eval(args[3])[args[1]:args[1] + args[2]])
#   elif operator=="left":
#     return eval(eval(args[2])[:args[1]])
#   elif operator=="right":
#     return eval(args[2][args[1]:])
#   elif operator=="=":
#     return eval(args[1]) == eval(args[2])
#   elif operator=="+":
#     return eval(args[1]) + eval(args[2])
#   elif operator =="*":
#     return eval(args[1]) * eval(args[2])
#   elif operator=="<":
#     return eval(args[1]) < eval(args[2])
#   elif operator=="if":

#         if (eval(arg[1])):
#               return eval(arg[2]) 
#         else:
#               return eval(arg[3])
#   else:
#         return args[0]




def auto_break(user_string, chunk_size):
    output = []
    word=user_string.replace('\n', ' ')
    words = word.split(" ")
    
    total_length = 0
    out=user_string
    while (total_length < len(user_string) and len(words) > 0):
        line = []
        next_word = words[0]
        line_len = len(next_word) + 1

        while  (line_len < chunk_size) and len(words) > 0:
            words.pop(0)
            line.append(next_word)


            if (len(words) > 0):
                next_word = words[0]
                line_len += len(next_word) + 1
        
        if line==[]:
            next_word=words[0]
            added_word=0
            rest_word=next_word
            add_word=''
            words.pop(0)
            while len(rest_word)>0:
                if len(rest_word) >=chunk_size:
                    add_word=rest_word[0:chunk_size]
                else:
                    add_word=rest_word[0:len(rest_word)]
                
                # print(add_word)
                added_word+=len(add_word)
                rest_word=next_word[added_word:]
                line = add_word
                output.append(line)
                total_length += len(line) 
                out=""
                # print(added_word)
                # print(len(rest_word))
            for line in output:
                out=out + '\n' + line.strip()
        else:
            line = " ".join(line)
            output.append(line)
            total_length += len(line) 
            out=""
            for line in output:
                out=out + '\n' + line.strip()
    return out




def terminate_excel_by_file_path(file_path_to_terminate):
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if 'EXCEL.EXE' in process.info['name']:
            try:
                # st.write(' '.join(process.info['cmdline']).lower())
                # Check if Excel process has the specified file path in its command line
                if file_path_to_terminate.lower() in ' '.join(process.info['cmdline']).lower():
                    
                    psutil.Process(process.info['pid']).terminate()
                    print(f"Terminated Excel process with PID {process.info['pid']} for file path: {file_path_to_terminate}")
            except Exception as e:
                print(f"Error terminating Excel process: {e}")


def get_latest_subfolder(parent_folder):
    # List all subdirectories in the parent folder
    subfolders = [f.path for f in os.scandir(parent_folder) if f.is_dir()]
    
    # If there are no subfolders, return None
    if not subfolders:
        return None

    # Find the latest subfolder based on creation time
    latest_subfolder = max(subfolders, key=os.path.getctime)
    return latest_subfolder



def list_files_in_folder(folder):
    # List all files in the given folder
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    return files