# Operaciones

## Procedimiento operativo estandar
1. Dejar un unico archivo fuente en `input/`.
2. Ejecutar `python run.py` o `correr.bat`.
3. Elegir una opcion del menu segun el objetivo.
4. Seleccionar columnas sugeridas o escribir una columna manualmente.
5. Revisar el archivo generado en `output/`.

## Opciones del menu
1. Transformar Name 1
2. Transformar Street 1
3. Verificar City + Region
4. Verificar ZIP Code / ZIP+4
5. Todo el pipeline transformacion + reporte

## Troubleshooting comun
- Si no se detecta archivo, verificar que exista un `.xlsx`, `.xlsb` o `.csv` dentro de `input/`.
- Si una columna no se detecta, agregar una palabra clave en el modulo correspondiente dentro de `scripts/`.
- Si no aparece ZIP+4 API, revisar que las variables de entorno esten configuradas.
- Si la opcion 3 no corre, confirmar que el archivo tenga columnas para City y Region.

## Logs y monitoreo
La herramienta no genera logs persistentes. El monitoreo actual es por salida de consola y revision del archivo generado.
