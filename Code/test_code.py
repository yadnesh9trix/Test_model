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


# class A:
#     def foo(self):
#         print('A')
#
# class B(A):
#     def foo(self):
#         print('B')
#
# class C(A):
#     def foo(self):
#         print('C')
#
# class D(B, C):
#     pass
#
# D().foo()
#
#


#-----------------------------------------------------------------------------------------------------------------------
## Define the today's date
today = datetime.datetime.today().date()
tday  =today.strftime("%d_%b_%Y")

last_day = today - timedelta(days=2)

td_date = last_day.strftime("%d")
td_month = last_day.strftime("%m")
last_day_fmt = last_day.strftime("%d%m%Y")


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

    def property_list(tax_data):
        # Read the property details data which is property parameters & details.
        property_list_df = pd.read_csv(tax_data + "Property_List_25062023.csv",low_memory=False)
        property_list_df = property_list_df[property_list_df['verified'] != 'N']
        property_list_df.dropna(subset=['propertycode','propertykey'], how='all', inplace=True)
        # property_list_df['propertykey'] = property_list_df['propertykey'].drop_duplicates()
        # property_list_df['propertycode'] = property_list_df['propertycode'].drop_duplicates()
        # property_list_df['propertycode'] = property_list_df['propertycode'].astype(float)

        return property_list_df

    plist = property_list(tax_data)

    df =pd.read_excel(inppath + "Ileagal_Samayojana.xlsx")

    df2 = df.merge(plist,on='propertycode',how='left')

    # Extract the first 10 digits of the property code
    df2['first_10_digits'] = df2['propertycode'].apply(lambda x: int(x // 1e-10))

    # Group the DataFrame byy the first 10 digits and count occurrences
    duplicate_codes = df2[df2.duplicated(subset=['first_10_digits'], keep=False)]

print(True)