import pandas as pd
import datetime

today= datetime.datetime.now()

std_path = r"C:\PTAX Project\PTAx\Manual Daily Report/"
in_path = std_path + "Input/" + str(today) + "/"
outpth = std_path + "Output/" + "/"
mappath = std_path + "Mapping/"
logopath = std_path + "logo/"
mailreport = std_path + "Mail_report/"

dff = pd.read_excel(r"C:\Users\Lenovo\Downloads/ContactNo_Updated874.xlsx")
dff['Column1.mseb_ContactNo'] = dff[dff.columns[5:]].apply(
    lambda x: ','.join(x.dropna().astype(str)),
    axis=1)

# dff['Column1.mseb_ContactNo'] = dff['Column1.mseb_ContactNo'].astype(int)
df3 = dff['Column1.mseb_ContactNo'].str.split(",",n=15, expand=True)

meregdff= dff.join(df3)

# make the new columns using string indexing
# df['col1'] = df['col'].str[0:10]
# df['col2'] = df['col'].str[11:21]
# df['col3'] = df['col'].str[22:31]

# df1 = (meregdff.set_index(['Column1.propertycode', 'Column1.propertyname','Column1.propertyaddress', 'Column1.Zone_Type'])
#          .stack()
#          .reset_index()
#          .rename(columns={'level_2':[0,15]}))

# df1 = (meregdff.set_index(dff.columns[0:5])
#          .stack()
#          .reset_index()
#          .rename(columns={'level_2':[0,15]}))

df1 = (meregdff.set_index(['propertycode','propertyname','propertyaddress','msebDate', 'Zone_Type'])
         .stack()
         .reset_index()
         .rename(columns={'level_2':[0,12]}))

df1 = df1.rename(columns={0:'Column1.mseb_ContactNo'})

df1_filter = df1[df1['level_5'] != 'Column1.mseb_ContactNo']
df1_filter = df1_filter.drop(columns='level_5')

df1_filter.to_excel(outpth + "ContactNo_17032023 (0 Arrears).xlsx",index=False)

# [   'Column1.propertycode',    'Column1.propertyname',
#        'Column1.propertyaddress',       'Column1.Zone_Type',
#         'Column1.mseb_ContactNo',                         0,
#                                1,                         2,
#                                3,                         4,
#                                5,                         6,
#                                7,                         8,
#                                9,                        10],

# import numpy as np
#
# index_to_copy = 0
# number_of_extra_copies = 2
# dd = pd.concat([meregdff,
#            pd.DataFrame(np.repeat(meregdff.iloc[[index_to_copy]].values,number_of_extra_copies,
#                                   axis=0),columns=dff.columns)]).sort_values(by='index').reset_index(drop=True)

# pd.concat([df,
#            pd.DataFrame(np.repeat(df.iloc[[index_to_copy]].values,
#                                   number_of_extra_copies,
#                                   axis=0),
#                         columns=df.columns)]).sort_values(by='index').drop(columns='index').reset_index(drop=True)
# df.columns = np.hstack((df.columns[:2], df.columns[2:].map(lambda x: f'Value{x}')))

# res = pd.wide_to_long(df, stubnames=['Value'], i='name', j='Date').reset_index()\
#         .sort_values(['location', 'name'])

