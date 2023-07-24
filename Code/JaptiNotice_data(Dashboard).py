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
    paidamount_folder = main_path + "Paidamount/"
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
df = pd.read_csv(inppath + "Japti_data 28-06-2023.csv",encoding='utf-8')

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

plist = pd.read_csv(tax_data + "Property_List_24042023.csv")
property_list_df = plist[plist['verified'] != "N"]
plist_df = property_list_df[['propertykey', 'propertycode','usetypekey','constructiontypekey', 'occupancykey', 'subusetypekey',
                             'specialownership','specialoccupantkey','propertyname','own_mobile', 'propertyaddress']]
plist_rearrange_data = plist_df.copy()
plist_rearrange_data['Use_Type'] = plist_rearrange_data['usetypekey'].map(usemap)
plist_rearrange_data['Construction_Type'] = plist_rearrange_data['constructiontypekey'].map(construcmap)
plist_rearrange_data['Occupancy_Type'] = plist_rearrange_data['occupancykey'].map(occpmap)
plist_rearrange_data['Subuse_Type'] = plist_rearrange_data['subusetypekey'].map(subusemap)
plist_rearrange_data['propertykey'] = plist_rearrange_data['propertykey'].drop_duplicates()
plist_rearrange_data['propertycode'] = plist_rearrange_data['propertycode'].drop_duplicates()

property_details = pd.DataFrame(plist_rearrange_data,columns=['propertykey', 'propertycode', 'own_mobile', 'propertyaddress',
       'Use_Type', 'Construction_Type', 'Occupancy_Type', 'Subuse_Type'])

property_finmth_df11 = df_receiptdata[['propertykey', 'receiptdate','paidamount']]
new_df_selected = property_finmth_df11.sort_values(['propertykey', 'receiptdate']).drop_duplicates('propertykey',keep='last')

# new_df = pd.DataFrame(property_finmth_df11.groupby('propertykey')['receiptdate'].agg(lambda x: x.tolist()).tolist()).replace({None: np.nan})
# new_df_selected = new_df.iloc[:,:27]
# new_df_selected.columns = [f'LastPayment_date_{i}' for i in new_df_selected.columns]
# new_df_selected['propertykey'] = property_finmth_df11['propertykey'].drop_duplicates().reset_index(drop=True)

df_merge = property_details.merge(new_df_selected,on ='propertykey',how='left')
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

ddd['mobileno'] = ddd['mobileno'].replace("9762398018 / 9561752879", "9762398018").replace("9822745427/9881777166","9881777166").replace(',',"")\
                                                                    .fillna(0).astype('int64')
# ddd['mobileno'] = ddd['mobileno'].apply(lambda x: x.replace(',', '').lstrip('0'))
# ddd['mobileno'] = ddd['mobileno'].apply(lambda x:x if len(x) == 10 else '')
ddd['New Mobile'] = np.where((ddd['mobileno'] > 5999999999) & (ddd['mobileno'] <= 9999999999), ddd['mobileno'], '')

ddd['New Mobile'] = ddd['New Mobile'].fillna(ddd['mobileUpdated'])

ddd = ddd[['propertycode','zonename', 'gatname', 'propertyname', 'receiptdate','Quarter', 'Last Paid Amount','propertykey',
           'propertyaddress','mobileno','balanceamount', 'status','New Mobile']]

filtered_japtidata =  ddd[~ddd['status'].isin(['L','F'])]

filtered_japtidata.to_excel(outpth + "Japti_data.xlsx",index=False)

# propertycode    zonename    gatname    propertyName    receiptdate    Quarter    lastYearPaidamount    propertykey propertyAddress    propertyContactNo    arrearsAmount    currentBill    totalAmount
