# Arquitectura

## Vision general
La herramienta esta diseñada como un flujo local de procesamiento por lotes para archivos de clientes. El usuario coloca un archivo en `input/`, ejecuta `run.py`, selecciona el proceso deseado y obtiene un archivo `.xlsx` en `output/`.

## Componentes principales
- `run.py`: orquesta la experiencia de usuario, la seleccion de columnas y el guardado del archivo final.
- `scripts/_core.py`: concentra reglas compartidas de normalizacion, validacion, referencias y lectura escritura de archivos.
- `scripts/name_cleaner.py`: transforma columnas nominales tipo Name 1.
- `scripts/address_cleaner.py`: transforma direcciones tipo Street 1.
- `scripts/city_region_cleaner.py`: separa transformacion de City de la verificacion City Region.
- `scripts/zip_code_cleaner.py`: separa transformacion de ZIP de la verificacion ZIP ZIP+4.
- `reference/`: contiene catálogos locales para abreviaciones, estados y referencias geograficas.

## Flujo de procesamiento
1. Deteccion del primer archivo disponible en `input/`.
2. Carga del archivo como `DataFrame` de pandas.
3. Seleccion de columnas por nombre o indice.
4. Aplicacion de transformaciones o verificaciones.
5. Escritura de un nuevo archivo con timestamp en `output/`.

## Decisiones de diseño
- Se separa transformacion de verificacion para evitar mezclar correccion automatica con reporte de calidad.
- Las referencias viven en archivos CSV para permitir mantenimiento sin tocar codigo.
- La salida siempre es `.xlsx` para facilitar revision por usuarios de negocio.
- El nombre del archivo incluye timestamp para distinguir el ultimo resultado generado.

## Dependencias del sistema
- Python 3.12
- pandas
- openpyxl
- pyxlsb
