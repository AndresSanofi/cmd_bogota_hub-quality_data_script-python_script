"""
Modulo: zip_code_cleaner.py
Descripcion: Transformacion de ZIP Code y verificacion de calidad ZIP y ZIP+4.
Autor: Andres Felipe YANEZ VILLARRAGA
Email: AndresFelipe.YANEZVILLARRAGA@sanofi.com
Fecha Creacion: 2026-05-14
Ultima Modificacion: 2026-05-14
Version: 1.0.0
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _core import (
    load_file,
    lookup_zip_plus4_via_api,
    normalize_zip_code,
    save_file,
    validate_zip_code,
)


ZIP_COLUMN_KEYWORDS = [
    'postal code',
    'zip code',
    'zipcode',
    'zip',
    'postal',
]


def _find_columns(df, keywords):
    found = []
    for col in df.columns:
        col_lower = col.lower().strip()
        if any(keyword in col_lower for keyword in keywords):
            found.append(col)
    return found


def find_zip_columns(df):
    return _find_columns(df, ZIP_COLUMN_KEYWORDS)


def normalize_zip_field(df, zip_column=None):
    zip_column = zip_column or next(iter(find_zip_columns(df)), None)

    if not zip_column:
        return df, {
            'success': False,
            'message': 'Se requiere una columna de ZIP Code.',
            'issues': 0,
            'changes': 0,
        }

    original_zip = df[zip_column].copy()
    df[zip_column] = df[zip_column].apply(normalize_zip_code)

    total_changes = (original_zip.fillna('') != df[zip_column].fillna('')).sum()

    return df, {
        'success': True,
        'message': '',
        'issues': 0,
        'changes': int(total_changes),
        'zip_column': zip_column,
    }


def add_zip_review(df, zip_column=None, city_column=None, region_column=None, country_column=None, street_column=None):
    zip_column = zip_column or next(iter(find_zip_columns(df)), None)

    if not zip_column:
        return df, {
            'success': False,
            'message': 'Se requiere una columna de ZIP Code.',
            'issues': 0,
            'changes': 0,
        }

    reviews = []
    suggestions = []
    api_values = []
    api_statuses = []

    required_columns = [zip_column]
    for optional_column in [city_column, region_column, country_column, street_column]:
        if optional_column:
            required_columns.append(optional_column)

    for row in df[required_columns].fillna('').itertuples(index=False):
        zip_value = row[0]
        city_value = row[1] if city_column else ''
        region_value = row[2] if region_column else ''
        country_index = 3 if city_column and region_column else 1 if country_column and not city_column and not region_column else None
        street_value = row[-1] if street_column else ''

        if country_column:
            if city_column and region_column:
                country_value = row[3]
            elif city_column or region_column:
                country_value = row[2]
            else:
                country_value = row[1]
        else:
            country_value = ''

        result = validate_zip_code(zip_value, region=region_value, country=country_value)
        reviews.append('OK' if not result['issues'] else '; '.join(result['issues']))
        suggestions.append(result['suggested_zip'])

        if reuses_api_lookup(zip_value, street_value, city_value, region_value):
            api_zip, api_status = lookup_zip_plus4_via_api(street_value, city_value, region_value, zip_value)
        else:
            api_zip, api_status = '', 'No aplica o faltan datos para ZIP+4'

        api_values.append(api_zip)
        api_statuses.append(api_status)

    df['ZIP Review'] = reviews
    df['ZIP Suggested'] = suggestions
    df['ZIP+4 API'] = api_values
    df['ZIP+4 Status'] = api_statuses

    issue_count = sum(1 for item in reviews if item != 'OK')

    return df, {
        'success': True,
        'message': '',
        'issues': int(issue_count),
        'changes': 0,
        'zip_column': zip_column,
    }


def apply_to_dataframe(df, zip_column=None, city_column=None, region_column=None, country_column=None, street_column=None):
    df, normalization_result = normalize_zip_field(df, zip_column=zip_column)

    if not normalization_result['success']:
        return df, normalization_result

    df, review_result = add_zip_review(
        df,
        zip_column=normalization_result['zip_column'],
        city_column=city_column,
        region_column=region_column,
        country_column=country_column,
        street_column=street_column,
    )
    if not review_result['success']:
        return df, review_result

    review_result['changes'] = normalization_result['changes']
    return df, review_result


def reuses_api_lookup(zip_value, street_value, city_value, region_value):
    zip_value = str(zip_value).strip()
    if not zip_value:
        return False
    if len(zip_value) == 10 and zip_value.endswith('-0000'):
        return True
    if len(zip_value) == 5 and street_value and city_value and region_value:
        return True
    return False


def run(input_path, output_path, zip_column=None, city_column=None, region_column=None, country_column=None, street_column=None):
    input_path = Path(input_path)
    output_path = Path(output_path)

    print(f"\n[Revisión de ZIP Code]")
    print(f"  Leyendo: {input_path.name}")

    df = load_file(input_path)
    df, result = apply_to_dataframe(
        df,
        zip_column=zip_column,
        city_column=city_column,
        region_column=region_column,
        country_column=country_column,
        street_column=street_column,
    )

    if not result['success']:
        print('  AVISO: No se pudo identificar la columna de ZIP Code.')
        print(f"  Columnas disponibles: {list(df.columns)}")
        return False

    print(f"  ZIP Code: {result['zip_column']}")
    print(f"  Cambios de formato: {result['changes']}")
    print(f"  Filas con observaciones: {result['issues']}")

    save_file(df, output_path)
    return True