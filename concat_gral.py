import sys
from netCDF4 import Dataset
import csv
import datetime as dt

filename = sys.argv[1]
print (filename)
gral_atr = sys.argv[2]
print( 'csv:', gral_atr)

mod_date = dt.datetime.today()
mod_date = mod_date.strftime("%Y-%m-%d")
print("fecha:",  mod_date)
with Dataset(filename, 'a') as ifile, open(gral_atr) as atr_file:
    atr_reader= csv.reader(atr_file, delimiter= ',' )
    for atr_name, atr_val in atr_reader:
        print(atr_name, ':', atr_val)
        ifile.setncattr(atr_name, atr_val)
    ifile.date_metadata_modified = mod_date


