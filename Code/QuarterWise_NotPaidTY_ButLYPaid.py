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

last_day = today - timedelta(days=2)

td_date = last_day.strftime("%d")
td_month = last_day.strftime("%m")
last_day_fmt = last_day.strftime("%d%m%Y")

#-----------------------------------------------------------------------------------------------------------------------

## Start
if __name__ == '__main__':
    main_path = r"D:/"
    std_path= r"D:\Test_model/"
    inppath = std_path + "Input/"
    outpth = std_path + "OutPut/" + tday + "/"
    paidamount_folder = main_path + "Paidamount/"
    tax_data = main_path + "/Tax_Data/"
    if os.path.exists(outpth):
        pass
    else:
        os.mkdir(outpth)
wrong_pid = pd.read_excel(inppath + "japtiwrong_pid.xlsx")

lypaid = pd.read_csv(inppath + "Paid_amount 2022-04-01 To 2023-03-31.csv")
lypaid["propertycode"] = lypaid["propertycode"].replace("1100900002.10.10", "1100900002.20")
lypaid['propertycode'] = lypaid['propertycode'].astype(float)
lypaid['propertycode'] = lypaid['propertycode'].apply("{:.02f}".format)
lypaid = lypaid.drop_duplicates('propertycode')
# lypaid =  lypaid[['propertycode']]
lypaid = lypaid.rename(columns={'paidamount':'Last Year Paidamount'})
lypaid.dropna(subset=['propertycode'], how='all', inplace=True)

typaid = pd.read_excel(paidamount_folder + f"Paidamount_list_{last_day_fmt}.xlsx")
typaid['propertycode'] = typaid['propertycode'].astype(float)
typaid['propertycode'] = typaid['propertycode'].apply("{:.02f}".format)
# lypaid = lypaid.drop_duplicates('propertycode')
typaid = typaid.rename(columns={'paidamount':'This Year Paidamount'})
typaid =  typaid[['propertycode','This Year Paidamount']]
typaid.dropna(subset=['propertycode'], how='all', inplace=True)
typaid = typaid.groupby(['propertycode'])['This Year Paidamount'].sum().reset_index()
typaid['This Year Paid Flag'] = 1

merge_tyly  = lypaid.merge(typaid,on='propertycode',how='left')
merge_tyly['This Year Paid Flag'] = merge_tyly['This Year Paid Flag'].fillna(0)

# merge_tyly['receiptdate'] = pd.to_datetime(merge_tyly['receiptdate'], errors='coerce', format='%Y-%m-%d')
# merge_tyly['fin_year_r'] = merge_tyly['receiptdate'].dt.year
# merge_tyly['fin_month_r'] = merge_tyly['receiptdate'].dt.month
#
# merge_tyly['fin_year_r'] = np.where(merge_tyly['fin_month_r'] < 4,
#                                 merge_tyly['fin_year_r'] - 1,
#                                 merge_tyly['fin_year_r'])
# merge_tyly['fin_month_r'] = np.where(merge_tyly['fin_month_r'] < 4,
#                                  merge_tyly['fin_month_r'] + 9,
#                                  merge_tyly['fin_month_r'] - 3)

# # Calculate the financial year based on the receipt date
# merge_tyly["FinancialYear"] = pd.PeriodIndex(merge_tyly["receiptdate"], freq="Q-APR").to_timestamp(how="start").dt.year
# merge_tyly.loc[merge_tyly["receiptdate"].dt.month >= 4, "FinancialYear"] += 1

# Calculate the quarter within the financial year
merge_tyly["Quarter"] = pd.PeriodIndex(merge_tyly["receiptdate"], freq="Q-Mar").strftime("Q%q")
# merge_tyly["Quarter"] = merge_tyly["receiptdate"].dt.quarter

dfff = merge_tyly[['propertycode', 'ezname', 'gatname', 'propertyname', 'receiptdate', 'Quarter','Last Year Paidamount',
                   'This Year Paid Flag','This Year Paidamount']]
dfff = dfff.rename(columns ={'ezname':'Zone','gatname':'Gat'})

plist = pd.read_csv(tax_data + "Property_List_24042023.csv")
property_list_df = plist[plist['verified'] != "N"]
property_list_df['propertycode'] = property_list_df['propertycode'].apply(pd.to_numeric, errors='coerce' ,downcast='float')
property_list_df['propertycode'] = property_list_df['propertycode'].apply("{:.02f}".format)

#-----------------------------------------------------------------------------------------------------------------------
property_bill_df = pd.read_csv(tax_data + "Property_Bill_24042023.csv")
## Starting the Property bill data
property_bill_df_selcted = property_bill_df[['propertykey', 'financialyearkey', 'balanceamount']]
property_bill_df_NonZero = property_bill_df_selcted[property_bill_df_selcted['balanceamount'] > 0]
property_bill_df_NonZeropkey = property_bill_df_NonZero[property_bill_df_NonZero['propertykey'] > 0]

###-----------------------------------------------------------------------------------------------------------------
# 152- 2022-2023
# 153- 2023-2024
## Current Arrears till last years
Not_TY = property_bill_df_NonZeropkey[property_bill_df_NonZeropkey['financialyearkey'] != 153]
arrears_TY = Not_TY.groupby(['propertykey'])['balanceamount'].sum().reset_index()
arrears_TY = arrears_TY.rename(columns={'balanceamount': 'Arrears Amount'})

# Only Current Year bills
only_TY = property_bill_df_NonZeropkey[property_bill_df_NonZeropkey['financialyearkey'] == 153]
current_TY = only_TY.groupby(['propertykey'])['balanceamount'].sum().reset_index()
current_TY = current_TY.rename(columns={'balanceamount': 'Current Bill'})

## Read Property list
plist_df = property_list_df[['propertykey', 'propertycode','propertyaddress','own_mobile']]
plist_df['propertykey'] = plist_df['propertykey'].drop_duplicates()
plist_df['propertycode'] = plist_df['propertycode'].drop_duplicates()

## Merge Property list with cuurent arrears & arrears
merge_plist_arrears = plist_df.merge(arrears_TY, on='propertykey', how='left')
merge_plist_arrearsTY = merge_plist_arrears.merge(current_TY, on='propertykey', how='left')

merge_lypaid_wbilldetails = dfff.merge(merge_plist_arrearsTY,on='propertycode',how='left')

merge_lypaid_wbilldetails['own_mobile'] = merge_lypaid_wbilldetails['own_mobile'].str.extract(r'(\d{10})')
merge_lypaid_wbilldetails['own_mobile'] = merge_lypaid_wbilldetails['own_mobile'].fillna(0000000000).astype("int64")
merge_lypaid_wbilldetails['own_mobile'] = np.where((merge_lypaid_wbilldetails['own_mobile'] > 5999999999)
                                                   & (merge_lypaid_wbilldetails['own_mobile'] <= 9999999999),
                                                                                merge_lypaid_wbilldetails['own_mobile'], '')

merge_lypaid_wbilldetails['Total Amount']= merge_lypaid_wbilldetails.loc[:,['Arrears Amount','Current Bill']].sum(axis=1)

#################
# bill_distributed_details = pd.read_csv(inppath + "Master_Bill_Distributed_Payments.csv")
# bill_distributed_details['propertycode'] = bill_distributed_details['propertycode'].astype(float)
# bill_distributed_details['propertycode'] = bill_distributed_details['propertycode'].apply("{:.02f}".format)
# data =  merge_lypaid_wbilldetails.merge(bill_distributed_details,on='propertycode',how='left')

#------------------------------------------------------------------------------------------------------------------------------
# new_bills_demand = pd.read_csv(tax_data + "PropertyList with Demand & Recovery Excluding IllegalShasti 2023-24.csv")
# new_bills_demand['propertycode'] = new_bills_demand['propertycode'].str.replace("/", ".").str.replace('`', '')
# for i, j in zip(wrong_pid['Wrong_pid'], wrong_pid['pid']):
#     new_bills_demand['propertycode'] = new_bills_demand['propertycode'].str.replace(str(i), str(j))
# new_bills_demand['propertycode'] = new_bills_demand['propertycode'].astype(float)
# new_bills_demand['propertycode'] = new_bills_demand['propertycode'].apply("{:.02f}".format)
# property_billdetails = new_bills_demand.drop_duplicates('propertycode')
# property_billdetails.dropna(subset=['propertycode'], how='all', inplace=True)
#
# property_billdetails = property_billdetails[['propertycode', 'arrearsdemand', 'currentdemand', 'totaldemand']]
#
# data_billsinfo = merge_lypaid_wbilldetails.merge(property_billdetails, on='propertycode', how='left')

merge_lypaid_wbilldetails.to_excel(outpth + f"QuarterWise_NotPaidTY_ButLYPaid1_{tday}.xlsx",index=False)
