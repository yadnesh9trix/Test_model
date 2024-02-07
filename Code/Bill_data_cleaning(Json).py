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
import json

#-----------------------------------------------------------------------------------------------------------------------
## Define the today's date
today = datetime.datetime.today().date()
tday  =today.strftime("%d_%b_%Y")

#-----------------------------------------------------------------------------------------------------------------------

'''Json format to dataframe'''

## Start
if __name__ == '__main__':
    std_path= r"D:\Test_model/"
    inppath = std_path + "Input/"
    outpth = std_path + "OutPut/" + tday + "/"
    if os.path.exists(outpth):
        pass
    else:
        os.mkdir(outpth)

## Visit Person list
wout_visitperson = pd.read_excel(inppath + "VisitPerson.xlsx", sheet_name="OG")
wout_visitperson_list = wout_visitperson['visitingPersonName'].tolist()


with open(inppath + 'propertyconflights_20052023_1558.json',encoding='utf-8') as f:
  data = json.load(f)
# df = pd.json_normalize(data,record_prefix='_')

df = pd.json_normalize(data, 'visitors', ['_id', 'propertyCode'])
df123 = pd.concat([df.drop(['_id'], axis=1), df['_id'].apply(pd.Series)], axis=1)

# Group the DataFrame by the 'propertyCode' and filter out the groups with a count greater than 1:
duplicates = df123.groupby('propertyCode').filter(lambda x: len(x) > 1)
duplicates = duplicates.reset_index(drop=True)

drop_duplicte = duplicates.drop_duplicates(['propertyCode','visitingPersonName'])

sameproperty_diff_visit = drop_duplicte.groupby('propertyCode').filter(lambda x: len(x) > 1)
ddd = sameproperty_diff_visit.sort_values('propertyCode')

# grouped = duplicates.groupby('propertyCode')['visitingPersonName'].unique()
# wout_singles = duplicates.groupby('propertyCode').filter(lambda x: len(x) != 1)
# wout_singles = wout_singles.reset_index(drop=True)

# ddd = grouped.sort_values('propertyCode')
visit_person_data = ddd[~ddd['visitingPersonName'].isin(wout_visitperson_list)]

proeprtylist = pd.read_csv(inppath + "Property_List_24042023.csv", low_memory=False)
proeprtylist = proeprtylist[['propertykey', 'propertycode',
       'zone', 'gat', 'verified']]
ppp = proeprtylist[proeprtylist['verified'] != 'N']
visit_person_data = visit_person_data.rename(columns ={'propertyCode':'propertycode'})
bill_data_merge = visit_person_data.merge(ppp,on='propertycode',how='left')

mappath = 'D:\PTAX Project\Ptax_Project\Mapping/'
zonetype = pd.read_csv(mappath + "zone.csv")
zonemap = dict(zip(zonetype['zonekey'], zonetype['eng_zonename']))

gattype = pd.read_csv(mappath + "gat.csv")
gattype['gatname_z'] = gattype['gatname'].astype(str)
gatnamemap = dict(zip(gattype['gat'], gattype['gatname_z']))

bill_data_merge['Zone'] = bill_data_merge['zone'].map(zonemap)
bill_data_merge['Gat'] = bill_data_merge['gat'].map(gatnamemap)

visitreports = pd.read_csv(inppath + "propertyconflights_20052023_1555.csv", low_memory=False)
visitreports = visitreports.rename(columns ={'propertyCode':'propertycode'})

aa1 = bill_data_merge.merge(visitreports,on='propertycode',how='left')

sameproperty_multivisit =  aa1[['Zone', 'Gat','visitingPerson_id', 'visitingPersonName', 'visitingPersonContactNo',
       'propertycode', '$oid', 'propertykey',
       'createdAt', 'updatedAt']]

sameproperty_multivisit.to_excel(outpth + "Property_Bill_Details_After_Cleaning.xlsx",index=False )


# Convert the JSON data to a DataFrame
# df11 = pd.DataFrame.from_dict(data, orient='index', columns=['visitors'])
# df = pd.DataFrame(columns=['_id','visitors','propertyCode'])

# If you want to remove the duplicates and keep only the single values (non-duplicates), you can modify step 3 as follows:
# singles = df.groupby('Column').filter(lambda x: len(x) == 1)
# singles = singles.reset_index(drop=True)

print(True)

