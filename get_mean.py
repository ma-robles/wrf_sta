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
import numpy as np
import datetime as dt
import os.path as path
import json

start = int(sys.argv[1])
end = int(sys.argv[2])
root = path.normpath( sys.argv[3] )
root_out = path.normpath( sys.argv[4] )
if (path.exists(root)):
    print("Ruta:", root)
else:
    print("La ruta no existe:", root)
    exit(-1)
if (path.exists(root_out)):
    print("Ruta de salida:", root_out)
else:
    print("La ruta no existe:", root_out)
    exit(-1)
fmt_date = "out_%Y.nc"
outfile = sys.argv[4]+"clim.nc"
file_meta = "metadata.json"
with open(file_meta) as md:
    metadata = json.load(md)
file_vars = "vars.json"
with open( file_vars ) as fv:
    all_vars= json.load(fv)
stat_dic = {
        "mean":{"abrv" : "Mes_",
            "vars" : all_vars["mean"],
            "iname" : "acc",
            "itype": "mean",
            "otype": "mean",
            "name": "climatologia mensual",
            },
        "mmax":{"abrv" : "MaxProm_Mes_",
            "vars": all_vars["mmax"],
            "iname": "max",
            "itype": "maximum",
            "otype": "mean",
            "name": "maxima promedio mensual",
            },
        "mmin":{"abrv" : "MinProm_Mes_",
            "vars" : all_vars["mmin"],
            "iname": "min",
            "itype": "minimum",
            "otype": "mean",
            "name": "minima promedio mensual",
            },
        "amax":{"abrv" : "MaxAbs_Mes_",
            "vars" : all_vars["amax"],
            "iname" : "max",
            "itype" : "maximum",
            "otype": "maximum",
            "name": "maxima absoluta mensual",
            },
        "amin":{"abrv" : "MinAbs_Mes_",
            "vars" : all_vars["amin"],
            "iname" : "min",
            "itype" : "minimum",
            "otype": "minimum",
            "name": "minima absoluta mensual",
            },
        }
data_dic = {}

for año in range(start, end+1):
    filename = path.join(root, "out_{}.nc".format(año))
    print('*'*40)
    print(año)
    if (not path.exists(filename)):
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
        for mes in range(1, 13):
            kmes =  months == mes
            if ( kmes.any() == False ):
                print("Sin datos")
                continue
            for stat in stat_dic.keys():
                for varst in stat_dic[stat]["vars"]:
                    k_data = stat_dic[stat]["abrv"]+varst+ '_'+ str(mes)
                    post = stat_dic[stat]["iname"]
                    if (stat_dic[stat]["otype"] == "mean" ):
                        tmp_data = np.sum(myfile[varst+"_" + post][kmes], axis=0)
                        if k_data in data_dic:
                            data_dic[k_data] += tmp_data
                            if (stat_dic[stat]["iname"] == "acc" ):
                                data_dic["ndata_"+ k_data] += np.sum(myfile[varst+"_ndata"][kmes], axis=0)
                            else:
                                data_dic["ndata_"+ k_data] += myfile[varst+"_ndata"][kmes].shape[0]
                        else:
                            data_dic[k_data] = tmp_data
                            if (stat_dic[stat]["iname"] == "acc" ):
                                data_dic["ndata_"+ k_data] = np.sum(myfile[varst+"_ndata"][kmes], axis=0)
                            else:
                                data_dic["ndata_"+ k_data] = myfile[varst+"_ndata"][kmes].shape[0]
                    elif (stat_dic[stat]["otype"] == "maximum" ):
                        tmp_data = np.amax(myfile[varst+"_max"][kmes], axis=0)
                        if k_data in data_dic:
                            data_dic[k_data] = np.fmax(data_dic[k_data], tmp_data )
                        else:
                            data_dic[k_data] = tmp_data
                    elif (stat_dic[stat]["otype"] == "minimum" ):
                        tmp_data = np.amin(myfile[varst+"_min"][kmes], axis=0)
                        if k_data in data_dic:
                            data_dic[k_data] = np.fmin(data_dic[k_data], tmp_data )
                        else:
                            data_dic[k_data] = tmp_data
print('*'*40)
#Dividiendo datos para calcular promedios
for varname in data_dic.keys():
    if (varname[0:5] == "ndata"):
        acc_name = varname[6:]
        accdata = data_dic[acc_name]
        accdata /= data_dic[varname]
#print(data_dic)
#agrupando en arreglos 
data_arr_dic= {}
for varname in data_dic.keys():
    if (varname[0:5] == "ndata"):
        continue
    elif (varname.split('_')[-1].isnumeric()):
        new_name = varname[:varname.rindex('_')]
        idx_mes = varname.split('_')[-1]
        idx_mes = int(idx_mes)-1
        if (not new_name in data_arr_dic.keys()):
            new_shape = (12, data_dic[varname].shape[0], data_dic[varname].shape[1])
            data_arr_dic[new_name] = np.zeros(new_shape)
            
        data_arr_dic [new_name][idx_mes] = np.array([data_dic[varname]])

#creacion de archivos de salida
size_time = 12
size_sn = len(lat)
size_we = len(lon)

# Separando por estadístico
for istat in stat_dic:
    pre = stat_dic[istat]['abrv']
    desc = stat_dic[istat]['name']
    outfile = path.join(root_out, pre[:-1] + ".nc")
    dt_start = dt.datetime(int(start), 1, 1)
    dt_end= dt.datetime(int(end), 1, 1)
    print(istat, "periodo:", start, end)
    method1 = stat_dic[istat]["itype"] 
    method2 = stat_dic[istat]["otype"] 
    with Dataset (outfile, 'w', format= "NETCDF4") as ofile:
        ofile.createDimension("time", size_time)
        ofile.createDimension("south_north", size_sn)
        ofile.createDimension("west_east", size_we)
        ofile.createDimension("nv", 2)
        #tiempo
        var = ofile.createVariable(
                "time",
                "u2",
                ("time"),
                )
        var.units = dt_start.strftime("days since %Y-%m-%d")
        var.climatology  = "climatology_bounds"
        time_arr = []
        for nmes in range(1,13):
            dt_mes =  dt.datetime(dt_start.year, nmes, 15)
            time_arr.append((dt_mes-dt_start).total_seconds()/(3600*24))
        var[:] = time_arr
        var = ofile.createVariable(
                "climatology_bounds",
                "u2",
                ("time", "nv"),
                )
        time_arr = np.zeros((size_time,2), dtype=np.int16)
        for nmes in range(1,13):
            dt_mes = [dt.datetime( start, nmes, 1)]
            if nmes == 12:
                dt_mes.append( dt.datetime( end+1, 1, 1) - dt.timedelta(days=1))
            else:
                dt_mes.append( dt.datetime( end, nmes+1, 1) - dt.timedelta(days=1))
            dt_mes[0]= (dt_mes[0]-dt_start).total_seconds()/(3600*24)
            dt_mes[1]= (dt_mes[1]-dt_start).total_seconds()/(3600*24)
            time_arr[nmes-1] = dt_mes
        var[:] = time_arr
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
        for vname in stat_dic[istat]['vars']:
            varname = pre + vname
            print (outfile, vname, varname)
            var = ofile.createVariable(
                vname,
                "f4",
                ( "time", "south_north", "west_east" )
                )
            var[:] = data_arr_dic[varname]
            if vname in metadata:
                var.long_name = metadata[vname]["long_name"] + ', ' + desc
                for atribs in metadata[vname]["atribs"]:
                    var.setncattr( atribs , metadata[vname]["atribs"][atribs] )
                var.cell_methods = "time: " + method1 + " within years "
                var.cell_methods += "time: " + method2 + " over years"
