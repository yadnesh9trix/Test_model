# import module
import pandas as pd
from datetime import datetime,timedelta
import warnings
warnings.filterwarnings('ignore')
import os
import warnings
warnings.filterwarnings('ignore')
from pdf2docx import parse
#-----------------------------------------------------------------------------------------------------------------------
## Define the today's date
today = datetime.today().date()
tday  =today.strftime("%d_%b_%Y")

#-----------------------------------------------------------------------------------------------------------------------
## Start
if __name__ == '__main__':
    tax_data = "D:/"
    std_path= r"D:\Test_model/"
    inppath = std_path + "Input/"
    outpth = std_path + "OutPut/" + tday + "/"

    os.makedirs(outpth,exist_ok=True)

pdf_file = "test.pdf"
word_file = "test.docx"

pth = inppath + "Ptax Activites.pdf"
parse(pth, word_file, start=0, end=None)

------------------------------------------------------------------------------------------------
from typing import Tuple

def convert_pdf2docs(input_file :str, output_file : str, pages: Tuple = None):

    if pages:
        pages = [int(i) for i in list(pages) if i.isnumeric()]
    result = parse(pdf_file=input_file,
                   docx_file= output_file, pages=pages)

    summary = {"File" : input_file, "Pages": str(pages), "Output File": output_file}

    print("## Summary #########################################################")
    print("\n".join("{}:{}".format(i, j) for i , j in summary.items()))
    print("#####################################################################")
    return result

output_file = "test20230712.docx"
convert_pdf2docs(pth, output_file)
