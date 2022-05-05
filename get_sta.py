#Author: Miguel Ángel Robles Roldán
'''
Procesamiento de salidas WRF para generar estadísticos
'''
import sys
from netCDF4 import Dataset
import numpy as np
import datetime as dt

root = sys.argv[1]
fmt_date = "a%Y/salidas/wrfout_c1h_d01_%Y-%m-%d_%H:%M:%S.a%Y"
año = sys.argv[2]
start = año + "0101"
end = año + "1231"
fmt_par = "%Y%m%d"
dt_start = dt.datetime.strptime(start, fmt_par)
dt_end = dt.datetime.strptime(end, fmt_par)
dt_pointer = dt.datetime.strptime(start, fmt_par)
outfile = sys.argv[3]+"out_" + año + ".nc"
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
        "LH",
        "HFX",
        )
#tamaño de datos
#data_size=(348,617)
#recorte para GdM
sn = (121, 307)
we = (313, 533)
size_sn = sn[1] - sn[0]
size_we = we[1] - we[0]
size_time = 0
data_dic = {}
for var_name in data_vars:
    data_dic[var_name] = {'data_max': np.array ([]),
            'data_min': np.array ([]),
            'data_acc': np.array ([]),
            'ndata': 0,
            }

name_timevar = "Times"
date_list = []
while dt_pointer <= dt_end:
    dayfile = root + dt_pointer.strftime(fmt_date)
    try:
        with Dataset (dayfile, 'r') as myfile:
            print( dayfile)
    except:
        print('Archivo no encontrado', dayfile)
        dt_pointer += dt.timedelta(days=1)
        continue
    with Dataset (dayfile, 'r') as myfile:
        #Obteniendo la fecha
        mytime = myfile[name_timevar][0,:]
        mytime = (bytes(mytime).decode('utf-8'))
        mytime = mytime.split('_')[0]
        mytime = dt.datetime.strptime(mytime, "%Y-%m-%d")
        date_list.append((mytime - dt_start).total_seconds()/3600)
        for var_name in data_vars:
            print(var_name)
            if var_name == 'T2':
                values = myfile[var_name][:, sn[0]: sn[1], we[0]: we[1]] - 273.15 
            elif var_name == "WS":
                U = myfile["U10"][:, sn[0]: sn[1], we[0]: we[1]]
                V = myfile["V10"][:, sn[0]: sn[1], we[0]: we[1]]
                values = np.sqrt(np.square(V) + np.square(U))
                print('wind', values.shape,)

            else:
                values = myfile[var_name][:, sn[0]: sn[1], we[0]: we[1]]
            try:
                data_dic[ var_name ][ 'data_max']= np.append( data_dic[ var_name ][ 'data_max' ],
                    [np.amax( values, axis=0 )],
                    axis=0,
                    )
            except:
                data_dic[ var_name ][ 'data_max']= np.array([np.amax( values, axis=0 )])
            try:
                data_dic[ var_name ][ 'data_min']= np.append( data_dic[ var_name ][ 'data_min' ],
                    [np.amin( values, axis=0 )],
                    axis=0,
                    )
            except:
                data_dic[ var_name ][ 'data_min']= np.array([np.amin( values, axis=0 )])
            try:
                data_dic[ var_name ][ 'data_acc']= np.append( data_dic[ var_name ][ 'data_acc' ],
                    [np.sum( values, axis=0 )],
                    axis=0,
                    )
            except:
                data_dic[ var_name ][ 'data_acc']= np.array([np.sum( values, axis=0 )])

            data_dic[ var_name ][ 'ndata'] += values.shape[0]
            print('values 0:', values.shape[0])
        size_time += 1
        dt_pointer += dt.timedelta(days=1)

metadata = {}
metadata['T2']={
         'units':'C',
         'standard_name':'Air temperature',
         'long_name':'Air temperature',
         'description': ' Air Temperature at 2 m',
         'dtype':"f4",
         }
metadata['WS']={
         'units':'m s-1',
         'standard_name':'wind',
         'long_name':'wind',
         'description': 'wind',
         'dtype':"f4",
         }
metadata['SWDOWN']={
         'units':'u',
         'standard_name':'Rad',
         'long_name':'Rad',
         'description': 'Rad',
         'dtype':"f4",
         }
metadata['GLW']={
         'units':'u',
         'standard_name':'rad',
         'long_name':'rad',
         'description': 'rad',
         'dtype':"f4",
         }
metadata['QFX']={
         'units':'u',
         'standard_name':'eva',
         'long_name':'eva',
         'description': 'eva',
         'dtype':"f4",
         }
metadata['LH']={
         'units':'w m-2',
         'standard_name':'',
         'long_name':'Calor latente en la superficie',
         'description': '',
         'dtype':"f4",
         }
metadata['HFX']={
         'units':'w m-2',
         'standard_name':'',
         'long_name':'Calor sensible',
         'description': '',
         'dtype':"f4",
         }

axis_fname = "a1979/salidas/wrfout_c_anio_d01_1979-01-02_00:00:00.a1979"
with Dataset (root + axis_fname, 'r') as axis_file:
    lat = axis_file["XLAT"][0,sn[0]:sn[1],0]
    lon = axis_file["XLONG"][0,0,we[0]:we[1]]
    print(lat.shape, lat)
    print(lon.shape, lon)

#crea archivo de salida
print("Escribiendo", outfile)
with Dataset (outfile, 'w', format= "NETCDF4") as ofile:
    s_time = ofile.createDimension("Time", size_time)
    s_sn = ofile.createDimension("south_north", size_sn)
    s_we = ofile.createDimension("west_east", size_we)
    #tiempo
    var = ofile.createVariable(
            "Time",
            "f8",
            ("Time"),
            )
    var.units = dt_start.strftime("hours since %Y-%m-%d %H:%M:%S")
    var[:] = date_list
    #lat
    var = ofile.createVariable(
            "latitude",
            "f8",
            ("south_north"),
            )
    var.units = "degree_north"
    var.standard_name = "latitude"
    var[:] = lat
    #lon
    var = ofile.createVariable(
            "longitude",
            "f8",
            ("west_east"),
            )
    var.units = "degree_east"
    var.standard_name = "longitude"
    var[:] = lon
    for vname in data_dic.keys():
        print(vname)
        for stat in ["data_max", "data_min", "data_acc",]:
            var = ofile.createVariable(
                    vname+'_'+stat.split('_')[1],
                    metadata[vname]['dtype'],
                    ("Time", "south_north", "west_east"),
                    )
            var.units = metadata[vname]['units']
            #var.standard_name = metadata[vname]['standard_name']
            var.long_name = metadata[vname]['long_name'] + ' ' + stat.split('_')[1]
            var.description = var.long_name + ' del día'
            var[:] = data_dic[vname][stat]
        var = ofile.createVariable(
                vname+ '_ndata',
                'u4',
                )
        var.description = "cantidad de datos acumulados para " + vname
        var[:] = data_dic[vname]['ndata']
    
