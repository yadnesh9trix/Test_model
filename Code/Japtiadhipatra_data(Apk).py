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

#-----------------------------------------------------------------------------------------------------------------------

## Start
if __name__ == '__main__':
    main_path = r"D:/"
    std_path= r"D:\Test_model/"
    inppath = std_path + "Input/"
    outpth = std_path + "OutPut/" + tday + "/"
    tax_data = main_path + "/Tax_Data/"
    if os.path.exists(outpth):
        pass
    else:
        os.mkdir(outpth)
    mappath = std_path +  "Mapping/"

def mapping_type(mappath):
    usetype = pd.read_csv(mappath + "usetype.csv")
    usemap = dict(zip(usetype['usetypekey'],usetype['eng_usename']))

    consttype = pd.read_csv(mappath + "constructiontype.csv")
    construcmap = dict(zip(consttype['constructiontypekey'],consttype['eng_constructiontypename']))

    occptype=  pd.read_csv(mappath + "occupancy.csv")
    occpmap = dict(zip(occptype['occupancykey'],occptype['occupancyname']))

    subusetype= pd.read_csv(mappath + "subusetype.csv")
    subusemap = dict(zip(subusetype['subusetypekey'],subusetype['eng_subusename']))

    zonetype =pd.read_csv(mappath + "zone.csv")
    zonemap = dict(zip(zonetype['zonekey'],zonetype['eng_zonename']))

    gattype = pd.read_csv(mappath + "gat.csv")
    # gattype['gatname_z'] = gattype['gatname'].astype(str) + "_" + gattype['zonetype'].astype(str)
    gattype['gatname_z'] = gattype['gatname'].astype(str)
    gatnamemap = dict(zip(gattype['gat'], gattype['gatname_z']))

    specialowner = pd.read_csv(mappath + "specialownership.csv")
    splownmap = dict(zip(specialowner['specialownership'], specialowner['eng_specialownershipname']))

    splacctype = pd.read_csv(mappath + "specialoccupant.csv")
    splaccmap = dict(zip(splacctype['specialoccupantkey'], splacctype['eng_specialoccupantname']))

    return zonemap,usemap,construcmap,occpmap,subusemap,gatnamemap,splownmap,splaccmap


zonemap,usemap,construcmap,occpmap,subusemap,\
    gatnamemap,splownmap,splaccmap = mapping_type(mappath)

#-----------------------------------------------------------------------------------------------------------------------
df = pd.read_csv(inppath + "Japti_data 19-06-2023.csv",encoding='utf-8')

wrong_pid = pd.read_excel(inppath + "japtiwrong_pid.xlsx")

for i in wrong_pid['Wrong_pid']:
    for j in wrong_pid['pid']:
        df['propertycode'] = df['propertycode'].str.replace(str(i),str(j))

df['propertycode'] = df['propertycode'].str.replace('1040705608.00.00','1040705608.00')\
                                .str.replace('1150406630 .00','1150406630.00').str.replace('`','')

df['propertycode'] = df['propertycode'].astype(float)
df['propertycode'] = df['propertycode'].apply("{:.02f}".format)
#-------------------------------------------------------------------------------------------------
df_receiptdata = pd.read_csv(tax_data + "Property_Tax_Receipt_Amount_Dump_24042023.csv")
df_receiptdata.dropna(subset=['propertykey'], how='all', inplace=True)

##----------------------------------------------------------------------------------------------------------------------
plist = pd.read_csv(tax_data + "Property_List_24042023.csv")
property_list_df = plist[plist['verified'] != "N"]
property_list_df['propertycode'] = property_list_df['propertycode'].apply(pd.to_numeric, errors='coerce' ,downcast='float')
property_list_df['propertycode'] = property_list_df['propertycode'].apply("{:.02f}".format)

property_finmth_df11 = df_receiptdata[['propertykey', 'receiptdate','paidamount']]
new_df_selected = property_finmth_df11.sort_values(['propertykey', 'receiptdate']).drop_duplicates('propertykey',keep='last')

df_merge = property_list_df.merge(new_df_selected,on ='propertykey',how='left')
df_merge.dropna(subset=['propertykey'], how='all', inplace=True)
# df_merge =df_merge.rename(columns={"receiptdate":"Last Payments Date","paidamount":'Last Paid Amount'})
df_merge =df_merge.rename(columns={"paidamount":'Last Paid Amount'})

df_merge_japti = df.merge(df_merge,on='propertycode',how='left')

#-----------------------------------------------------------------------------------------------------------------------
bill_details = pd.read_csv(inppath + "Master_Bill_Distributed_Payments.csv")
billsdetails = pd.DataFrame(bill_details, columns=['propertycode','visitDate','mobileUpdated','propertyLat','propertyLong'])
bill_details['BillDist_Flag'] = 1
bill_details['propertycode'] = bill_details['propertycode'].astype(float)
bill_details['propertycode'] = bill_details['propertycode'].apply("{:.02f}".format)

dmf = df_merge_japti.merge(bill_details,on='propertycode',how='left')
ddd = dmf.sort_values('propertycode',ascending=False)

ddd["Quarter"] = pd.PeriodIndex(ddd["receiptdate"], freq="Q-Mar").strftime("Q%q")

ddd['mobileno'] = ddd['mobileno'].replace("9762398018 / 9561752879", "9762398018").\
                                                replace("9822745427/9881777166", "9881777166").replace(',',"").fillna(0).astype('int64')
ddd['New Mobile'] = np.where((ddd['mobileno'] > 5999999999) & (ddd['mobileno'] <= 9999999999), ddd['mobileno'], '')
ddd['New Mobile'] = ddd['New Mobile'].fillna(ddd['mobileUpdated'])

ddd = ddd[['propertycode','zonename', 'gatname', 'propertyname', 'receiptdate','Quarter', 'Last Paid Amount','propertykey',
           'propertyaddress','mobileno','balanceamount','status','New Mobile']]

###-----------------------------------------------------------------------------------------------------------------
property_bill_df = pd.read_csv(tax_data + "Property_Bill.csv")
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
plist_df = property_list_df[['propertykey', 'propertycode']]
plist_df['propertykey'] = plist_df['propertykey'].drop_duplicates()
plist_df['propertycode'] = plist_df['propertycode'].drop_duplicates()

## Merge Property list with cuurent arrears & arrears
merge_plist_arrears = plist_df.merge(arrears_TY, on='propertykey', how='left')
merge_plist_arrearsTY = merge_plist_arrears.merge(current_TY, on='propertykey', how='left')
merge_lypaid_wbilldetails = ddd.merge(merge_plist_arrearsTY,on='propertycode',how='left')

merge_lypaid_wbilldetails['Total Amount']= merge_lypaid_wbilldetails.loc[:,['Arrears Amount','Current Bill']].sum(axis=1)
#-----------------------------------------------------------------------------------------------------------------------
filtered_japtidata =  merge_lypaid_wbilldetails[~merge_lypaid_wbilldetails['status'].isin(['L','F'])]

filtered_japtidata.to_excel(outpth + "Japti_Data(APK).xlsx",index=False)

# propertycode    zonename    gatname    propertyName    receiptdate    Quarter    lastYearPaidamount    propertykey propertyAddress    propertyContactNo    arrearsAmount    currentBill    totalAmount
