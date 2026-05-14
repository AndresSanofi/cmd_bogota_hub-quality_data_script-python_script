"""
Modulo: city_region_cleaner.py
Descripcion: Transformacion de City y verificacion de consistencia City Region contra referencias de USA.
Autor: Andres Felipe YANEZ VILLARRAGA
Email: AndresFelipe.YANEZVILLARRAGA@sanofi.com
Fecha Creacion: 2026-05-14
Ultima Modificacion: 2026-05-14
Version: 1.0.0
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _core import fix_city, load_file, normalize_country, normalize_state_code, save_file, validate_city_region


CITY_COLUMN_KEYWORDS = [
    'city',
    'ciudad',
]

REGION_COLUMN_KEYWORDS = [
    'region',
    'state',
    'province',
]

COUNTRY_COLUMN_KEYWORDS = [
    'country',
    'country/region',
    'pais',
]


def _find_columns(df, keywords):
    found = []
    for col in df.columns:
        col_lower = col.lower().strip()
        if any(keyword in col_lower for keyword in keywords):
            found.append(col)
    return found


def find_city_columns(df):
    return _find_columns(df, CITY_COLUMN_KEYWORDS)


def find_region_columns(df):
    return _find_columns(df, REGION_COLUMN_KEYWORDS)


def find_country_columns(df):
    return _find_columns(df, COUNTRY_COLUMN_KEYWORDS)


def normalize_city_region_fields(df, city_column=None, region_column=None, country_column=None):
    city_column = city_column or next(iter(find_city_columns(df)), None)
    region_column = region_column or next(iter(find_region_columns(df)), None)

    if not city_column:
        return df, {
            'success': False,
            'message': 'Se requiere una columna de City.',
            'issues': 0,
            'changes': 0,
        }

    city_original = df[city_column].copy()
    df[city_column] = df[city_column].apply(fix_city)

    if region_column:
        region_original = df[region_column].copy()
        df[region_column] = df[region_column].apply(normalize_state_code)
        region_changes = (region_original.fillna('') != df[region_column].fillna('')).sum()
    else:
        region_changes = 0

    if country_column:
        country_original = df[country_column].copy()
        df[country_column] = df[country_column].apply(normalize_country)
        country_changes = (country_original.fillna('') != df[country_column].fillna('')).sum()
    else:
        country_changes = 0

    total_changes = (
        (city_original.fillna('') != df[city_column].fillna('')).sum() +
        region_changes +
        country_changes
    )

    return df, {
        'success': True,
        'message': '',
        'issues': 0,
        'changes': int(total_changes),
        'city_column': city_column,
        'region_column': region_column,
        'country_column': country_column,
    }


def add_city_region_review(df, city_column=None, region_column=None, country_column=None):
    city_column = city_column or next(iter(find_city_columns(df)), None)
    region_column = region_column or next(iter(find_region_columns(df)), None)

    if not city_column or not region_column:
        return df, {
            'success': False,
            'message': 'Se requieren columnas de City y Region para la verificacion.',
            'issues': 0,
            'changes': 0,
        }

    reviews = []
    suggestions = []
    reference_states = []

    for row in df[[city_column, region_column] + ([country_column] if country_column else [])].fillna('').itertuples(index=False):
        city_value = row[0]
        region_value = row[1]
        country_value = row[2] if country_column else ''
        result = validate_city_region(city_value, region_value, country_value)
        reviews.append('OK' if not result['issues'] else '; '.join(result['issues']))
        suggestions.append(result['suggested_region'])
        reference_states.append(', '.join(result['reference_states']))

    df['City/Region Review'] = reviews
    df['Region Suggested'] = suggestions
    df['City Reference States'] = reference_states

    issue_count = sum(1 for item in reviews if item != 'OK')

    return df, {
        'success': True,
        'message': '',
        'issues': int(issue_count),
        'changes': 0,
        'city_column': city_column,
        'region_column': region_column,
        'country_column': country_column,
    }


def apply_to_dataframe(df, city_column=None, region_column=None, country_column=None):
    df, normalization_result = normalize_city_region_fields(
        df,
        city_column=city_column,
        region_column=region_column,
        country_column=country_column,
    )

    if not normalization_result['success']:
        return df, normalization_result

    if normalization_result['region_column']:
        df, review_result = add_city_region_review(
            df,
            city_column=normalization_result['city_column'],
            region_column=normalization_result['region_column'],
            country_column=normalization_result['country_column'],
        )
        if not review_result['success']:
            return df, review_result
        review_result['changes'] = normalization_result['changes']
        return df, review_result

    normalization_result['message'] = 'City normalizada. Verificacion omitida por falta de Region.'
    return df, normalization_result


def run(input_path, output_path, city_column=None, region_column=None, country_column=None):
    input_path = Path(input_path)
    output_path = Path(output_path)

    print(f"\n[Revisión de City + Region]")
    print(f"  Leyendo: {input_path.name}")

    df = load_file(input_path)
    df, result = apply_to_dataframe(
        df,
        city_column=city_column,
        region_column=region_column,
        country_column=country_column,
    )

    if not result['success']:
        print('  AVISO: No se pudieron identificar City y Region.')
        print(f"  Columnas disponibles: {list(df.columns)}")
        return False

    print(f"  City: {result['city_column']}")
    print(f"  Region: {result['region_column']}")
    if result['country_column']:
        print(f"  Country: {result['country_column']}")
    print(f"  Cambios de normalización: {result['changes']}")
    print(f"  Filas con observaciones: {result['issues']}")

    save_file(df, output_path)
    return True