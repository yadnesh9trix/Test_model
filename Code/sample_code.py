"""
Created on August 2021

@author: Yadnesh Kolhe

Updated on 05 June 2022
"""

"""
Importing all libraries required
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime,date,timedelta
import time
from pathlib import Path
import shutil
import warnings
warnings.filterwarnings('ignore')

"""
        This code converts the OTA data of Staah_max property into Staah property OTA data format which will then passed on Revseed
         The output file name will be as "Staah_booking_OTAData_htlcode".
        
        :param stdpath: The standard folder path, it will be the Parent folder
        :param in_path: Input file path
        :param map_path will be the 
        :param mapping: utility mapping file
        :param mapfile: In mapping Folder to read map_col file
       
"""

# infile = in_path + "{}_OTA Data".format(htlname)

def process_staahmax(htlcode,infile,mapfile,dateformat,chname):
    """
    :param htlcode: The hotel Code for which Data to be converted / the property id
    :param infile: The input File name
    :param mapfile:
    :return:
    """

    if infile.endswith('.txt'):
        data = pd.read_csv(infile, sep="|")
    elif infile.endswith('.xlsx'):
        if chname == "StaahMax":
            data = pd.read_excel(infile, skiprows=2)
        else:
            data = pd.read_excel(infile)
    elif infile.endswith(".xls"):
        try:
            data = pd.read_excel(infile)
        except:
            data = pd.read_csv(infile, encoding='unicode_escape')
    else:
        try:
            data = pd.read_csv(infile, encoding='utf-8')
        except:
            data = pd.read_csv(infile, encoding='latin1')

    # if chname == 'StaahMax':
    #     data = pd.read_excel(infile, skiprows=2)
    # else:
    #     data = pd.read_excel(infile)

    mapfile = pd.read_excel(mapfile)
    dateformat = pd.read_excel(dateformat)

    # To Create the dictionary of col_name used for col_rename of data
    # ren_dict =dict(zip(mapfile.before,mapfile.after))

    ren_dict = dict(zip(mapfile[chname], mapfile.standard))
    # data = pd.DataFrame(data,columns=mapfile.before.to_list())
    data = pd.DataFrame(data, columns=mapfile[chname].to_list())

    data.rename(columns=ren_dict,inplace=True)

    data["Net Amount"] = data["Total Amount"]

# In Room type column separate the Specific values include ","
    try:
        data['Room Type'] = data['Room Type'].str.split(",").str[0]
    except:
        pass
# To Check and Drop NAN or Na Values
    data.dropna(subset=['Channel'], inplace=True)
    data.loc[:, 'NoExtraAdult':'Addon Rate'] = data.loc[:, 'NoExtraAdult':'Addon Rate'].fillna(0)


    # form_dict = dict(zip(dateformat["CM"], dateformat[chname]))

    data['Date/ Time Modified (GMT)'] = np.where(data['Date/ Time Modified (GMT)'] == '0000-00-00 00:00:00',
                                                 data['Date/ Time Booked (GMT)'], data['Date/ Time Modified (GMT)'])

    data['Date/ Time Booked (GMT)'] = np.where(data['Date/ Time Booked (GMT)'] == '0000-00-00 00:00:00',
                                                 data['Date/ Time Modified (GMT)'],data['Date/ Time Booked (GMT)'])


# converting the Date columns into datetime format.

    # if chname == 'StaahMax':
    #     try:
    #         data['Date/ Time Booked (GMT)'] = pd.to_datetime(data['Date/ Time Booked (GMT)'],
    #                                                          format='%d-%b-%Y %I:%M:%S %p (IST)')
    #     except:
    #         try:
    #             data['Date/ Time Booked (GMT)'] = pd.to_datetime(data['Date/ Time Booked (GMT)'],
    #                                                              format='%d-%b-%Y %I:%M:%S %p')
    #         except:
    #             data['Date/ Time Booked (GMT)'] = pd.to_datetime(data['Date/ Time Booked (GMT)'],
    #                                                              format='%d-%b-%Y %I:%M:%S %p (+%f)')

    try:
        data['Date/ Time Booked (GMT)'] = pd.to_datetime(data['Date/ Time Booked (GMT)'],infer_datetime_format=True)

    except:
        form_dict = dict(zip(dateformat["CM"], dateformat[chname]))
        data['Date/ Time Booked (GMT)'] = pd.to_datetime(data['Date/ Time Booked (GMT)'],
                                                                 format="{}".format(form_dict["Date/ Time Booked (GMT)"]))

    # else:
    #     form_dict = dict(zip(dateformat["CM"], dateformat[chname]))
    #     data['Date/ Time Booked (GMT)'] = pd.to_datetime(data['Date/ Time Booked (GMT)'],
    #                                                          format="{}".format(form_dict["Date/ Time Booked (GMT)"]))


    # try:
    #     data['Date/ Time Booked (GMT)'] = pd.to_datetime(data['Date/ Time Booked (GMT)'],
    #                                                                format="{}".format(form_dict["Date/ Time Booked (GMT)"]))
    # except:
    #     data['Date/ Time Booked (GMT)'] = pd.to_datetime(data['Date/ Time Booked (GMT)'],
    #                                                      format='%d-%b-%Y %I:%M:%S %p (IST)')
    #     try:
    #         data['Date/ Time Booked (GMT)'] = pd.to_datetime(data['Date/ Time Booked (GMT)'],
    #                                                    format='%d-%b-%Y %I:%M:%S %p')
    #      except:
    #         data['Date/ Time Booked (GMT)'] = pd.to_datetime(data['Date/ Time Booked (GMT)'],
    #                                                            format='%d-%b-%Y %I:%M:%S %p (+%f)')


# Converting the Date Dtype in to datetime format.
    form_dict = dict(zip(dateformat["CM"], dateformat[chname]))
    data["CheckIn Date"]=pd.to_datetime(data["CheckIn Date"],format="{}".format(form_dict["CheckIn Date"]),errors='coerce')
    data["CheckOut Date"] = pd.to_datetime(data["CheckOut Date"],format="{}".format(form_dict["CheckOut Date"]),errors='coerce')


    data["Date/ Time Modified (GMT)"] = data["Date/ Time Booked (GMT)"] + timedelta(days = 1)
    today = datetime.today()
    data["Date/ Time Modified (GMT)"] = np.where(data["Date/ Time Modified (GMT)"] < today,
                                                       np.where(data["Date/ Time Modified (GMT)"] <= data["CheckIn Date"],
                                                                np.where(data["Status"] != "Confirmed",
                                                                         data["Date/ Time Modified (GMT)"],data["Date/ Time Booked (GMT)"]),
                                                                         data["Date/ Time Booked (GMT)"]),data["Date/ Time Booked (GMT)"])

#  Again, Converting the Modified & CheckIn Date column in DD-MM-YYYY

    # data["Date/ Time Modified (GMT)"] = pd.to_datetime( data["Date/ Time Modified (GMT)"]).dt.strftime('%Y-%m-%d %I:%M:%S')
    # data["CheckIn Date"] = pd.to_datetime(data["CheckIn Date"]).dt.strftime('%Y-%m-%d')
    # data["CheckOut Date"] = pd.to_datetime(data["CheckOut Date"]).dt.strftime('%Y-%m-%d')
    data["CheckIn Date"] = data["CheckIn Date"].dt.date
    # data["CheckOut Date"] = pd.to_datetime(data["CheckOut Date"])
    data["CheckOut Date"] = data["CheckOut Date"].dt.date


    try:
        data['Date/ Time Booked (GMT)'] = pd.to_datetime(data['Date/ Time Booked (GMT)'],
                                                               format='%d-%b-%Y %I:%M:%S %p (IST)')
    except:
        data['Date/ Time Booked (GMT)'] = pd.to_datetime(data['Date/ Time Booked (GMT)'],
                                                               format='%d-%b-%Y %I:%M:%S %p')


    # try:
    #     data['Date/ Time Booked (GMT)'] = pd.to_datetime(data['Date/ Time Booked (GMT)'],
    #                                                            format='%d-%b-%Y %I:%M:%S %p (IST)').dt.strftime('%Y-%m-%d %I:%M:%S')
    # except:
    #     data['Date/ Time Booked (GMT)'] = pd.to_datetime(data['Date/ Time Booked (GMT)'],
    #                                                            format='%d-%b-%Y %I:%M:%S %p').dt.strftime('%Y-%m-%d %I:%M:%S')

    data['Property Id'] = htlcode
    data['Currency'] = 'INR'
    # data['Booking No'] = data['Booking No'].astype(np.int)
    try:
        data['Booking No'] = data['Booking No'].astype(np.int64)
    except:
        pass
    # data['Booking No'] = data['Booking No'].apply(lambda x: "'" + str(x))

    # if data['Booking No'][0].__contains__("'"):
    #     data['Booking No'] =  data['Booking No']
    # else:
    #     data['Booking No'] = data['Booking No'].apply(lambda x: "'" + str(x))
    #     print(True)

    try:
        data['Booking No'] = np.where(data['Booking No'][0].__contains__("'"),data['Booking No'],data['Booking No'].apply(lambda x: "'" + str(x)))
    except:
        data['Booking No'] = np.where(data['Booking No'].__contains__("'"),data['Booking No'],data['Booking No'].apply(lambda x: "'" + str(x)))

    data['Tax Value'] = np.where(data['Tax Value'].isna(),data['Tax Value'].fillna(0),data['Tax Value'])
    data['Commission'] = np.where(data['Commission'].isna(), data['Commission'].fillna(0), data['Commission'])
    data['Total Amount'] = np.where(data['Total Amount'].isna(), data['Total Amount'].fillna(0), data['Total Amount'])
    data['Net Amount'] = np.where(data['Net Amount'].isna(), data['Net Amount'].fillna(0), data['Net Amount'])

    data['Rate Id'] = np.where(data['Rate Id'].isna(), data['Rate Id'].fillna(0), data['Rate Id'])
    data['Room Id'] = np.where(data['Room Id'].isna(), data['Room Id'].fillna(0), data['Room Id'])
    data['Rate Plan'] = np.where(data['Rate Plan'].isna(), data['Rate Plan'].fillna(0), data['Rate Plan'])
    try:
        cols = {'Room Id': 'int', 'Rate Id': 'int','Rate Plan': 'int',
                'Commission': 'int', 'Tax Value': 'int',
                'NoExtraAdult': 'int', 'Extra Adult Rate': 'int',
                'NoExtraChild': 'int', 'Extra Child Rate': 'int'}
        data = data.astype(cols)
    except:
        cols = {'Room Id': 'int', 'Rate Id': 'int', 'Rate Plan': 'str',
                'Commission': 'int', 'Tax Value': 'int',
                'NoExtraAdult': 'int', 'Extra Adult Rate': 'int',
                'NoExtraChild': 'int', 'Extra Child Rate': 'int'}
        data = data.astype(cols)

    # 'Total Amount': 'int', 'Net Amount': 'int'
    # cols = ['No Of Rooms', 'NoExtraAdult', 'NoExtraChild', 'Addon']          # Convert float into int dtypes. 11 Oct
    # data['No Of Rooms'] = data['No Of Rooms'].astype(np.int64)
    # data.fillna(0)


    data["No Of Rooms"] = data["No Of Rooms"].fillna(0)
    data["No Of Rooms"] = data["No Of Rooms"].astype(int)

    return data



if __name__ == '__main__':

    today = datetime.today().date()
    # htlname = "Rhythm"
    # htlname = "Breathing Earth"
    # htlcode = 2568
    # htlcode = 9462

    std_path = r"C:\Staah_Data_Conversion_Tool"
    in_path = std_path + "/Input/"
    outpath = std_path + "\Output/" + str(today)
    map_path = std_path + "\Mapping/"
    mapfile = map_path + "\map_col.xlsx"
    dateformat = map_path + "\DateFormat.xlsx"
    arc_file = std_path + "/archieve/"

    if os.path.isdir(in_path):
        files = os.listdir(in_path)
        if len(files) > 0 :
            if files[0].__contains__("OTAData"):
                infile = in_path + "/" + files[0]
                htlcode= (infile.split("_")[-1]).split(".")[0]
                chname = (infile.split("_")[-3]).split("/")[3]
                fin_data = process_staahmax(htlcode, infile, mapfile,dateformat,chname)
                if os.path.isdir(outpath):
                    print("Already Present")
                else:
                    os.mkdir(outpath)
                # fin_data.to_csv(outpath + "\Staah_booking_OTAData_{}.csv".format(htlcode), index=False)
                batchsize = 2200
                for i in range(0, len(fin_data), batchsize):
                    fin_data1 = fin_data[i:i + batchsize]
                    print(fin_data.shape)
                    t = datetime.today().strftime("%H_%M_%S %p")
                    fin_data1.to_csv(outpath + "\staah_booking_OTAData_{}_{}.csv".format(htlcode,t), index=False)
                    print(htlcode + chname + " data is dumped")
                    time.sleep(2)
                # shutil.move(infile , arc_file + "{}_{}.archived".format(today,files) )
                # shutil.move(infile , arc_file)

            else:
                print("No Booking Data found")
        else:
            print("No Booking Data found")
    else:
        print("({})'s s booking data folder not found".format(today))
