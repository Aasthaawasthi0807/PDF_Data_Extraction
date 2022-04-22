
from PyPDF2 import PdfFileReader
import csv
from msilib.schema import File
import re
import pdfplumber
import pandas as pd
from pathlib import Path
from collections import namedtuple

jrnl_re = re.compile(r'NAME (\d+) (.*) \(.*? Phone (.*) Email.*\).+(\d+ [A-Z].*)')
Row = namedtuple('Row', 'Name Phone Mobile Email Office_Address Residence_Address')

def dr_cr(last_pos , row):
    return 'name' if last_pos[row] < 680 else 'email'

def numbify(num):
    return int(num.replace('$', '').replace(',',''))

def page_to_df(lines , last_pos , name_info =('','','','','','','')):
    jrnl, person_name, phone ,mobile,email, Office_Address , Residence_Address = name_info
    rows = []

    for idx , line in enumerate(lines.split('\n')):
        if line.startswith('NAME'):
            jrnl = jrnl_re.search(line)
            person_name = jrnl.group(1)
            phone = jrnl.group(2)
            mobile = jrnl.group(3)
            email = jrnl.group(4)
            Office_Address = jrnl.group(5)
            Residence_Address = jrnl.group(6)

        df = pd.DataFrame(rows)
    return df , (jrnl,person_name,phone,mobile , email,Office_Address,Residence_Address)

df = pd.DataFrame()
name_info = ('','','','','','' , '')
with pdfplumber.open("File.pdf") as pdf:
    for page in pdf.pages:
        lines = page.extract_text(x_tolerance=2 , y_tolerance = 0)
        words = page.extract_words(x_tolerance=2 , y_tolerance=0)
        rows_dict =  {b:a for a , b in enumerate(sorted(set([word['bottom'] for word in words])))}
        last_pos = {rows_dict.get(word['bottom']): word['x1'] for word in words}
        new_df , name_info = page_to_df(lines , last_pos , name_info )
        df = pd.concat([df,new_df]).reset_index(drop=True)
        
        
with pdfplumber.open("File.pdf") as pdf:
    lines = pdf.pages[0].extract_text(x_tolerance=3, y_tolerance=4)
    print(lines)





pdf = PdfFileReader('File.pdf')

page_1_object = pdf.getPage(0)


page_1_text = page_1_object.extractText()


with Path('File_text.csv').open(mode='w' , encoding="utf-8") as output_file:
    text=''
    for page in pdf.pages:
        text += page.extractText()
    output_file.write(text)



