import pandas as pd
import numpy as np
from datetime import datetime,timedelta
import warnings
warnings.filterwarnings('ignore')
import os
import datetime
import time
import warnings
warnings.filterwarnings('ignore')

#-----------------------------------------------------------------------------------------------------------------------
## Define the today's date
today = datetime.datetime.today().date()
tday  =today.strftime("%d_%b_%Y")

last_day = today - timedelta(days=1)

td_date = last_day.strftime("%d")
td_month = last_day.strftime("%m")
day = last_day.strftime("%d%m%Y")
#-----------------------------------------------------------------------------------------------------------------------

## Start
if __name__ == '__main__':
    main_path = r"D:/"
    std_path= r"D:\Test_model/"
    inppath = std_path + "Input/"
    outpth = std_path + "OutPut/" + tday + "/"
    tax_data = main_path + "/Tax_Data/"
    paidamount_folder = main_path + "Paidamount/"
    if os.path.exists(outpth):
        pass
    else:
        os.mkdir(outpth)
    mappath = std_path +  "Mapping/"


def Ty_paid(paidamount_folder, day):
    typaid = pd.read_excel(paidamount_folder + f"Paidamount_list_{day}.xlsx")
    typaid['propertycode'] = typaid['propertycode'].astype(float)
    typaid['propertycode'] = typaid['propertycode'].apply("{:.02f}".format)
    typaid.dropna(subset=['propertycode'], how='all', inplace=True)

    return typaid

this_year_paid_data = Ty_paid(paidamount_folder, day)

#-------------------------------------------------------------------------------------------------
df_receiptdata = pd.read_csv(tax_data + "Property_Tax_Receipt_Amount_Dump_24042023.csv")
df_receiptdata.dropna(subset=['propertykey'], how='all', inplace=True)
property_receipt_data = df_receiptdata[['propertykey', 'receiptdate']]

plist = pd.read_csv(tax_data + "Property_List_24042023.csv")
property_list_df = plist[plist['verified'] != "N"]
plist_df = property_list_df[['propertykey', 'propertycode']]

new_df_selected = property_receipt_data.sort_values(['propertykey', 'receiptdate']).drop_duplicates('propertykey',keep='last')

plist_vs_receipt = plist_df.merge(new_df_selected,on ='propertykey',how='left')
plist_vs_receipt.dropna(subset=['propertykey'], how='all', inplace=True)
plist_Vs_receipt = plist_vs_receipt.rename(columns={"receiptdate":'Last Paid Date'})

# typaid_Vs_plist = this_year_paid_data.merge(plist_df,on='propertycode',how='left')

df_ytd = this_year_paid_data.merge(plist_Vs_receipt,on='propertycode',how='left')

df_ytd.to_excel(outpth + f"paidamount_WLydate.xlsx",index=False)