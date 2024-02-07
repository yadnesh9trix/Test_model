import pandas as pd
import numpy as np
from datetime import datetime,timedelta
import warnings
warnings.filterwarnings('ignore')
# from openpyxl import load_workbook
import os

today = datetime.today().date()
last_day = today - timedelta(days=0)
td_date = last_day.strftime("%d")
td_month = last_day.strftime("%m")
last_day_fmt = last_day.strftime("%d%m%Y")
tday  = today.strftime("%d_%b_%Y")

## Start
# Define constants
MAIN_PATH = r"D:/"
STD_PATH = r"D:\Test_model/"
INP_PATH = STD_PATH + "Input/"
PAID_AMOUNT_FOLDER = MAIN_PATH + "Paidamount/"
OUT_PATH = STD_PATH + "OutPut/"


df = pd.read_excel(INP_PATH + "Defaulter List with Mobile number 271223.xlsx")


# Define a function 'convert_mobilefmt' to extract and format mobile numbers in a DataFrame column
def convert_mobilefmt(df, col_name):
    try:
        df[col_name] = df[col_name].str.replace(r'^\+91-', '', regex=True)
        df[col_name] = df[col_name].str.extract(r'(\d{10})')
    except:
        pass
    df[col_name] = df[col_name].fillna(0000000000).astype("int64")
    df[col_name] = np.where((df[col_name] > 5999999999) & (df[col_name] <= 9999999999),
                            df[col_name], np.nan)
    return df


df_cleaned = convert_mobilefmt(df, 'propertyContactNo')

# df_cleaned.dropna(subset=["propertyContactNo"])

df_cleaned.to_excel(OUT_PATH +"Defaulters_Data_ForTelecalling.xlsx",index=False )