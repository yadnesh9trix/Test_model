import pandas as pd
from pyspark.sql.functions import concat


dff = pd.read_excel("D:\Test_model\Input\Book2.xlsx")
# ['Sr. no.', 'propertyCode', 'propertyName', 'propertyAddress',
#        'businessAddress', 'isRented', 'ownerMobile', 'ownerName',
#        'rentedPersonMobile', 'rentedPersonName', 'subPropertyType',
#        'subPropertyTypeOther', 'lat', 'long', 'lat, long']

ssss= pd.pivot_table(dff,columns=['lat, long','ownerName','propertyCode'])
print(True)