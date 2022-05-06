#Author: Miguel Ángel Robles Roldán
'''
Procesamiento de estadísticos diarios para generar promedios
argumentos:
    año de inicio
    año de fin
    ruta de entrada
    ruta de salida
'''
import sys
from netCDF4 import Dataset
from netCDF4 import date2index
import numpy as np
import datetime as dt
import os.path

start = int(sys.argv[1])
end = int(sys.argv[2])
root = sys.argv[3]
fmt_date = "out_%Y.nc"
outfile = sys.argv[4]+"clim.nc"
mean_vars=(
        "T2",
        "WS",
        "LH",
        "HFX",
        )
mean_vars=(
        "T2",
        "WS",
        "LH",
        "HFX",
        )
mmax_vars=(
        "T2",
        "WS",
        )
mmin_vars=(
        "T2",
        )
amax_vars=(
        "T2",
        "WS",
        )
amin_vars=(
        "T2",
        )
stat_dic = {
        "mean":{"abrv" : "Mes_",
            "vars" : mean_vars},
        "mmax":{"abrv" : "MaxProm_Mes_",
            "vars": mmax_vars},
        "mmin":{"abrv" : "MinProm_Mes_",
            "vars" : mmin_vars},
        "amax":{"abrv" : "MaxAbs_Mes_",
            "vars" : amax_vars},
        "amin":{"abrv" : "MinAbs_Mes_",
            "vars" : amin_vars},
        }
data_dic = {}

for año in range(start, end+1):
    filename = root+ "out_{}.nc".format(año)
    print('*'*40)
    print(año)
    if (not os.path.exists(filename)):
        print("No se encontró el archivo", filename)
        continue
    print("procesando", filename)
    with Dataset(filename, 'r') as myfile:
        #calcula pertenencia a meses
        base = myfile["Time"].units.split()
        base = base[2] + " " + base[3]
        base = dt.datetime.strptime(base, "%Y-%m-%d %H:%M:%S")
        print('base:', base)
        months =  []
        for t in myfile["Time"][:]:
            date = base + dt.timedelta(hours=t)
            months.append( date.month)
        months = np.array(months)
        print(months)
        for mes in range(1, 13):
            kmes =  months == mes
            print("kmes", mes, kmes, kmes.all())
            if ( kmes.any() == False ):
                print("Sin datos")
                continue
            for stat in stat_dic.keys():
                print(stat)
                for varst in stat_dic[stat]["vars"]:
                    k_data = stat_dic[stat]["abrv"]+varst+ '_'+ str(mes)
                    print('varst:', varst, k_data)
                    if (stat == "mean" ):
                            if k_data in data_dic:
                                data_dic[k_data] += np.sum(myfile[varst+"_acc"][kmes], axis=0)
                                data_dic["ndata_"+ k_data] += np.sum(myfile[varst+"_ndata"][kmes], axis=0)
                            else:
                                data_dic[k_data] = np.sum(myfile[varst+"_acc"][kmes], axis=0)
                                data_dic["ndata_"+ k_data] = np.sum(myfile[varst+"_ndata"][kmes], axis=0)

                    if (stat == "mmax" ):
                            if k_data in data_dic:
                                data_dic[k_data] += np.sum(myfile[varst+"_max"][kmes], axis=0)
                                data_dic["ndata_"+ k_data] += myfile[varst+"_ndata"][kmes].shape[0]
                            else:
                                data_dic[k_data] = np.sum(myfile[varst+"_max"][kmes], axis=0)
                                data_dic["ndata_"+ k_data] = myfile[varst+"_ndata"][kmes].shape[0]

                    if (stat == "mmin" ):
                            if k_data in data_dic:
                                data_dic[k_data] += np.sum(myfile[varst+"_min"][kmes], axis=0)
                                data_dic["ndata_"+ k_data] += myfile[varst+"_ndata"][kmes].shape[0]
                            else:
                                data_dic[k_data] = np.sum(myfile[varst+"_min"][kmes], axis=0)
                                data_dic["ndata_"+ k_data] = myfile[varst+"_ndata"][kmes].shape[0]

                    if (stat == "amax" ):
                            tmp_data = np.amax(myfile[varst+"_max"][kmes], axis=0)
                            if k_data in data_dic:
                                data_dic[k_data] = np.fmax(data_dic[k_data], tmp_data )
                            else:
                                data_dic[k_data] = tmp_data

                    if (stat == "amin" ):
                            tmp_data = np.amax(myfile[varst+"_min"][kmes], axis=0)
                            if k_data in data_dic:
                                data_dic[k_data] = np.fmin(data_dic[k_data], tmp_data )
                            else:
                                data_dic[k_data] = tmp_data
print('*'*40)
print(data_dic)
for varname in data_dic.keys():
    print(varname)
    #print(data_dic[varname])
        
exit(0)

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
    
