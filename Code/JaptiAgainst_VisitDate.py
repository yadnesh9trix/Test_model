import pandas as pd
import numpy as np
from datetime import datetime,timedelta
import warnings
warnings.filterwarnings('ignore')
import os
import warnings
warnings.filterwarnings('ignore')

#-----------------------------------------------------------------------------------------------------------------------
## Define the today's date
today = datetime.today().date()
tday  =today.strftime("%d_%b_%Y")

last_day = today - timedelta(days=0)

td_date = last_day.strftime("%d")
td_month = last_day.strftime("%m")
day_fmt = last_day.strftime("%d%m%Y")

#-----------------------------------------------------------------------------------------------------------------------

## Start
if __name__ == '__main__':
    std_path= r"D:\Test_model/"
    inppath = std_path + "Input/"
    outpth = std_path + "OutPut/" + tday + "/"
    paidamount_folder = 'D:/' + "Paidamount/"
    if os.path.exists(outpth):
        pass
    else:
        os.mkdir(outpth)

japti_df = pd.read_csv(inppath + "Japti_data 28-06-2023.csv",encoding='utf-8')

wrong_pid = pd.read_excel(inppath + "japtiwrong_pid.xlsx")

for i in wrong_pid['Wrong_pid']:
    for j in wrong_pid['pid']:
        japti_df['propertycode'] = japti_df['propertycode'].str.replace(str(i),str(j))

japti_df['propertycode'] = japti_df['propertycode'].str.replace('1040705608.00.00','1040705608.00')\
                                .str.replace('1150406630 .00','1150406630.00').str.replace('`','')

japti_df['propertycode'] = japti_df['propertycode'].astype(float)
japti_df['propertycode'] = japti_df['propertycode'].apply("{:.02f}".format)

bill_distributed = pd.read_csv(inppath + "Master_Bill_Distributed_Payments.csv")
bill_distributed['propertycode'] = bill_distributed['propertycode'].astype(float)
bill_distributed['propertycode'] = bill_distributed['propertycode'].apply("{:.02f}".format)

japti_visistdate_df = japti_df.merge(bill_distributed,on='propertycode',how='left')

#-------------------------------------------------------------------------------------
typaid = pd.read_excel(paidamount_folder + f"Paidamount_list_{day_fmt}.xlsx")
typaid['propertycode'] = typaid['propertycode'].astype(float)
typaid['propertycode'] = typaid['propertycode'].apply("{:.02f}".format)
# lypaid = lypaid.drop_duplicates('propertycode')
typaid = typaid.rename(columns={'paidamount':'This Year Paidamount'})
typaid =  typaid[['propertycode','This Year Paidamount']]
typaid.dropna(subset=['propertycode'], how='all', inplace=True)
typaid = typaid.groupby(['propertycode'])['This Year Paidamount'].sum().reset_index()
typaid['This Year Paid Flag'] = 1
#------------------------------------------------------------------------------------------------

merge_japti_typaid = japti_visistdate_df.merge(typaid,on='propertycode',how='left')
merge_japti_typaid.to_excel(outpth + f"JaptiDataAgainstBillDetails{tday}.xlsx",index=False)

##------------------------------------------------------------------------------------------------------------
filtered_japtidata =  japti_visistdate_df[~japti_visistdate_df['status'].isin(['L','F'])]
filtered_japtidata.to_excel(outpth + f"JaptiDataWithBillDetails(Wout L-F){tday}.xlsx",index=False)

