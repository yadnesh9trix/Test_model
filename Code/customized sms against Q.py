import pandas as pd
import numpy as np
from datetime import datetime,timedelta
import warnings
warnings.filterwarnings('ignore')
from openpyxl import load_workbook
import os
import polars

today = datetime.today().date()
last_day = today - timedelta(days=0)

last_day_fmt = last_day.strftime("%d%m%Y")

tday  = today.strftime("%d%b%Y")


def paidamount_data(paidamount_file, last_dmyfmt):
    ## Read YTD data
    ytddata = pd.read_excel(paidamount_file + f"Paidamount_list_{last_dmyfmt}.xlsx")
    ## Replace the property code values in ytd data
    ytddata["propertycode"] = ytddata["propertycode"].replace("1100900002.10.10", "1100900002.20")
    ytddata['propertycode'] = ytddata['propertycode'].astype(float)
    ytddata.dropna(subset=['propertycode'], how='all', inplace=True)
    ytddata1 = ytddata.sort_values('receiptdate')
    ytddata1 = ytddata1.groupby(['propertycode']).agg({'receiptdate': 'last', 'paidamount': 'sum'}).reset_index()
    ytddata1 = ytddata1.rename(
        columns={'receiptdate': 'This Year Paiddate'})
    ytddata1 = ytddata1[['propertycode', 'This Year Paiddate']]
    ytddata1['paidTY_Flag'] = 1
    return ytddata1

def lastyear_paid(inppath):
    lypaid = pd.read_csv(inppath + "Paid_amount 2022-04-01 To 2023-03-31.csv")
    lypaid["propertycode"] = lypaid["propertycode"].replace("1100900002.10.10", "1100900002.20")
    lypaid['propertycode'] = lypaid['propertycode'].astype(float)
    lypaid = lypaid.rename(columns={'receiptdate': 'last payment date'})
    lypaid.dropna(subset=['propertycode'], how='all', inplace=True)
    lypaid = lypaid.rename(columns={'receiptdate': 'last payment date','paidamount':'last payment amount'})
    lypaid = lypaid[['propertycode', 'last payment date', 'last payment amount']]
    lypaid1 = lypaid.sort_values('last payment date')
    lypaid1 = lypaid1.groupby(['propertycode']).agg({'last payment date': 'last', 'last payment amount': 'sum'}).reset_index()

    return lypaid1

def convert_mobilefmt(df, col_name):
    try:
        df[col_name] = df[col_name].str.extract(r'(\d{10})')
    except:
        pass
    df[col_name] = df[col_name].fillna(0000000000).astype("int64")
    df[col_name] = np.where((df[col_name] > 5999999999)
                            & (df[col_name] <= 9999999999),
                            df[col_name], np.nan)
    return df


def Q1234_JaptiAgainstSMS(inppath,paidamount_path,outpth):

    df = pd.read_excel(inppath + "DefaultersList-19July23.xlsx")
    df['propertycode'] = df['propertycode'].astype(float)

    typaid = paidamount_data(paidamount_path,last_day_fmt)

    ly_paid =  lastyear_paid(inppath)
    df_lypaid = df.merge(ly_paid,on='propertycode',how='left')

    df_lypaid['last payment date'] = pd.to_datetime(df_lypaid['last payment date'])
    df_lypaid['Quarter'] = pd.PeriodIndex(df_lypaid['last payment date'],freq="Q-Mar").strftime("Q%q")

    df_lypaid['Quarter'] = np.where(pd.isna(df_lypaid['Quarter']), 'defaulter', df_lypaid['Quarter'])

    cleaned_data = convert_mobilefmt(df_lypaid, 'mobileno')

    cleaned_data_typaid = cleaned_data.merge(typaid,on='propertycode',how='left')

    cleaned_data1 = pd.DataFrame(cleaned_data_typaid,columns=['propertykey', 'propertycode', 'propertyname',
       'propertyaddress','mobileno', 'arrears', 'current', 'total',
       'last payment date', 'Quarter','paidTY_Flag'])

    # cleaned_data1.to_excel(outpth + f"SMSdefaulterlist_{tday}.xlsx",index=False)

    # Step 1: Rename the 'total' column to 'Amount' in one step
    rename_dataSMS = cleaned_data1.rename(columns={'total': 'Amount'})

    # Step 2: Filter out rows with 'paidTY_Flag' equal to 1
    woutpaid_dataSMS = rename_dataSMS[rename_dataSMS['paidTY_Flag'] != 1]

    sms_data = pd.DataFrame(woutpaid_dataSMS,columns=['mobileno', 'propertycode', 'propertyname','Amount', 'Quarter'])

    # Step 3: Create separate DataFrames for each quarter and the defaulters
    Q1 = sms_data[sms_data['Quarter'] == 'Q1'].drop(columns=['Quarter'])
    Q2 = sms_data[sms_data['Quarter'] == 'Q2'].drop(columns=['Quarter'])
    Q3_4 = sms_data[sms_data['Quarter'].isin(['Q3', 'Q4'])].drop(columns=['Quarter'])
    japti = sms_data[sms_data['Quarter'] == 'defaulter'].drop(columns=['Quarter'])

    # Step 4: Create Japti_25kabove DataFrame directly without using an intermediate variable
    Japti_25kabove = japti[japti['Amount'] >= 25000]

    # Step 5: Save the DataFrames to CSV files
    Q1.to_csv(outpth + f"Q1_SMS_data{tday}.csv", index=False, encoding='utf-8-sig')
    Q2.to_csv(outpth + f"Q2_SMS_data{tday}.csv", index=False, encoding='utf-8-sig')
    Q3_4.to_csv(outpth + f"Q3Q4_SMS_data{tday}.csv", index=False, encoding='utf-8-sig')
    Japti_25kabove.to_csv(outpth + f"Japti_SMS_data{tday}.csv", index=False, encoding='utf-8-sig')


## Start
if __name__ == '__main__':
    main_path = r"D:/"
    std_path= r"D:\Test_model/"
    inppath = std_path + "Input/"
    paidamount_path = main_path + "Paidamount/"
    outpth = std_path + "OutPut/" + tday + "/"

    os.makedirs(outpth,exist_ok=True)

    Q1234_JaptiAgainstSMS(inppath,paidamount_path,outpth)

