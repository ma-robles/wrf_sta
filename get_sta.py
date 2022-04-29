#Author: Miguel Ángel Robles Roldán
'''
Procesamiento de salidas WRF para generar estadísticos
'''
import sys
from netCDF4 import Dataset
import numpy as np

dayfile = sys.argv[1]
print('archivo:', dayfile)
data_vars=(
        #"QVAPOR",
        #"T",
        "T2",#Temperatura
        #"RH",#Humedad Relativa
        #"PSFC",
        #"Q2",
        #"RAIN",#lluvia
        "WS",#viento
        #"SWDOWN",#Radiación de onda corta
        #"GLW",# Radiación de onda larga
        #"QFX",#Evaporación (moisture flux)
        #"PBLH",#Altura de capa límite
        )
#tamaño de datos, leer de algún archivo?
data_size=(348,617)
with Dataset (dayfile, 'r') as myfile:
    print(myfile['T2'][:].shape)
    data_max = np.amax( myfile['T2'][:]- 273.15, axis=0 )
    data_min= np.amin( myfile['T2'][:]- 273.15, axis=0 )
    print('max:', data_max)
    print('min:', data_min)
    print(data_max - data_min )
