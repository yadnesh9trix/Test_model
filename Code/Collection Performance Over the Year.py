import pandas as pd
import numpy as np
from datetime import datetime,timedelta
import warnings
warnings.filterwarnings('ignore')
# from openpyxl import load_workbook
import os

today = datetime.today().date()
last_day = today - timedelta(days=0)

td_date = last_day.strftime("%d")
td_month = last_day.strftime("%m")
last_day_fmt = last_day.strftime("%d%m%Y")

tday  = today.strftime("%d_%b_%Y")

## Start
# Define constants
MAIN_PATH = r"D:/"
STD_PATH = r"D:\Test_model/"
INP_PATH = STD_PATH + "Input/"
PAID_AMOUNT_FOLDER = MAIN_PATH + "Paidamount/"
OUT_PATH = STD_PATH + "OutPut/"

def main():
    # Ensure the output directory exists
    os.makedirs(OUT_PATH, exist_ok=True)

    # Read and preprocess this year's paid data
    this_year_paid_data = Ty_paid(PAID_AMOUNT_FOLDER, last_day_fmt)

    # Read and preprocess historical data
    historical_data = read_and_preprocess_historical_data(INP_PATH, this_year_paid_data)

    # Create and save Ly_Ty_Collection.xlsx
    create_and_save_ly_ty_collection(historical_data)

    # Create and save L5Y_Collection.xlsx
    create_and_save_l5y_collection(historical_data)

def Ty_paid(paidamount_folder, last_day_fmt):
    try:
        typaid = pd.read_excel(f"{paidamount_folder}Paidamount_list_{last_day_fmt}.xlsx")
    except FileNotFoundError as e:
        print(f"paidamount file not found {e}")
    typaid['propertycode'] = typaid['propertycode'].astype(float).apply("{:.02f}".format)
    typaid.dropna(subset=['propertycode'], how='all', inplace=True)
    return typaid

def read_and_preprocess_historical_data(inppath, this_year_paid_data):
    historical_data = []

    for year in range(2018, 2024):
        filename = f"Paid_amountlist{year}-{year+1}.csv"
        filepath = os.path.join(inppath, f"paidamount2018-22/{filename}")

        if not os.path.exists(filepath):
            continue

        data = pd.read_csv(filepath)
        data['receiptdate'] = pd.to_datetime(data['receiptdate'], errors='coerce', format='%Y-%m-%d')
        data = data[data['receiptdate'].notna()]

        historical_data.append(data)

    historical_data.append(this_year_paid_data)
    historical_data = pd.concat(historical_data, ignore_index=True)
    historical_data['fin_year_r'] = historical_data['receiptdate'].dt.year
    historical_data['fin_month_r'] = historical_data['receiptdate'].dt.month

    # Adjust fin_year_r and fin_month_r for the financial year
    historical_data['fin_year_r'] = np.where(historical_data['fin_month_r'] < 4,
                                             historical_data['fin_year_r'] - 1,
                                             historical_data['fin_year_r'])
    historical_data['fin_month_r'] = np.where(historical_data['fin_month_r'] < 4,
                                              historical_data['fin_month_r'] + 9,
                                              historical_data['fin_month_r'] - 3)

    return historical_data

def create_and_save_ly_ty_collection(historical_data):
    # Create Ly_Ty_Collection.xlsx
    df = historical_data[(historical_data['fin_year_r'] >= 2022) & (historical_data['fin_year_r'] < 2024)]
    grpbydf = df.groupby(['receiptdate']).agg(
        {'propertycode': 'count', 'paidamount': 'sum'}).reset_index()

    grpbydf_Last_year = grpbydf[(grpbydf['receiptdate'] >= datetime(2022, 6, 1)) &
                                (grpbydf['receiptdate'] <= datetime(2022, 6, int(td_date)))].copy()
    grpbydf_Last_year = grpbydf_Last_year.rename(columns={'paidamount': 'paidamount_ly', 'propertycode': 'propertycode_ly'})

    grpbydf_This_year = grpbydf[grpbydf['receiptdate'] >= datetime(2023, 6, 1)].copy()
    grpbydf_This_year = grpbydf_This_year.rename(columns={'paidamount': 'paidamount_ty', 'propertycode': 'propertycode_ty'})
    grpbydf_This_year[['propertycode_ly', 'paidamount_ly']] = grpbydf_Last_year[['propertycode_ly', 'paidamount_ly']]
    grpbydf_This_year[['paidamount_ty', 'paidamount_ly']] = grpbydf_This_year[['paidamount_ty', 'paidamount_ly']] / 10000000

    grpbydf_This_year.to_excel(f"{OUT_PATH}Ly_Ty_Collection.xlsx", index=False)

def create_and_save_l5y_collection(historical_data):
    # Create L5Y_Collection.xlsx
    yr = [2018, 2019, 2020, 2021, 2022, 2023]
    lll = []

    for i in yr:
        finYr = i + 1
        finYr2023_24 = historical_data[(historical_data['fin_year_r'] >= i) & (historical_data['fin_year_r'] < finYr)]
        df_filtered = finYr2023_24[finYr2023_24['receiptdate'] <= datetime(i, int(td_month), int(td_date))]
        df_filtered['Financial_Year'] = f"{i}-{finYr}"
        df_filtered['STLY_Date'] = datetime(i, int(td_month), int(td_date))
        grpbydf = df_filtered.groupby(['Financial_Year', 'ezname', 'STLY_Date']).agg(
            {'propertycode': 'count', 'paidamount': 'sum'}).reset_index()
        lll.append(grpbydf)

    ddd1 = pd.DataFrame(pd.concat(lll))
    ddd1.to_excel(f"{OUT_PATH}L5Y_Collection.xlsx", index=False)


if __name__ == '__main__':
    main()