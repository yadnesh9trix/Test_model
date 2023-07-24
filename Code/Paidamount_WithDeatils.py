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

    ## Define the today's date
    today = datetime.datetime.today().date()
    tday = today.strftime("%d_%b_%Y")

    last_day = today - timedelta(days=0)

    td_date = last_day.strftime("%d")
    td_month = last_day.strftime("%m")
    last_day_fmt = last_day.strftime("%d%m%Y")

    def mapping_type(mappath):
        usetype = pd.read_csv(mappath + "usetype.csv")
        usemap = dict(zip(usetype['usetypekey'], usetype['eng_usename']))

        consttype = pd.read_csv(mappath + "constructiontype.csv")
        construcmap = dict(zip(consttype['constructiontypekey'], consttype['eng_constructiontypename']))

        occptype = pd.read_csv(mappath + "occupancy.csv")
        occpmap = dict(zip(occptype['occupancykey'], occptype['occupancyname']))

        subusetype = pd.read_csv(mappath + "subusetype.csv")
        subusemap = dict(zip(subusetype['subusetypekey'], subusetype['eng_subusename']))

        zonetype = pd.read_csv(mappath + "zone.csv")
        zonemap = dict(zip(zonetype['zonekey'], zonetype['eng_zonename']))

        gattype = pd.read_csv(mappath + "gat.csv")
        # gattype['gatname_z'] = gattype['gatname'].astype(str) + "_" + gattype['zonetype'].astype(str)
        gattype['gatname_z'] = gattype['gatname'].astype(str)
        gatnamemap = dict(zip(gattype['gat'], gattype['gatname_z']))

        specialowner = pd.read_csv(mappath + "specialownership.csv")
        splownmap = dict(zip(specialowner['specialownership'], specialowner['eng_specialownershipname']))

        splacctype = pd.read_csv(mappath + "specialoccupant.csv")
        splaccmap = dict(zip(splacctype['specialoccupantkey'], splacctype['eng_specialoccupantname']))

        return zonemap, usemap, construcmap, occpmap, subusemap, gatnamemap, splownmap, splaccmap

    zonemap, usemap, construcmap, occpmap, subusemap, \
        gatnamemap, splownmap, splaccmap = mapping_type(mappath)

    typaid = pd.read_excel(paidamount_folder + f"Paidamount_list_{last_day_fmt}.xlsx")
    typaid['propertycode'] = typaid['propertycode'].astype(float)
    typaid['propertycode'] = typaid['propertycode'].apply("{:.02f}".format)
    typaid.dropna(subset=['propertycode'], how='all', inplace=True)

    plist = pd.read_csv(tax_data + "Property_List_24042023.csv")
    property_list_df = plist[plist['verified'] != "N"]
    property_list_df['propertycode'] = property_list_df['propertycode'].apply(pd.to_numeric, errors='coerce',
                                                                              downcast='float')
    property_list_df['propertycode'] = property_list_df['propertycode'].apply("{:.02f}".format)
    plist_df = property_list_df[
        ['propertykey', 'propertycode', 'usetypekey', 'constructiontypekey', 'occupancykey', 'subusetypekey']]
    plist_df['propertykey'] = plist_df['propertykey'].drop_duplicates()
    plist_df['propertycode'] = plist_df['propertycode'].drop_duplicates()

    plist_df['Use_Type'] = plist_df['usetypekey'].map(usemap)
    plist_df['Construction_Type'] = plist_df['constructiontypekey'].map(construcmap)
    plist_df['Occupancy_Type'] = plist_df['occupancykey'].map(occpmap)
    plist_df['Subuse_Type'] = plist_df['subusetypekey'].map(subusemap)

    merge_ty_details = typaid.merge(plist_df, on='propertycode', how='left')

    merge_ty_details.drop(columns=[
        'propertykey', 'usetypekey', 'constructiontypekey', 'occupancykey',
        'subusetypekey'])
    merge_ty_details.to_excel(outpth + f"paidamount_list_{last_day_fmt}.xlsx",index=False)
