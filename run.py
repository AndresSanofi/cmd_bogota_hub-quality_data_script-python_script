"""
Modulo: run.py
Descripcion: Menu principal para ejecutar transformaciones y verificaciones de limpieza de datos.
Autor: Andres Felipe YANEZ VILLARRAGA
Email: AndresFelipe.YANEZVILLARRAGA@sanofi.com
Fecha Creacion: 2026-05-14
Ultima Modificacion: 2026-05-14
Version: 1.0.0
"""

import sys
from datetime import datetime
from pathlib import Path

BASE_DIR   = Path(__file__).parent
INPUT_DIR  = BASE_DIR / 'input'
OUTPUT_DIR = BASE_DIR / 'output'

sys.path.insert(0, str(BASE_DIR / 'scripts'))

from _core import get_column_by_index, load_file, save_file
from address_cleaner import apply_to_dataframe as apply_street_changes
from address_cleaner import find_address_columns
from city_region_cleaner import find_city_columns, find_country_columns, find_region_columns
from city_region_cleaner import add_city_region_review, normalize_city_region_fields
from name_cleaner import apply_to_dataframe as apply_name_changes
from name_cleaner import find_name_columns
from zip_code_cleaner import add_zip_review, normalize_zip_field
from zip_code_cleaner import find_zip_columns


# ─────────────────────────────────────────────────────────────────────────────

def find_input_file():
    """Retorna el primer archivo encontrado en la carpeta input/."""
    for ext in ['*.xlsx', '*.xlsb', '*.csv']:
        files = sorted(INPUT_DIR.glob(ext))
        if files:
            return files[0]
    return None


def show_header():
    print()
    print("=" * 52)
    print("   HERRAMIENTA DE LIMPIEZA DE DATOS")
    print("=" * 52)


def ask_option():
    """Muestra el menú y devuelve la opción elegida."""
    print("\n  ¿Qué desea procesar?")
    print()
    print("    1.  Transformar Name 1")
    print("    2.  Transformar Street 1")
    print("    3.  Verificar City + Region")
    print("    4.  Verificar ZIP Code / ZIP+4")
    print("    5.  Todo el pipeline (transformacion + reporte)")
    print()
    while True:
        opcion = input("  Ingrese 1, 2, 3, 4 o 5 y presione Enter: ").strip()
        if opcion in ('1', '2', '3', '4', '5'):
            return opcion
        print("  Por favor ingrese un número válido: 1, 2, 3, 4 o 5.")


def show_columns(df):
    print("\n  Columnas disponibles en el archivo:")
    for index, column in enumerate(df.columns, start=1):
        print(f"    {index:>2}. {column}")


def ask_column(columns, label, suggested=None, optional=False):
    suggestion_text = f" [Enter = {suggested}]" if suggested else ''
    optional_text = ' o Enter para omitir' if optional and not suggested else ''
    prompt = f"\n  Seleccione la columna para {label} (número o nombre){suggestion_text}{optional_text}: "

    while True:
        value = input(prompt).strip()
        if not value:
            if suggested:
                return suggested
            if optional:
                return None

        selected = get_column_by_index(columns, value) if value else None
        if selected:
            return selected

        print("  Selección inválida. Use el número de la columna o el nombre exacto.")


def build_output_file(input_file, suffix):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return OUTPUT_DIR / f"{input_file.stem}_{suffix}_{timestamp}.xlsx"


def main():
    show_header()

    # Verificar que exista la carpeta input
    if not INPUT_DIR.exists():
        INPUT_DIR.mkdir(parents=True)

    # Buscar archivo
    input_file = find_input_file()

    if not input_file:
        print("\n  ERROR: No se encontró ningún archivo en la carpeta 'input'.")
        print("  Por favor coloque un archivo .xlsx, .xlsb o .csv allí y vuelva a correr.")
        input("\nPresione Enter para salir...")
        sys.exit(1)

    print(f"\n  Archivo encontrado: {input_file.name}")

    df = load_file(input_file)
    show_columns(df)

    opcion = ask_option()

    print()
    print("-" * 52)

    if opcion == '1':
        name_column = ask_column(df.columns, 'Name 1', suggested=next(iter(find_name_columns(df)), None))
        output_file = build_output_file(input_file, 'name1_corregido')
        df_result, result = apply_name_changes(df.copy(), selected_columns=[name_column])
        success = result['success']
        if success:
            save_file(df_result, output_file)
            print(f"\n[Corrección de Name 1]")
            print(f"  Columna: {name_column}")
            print(f"  Total corregido: {result['changes']} celda(s)")

    elif opcion == '2':
        street_column = ask_column(df.columns, 'Street 1', suggested=next(iter(find_address_columns(df)), None))
        output_file = build_output_file(input_file, 'street1_corregido')
        df_result, result = apply_street_changes(df.copy(), selected_columns=[street_column])
        success = result['success']
        if success:
            save_file(df_result, output_file)
            print(f"\n[Corrección de Street 1]")
            print(f"  Columna: {street_column}")
            print(f"  Total corregido: {result['changes']} celda(s)")

    elif opcion == '3':
        city_column = ask_column(df.columns, 'City', suggested=next(iter(find_city_columns(df)), None))
        region_column = ask_column(df.columns, 'Region/State', suggested=next(iter(find_region_columns(df)), None))
        country_column = ask_column(df.columns, 'Country', suggested=next(iter(find_country_columns(df)), None), optional=True)
        output_file = build_output_file(input_file, 'city_region_verificacion')
        df_result = df.copy()
        df_result, normalization_result = normalize_city_region_fields(
            df_result,
            city_column=city_column,
            region_column=region_column,
            country_column=country_column,
        )
        df_result, result = add_city_region_review(
            df_result,
            city_column=city_column,
            region_column=region_column,
            country_column=country_column,
        )
        success = result['success']
        if success:
            save_file(df_result, output_file)
            print(f"\n[Verificación de City + Region]")
            print(f"  City: {city_column}")
            print(f"  Region: {region_column}")
            if country_column:
                print(f"  Country: {country_column}")
            print(f"  Cambios de normalización: {normalization_result['changes']}")
            print(f"  Filas con observaciones: {result['issues']}")

    elif opcion == '4':
        zip_column = ask_column(df.columns, 'ZIP Code', suggested=next(iter(find_zip_columns(df)), None))
        city_column = ask_column(df.columns, 'City', suggested=next(iter(find_city_columns(df)), None), optional=True)
        region_column = ask_column(df.columns, 'Region/State', suggested=next(iter(find_region_columns(df)), None), optional=True)
        country_column = ask_column(df.columns, 'Country', suggested=next(iter(find_country_columns(df)), None), optional=True)
        street_column = ask_column(df.columns, 'Street 1', suggested=next(iter(find_address_columns(df)), None), optional=True)
        output_file = build_output_file(input_file, 'zip_verificacion')
        df_result = df.copy()
        df_result, normalization_result = normalize_zip_field(
            df_result,
            zip_column=zip_column,
        )
        df_result, result = add_zip_review(
            df_result,
            zip_column=zip_column,
            city_column=city_column,
            region_column=region_column,
            country_column=country_column,
            street_column=street_column,
        )
        success = result['success']
        if success:
            save_file(df_result, output_file)
            print(f"\n[Verificación de ZIP Code]")
            print(f"  ZIP Code: {zip_column}")
            print(f"  Cambios de formato: {normalization_result['changes']}")
            print(f"  Filas con observaciones: {result['issues']}")

    else:
        name_column = ask_column(df.columns, 'Name 1', suggested=next(iter(find_name_columns(df)), None), optional=True)
        street_column = ask_column(df.columns, 'Street 1', suggested=next(iter(find_address_columns(df)), None), optional=True)
        city_column = ask_column(df.columns, 'City', suggested=next(iter(find_city_columns(df)), None), optional=True)
        region_column = ask_column(df.columns, 'Region/State', suggested=next(iter(find_region_columns(df)), None), optional=True)
        country_column = ask_column(df.columns, 'Country', suggested=next(iter(find_country_columns(df)), None), optional=True)
        zip_column = ask_column(df.columns, 'ZIP Code', suggested=next(iter(find_zip_columns(df)), None), optional=True)

        output_file = build_output_file(input_file, 'pipeline_completo')
        df_result = df.copy()
        success = False
        total_issues = 0

        if name_column:
            df_result, name_result = apply_name_changes(df_result, selected_columns=[name_column])
            success = success or name_result['success']

        if street_column:
            df_result, street_result = apply_street_changes(df_result, selected_columns=[street_column])
            success = success or street_result['success']

        if city_column:
            df_result, city_transform_result = normalize_city_region_fields(
                df_result,
                city_column=city_column,
                region_column=region_column,
                country_column=country_column,
            )
            success = success or city_transform_result['success']
            if region_column:
                df_result, city_review_result = add_city_region_review(
                    df_result,
                    city_column=city_column,
                    region_column=region_column,
                    country_column=country_column,
                )
                success = success or city_review_result['success']
                total_issues += city_review_result['issues']

        if zip_column:
            df_result, zip_transform_result = normalize_zip_field(
                df_result,
                zip_column=zip_column,
            )
            success = success or zip_transform_result['success']
            df_result, zip_review_result = add_zip_review(
                df_result,
                zip_column=zip_column,
                city_column=city_column,
                region_column=region_column,
                country_column=country_column,
                street_column=street_column,
            )
            success = success or zip_review_result['success']
            total_issues += zip_review_result['issues']

        if success:
            save_file(df_result, output_file)
            print("\n[Pipeline completo]")
            print("  Se aplicaron las transformaciones seleccionadas y se agregaron columnas de verificación cuando hubo datos suficientes.")
            print(f"  Filas con observaciones en verificaciones: {total_issues}")

    print("-" * 52)

    if success:
        print(f"\n  ¡Listo! Archivo guardado en:")
        print(f"  output/{output_file.name}")
    else:
        print("\n  No se realizaron cambios. Revise los avisos anteriores.")

    input("\nPresione Enter para salir...")


if __name__ == '__main__':
    main()
