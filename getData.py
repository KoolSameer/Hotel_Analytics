# -*- coding: utf-8 -*-
"""
This is the first level of validation

1. Check all the Columns
2. Identify how many columns have missing values
3. Identify if the column values are as per expected format
"""

#import codecs
#import numpy  as np

import pandas as pd
import csv
import datetime as dt

#01.01.15-31.12.15
#01.01.16-31.12.16
#01.01.17-31.12.17
#01.01.18-31.12.18

def getData(flName, osrField):
    
    flname = flName #'G:/Revnomix_backup/GDrive/MAF/Kempinsky/01.01.15-31.12.15.txt'
    
    #doc = codecs.open(flname,'rU','UTF-16') #open for reading with "universal" type set
    
    df_osr = pd.read_csv(flname, delimiter = "|", index_col=None, header=None, low_memory=False, quoting=csv.QUOTE_NONE, error_bad_lines=False, skiprows = 3)
    
    xlfile    = osrField #'G:\Revnomix_backup\GDrive\MAF\Kempinsky\List_Of_Fields_For_OSR.xlsx'
    df_header = pd.read_excel(xlfile, index_col=None, na_values=['NA'])
    
    df_Data   = df_osr.rename(columns=df_header.set_index('Sl_No')['Rep_Fields'])
    
#    df_Data.dtypes
    
    df_Data['ActualCheckinDate']   = pd.to_datetime(df_Data['ActualCheckinDate'], format='%d-%b-%y', errors = 'coerce')
    df_Data['ActualDepartureDate'] = pd.to_datetime(df_Data['ActualDepartureDate'], format='%d-%b-%y', errors = 'coerce')
    df_Data['ArrivalDate']          = pd.to_datetime(df_Data['ArrivalDate'], format='%d-%b-%y', errors = 'coerce')
    df_Data['DepartureDate']         = pd.to_datetime(df_Data['DepartureDate'], format='%d-%b-%y', errors = 'coerce')
    df_Data['CancellationDate']     = pd.to_datetime(df_Data['CancellationDate'], format='%d-%b-%y', errors = 'coerce')
    df_Data['CreationDate']         = pd.to_datetime(df_Data['CreationDate'], format='%d-%b-%y', errors = 'coerce')
    
    df_Data_clean = pd.DataFrame(df_Data.dropna(thresh = 3))
        
    df_Data_clean.to_csv('G:/Revnomix_backup/GDrive/MAF/Kempinsky/2015_ETL_13JUN18.csv', sep=',', encoding='utf-8')

    return df_Data_clean

def addYears(d, years):
    try:
#Return same day of the current year        
        return d.replace(year = d.year + years)
    except ValueError:
#If not same day, it will return other, i.e.  February 29 to March 1 etc.        
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))
