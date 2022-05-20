# wrf_sta
Generación de estadísticos de salidas WRF

Se compone de 2 scripts: get_sta.py y calc_m.py
El primero procesa las salidas del WRF para obtener estadísticos diarios (máximos, mínimos y acumulados).
El segundo script, procesa las salidas del primero para calcular estadísticos por mes, así como agregar información 

## get_sta.py
Procesa todas las variables encontradas en las salidas. 
Recibe como parámetros de entrada, la carpeta donde se encuentran los archivos y el año que se debe procesar.

###Sintaxis
python get_sta.py PATH YEAR

PATH ruta donde se encuentra la carpeta con los archivos a procesar
YEAR año que se debe procesar

Se asume que la ruta de los archivos tienen el formato: "a%Y/salidas/wrfout_c1h_d01_%Y-%m-%d_%H:%M:%S.a%Y"

### Ejemplo
python get_sta.py /CHACMOOL/DATOS/RESPALDO_V4/a1979/ 1979

### Salidas
Genera archivo con los datos del año procesado.
El formato del nombre de los archivos es: out_[year].nc,
donde [year] es el año que se procesó.

## calc_m.py
Procesa los archivos anuales generados por get_mean.py.
Asume que el nombre de los archivos tienen la sintaxis: out_[year].nc
Genera un archivo para cada tipo de estadístico.

### Archivos extra
Se utiliza un archivo JSON para configurar el nombre de las variables así como los estadísticos que se requiere generar. El archivo se llama vars.json

Partiendo del archivo de configuración se generan arreglos de promedios mensuales.

metadata.json se utiliza para obtener los nombres de las variables y los parámetros que debe contener cada una de ellas.

