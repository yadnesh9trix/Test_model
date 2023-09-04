# import required libraries
import pandas as pd
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ---------------------------------------------------------------------------------------------------
# Define today's date
today = datetime.today().date()

# Date format's
tday_dbyfmt = today.strftime("%d_%b_%Y")
tday_dmyfmt = today.strftime("%d%m%Y")

# Define the that day's date
day = today - timedelta(days=3)
day_ddmmyyyy = day.strftime("%d%m%Y")

# Start
if __name__ == '__main__':
    main_path = r"D:/"
    std_path = r"D:\Master Data/"
    inppath = std_path + "Input/"
    outpth = std_path + "Output/" + tday_dbyfmt + "/"
    paidamount_file = main_path + "Paidamount/"
    tax_data = main_path + "/Tax_Data/"
    os.makedirs(outpth,exist_ok=True)

def read_paidamount_data(paidamount_file, day):
    ## Read YTD data
    ytddata = pd.read_excel(paidamount_file + f"Paidamount_list_{day}.xlsx")

    ## Replace the property code values in ytd data
    ytddata["propertycode"] = ytddata["propertycode"].replace("1100900002.10.10", "1100900002.20")
    ytddata['propertycode'] = ytddata['propertycode'].astype(float)
    ytddata.dropna(subset=['propertycode'], how='all', inplace=True)
    ytddata1 = ytddata.sort_values('receiptdate')
    ytddata1 = ytddata1.groupby(['propertycode']).agg({'receiptdate': 'last', 'paidamount': 'sum'}).reset_index()

    ytddata1 = ytddata1.rename(
        columns={'receiptdate': 'This Year Paiddate', 'paidamount': 'This Year Paidamount'})
    ytddata1 = ytddata1[['propertycode', 'This Year Paiddate', 'This Year Paidamount']]
    ytddata1['paidTY_Flag'] = 1
    return ytddata1

def execute_data(inppath,tax_data):
    # Read property data
    property_file = "Demand Excluding Illegal 2023-24 27072023.csv"
    property_data = pd.read_csv(inppath + property_file)
    property_data.dropna(subset=['propertycode', 'propertykey'], how='all', inplace=True)
    property_data['propertycode'] = property_data['propertycode'].astype(float)

    return property_data

# Defined the property bill details, receipt details and property list details.
property_data = execute_data(inppath,tax_data)

# Excecuting the Today's Paid Amount Data.
paidamount_ty = read_paidamount_data(paidamount_file, day_ddmmyyyy)

# Rename in standard columns 'arrearsdemand', 'currentdemand', and 'totaldemand'
property_data_list = property_data.rename(columns={'arrearsdemand': 'Arrears',
                                                        'currentdemand': 'Current Bill',
                                                        'totaldemand': 'Total_Amount',
                                                        'zonename': 'Zone',
                                                        'gatname': 'Gat'})

pdata =  property_data_list[['propertycode', 'Arrears', 'Current Bill', 'Total_Amount']]

pty_pdata =  paidamount_ty.merge(pdata,on='propertycode',how='left')