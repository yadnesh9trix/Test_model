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

td_date = last_day.strftime("%d")
td_month = last_day.strftime("%m")
last_day_fmt = last_day.strftime("%d%m%Y")

tday  = today.strftime("%d_%b_%Y")

## Start
if __name__ == '__main__':
    main_path = r"D:/"
    std_path= r"D:\Test_model/"
    inppath = std_path + "Input/"
    paidamount_folder = main_path + "Paidamount/"
    outpth = std_path + "OutPut/" + tday + "/"
    if os.path.exists(outpth):
        pass
    else:
        os.mkdir(outpth)


df= pd.read_excel(inppath+"Book1.xlsx")
#
# bill_distributed['Gat'] = bill_distributed['Gat'].astype(int)
# pvotable = bill_distributed.pivot_table(index=['Zone'], columns='Gat', values='propertycode',aggfunc='count')
# # bbb = list(range(1, 19))
# dfff = pd.DataFrame(pvotable)
# pp = dfff.reset_index()
# -------------------------------------------------------------------------------------------------------------------
lissy = ['Nigdi Pradhikaran', 'Akurdi', 'Chinchwad', 'Thergaon', 'Sangvi', 'Pimpri Waghere',
         'Pimpri Nagar', 'MNP Bhavan', 'Fugewadi Dapodi', 'Bhosari', 'Charholi',
         'Moshi', 'Chikhali', 'Talvade', 'Kivle', 'Dighi Bopkhel', 'Wakad']

d = {v: k for k, v in enumerate(lissy)}
df_TD = df.sort_values('Zone', key=lambda x: x.map(d), ignore_index=True)
# # -------------------------------------------------------------------------------------------------------------------
collen = df_TD.columns.to_list()[2:]
df_TD['Grand Total'] = df_TD[collen].sum(axis=1)
df_TD.index = df_TD.index + 1
df_TD.loc["Grand Total"] = df_TD.sum(numeric_only=True)
# # -------------------------------------------------------------------------------------------------------------------
# df_TD = df_TD.drop(columns='eng_zone')
df_TD1 = df_TD.reset_index()
final_df_TD = df_TD1.rename(
    columns={'index': 'अ.क्र.', 'ezname': 'विभागीय कार्यालय', 'Grand Total': 'एकूण'})
final_df_TD = final_df_TD.replace("Grand Total", 'एकूण')

final_df_TD.to_excel(outpth+"Bill_Distributed_Count_Zone&GatWise.xlsx",index=False)