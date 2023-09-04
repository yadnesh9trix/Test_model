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

last_day = today - timedelta(days=0)

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


def Ty_paid(paidamount_file, day):
    ## Read YTD data
    ytddata = pd.read_excel(paidamount_file + f"Paidamount_list_{day}.xlsx")

    ## Replace the property code values in ytd data
    ytddata["propertycode"] = ytddata["propertycode"].replace("1100900002.10.10", "1100900002.20")
    ytddata['propertycode'] = ytddata['propertycode'].astype(float)
    ytddata.dropna(subset=['propertycode'], how='all', inplace=True)
    ytddata1 = ytddata.sort_values('receiptdate')
    # ytddata1 = ytddata1.groupby(['propertycode']).agg({'receiptdate': 'last', 'paidamount': 'sum'}).reset_index()
    ytddata1 = ytddata1.groupby(['ezname', 'gatname','propertycode', 'propertyname',
           'modeofpayment', 'magil', 'chalu']).agg({'receiptdate': 'last', 'paidamount': 'sum'}).reset_index()

    # ytddata1 = ytddata1.rename(
    #     columns={'receiptdate': 'This Year Paiddate', 'paidamount': 'This Year Paidamount'})
    # ytddata1 = ytddata1[['propertycode', 'This Year Paiddate', 'This Year Paidamount']]
    return ytddata1

this_year_paid_data = Ty_paid(paidamount_folder, day)

#-------------------------------------------------------------------------------------------------
df_receiptdata = pd.read_csv(tax_data + "Property_Receipt_25062023.csv")
df_receiptdata.dropna(subset=['propertykey'], how='all', inplace=True)
df_receiptdata = df_receiptdata[df_receiptdata['financialyearkey'] != 153]
property_receipt_data = df_receiptdata[['propertykey', 'receiptdate']]


def property_list(tax_data):
    # Read the property details data which is property parameters & details.
    property_list_df = pd.read_csv(tax_data + "Property_List_25062023.csv", low_memory=False)
    property_list_df = property_list_df[property_list_df['verified'] != 'N']
    property_list_df.dropna(subset=['propertycode', 'propertykey'], how='all', inplace=True)
    property_list_df['propertykey'] = property_list_df['propertykey'].drop_duplicates()
    property_list_df['propertycode'] = property_list_df['propertycode'].drop_duplicates()
    property_list_df['propertycode'] = property_list_df['propertycode'].astype(float)
    property_list_df = pd.DataFrame(property_list_df, columns=['propertycode', 'propertykey'])

    return property_list_df

new_df_selected = property_receipt_data.sort_values(['propertykey', 'receiptdate']).drop_duplicates('propertykey',keep='last')

property_list_df = property_list(tax_data)
plist_vs_receipt = property_list_df.merge(new_df_selected,on ='propertykey',how='left')
plist_vs_receipt.dropna(subset=['propertykey'], how='all', inplace=True)
plist_Vs_receipt = plist_vs_receipt.rename(columns={"receiptdate":'Last Paid Date'})

# typaid_Vs_plist = this_year_paid_data.merge(plist_df,on='propertycode',how='left')

df_ytd = this_year_paid_data.merge(plist_Vs_receipt,on='propertycode',how='left')

df_ytd['receiptdate'] = pd.to_datetime(df_ytd['receiptdate'], errors='coerce', format='%Y-%m-%d')
df_ytd['fin_year_r'] = df_ytd['receiptdate'].dt.year
df_ytd['fin_month_r'] = df_ytd['receiptdate'].dt.month

def finanacial_yr(df_ytd,col_name1,col_name2):
    df_ytd[col_name1] = np.where(df_ytd[col_name2] < 4,
                                    df_ytd[col_name1] - 1,
                                    df_ytd[col_name1])
    df_ytd[col_name2] = np.where(df_ytd[col_name2] < 4,
                                     df_ytd[col_name2] + 9,
                                     df_ytd[col_name2] - 3)
    return df_ytd

dfff =  finanacial_yr(df_ytd,'fin_year_r','fin_month_r')


df_ytd['Last Paid Date'] = pd.to_datetime(df_ytd['Last Paid Date'], errors='coerce', format='%Y-%m-%d')
df_ytd['fin_year_ly'] = df_ytd['Last Paid Date'].dt.year
df_ytd['fin_month_ly'] = df_ytd['Last Paid Date'].dt.month


dfff2 =  finanacial_yr(df_ytd,'fin_year_ly','fin_month_ly')

dfff2['diff'] = dfff2['fin_year_r'] - dfff2['fin_year_ly']
dfff2['diff'] = dfff2['diff'].fillna(0).astype(int)
# Extract and format the "Quarter" from the "last payment date" column using Q-Mar frequency
dfff2["Quarter"] =  pd.PeriodIndex(dfff2["Last Paid Date"],freq="Q-Mar").strftime("Q%q")

dfff2["Quarter"] = np.where(dfff2["fin_year_ly"] == 2022,dfff2["Quarter"],dfff2["diff"].astype(str) + "_Year Defaulter")

# dfff2["Quarter"] = dfff2["Quarter"].apply(x:x fillna('defaulter'))

dfff2 = dfff2[['ezname', 'gatname', 'propertycode', 'propertyname', 'modeofpayment',
       'magil', 'chalu', 'receiptdate', 'paidamount', 'propertykey',
       'Last Paid Date', 'fin_year_r', 'fin_year_ly', 'diff', 'Quarter']]

dfff2.to_excel(outpth + f"Paidamount_LYPaidDate.xlsx",index=False)