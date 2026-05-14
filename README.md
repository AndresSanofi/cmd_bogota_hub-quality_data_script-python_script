# master-data-quality-cleaner-python

## Descripcion
Herramienta interna de Python para usuarios no tecnicos que necesitan limpiar y revisar archivos Excel o CSV con datos maestros de clientes. El flujo toma un archivo desde `input/`, aplica transformaciones o verificaciones segun la opcion elegida y guarda el resultado en `output/` sin modificar el archivo original.

## Proposito del negocio
Este proyecto reduce trabajo manual en tareas repetitivas de data quality para Customer Master Data. Estandariza campos criticos como Name, Street, City y ZIP, y separa claramente las transformaciones de los reportes de verificacion para facilitar la revision operativa y la toma de accion.

## Caracteristicas principales
- Transformacion de `Name 1` a mayusculas con reglas de limpieza y abreviaciones.
- Transformacion de `Street 1` con abreviaciones tipo USPS y normalizacion de formato.
- Transformacion independiente de `City`, incluso cuando no existe `Region`.
- Verificacion de `City + Region` contra referencias de estados de Estados Unidos.
- Verificacion de `ZIP Code / ZIP+4`, incluyendo deteccion de ZIP+4 incompleto.
- Nombres de salida con timestamp para identificar rapidamente el ultimo archivo generado.
- Interfaz por consola pensada para usuarios no tecnicos.

## Tecnologias utilizadas
- Python 3.12
- pandas
- openpyxl
- pyxlsb

## Instalacion y configuracion
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Uso
```powershell
python run.py
```

Pasos operativos:
1. Colocar un unico archivo de trabajo en `input/`.
2. Ejecutar `python run.py` o hacer doble clic en `correr.bat`.
3. Elegir una opcion del menu.
4. Seleccionar las columnas sugeridas o escribir el nombre exacto.
5. Revisar el archivo generado en `output/`.

## Estructura del proyecto
```text
cleaner/
|-- .github/
|   `-- CODEOWNERS
|-- docs/
|   |-- ARCHITECTURE.md
|   |-- HANDOVER.md
|   |-- OPERATIONS.md
|   `-- SETUP.md
|-- input/
|   |-- .gitkeep
|   `-- ejemplo.csv
|-- output/
|   `-- .gitkeep
|-- reference/
|   |-- address_abbreviations.csv
|   |-- name_abbreviations.csv
|   |-- us_city_state_reference.csv
|   |-- us_states.csv
|   `-- zip_prefix_regions.csv
|-- scripts/
|   |-- _core.py
|   |-- address_cleaner.py
|   |-- city_region_cleaner.py
|   |-- name_cleaner.py
|   `-- zip_code_cleaner.py
|-- AUTHORS.md
|-- CHANGELOG.md
|-- LICENSE
|-- MAINTAINERS.md
|-- README.md
|-- README.txt
|-- requirements.txt
`-- run.py
```

## Nombre del repositorio
Nombre definido para el repositorio: `master-data-quality-cleaner-python`.

## Autor y contacto
Autor original: Andres Felipe YANEZ VILLARRAGA  
Email: AndresFelipe.YANEZVILLARRAGA@sanofi.com  
Rol: Customer Master Data Analyst  
Fecha de creacion: Mayo 2026

## Contribuidores
Actualmente no hay contribuidores adicionales registrados.

## Licencia
Sanofi Internal Use Only.

## Documentacion adicional
- Ver [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) para arquitectura y decisiones tecnicas.
- Ver [docs/SETUP.md](docs/SETUP.md) para instalacion detallada.
- Ver [docs/OPERATIONS.md](docs/OPERATIONS.md) para uso operativo y troubleshooting.
- Ver [docs/HANDOVER.md](docs/HANDOVER.md) para transferencia de conocimiento.

## Estado del proyecto
Estado: Activo  
Ultima actualizacion: 2026-05-14  
Mantenedor actual: Andres Felipe YANEZ VILLARRAGA
