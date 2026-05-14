# Documento de Transferencia de Conocimiento

## Contexto del proyecto
Esta herramienta existe para acelerar tareas recurrentes de limpieza y revision de datos maestros de clientes sin depender de usuarios tecnicos ni de notebooks manuales.

## Stakeholders clave
- Andres Felipe YANEZ VILLARRAGA: Customer Master Data Analyst y autor original.
- Daniela Pulgarin: propietaria operativa y mantenedora actual.
- Nicolas Pinzon Gualdron: propietario operativo y mantenedor actual.
- Equipo de Customer Master Data: usuarios funcionales del proceso.

## Procesos criticos
1. Limpieza operativa de archivos de clientes antes de carga o revision.
2. Verificacion de consistencia geografica para City Region y ZIP.
3. Mantenimiento de referencias locales en `reference/`.

## Problemas conocidos
- El analisis estatico del editor puede marcar imports no resueltos en `run.py` por el uso deliberado de `sys.path.insert`; la ejecucion real funciona.
- La validacion City Region depende de la cobertura del archivo `us_city_state_reference.csv`.
- La completitud de ZIP+4 automatica depende de una API externa opcional.

## Roadmap futuro
- Generar dos archivos separados en la opcion 5: uno de transformacion y otro de reporte.
- Agregar una columna resumen con estatus final por fila.
- Integrar una API real para completar ZIP+4 automaticamente.

## Contactos de soporte
- Mantenimiento funcional y operativo: Daniela.Pulgarin@sanofi.com; Nicolas.PINZONGUALDRON@sanofi.com
- Desarrollo original del proyecto: AndresFelipe.YANEZVILLARRAGA@sanofi.com
