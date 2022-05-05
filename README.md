# wrf_sta
estadísticos de salidas WRF

## Configuración
Se utiliza un archivo JSON para configurar el nombre de las variables así como los estadísticos que se requiere generar. El archivo se llama config.json

Partiendo del archivo de configuración se generan arreglos de promedios diarios, máximos diarios y mínimos diarios. Estos arreglos son la base para generar los demás estadísticos

## Ejemplo
python get_sta.py /CHACMOOL/DATOS/RESPALDO_V4/a1979/salidas/wrfout_c1h_d01_1979-01-02_00:00:00.a1979
