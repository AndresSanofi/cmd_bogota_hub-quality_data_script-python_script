"""
Modulo: _core.py
Descripcion: Funciones compartidas para transformacion, normalizacion y verificacion de datos maestros.
Autor: Andres Felipe YANEZ VILLARRAGA
Email: AndresFelipe.YANEZVILLARRAGA@sanofi.com
Fecha Creacion: 2026-05-14
Ultima Modificacion: 2026-05-14
Version: 1.0.0
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from urllib import error, request

import pandas as pd


# ─────────────────────────────────────────────────────────────────────────────
# ABREVIACIONES ESTÁNDAR DE DIRECCIONES (completo → abreviado)
# Se cargan desde  reference/address_abbreviations.csv
# Si ese archivo no existe se usa la lista de respaldo interna.
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
LOCAL_REFERENCE_DIR = BASE_DIR / 'reference'
ROOT_REFERENCE_DIR = BASE_DIR.parent / 'reference'

_ADDRESS_ABBREVIATIONS_CSV = 'address_abbreviations.csv'
_NAME_ABBREVIATIONS_CSV = 'name_abbreviations.csv'
_US_STATES_CSV = 'us_states.csv'
_ZIP_PREFIX_CSV = 'zip_prefix_regions.csv'
_CITY_STATE_REFERENCE_CSV = 'us_city_state_reference.csv'

_FALLBACK_ABBREVIATIONS = {
    'AVENUE': 'AVE', 'STREET': 'ST', 'BOULEVARD': 'BLVD',
    'DRIVE': 'DR', 'ROAD': 'RD', 'PARKWAY': 'PKWY',
    'LANE': 'LN', 'APARTMENT': 'APT', 'SUITE': 'STE',
    'NORTH': 'N', 'SOUTH': 'S', 'WEST': 'W', 'EAST': 'E',
    'COURT': 'CR', 'TERRACE': 'TERR', 'CIRCLE': 'CIR',
    'PLACE': 'PL', 'TRAIL': 'TRL', 'BUILDING': 'BLDG', 'FREEWAY': 'FWY',
}

_FALLBACK_NAME_ABBREVIATIONS = {
    'HOSPITAL': 'HSPTL',
    'HOSP': 'HSPTL',
    'CENTER': 'CTR',
    'CENTRE': 'CTR',
    'CLINIC': 'CLNC',
    'MEDICAL': 'MED',
    'UNIVERSITY': 'UNIV',
    'SAINT': 'ST',
    'MOUNT': 'MT',
    'ASSOCIATION': 'ASSN',
    'COMPANY': 'CO',
    'CORPORATION': 'CORP',
    'LIMITED': 'LTD',
}

_US_COUNTRY_VALUES = {
    'US',
    'USA',
    'UNITED STATES',
    'UNITED STATES OF AMERICA',
}

_STATE_CODE_TO_NAME: dict[str, str] = {}
_STATE_NAME_TO_CODE: dict[str, str] = {}
_CITY_STATE_LOOKUP: dict[str, set[str]] | None = None
_ZIP_PREFIX_MAPPING: dict[str, set[str]] | None = None


def _find_reference_file(file_name: str) -> Path | None:
    for base_dir in (LOCAL_REFERENCE_DIR, ROOT_REFERENCE_DIR):
        candidate = base_dir / file_name
        if candidate.exists():
            return candidate
    return None


def _load_abbreviations(file_name: str, fallback: dict[str, str]):
    """
    Lee un CSV de abreviaciones y devuelve un diccionario
    { 'FULL_WORD': 'ABBR', ... }.
    Si el archivo no existe o tiene un error, usa la lista de respaldo.
    """
    csv_path = _find_reference_file(file_name)
    if not csv_path:
        return fallback.copy()
    try:
        df = pd.read_csv(csv_path, dtype=str).dropna()
        df.columns = [c.strip().lower() for c in df.columns]
        result = {}
        for _, row in df.iterrows():
            full = str(row['full_word']).strip().upper()
            abbr = str(row['abbreviation']).strip().upper()
            if full and abbr and full != abbr:
                result[full] = abbr
        return result if result else fallback.copy()
    except Exception:
        return fallback.copy()


def _load_states():
    global _STATE_CODE_TO_NAME, _STATE_NAME_TO_CODE

    csv_path = _find_reference_file(_US_STATES_CSV)
    if not csv_path:
        _STATE_CODE_TO_NAME = {}
        _STATE_NAME_TO_CODE = {}
        return

    df = pd.read_csv(csv_path, dtype=str).fillna('')
    _STATE_CODE_TO_NAME = {
        str(row['state_code']).strip().upper(): str(row['state_name']).strip().upper()
        for _, row in df.iterrows()
        if str(row['state_code']).strip()
    }
    _STATE_NAME_TO_CODE = {
        state_name: state_code
        for state_code, state_name in _STATE_CODE_TO_NAME.items()
    }


def _load_city_state_lookup() -> dict[str, set[str]]:
    global _CITY_STATE_LOOKUP

    if _CITY_STATE_LOOKUP is not None:
        return _CITY_STATE_LOOKUP

    csv_path = _find_reference_file(_CITY_STATE_REFERENCE_CSV)
    if not csv_path:
        _CITY_STATE_LOOKUP = {}
        return _CITY_STATE_LOOKUP

    df = pd.read_csv(csv_path, dtype=str).fillna('')
    lookup: dict[str, set[str]] = {}
    for _, row in df.iterrows():
        city = normalize_city_for_lookup(row.get('normalized_city') or row.get('city'))
        state_code = normalize_state_code(row.get('state_code'))
        if not city or not state_code:
            continue
        lookup.setdefault(city, set()).add(state_code)

    _CITY_STATE_LOOKUP = lookup
    return _CITY_STATE_LOOKUP


def _load_zip_prefix_mapping() -> dict[str, set[str]]:
    global _ZIP_PREFIX_MAPPING

    if _ZIP_PREFIX_MAPPING is not None:
        return _ZIP_PREFIX_MAPPING

    csv_path = _find_reference_file(_ZIP_PREFIX_CSV)
    if not csv_path:
        _ZIP_PREFIX_MAPPING = {}
        return _ZIP_PREFIX_MAPPING

    df = pd.read_csv(csv_path, dtype=str).fillna('')
    mapping: dict[str, set[str]] = {}
    for _, row in df.iterrows():
        prefix = str(row.get('zip_prefix', '')).strip()
        states = {
            token.strip().upper()
            for token in str(row.get('states_description', '')).split(',')
            if token.strip()
        }
        if prefix:
            mapping[prefix] = states

    _ZIP_PREFIX_MAPPING = mapping
    return _ZIP_PREFIX_MAPPING


ADDRESS_ABBREVIATIONS = _load_abbreviations(_ADDRESS_ABBREVIATIONS_CSV, _FALLBACK_ABBREVIATIONS)
NAME_ABBREVIATIONS = _load_abbreviations(_NAME_ABBREVIATIONS_CSV, _FALLBACK_NAME_ABBREVIATIONS)
_load_states()


def normalize_spaces(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def apply_abbreviation_map(text: str, abbreviation_map: dict[str, str]) -> str:
    result = text
    for full_word in sorted(abbreviation_map, key=len, reverse=True):
        abbr = abbreviation_map[full_word]
        if full_word == abbr:
            continue
        result = re.sub(rf'\b{re.escape(full_word)}\b', abbr, result)
    return result


def normalize_state_code(value) -> str:
    if pd.isna(value) or str(value).strip() == '':
        return ''

    raw = normalize_spaces(str(value).upper())
    if raw in _STATE_CODE_TO_NAME:
        return raw
    if raw in _STATE_NAME_TO_CODE:
        return _STATE_NAME_TO_CODE[raw]
    return raw


def normalize_country(value) -> str:
    if pd.isna(value) or str(value).strip() == '':
        return ''
    return normalize_spaces(str(value).upper())


def is_us_country(value) -> bool:
    return normalize_country(value) in _US_COUNTRY_VALUES


def fix_city(text):
    if pd.isna(text) or str(text).strip() == '':
        return text
    result = str(text).strip().upper()
    result = re.sub(r'[^A-Z0-9\s\-\.]', ' ', result)
    return normalize_spaces(result)


def normalize_city_for_lookup(value) -> str:
    city = fix_city(value)
    if pd.isna(city):
        return ''
    result = str(city)
    result = re.sub(r'[^A-Z0-9\s]', ' ', result)
    return normalize_spaces(result)


# ─────────────────────────────────────────────────────────────────────────────
# CORRECCIÓN DE NOMBRES
# ─────────────────────────────────────────────────────────────────────────────

def fix_name(text):
    """
    Corrige un nombre de cuenta.

    Reglas aplicadas (en orden):
      1. Convierte a MAYÚSCULAS
      2. & → AND
      3. Guión entre dos dígitos → espacio  (ej: "ROOM 2-3" → "ROOM 2 3")
      4. Símbolos que se convierten en espacio: # . , ( ) / @ ! ? : ; _ \\ 
         (ej: "Clinical Farmacy#1" → "CLINICAL FARMACY 1")
      5. Elimina cualquier otro símbolo especial restante (ej: comillas, ')
      6. Normaliza espacios dobles o triples

    Ejemplos:
      "Clinical Farmacy#1"  → "CLINICAL FARMACY 1"
      "St. Mary's Hospital" → "ST MARYS HOSPITAL"
      "Health & Wellness"   → "HEALTH AND WELLNESS"
      "Lab (North)"         → "LAB NORTH"
    """
    if pd.isna(text) or str(text).strip() == '':
        return text

    result = str(text).strip().upper()
    result = re.sub(r'\s*&\s*', ' AND ', result)
    result = re.sub(r'(\d)[\-/](\d)', r'\1 \2', result)
    result = re.sub(r"['\"`]", '', result)
    result = re.sub(r'[#,()/@!?:;_\\.]', ' ', result)
    result = re.sub(r'(?<=[A-Z0-9])-(?=[A-Z0-9])', ' ', result)
    result = re.sub(r'[^A-Z0-9\s]', '', result)
    result = normalize_spaces(result)
    result = apply_abbreviation_map(result, NAME_ABBREVIATIONS)
    return normalize_spaces(result)


# ─────────────────────────────────────────────────────────────────────────────
# CORRECCIÓN DE DIRECCIONES
# ─────────────────────────────────────────────────────────────────────────────

def fix_address(text):
    """
    Corrige una dirección.

    Reglas aplicadas (en orden):
      1. Convierte a MAYÚSCULAS
      2. Aplica abreviaciones estándar (SUITE→STE, AVENUE→AVE, STREET→ST, etc.)
      3. Elimina símbolos no permitidos — conserva: # / - .
      4. Normaliza espacios

    Ejemplos:
      "123 Main Suite 4"      → "123 MAIN STE 4"
      "456 Oak Avenue"        → "456 OAK AVE"
      "789 North Boulevard"   → "789 N BLVD"
      "Apt. 12, 5th Street"   → "APT 12 5TH ST"
    """
    if pd.isna(text) or str(text).strip() == '':
        return text

    result = str(text).strip().upper()
    result = re.sub(r'[(),;:_\\]', ' ', result)
    result = re.sub(r'(?<=\w)#(?=\w)', ' # ', result)
    result = apply_abbreviation_map(result, ADDRESS_ABBREVIATIONS)
    result = re.sub(r'[^A-Z0-9\s#/\.\-]', '', result)
    return normalize_spaces(result)


def normalize_zip_code(value) -> str:
    if pd.isna(value) or str(value).strip() == '':
        return ''

    raw = str(value).strip()
    digits = re.sub(r'\D', '', raw)

    if len(digits) == 5:
        return digits
    if len(digits) == 9:
        return f'{digits[:5]}-{digits[5:]}'
    if re.match(r'^\d{5}-\d{4}$', raw):
        return raw
    return raw.upper()


def validate_city_region(city, region, country=None):
    city_value = fix_city(city)
    region_value = normalize_state_code(region)
    country_value = normalize_country(country)
    issues = []
    suggestion = ''
    reference_states = []

    if country_value and country_value not in _US_COUNTRY_VALUES:
        issues.append('COUNTRY NO ES USA')

    if region_value and region_value not in _STATE_CODE_TO_NAME:
        issues.append('REGION NO ES ESTADO/TERRITORIO US')

    normalized_city = normalize_city_for_lookup(city_value)
    if normalized_city:
        reference_states = sorted(_load_city_state_lookup().get(normalized_city, set()))
        if not reference_states:
            issues.append('CITY NO EN REFERENCIA US')
        elif region_value and region_value not in reference_states:
            issues.append(f'CITY/STATE MISMATCH: CITY VALIDA EN {", ".join(reference_states)}')
            if len(reference_states) == 1:
                suggestion = reference_states[0]

    return {
        'city': city_value,
        'region': region_value,
        'country': country_value,
        'issues': issues,
        'reference_states': reference_states,
        'suggested_region': suggestion,
    }


def validate_zip_code(zipcode, region=None, country=None):
    normalized_zip = normalize_zip_code(zipcode)
    region_value = normalize_state_code(region)
    country_value = normalize_country(country)
    issues = []
    suggestion = ''

    if country_value and country_value not in _US_COUNTRY_VALUES:
        issues.append('COUNTRY NO ES USA')

    if not normalized_zip:
        issues.append('SIN ZIP CODE')
        return {
            'zip_code': normalized_zip,
            'issues': issues,
            'suggested_zip': suggestion,
        }

    if not re.match(r'^\d{5}(-\d{4})?$|^\d{9}$', normalized_zip):
        issues.append('FORMATO INVALIDO')
    elif re.match(r'^\d{5}-0000$', normalized_zip):
        issues.append('ZIP+4 INCOMPLETO (-0000)')
        suggestion = normalized_zip[:5] + '-XXXX'

    if re.match(r'^\d{5}(-\d{4})?$', normalized_zip) and region_value in _STATE_CODE_TO_NAME:
        expected_states = _load_zip_prefix_mapping().get(normalized_zip[0], set())
        if expected_states and region_value not in expected_states:
            issues.append(f'ZIP/STATE MISMATCH: ESPERADO {", ".join(sorted(expected_states))}')

    return {
        'zip_code': normalized_zip,
        'issues': issues,
        'suggested_zip': suggestion,
    }


def lookup_zip_plus4_via_api(street, city, region, zip_code):
    api_url = os.getenv('ZIP4_API_URL', '').strip()
    api_key = os.getenv('ZIP4_API_KEY', '').strip()
    api_key_header = os.getenv('ZIP4_API_KEY_HEADER', 'Authorization').strip() or 'Authorization'

    if not api_url:
        return '', 'API no configurada'

    street_value = fix_address(street)
    city_value = fix_city(city)
    region_value = normalize_state_code(region)
    zip_value = normalize_zip_code(zip_code)

    if not street_value or not city_value or not region_value:
        return '', 'Faltan datos de address/city/state para consultar ZIP+4'

    payload = {
        'street': street_value,
        'city': city_value,
        'state': region_value,
        'zip_code': zip_value,
    }
    body = json.dumps(payload).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    if api_key:
        headers[api_key_header] = api_key

    try:
        req = request.Request(api_url, data=body, headers=headers, method='POST')
        with request.urlopen(req, timeout=20) as response:
            data = json.loads(response.read().decode('utf-8'))
    except error.HTTPError as exc:
        return '', f'API error HTTP {exc.code}'
    except Exception as exc:
        return '', f'API error: {exc}'

    zip_plus4 = _extract_zip_plus4_from_payload(data)
    if zip_plus4:
        return zip_plus4, 'ZIP+4 encontrado por API'
    return '', 'API respondio sin ZIP+4 utilizable'


def _extract_zip_plus4_from_payload(payload):
    if isinstance(payload, dict):
        direct_keys = [
            'zip_plus4',
            'zipcode_plus4',
            'postal_code_plus4',
            'zip4',
            'plus4',
        ]
        for key in direct_keys:
            value = payload.get(key)
            if value:
                return normalize_zip_code(value)

        zip_code = payload.get('zip_code') or payload.get('zipcode') or payload.get('postal_code')
        plus4 = payload.get('plus4') or payload.get('plus_4') or payload.get('zip4')
        if zip_code and plus4:
            digits = re.sub(r'\D', '', str(zip_code) + str(plus4))
            if len(digits) == 9:
                return normalize_zip_code(digits)

        for value in payload.values():
            extracted = _extract_zip_plus4_from_payload(value)
            if extracted:
                return extracted

    if isinstance(payload, list):
        for item in payload:
            extracted = _extract_zip_plus4_from_payload(item)
            if extracted:
                return extracted

    return ''


def get_column_by_index(columns, value: str):
    if value.isdigit():
        idx = int(value)
        if 1 <= idx <= len(columns):
            return columns[idx - 1]
    for column in columns:
        if column.lower() == value.lower().strip():
            return column
    return None


# ─────────────────────────────────────────────────────────────────────────────
# UTILIDADES DE ARCHIVO
# ─────────────────────────────────────────────────────────────────────────────

def load_file(path):
    """
    Carga un archivo .xlsx, .xlsb o .csv como DataFrame.
    Todos los valores se cargan como texto (str) para preservar el formato.
    """
    path = str(path)
    ext = path.lower().rsplit('.', 1)[-1]

    if ext == 'xlsb':
        return pd.read_excel(path, engine='pyxlsb', dtype=str)
    elif ext in ('xlsx', 'xls'):
        return pd.read_excel(path, dtype=str)
    elif ext == 'csv':
        for sep in [',', ';', '\t']:
            for enc in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    df = pd.read_csv(path, sep=sep, dtype=str, encoding=enc)
                    if len(df.columns) > 1:
                        return df
                except Exception:
                    continue
        raise ValueError(f"No se pudo leer el CSV: {path}")
    else:
        raise ValueError(f"Formato no soportado: .{ext}  (use .xlsx, .xlsb o .csv)")


def save_file(df, path):
    """Guarda el DataFrame como .xlsx."""
    from pathlib import Path
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(path, index=False)
    print(f"  Guardado: {Path(path).name}")
