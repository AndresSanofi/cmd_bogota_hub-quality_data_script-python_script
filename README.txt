================================================================
 HERRAMIENTA DE LIMPIEZA DE DATOS
 Guia rapida para usuarios
================================================================

AUTOR
-----
Andres Felipe YANEZ VILLARRAGA
Customer Master Data Analyst
AndresFelipe.YANEZVILLARRAGA@sanofi.com

ALCANCE DEL REPOSITORIO
----------------------
Esta carpeta debe tratarse como un repositorio independiente.
Aunque localmente este dentro de otra ruta mayor, la raiz real del
repositorio es esta carpeta y su nombre objetivo es:

  master-data-quality-cleaner-python

QUE HACE ESTA HERRAMIENTA
-------------------------
Esta herramienta permite limpiar y revisar archivos Excel o CSV
de forma simple, sin modificar el archivo original.

Puede:
  1. Transformar Name 1
  2. Transformar Street 1
  3. Verificar City + Region
  4. Verificar ZIP Code / ZIP+4
  5. Ejecutar todo el pipeline en un solo paso

Los resultados se guardan en la carpeta output/ con fecha y hora
en el nombre del archivo para identificar facilmente el mas reciente.

ANTES DE EMPEZAR
----------------
  - Coloque un solo archivo dentro de input/
  - Formatos soportados: .xlsx, .xlsb, .csv
  - El archivo original no se modifica

COMO USARLO
-----------
Paso 1
  Copie su archivo en la carpeta input/

Paso 2
  Ejecute la herramienta de una de estas dos formas:
    - Doble clic en correr.bat
    - Terminal: python run.py

Paso 3
  Elija la opcion del menu.

Paso 4
  Seleccione las columnas correctas usando:
    - El numero de columna, o
    - El nombre exacto de la columna

Paso 5
  Revise el archivo generado en output/

QUE HACE CADA OPCION
--------------------
1. Transformar Name 1
  - Convierte a mayusculas
  - Limpia simbolos no deseados
  - Aplica abreviaciones configuradas

2. Transformar Street 1
  - Convierte a mayusculas
  - Aplica abreviaciones estandar
  - Mantiene el formato util para direcciones

3. Verificar City + Region
  - Normaliza City y Region
  - Revisa si la ciudad corresponde al estado indicado
  - Revisa si Region es un estado o territorio valido de USA

4. Verificar ZIP Code / ZIP+4
  - Normaliza ZIP a 5 digitos o ZIP+4
  - Detecta ZIP+4 incompleto como 12345-0000
  - Reporta observaciones de formato o consistencia

5. Todo el pipeline
  - Aplica transformaciones
  - Agrega columnas de verificacion cuando hay datos suficientes
  - Genera un solo archivo final

SI UNA COLUMNA NO SE DETECTA
----------------------------
La herramienta busca palabras clave en el nombre de la columna.
Si no encuentra una columna, puede escribir el nombre manualmente.

Si quiere mejorar la deteccion automatica:
  - Name 1: scripts/name_cleaner.py
  - Street 1: scripts/address_cleaner.py
  - City/Region: scripts/city_region_cleaner.py
  - ZIP Code: scripts/zip_code_cleaner.py

SALIDA ESPERADA
---------------
Los archivos se guardan en output/ con un nombre similar a:

  ejemplo_pipeline_completo_20260514_143913.xlsx

Eso permite distinguir claramente cual es el ultimo archivo generado.

INSTALACION
-----------
Si es la primera vez que usa la herramienta:

  pip install -r requirements.txt

Dependencias:
  - pandas
  - openpyxl
  - pyxlsb

ZIP+4 VIA API (OPCIONAL)
------------------------
Si el equipo decide conectar una API externa para completar ZIP+4,
se pueden configurar estas variables:

  ZIP4_API_URL
  ZIP4_API_KEY
  ZIP4_API_KEY_HEADER

REFERENCIAS LOCALES
-------------------
La carpeta reference/ contiene las tablas usadas por la herramienta:

  - address_abbreviations.csv
  - name_abbreviations.csv
  - us_states.csv
  - zip_prefix_regions.csv
  - us_city_state_reference.csv

CONTACTO
--------
Para dudas funcionales o tecnicas, contacte a:
AndresFelipe.YANEZVILLARRAGA@sanofi.com

================================================================
