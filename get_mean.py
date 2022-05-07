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
            "vars" : mean_vars,
            "itype": "acc",
            "otype": "mean",
            },
        "mmax":{"abrv" : "MaxProm_Mes_",
            "vars": mmax_vars,
            "itype": "max",
            "otype": "mean",
            },
        "mmin":{"abrv" : "MinProm_Mes_",
            "vars" : mmin_vars,
            "itype": "min",
            "otype": "mean",
            },
        "amax":{"abrv" : "MaxAbs_Mes_",
            "vars" : amax_vars,
            "itype" : "max",
            "otype": "max",
            },
        "amin":{"abrv" : "MinAbs_Mes_",
            "vars" : amin_vars,
            "itype" : "min",
            "otype": "min",
            },
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
        #obteniendo lat y lon
        lat = myfile["latitude"][:]
        lon = myfile["longitude"][:]
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
            if ( kmes.any() == False ):
                print("Sin datos")
                continue
            for stat in stat_dic.keys():
                print(stat)
                for varst in stat_dic[stat]["vars"]:
                    k_data = stat_dic[stat]["abrv"]+varst+ '_'+ str(mes)
                    post = stat_dic[stat]["itype"]
                    print('varst:', varst, k_data, post)
                    if (stat_dic[stat]["otype"] == "mean" ):
                        tmp_data = np.sum(myfile[varst+"_" + post][kmes], axis=0)
                        print('acc:', myfile[varst+"_ndata"][kmes])
                        print(myfile[varst+"_"+post][kmes].shape)
                        print(myfile[varst+"_"+post][kmes][0])
                        if k_data in data_dic:
                            data_dic[k_data] += tmp_data
                            if (stat_dic[stat]["itype"] == "acc" ):
                                data_dic["ndata_"+ k_data] += np.sum(myfile[varst+"_ndata"][kmes], axis=0)
                            else:
                                data_dic["ndata_"+ k_data] += myfile[varst+"_ndata"][kmes].shape[0]
                        else:
                            data_dic[k_data] = tmp_data
                            if (stat_dic[stat]["itype"] == "acc" ):
                                data_dic["ndata_"+ k_data] = np.sum(myfile[varst+"_ndata"][kmes], axis=0)
                            else:
                                data_dic["ndata_"+ k_data] = myfile[varst+"_ndata"][kmes].shape[0]
                    elif (stat_dic[stat]["otype"] == "max" ):
                        tmp_data = np.amax(myfile[varst+"_max"][kmes], axis=0)
                        if k_data in data_dic:
                            data_dic[k_data] = np.fmax(data_dic[k_data], tmp_data )
                        else:
                            data_dic[k_data] = tmp_data
                    elif (stat_dic[stat]["otype"] == "min" ):
                        tmp_data = np.amin(myfile[varst+"_min"][kmes], axis=0)
                        if k_data in data_dic:
                            data_dic[k_data] = np.fmin(data_dic[k_data], tmp_data )
                        else:
                            data_dic[k_data] = tmp_data
print('*'*40)
#Dividiendo datos para calcular promedios
for varname in data_dic.keys():
    print(varname)
    if (varname[0:5] == "ndata"):
        acc_name = varname[6:]
        accdata = data_dic[acc_name]
        print(accdata)
        accdata /= data_dic[varname]
        print(data_dic[varname])
        print(accdata)
#print(data_dic)
#creacion de archivo de salida
size_time = 12
size_sn = len(lat)
size_we = len(lon)

outfile = "out_mes.nc"
dt_start = dt.datetime(1979, 1, 1)
with Dataset (outfile, 'w', format= "NETCDF4") as ofile:
    ofile.createDimension("time", size_time)
    ofile.createDimension("south_north", size_sn)
    ofile.createDimension("west_east", size_we)
    #tiempo
    var = ofile.createVariable(
            "time",
            "u2",
            ("time"),
            )
    var.units = dt_start.strftime("days since %Y-%m-%d")
    var[:] = np.array(range(1,13))
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
    for varname in data_dic.keys():
        print(varname)
        if (varname[0:5] == "ndata"):
            continue
        var = ofile.createVariable(
            varname,
            "f4",
            ( "time", "south_north", "west_east" )
            )
        var[:] = data_dic[varname]
exit(0)

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
    
