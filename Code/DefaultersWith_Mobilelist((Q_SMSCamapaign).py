import pandas as pd
import numpy as np
from datetime import datetime,timedelta
import warnings
warnings.filterwarnings('ignore')
import os
import datetime
import warnings
warnings.filterwarnings('ignore')

#-----------------------------------------------------------------------------------------------------------------------
## Define the today's date
today = datetime.datetime.today().date()
tday  =today.strftime("%d_%b_%Y")

last_day = today - timedelta(days=0)

td_date = last_day.strftime("%d")
td_month = last_day.strftime("%m")
last_day_fmt = last_day.strftime("%d%m%Y")

#-----------------------------------------------------------------------------------------------------------------------

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

    df = pd.read_excel(inppath + "DefaulterList with Consession-23June23.xlsx")

    df['propertycode'] = df['propertycode'].str.replace("/",".")
    wrong_pid = pd.read_excel(inppath + "japtiwrong_pid.xlsx")

    def replace_pid(df,wrong_pid):
        for i, j in zip(wrong_pid['Wrong_pid'], wrong_pid['pid']):
            df['propertycode'] = df['propertycode'].str.replace(str(i), str(j))
        return df

    df = replace_pid(df,wrong_pid)

    # for i in wrong_pid['Wrong_pid']:
    #     for j in wrong_pid['pid']:
    #         df['propertycode'] = df['propertycode'].str.replace(str(i), str(j))

    # df['propertycode'] = df['propertycode'].str.replace('1040705608.00.00', '1040705608.00') \
    #     .str.replace('1150406630 .00', '1150406630.00').str.replace('`', '')
    # df['propertycode'] = df['propertycode'].str.replace("1150406630 .00", "1150406630.00").str.replace(
    #     '1100900002.10.10', '1100900002.20').str.replace('`','').str.replace('1040705608.00.00','1040705608.00')

    df['propertycode'] = df['propertycode'].astype(float)
    df['propertycode'] = df['propertycode'].apply("{:.02f}".format)

    #-------------------------------------------------------------------------------------------------------------------
    propertyreceipt_df = pd.read_csv(tax_data + "Property_Tax_Receipt_Amount_Dump_24042023.csv", low_memory=False,
                                     encoding='utf-8-sig')

    ## find the (receiptdate) column year or month
    propertyreceipt_df['receiptdate'] = pd.to_datetime(propertyreceipt_df['receiptdate'], errors='coerce',
                                                       format='%Y-%m-%d')
    # propertyreceipt_df['fin_year_r'] = propertyreceipt_df['receiptdate'].dt.year
    # propertyreceipt_df['fin_month_r'] = propertyreceipt_df['receiptdate'].dt.month

    lastreceiptdate = propertyreceipt_df.sort_values(['propertykey', 'receiptdate']).drop_duplicates('propertykey',
                                                                                                  keep='last')
    preceipt_woutty_data = lastreceiptdate[['propertykey', 'receiptdate']]
    preceipt_woutty_data = preceipt_woutty_data.rename(columns={"receiptdate": 'Last_yr_receiptdate'})

    defaulter_lastpreceipt = df.merge(preceipt_woutty_data,on='propertykey',how='left')

    defaulter_lastpreceipt['Quarters'] = pd.PeriodIndex(defaulter_lastpreceipt['Last_yr_receiptdate'], freq="Q-Mar").strftime("Q%q")

    defaulter_lastpreceipt = defaulter_lastpreceipt.drop_duplicates('propertycode')
    defaulter_lastpreceipt = defaulter_lastpreceipt.drop_duplicates('mobileno')

    # defaulter_lastpreceipt.to_excel(outpth + "DeafulterListWithMobile-23June23.xlsx",index=False)
    #------------------------------------------------------------------------------------------------
    q1_list = defaulter_lastpreceipt[defaulter_lastpreceipt['Quarters'] == 'Q1']
    filterddefaulters_q1list = q1_list[['mobileno','propertycode','propertyname','concession']]
    # filterddefaulters_q1list['concession'] = round(filterddefaulters_q1list['consession'])
    filterddefaulters_q1list.to_csv(outpth+"SMS_defaulterslist_Q1.csv",index=False,encoding="utf-8-sig")

    #------------------------------------------------------------------------------------------------
    q234_list = defaulter_lastpreceipt[defaulter_lastpreceipt['Quarters'].isin(['Q2','Q3','Q4'])]
    filterddefaulters_q234list = q234_list[['mobileno','propertycode','propertyname','concession']]
    # filterddefaulters_q234list['consession'] = round(filterddefaulters_q234list['concession'])
    filterddefaulters_q234list.to_csv(outpth+"SMS_defaulterslist_Q2toQ4.csv",index=False,encoding="utf-8-sig")
    #------------------------------------------------------------------------------------------------
